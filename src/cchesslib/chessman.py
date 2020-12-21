from util.logger import logger
from cchesslib.chessboard import Chessboard


class Point:

    def __init__(self, x: int = None, y: int = None) -> None:
        self.x = x
        self.y = y


def generate_sqaure(list_points, list_vs, list_hs):
    for v in list_vs:
        for h in list_hs:
            list_points.append(Point(v, h))


class Chessman:

    def __init__(self,
                 name_en: str,
                 name_cn: str,
                 color: bool,
                 token: str,
                 chessboard: Chessboard = None) -> None:
        self.__name_en: str = name_en  # english name of the chessman
        self.__name_cn: str = name_cn  # chinese name of the chessman
        self.__color: bool = color  # color of the chessman: True for red and Flase for black
        self.__chessboard: Chessboard = chessboard  # chessboard for the chessman
        # the token to display the chessman while printing chessboard in CLI, such as 'R','r','C'
        self.__token: str = token
        self.__position: Point = Point()  # the position (x, y) of the chesman
        self.__moving_list: list = [
        ]  # the list of all legal movings for the chessman
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
        return self.__color

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

    def reset_chessboard(self, chessboard: Chessboard) -> None:
        '''reset the chessboard'''
        self.__chessboard = chessboard

    def clear_moving_list(self) -> None:
        '''clear the moving_list'''
        self.__moving_list = []

    def border_check(self, col_num: int, row_num: int) -> bool:
        '''pcheck border of the chessman, return True if given position is legal'''
        return self.__top >= row_num and self.__bottom <= row_num and\
            self.__right >= col_num and self.__left <= col_num

    def put_on_chessboard(self, col_num: int, row_num: int,
                          chessboard: Chessboard) -> None:
        '''put the chessman on a chessboard'''
        if self.border_check(col_num, row_num):
            self.__position.x = col_num
            self.__position.y = row_num
            self.__chessboard = chessboard
        else:
            logger.warning(
                f"In put_on_chessboard: chess {self.name_en} cannot be put at ({col_num}, {row_num})"
            )

    def move(self, col_num: int, row_num: int) -> bool:
        '''move the chessman to given position'''
        if self.is_reachable(col_num, row_num):
            self.__chessboard.remove_chessman(self.__position.x,
                                              self.position.y)
            old_x = self.__position.x
            old_y = self.__position.y
            self.__position.x = col_num
            self.__position.y = row_num
            if not self.__chessboard.move_chessman(self, col_num, row_num, True,
                                                   old_x, old_y):
                self.__position.x = old_x
                self.__position.y = old_y
                self.__chessboard.put_on_chessman(self, self.__position.x,
                                                  self.__position.y)
                self.clear_moving_list()
                self.calc_moving_list()
                return False
            return True
        else:
            self.clear_moving_list()
            self.calc_moving_list()
            if self.is_reachable(col_num, row_num):
                return self.move(col_num, row_num)
            logger.warning("the wrong target position: ", self.name_en,
                           self.name_cn, col_num, row_num)
            for point in self.moving_list:
                logger.debug(point.x, point.y)
            return False

    def is_reachable(self, col_num: int, row_num: int) -> bool:
        '''check if given postion is reachable for this chessman'''
        for point in self.__moving_list:
            if point.x == col_num and point.y == row_num:
                return True
        return False

    def calc_moving_list(self):
        '''calculate all reachable position for this chessman'''
        pass  # virtual function for children class

    def RCmoving(self,
                 target_chessman,
                 target_x: int,
                 target_y: int,
                 source_x: int,
                 source_y: int,
                 direction: int,
                 border: int,
                 h_or_v: bool,
                 ignore_color=False):
        '''calculate all reachable paths for rook and cannon'''
        if target_chessman != None:
            if target_chessman.is_red == self.is_red or ignore_color:
                for i in range(target_x + direction, source_x, direction):
                    self.__moving_list.append(
                        Point(i, target_y) if h_or_v else Point(target_y, i))
            else:
                for i in range(target_x, source_x, direction):
                    self.__moving_list.append(
                        Point(i, target_y) if h_or_v else Point(target_y, i))
        else:
            for i in range(border, source_x, direction):
                self.__moving_list.append(
                    Point(i, target_y) if h_or_v else Point(target_y, i))

    def add_to_moving_list(self, targets: list, color: bool):
        '''check the list of point, if the point is reachable for chessman, add it into moving list'''
        for point in targets:
            if self.border_check(point.x, point.y):
                chessman = self.chessboard.get_chessman(point.x, point.y)
                if chessman is None or chessman.is_red != color:
                    self.moving_list.append(point)


class Rook(Chessman):
    '''车'''

    def __init__(self, name_en: str, name_cn: str, color: bool, token: str,
                 chessboard: Chessboard) -> None:
        super().__init__(name_en, name_cn, color, token, chessboard=chessboard)
        self._Chessman__top = 9
        self._Chessman__bottom = 0
        self._Chessman__left = 0
        self._Chessman__right = 8

    def calc_moving_list(self):
        x = super(Rook, self).position.x
        y = super(Rook, self).position.y
        left = super(Rook, self).chessboard.get_left_first_chessman(x, y)
        right = super(Rook, self).chessboard.get_right_first_chessman(x, y)
        top = super(Rook, self).chessboard.get_top_first_chessman(x, y)
        bottom = super(Rook, self).chessboard.get_bottom_first_chessman(x, y)

        super(Rook,
              self).RCmoving(left, (left.position.x if left != None else None),
                             x, y, 1, 0, True)
        super(Rook,
              self).RCmoving(right,
                             (right.position.x if right != None else None), x,
                             y, -1, 8, True)
        super(Rook,
              self).RCmoving(top, (top.position.y if top != None else None), y,
                             x, -1, 9, False)
        super(Rook,
              self).RCmoving(bottom,
                             (bottom.position.y if bottom != None else None), y,
                             x, 1, 0, False)


class Knight(Chessman):
    '''马'''

    def __init__(self, name_en: str, name_cn: str, color: bool, token: str,
                 chessboard: Chessboard) -> None:
        super().__init__(name_en, name_cn, color, token, chessboard=chessboard)
        self._Chessman__top = 9
        self._Chessman__bottom = 0
        self._Chessman__left = 0
        self._Chessman__right = 8

    def calc_moving_list(self):
        x = super(Knight, self).position.x
        y = super(Knight, self).position.y
        obstacle_points = []
        moving_points = []
        vs1 = (x + 1, x - 1)
        hs1 = (y,)
        vs2 = (x,)
        hs2 = (y + 1, y - 1)
        generate_sqaure(obstacle_points, vs1, hs1)
        generate_sqaure(obstacle_points, vs2, hs2)
        color = super(Knight, self).is_red
        for point in obstacle_points:
            if super(Knight, self).border_check(point.x, point.y):
                chessman = super(Knight, self).chessboard.get_chessman(
                    point.x, point.y)
                if chessman is None:
                    if point.x == x:
                        moving_points.append(Point(point.x + 1,
                                                   2 * point.y - y))
                        moving_points.append(Point(point.x - 1,
                                                   2 * point.y - y))
                    else:
                        moving_points.append(Point(2 * point.x - x,
                                                   point.y + 1))
                        moving_points.append(Point(2 * point.x - x,
                                                   point.y - 1))
        super(Knight, self).add_to_moving_list(moving_points, color)


class Cannon(Chessman):
    '''炮'''

    def __init__(self, name_en: str, name_cn: str, color: bool, token: str,
                 chessboard: Chessboard) -> None:
        super().__init__(name_en, name_cn, color, token, chessboard=chessboard)
        self._Chessman__top = 9
        self._Chessman__bottom = 0
        self._Chessman__left = 0
        self._Chessman__right = 8

    def calc_moving_list(self):
        x = super(Cannon, self).position.x
        y = super(Cannon, self).position.y
        left = super(Cannon, self).chessboard.get_left_first_chessman(x, y)
        right = super(Cannon, self).chessboard.get_right_first_chessman(x, y)
        top = super(Cannon, self).chessboard.get_top_first_chessman(x, y)
        bottom = super(Cannon, self).chessboard.get_bottom_first_chessman(x, y)
        next_left = super(Cannon,
                          self).chessboard.get_left_second_chessman(x, y)
        next_right = super(Cannon,
                           self).chessboard.get_right_second_chessman(x, y)
        next_top = super(Cannon, self).chessboard.get_top_second_chessman(x, y)
        next_bottom = super(Cannon,
                            self).chessboard.get_bottom_second_chessman(x, y)
        super(Cannon,
              self).RCmoving(left, (left.position.x if left != None else None),
                             x, y, 1, 0, True, True)
        super(Cannon,
              self).RCmoving(right,
                             (right.position.x if right != None else None), x,
                             y, -1, 8, True, True)
        super(Cannon,
              self).RCmoving(top, (top.position.y if top != None else None), y,
                             x, -1, 9, False, True)
        super(Cannon,
              self).RCmoving(bottom,
                             (bottom.position.y if bottom != None else None), y,
                             x, 1, 0, False, True)
        color = super(Cannon, self).is_red
        if next_left != None and next_left.is_red != color:
            super(Cannon, self).moving_list.append(
                Point(next_left.position.x, next_left.position.y))
        if next_right != None and next_right.is_red != color:
            super(Cannon, self).moving_list.append(
                Point(next_right.position.x, next_right.position.y))
        if next_top != None and next_top.is_red != color:
            super(Cannon, self).moving_list.append(
                Point(next_top.position.x, next_top.position.y))
        if next_bottom != None and next_bottom.is_red != color:
            super(Cannon, self).moving_list.append(
                Point(next_bottom.position.x, next_bottom.position.y))


class Mandarin(Chessman):
    '''仕/士'''

    def __init__(self, name_en: str, name_cn: str, color: bool, token: str,
                 chessboard: Chessboard) -> None:
        super().__init__(name_en, name_cn, color, token, chessboard=chessboard)
        if self.is_red:
            self._Chessman__top = 2
            self._Chessman__bottom = 0
            self._Chessman__left = 3
            self._Chessman__right = 5
        else:
            self._Chessman__top = 9
            self._Chessman__bottom = 7
            self._Chessman__left = 3
            self._Chessman__right = 5

    def calc_moving_list(self):
        x = super(Mandarin, self).position.x
        y = super(Mandarin, self).position.y
        moving_points = []
        vs1 = (x + 1, x - 1)
        hs1 = (y + 1, y - 1)
        generate_sqaure(moving_points, vs1, hs1)
        color = super(Mandarin, self).is_red

        super(Mandarin, self).add_to_moving_list(moving_points, color)


class Elephant(Chessman):
    '''象/相'''

    def __init__(self, name_en: str, name_cn: str, color: bool, token: str,
                 chessboard: Chessboard) -> None:
        super().__init__(name_en, name_cn, color, token, chessboard=chessboard)
        if self.is_red:
            self._Chessman__top = 4
            self._Chessman__bottom = 0
            self._Chessman__left = 0
            self._Chessman__right = 8
        else:
            self._Chessman__top = 9
            self._Chessman__bottom = 5
            self._Chessman__left = 0
            self._Chessman__right = 8

    def calc_moving_list(self):
        x = super(Elephant, self).position.x
        y = super(Elephant, self).position.y
        obstacle_points = []
        moving_points = []
        vs1 = (x + 1, x - 1)
        hs1 = (y + 1, y - 1)
        generate_sqaure(obstacle_points, vs1, hs1)
        color = super(Elephant, self).is_red
        for point in obstacle_points:
            if super(Elephant, self).border_check(point.x, point.y):
                chessman = super(Elephant, self).chessboard.get_chessman(
                    point.x, point.y)
                if chessman is None:
                    moving_points.append(Point(2 * point.x - x,
                                               2 * point.y - y))
        super(Elephant, self).add_to_moving_list(moving_points, color)


class Pawn(Chessman):
    '''卒/兵'''

    def __init__(self, name_en: str, name_cn: str, color: bool, token: str,
                 chessboard: Chessboard) -> None:
        super().__init__(name_en, name_cn, color, token, chessboard=chessboard)
        if self.is_red:
            self._Chessman__top = 9
            self._Chessman__bottom = 3
            self._Chessman__left = 0
            self._Chessman__right = 8
            self.__direction = 1
            self.__river = 5
        else:
            self._Chessman__top = 6
            self._Chessman__bottom = 0
            self._Chessman__left = 0
            self._Chessman__right = 8
            self.__direction = -1
            self.__river = 4

    def calc_moving_list(self):
        x = super(Pawn, self).position.x
        y = super(Pawn, self).position.y
        moving_points = []
        color = super(Pawn, self).is_red
        moving_points.append(Point(x, y + self.__direction))
        if y * self.__direction >= self.__river * self.__direction:
            moving_points.append(Point(x + 1, y))
            moving_points.append(Point(x - 1, y))
        super(Pawn, self).add_to_moving_list(moving_points, color)


class King(Chessman):
    '''将/帅'''

    def __init__(self, name_en: str, name_cn: str, color: bool, token: str,
                 chessboard: Chessboard) -> None:
        super().__init__(name_en, name_cn, color, token, chessboard=chessboard)
        if self.is_red:
            self._Chessman__top = 2
            self._Chessman__bottom = 0
            self._Chessman__left = 3
            self._Chessman__right = 5
        else:
            self._Chessman__top = 9
            self._Chessman__bottom = 7
            self._Chessman__left = 3
            self._Chessman__right = 5

    def calc_moving_list(self):
        x = super(King, self).position.x
        y = super(King, self).position.y
        moving_points = []
        vs1 = (x + 1, x - 1)
        hs1 = (y,)
        vs2 = (x,)
        hs2 = (y + 1, y - 1)
        generate_sqaure(moving_points, vs1, hs1)
        generate_sqaure(moving_points, vs2, hs2)
        color = super(King, self).is_red
        super(King, self).add_to_moving_list(moving_points, color)
