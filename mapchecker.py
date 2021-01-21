from penguin_game import *
from utils import get_avg_distance_between_all_icebergs, get_avg_distance_between_natural_groups

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
        avg_distance = get_avg_distance_between_natural_groups(game)

        if avg_distance <= 10:
            self.__is_2X2_map = True
        elif avg_distance <= 15:
            if game.get_my_icebergs()[0].get_turns_till_arrival(game.get_enemy_icebergs()[0]) < get_avg_distance_between_all_icebergs(game):
                self.__is_extra_far = True
            else:
                self.__is_extra_far_treasure = True
        elif avg_distance <= 18:
            self.__is_default_map = True
        else:
            self.__is_circles = True


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
