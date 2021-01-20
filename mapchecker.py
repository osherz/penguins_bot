from penguin_game import *

map_checker = None


class MapChecker:
    """
    Class that check in which map we play.
    """

    def __init__(self, game, stay_default=False):

        self.__is_2X2_map = False
        self.__is_tricky_map = False
        self.__is_extra_far_treasure = False
        self.__is_extra_far = False
        self.__is_circles = False
        self.__is_default_map = stay_default
        self.__is_2020_map = False
        if not stay_default:
            self.init_maps(game)

        print self.__is_2X2_map, \
                self.__is_tricky_map, \
                self.__is_extra_far_treasure, \
                self.__is_extra_far, \
                self.__is_circles, \
                self.__is_default_map, \
                self.__is_2020_map

        global map_checker
        if map_checker is None:
            map_checker = self

    def init_maps(self, game):
        """
        Active this function in the first turn of the game only!
        Check in which maps we play.
        """
        starter_amount = game.get_my_icebergs()[0].penguin_amount
        if starter_amount == 16:
            self.__is_2X2_map = True
        elif len(game.get_all_icebergs()) == 5:
            self.__is_tricky_map = True
        elif starter_amount == 19:
            self.__is_extra_far = True
        elif starter_amount == 10:
            self.__is_circles = True
        elif starter_amount == 11:
            self.__is_extra_far_treasure = True
        else:
            level1_20_penguins = [
                iceberg
                for iceberg in game.get_neutral_icebergs()
                if iceberg.level == 1 and iceberg.penguin_amount == 20
            ]
            if any(level1_20_penguins):
                self.__is_2020_map = True
            else:
                self.__is_default_map = True

    def is_2X2_map(self):
        return self.__is_2X2_map

    def is_2020_map(self):
        return self.__is_2020_map

    def is_tricky_map(self):
        return self.__is_tricky_map

    def is_extra_far(self):
        return self.__is_extra_far

    def is_extra_far_treasure(self):
        return self.__is_extra_far_treasure

    def is_circles(self):
        return self.__is_circles

    def is_default_map(self):
        return self.__is_default_map

    @staticmethod
    def get():
        global map_checker
        return map_checker
