from penguin_game import *


class ScoreData:
    def __init__(self, source_iceberg, destination_iceberg, min_penguins_for_occupy, min_penguins_for_neutral,
                 max_penguins_can_be_sent, close_strong_enemy, score,
                 send_penguins=False, build_bridge=False):
        self.__source_iceberg = source_iceberg
        self.__destination_iceberg = destination_iceberg
        self.__min_penguins_for_occupy = min_penguins_for_occupy
        self.__min_penguins_for_neutral = min_penguins_for_neutral
        self.__max_penguins_can_be_sent = max_penguins_can_be_sent
        self.__score = score
        self.__close_strong_enemy_to_destination = close_strong_enemy
        self.__send_penguins = send_penguins
        self.__build_bridge = build_bridge

    def get_source(self):
        return self.__source_iceberg

    def get_destination(self):
        return self.__destination_iceberg

    def get_min_penguins_for_occupy(self):
        return self.__min_penguins_for_occupy

    def get_min_penguins_for_neutral(self):
        return self.__min_penguins_for_neutral

    def get_max_penguins_can_be_sent(self):
        return self.__max_penguins_can_be_sent

    def get_close_strong_enemy_to_destination(self):
        return self.__close_strong_enemy_to_destination

    def get_score(self):
        return self.__score

    def build_bridge(self):
        return self.__build_bridge

    def send_penguins(self):
        return self.__send_penguins
