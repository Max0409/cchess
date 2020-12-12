from util.logger import logger
from cchesslib.chessboard import Chessboard


class Point:
    def __init__(self, x: int = None, y: int = None) -> None:
        self.x = x
        self.y = y


class Chessman:
    def __init__(self, name_en: str, name_cn: str, color: bool, token: str, chessboard: Chessboard = None) -> None:
        self.__name_en: str = name_en  # english name of the chessman
        self.__name_cn: str = name_cn  # chinese name of the chessman
        self.__color: bool = color  # color of the chessman: True for red and Flase for black
        self.__chessboard: Chessboard = chessboard  # chessboard for the chessman
        # the token to display the chessman while printing chessboard in CLI, such as 'R','r','C'
        self.__token: str = token
        self.__position: Point = Point()  # the position (x, y) of the chesman
        self.__moving_list: list = []  # the list of all legal movings for the chessman
        self.__top: int = 9  # the location limit of the chessman
        self.__bottom: int = 0
        self.__left: int = 0
        self.__right: int = 8
        self.__is_alive: bool = True  # is the chessman alive

    @property
    def row_num(self) -> int:
        return self.__position.y

    @property
    def col_num(self) -> int:
        return self.__position.x

    @property
    def is_alive(self) -> bool:
        return self.__is_alive

    @is_alive.setter
    def is_alive(self, is_alive) -> None:
        self.__is_alive = is_alive

    @property
    def chessboard(self) -> Chessboard:
        return self.__chessboard

    @property
    def is_red(self) -> bool:
        return self.__is_red

    @property
    def name_en(self) -> str:
        return self.__name_en

    @property
    def name_cn(self) -> str:
        return self.__name_cn

    @property
    def position(self) -> Point:
        return self.__position

    @property
    def moving_list(self) -> list:
        return self.__moving_list

    @property
    def token(self) -> str:
        return self.__token

    # reset the chessboard
    def reset_chessboard(self, chessboard: Chessboard) -> None:
        self.__chessboard = chessboard

    # clear the moving_list
    def clear_moving_list(self) -> None:
        self.__moving_list = []

    # check border of the chessman, return True if given position is legal
    def border_check(self, col_num: int, row_num: int) -> bool:
        return self.__top >= row_num and self.__bottom <= row_num and\
            self.__right >= col_num and self.__left <= col_num

    # put the chessman on a chessboard
    def put_on_chessboard(self, col_num: int, row_num: int, chessboard: Chessboard) -> None:
        if self.border_check(col_num, row_num):
            self.__position.x = col_num
            self.__position.y = row_num
            self.__chessboard = chessboard
        else:
            logger.warning(
                f"In put_on_chessboard: chess {self.name_en} cannot be put at ({col_num}, {row_num})")
