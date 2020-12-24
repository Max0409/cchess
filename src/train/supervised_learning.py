import os
import pandas as pd
import numpy as np
from collections import deque
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from logging import getLogger
from time import time
from time import sleep
from random import shuffle

from cchess_alphazero.agent.model import CChessModel
from cchess_alphazero.config import Config
from cchess_alphazero.lib.data_helper import get_game_data_filenames, read_game_data_from_file
from cchess_alphazero.lib.model_helper import load_sl_best_model_weight, save_as_sl_best_model
from cchess_alphazero.environment.env import CChessEnv
from cchess_alphazero.environment.lookup_tables import ActionLabelsRed, flip_policy, flip_move
from cchess_alphazero.lib.tf_util import set_session_config

from keras.optimizers import Adam
from keras.callbacks import TensorBoard
import keras.backend as K

logger = getLogger(__name__)

def start(config: Config):
    set_session_config(per_process_gpu_memory_fraction=1, allow_growth=True, device_list='0,1')
    return SupervisedLearingWorker(config).start()

class SupervisedLearingWorker:
    def __init__(self, config:Config):
        self.config = config
        self.model = None
        self.loaded_data = deque(maxlen=self.config.trainer.dataset_size)
        self.dataset = deque(), deque(), deque()
        self.filenames = []
        self.opt = None
        self.buffer = []
        self.gameinfo = None
        self.moves = None
        self.config.opts.light = True

    def start(self):
        self.model = self.load_model()
        self.gameinfo = pd.read_csv(self.config.resource.sl_data_gameinfo)
        self.moves = pd.read_csv(self.config.resource.sl_data_move)
        self.training()

    def training(self):
        self.load_model()
        total_steps = self.config.trainer.start_total_steps
        logger.info(f"Start training, game count = {len(self.gameinfo)}, step = {self.config.trainer.sl_game_step} games")

        for i in range(0, len(self.gameinfo), self.config.trainer.sl_game_step):
            games = self.gameinfo[i:i+self.config.trainer.sl_game_step]
            self.fill_sampling_pool(games)
            if len(self.dataset[0]) > self.config.trainer.batch_size:
                steps = self.train_single_epoch(self.config.trainer.epoch_to_checkpoint)
                total_steps += steps
                self.save_model()
                data1, data2, data3 = self.dataset
                data1.clear()
                data2.clear()
                data3.clear()

    def train_single_epoch(self, epochs):
        state_array, policy_array, value_array = self.gather_loaded_data()
        config_trainer=self.config.trainer
        tensor_board = TensorBoard(log_dir="./logs/tensorboard_sl/", batch_size=config_trainer.batch_size, histogram_freq=1)
        self.model.model.fit(state_array, [policy_array, value_array],
                             batch_size=config_trainer.batch_size,
                             epochs=epochs,
                             shuffle=True,
                             validation_split=0.02,
                             callbacks=[tensor_board])
        return (state_array.shape[0] // config_trainer.batch_size) * epochs
       

    def load_model(self):
        self.opt = Adam(lr=1e-2)
        losses = ['categorical_crossentropy', 'mean_squared_error']
        self.model.model.compile(optimizer=self.opt, loss=losses, loss_weights=self.config.trainer.loss_weights)
        
    def gather_loaded_data(self):
        state_array, policy_array, value_array = self.dataset
        tmp_state_array = np.asarray(state_array, dtype=np.float32)
        tmp_policy_array = np.asarray(policy_array, dtype=np.float32)
        tmp_value_array = np.asarray(value_array, dtype=np.float32)
        return tmp_state_array, tmp_policy_array, tmp_value_array


    def fill_sampling_pool(self, games):
        _element = self.sample_a_game(games)
        if _element is not None:
            for x, y in zip(self.dataset, _element):
                x.extend(y)

    def load_model(self):
        model = CChessModel(self.config)
        if self.config.opts.new or not load_sl_best_model_weight(model):
            model.build()
            save_as_sl_best_model(model)
        return model

    def save_model(self):
        save_as_sl_best_model(self.model)

    def sample_a_game(self, games):
        self.buffer = []
        for idx, game in games.iterrows():
            game_id = game['gameID']
            winner_id = game['winner']
            move = self.moves[self.moves.gameID == game_id]
            red_flag = move[move.side == 'red']
            black_flag = move[move.side == 'black']
            self.load_game(red_flag, black_flag, winner_id, idx)
        return self.transform_game_info_to_traing_data()

    def load_game(self, red, black, winner, idx):
        env = CChessEnv(self.config).reset()
        red_moves = []
        black_moves = []
        turns = 1
        black_max_turn = black['turn'].max()
        red_max_turn = red['turn'].max()

        while turns < black_max_turn or turns < red_max_turn:
            if turns < red_max_turn:
                wxf_move = red[red.turn == turns]['move'].item()
                action = env.board.parse_WXF_move(wxf_move)
                try:
                    red_moves.append([env.observation, self.set_policy(action, flip=False)])
                except Exception as e:
                    for i in range(10):
                        logger.debug(f"{env.board.screen[i]}")
                    logger.debug(f"{turns} {wxf_move} {action}")
                
                env.step(action)
            if turns < black_max_turn:
                wxf_move = black[black.turn == turns]['move'].item()
                action = env.board.parse_WXF_move(wxf_move)
                try:
                    black_moves.append([env.observation, self.set_policy(action, flip=True)])
                except Exception as e:
                    for i in range(10):
                        logger.debug(f"{env.board.screen[i]}")
                    logger.debug(f"{turns} {wxf_move} {action}")
                
                env.step(action)
            turns += 1

        if winner == 'red':
            red_win = 1
        elif winner == 'black':
            red_win = -1
        else:
            red_win = 0

        for move in red_moves:
            move += [red_win]
        for move in black_moves:
            move += [-red_win]

        data = []
        for i in range(len(red_moves)):
            data.append(red_moves[i])
            if i < len(black_moves):
                data.append(black_moves[i])
        self.buffer += data
   

    def transform_game_info_to_traing_data(self):
        buffer = self.buffer
        state_array = []
        policy_array = []
        value_array = []
        env = CChessEnv()

        for state_fen, policy, value in buffer:
            state_planning = env.fen_to_planes(state_fen)
            supervised_learing_value = value
            state_array .append(state_planning)
            policy_array.append(policy)
            value_array.append(supervised_learing_value)

        return np.asarray(state_array, dtype=np.float32), \
               np.asarray(policy_array, dtype=np.float32), \
               np.asarray(value_array, dtype=np.float32)

    def set_policy(self, action, flip_flag):
        labels = len(ActionLabelsRed)
        move_lookup = {move: i for move, i in zip(ActionLabelsRed, range(labels))}
        policy = np.zeros(labels)
        policy[move_lookup[action]] = 1
        if flip_flag:
            policy = flip_policy(policy)
        return policy



