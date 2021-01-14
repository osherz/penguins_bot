from penguin_game import *

map_checker = None


class MapChecker:
    """
    Class that check in which map we play.
    """

    def __init__(self, game):
        self.__is_2X2_map = False
        self.__is_tricky_map = False
        self.__is_default_map = True
        self.__is_2020_map = False
        self.init_maps(game)

        global map_checker
        if map_checker is None:
            map_checker = self

    def init_maps(self, game):
        """
        Active this function in the first turn of the game only!
        Check in which maps we play.
        """
        if len(game.get_my_icebergs()) == 2:
            self.__is_2X2_map = True
        elif len(game.get_all_icebergs()) == 5:
            self.__is_tricky_map = True
        else:
            level1_20_penguins = [
                iceberg
                for iceberg in game.get_neutral_icebergs()
                if iceberg.level == 1 and iceberg.penguin_amount == 20
            ]
            if any(level1_20_penguins):
                self.__is_2020_map = True

        if self.__is_2020_map or self.__is_tricky_map or self.__is_2X2_map:
            self.__is_default_map = False

    def is_2X2_map(self):
        return self.__is_2X2_map

    def is_2020_map(self):
        return self.__is_2020_map

    def is_tricky_map(self):
        return self.__is_tricky_map

    def is_default_map(self):
        return self.__is_default_map

    @staticmethod
    def get():
        global map_checker
        return map_checker
