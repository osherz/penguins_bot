from penguin_game import *
import utils

ENEMY_BELONGS_SCORE = 2
NEUTRAL_BELONGS_SCORE = 1
MY_BELONGS_SCORE = 0
CANT_BE_OCCUPIED_SCORE = -9999


class Scores:
    def __init__(self, game):
        """
        :type game: Game
        """
        self.update_game(game)
        self.__max_distance = self.__find_max_distance()

    def update_game(self, game):
        """
        Update the game.
        Active every new turn.

        :type game: Game
        """
        self.__game = game
        self.__max_price = self.__find_max_price()

    def score_by_iceberg_belogns(self, iceberg_to_score):
        """
        Scoring by the belongs of the iceberg (my, enemy, neutrial)

        :type iceberg_to_score: Iceberg
        :rtype: float
        """
        game = self.__game
        iceberg_owner = iceberg_to_score.owner
        if iceberg_owner.equals(game.get_enemy()):
            return ENEMY_BELONGS_SCORE

        if self.__is_belong_to_me(iceberg_to_score):
            return MY_BELONGS_SCORE

        return NEUTRAL_BELONGS_SCORE

    def score_by_iceberg_level(self, iceberg_to_score):
        """
        Scoring by the iceberg level.

        :type iceberg_to_score: Iceberg
        :rtype: float
        """
        return iceberg_to_score.level

    def score_by_iceberg_distance(self, source_iceberg, destination_iceberg_to_score):
        """
        Scoring by the distance between source iceberg to the destination iceberg.

        :type source_iceberg: Iceberg
        :type destination_iceberg_to_score: Iceberg
        :rtype: float:
        """
        return self.__max_distance - destination_iceberg_to_score.get_turns_till_arrival(source_iceberg)

    def score_by_iceberg_price(self, source_iceberg, destination_iceberg_to_score):
        """
        Scoring by the price of the destination iceberg.
        Taking in account the number of the penguins when the penguins-group from the source iceberg will arrive.
        If there is not enoght penguins in the source iceberg return (-999, -1).
        If the iceberg belong or will belong to us, return (0,0).
        :type source_iceberg: Iceberg
        :type destination_iceberg_to_score: Iceberg
        :rtype: (int, int)
        :return: (score, min_penguins_for_occupy)
        """

        min_penguins_for_occupy = utils.min_penguins_for_occupy(
            self.__game, source_iceberg, destination_iceberg_to_score)

        if min_penguins_for_occupy == 0:
            return MY_BELONGS_SCORE, 0

        if min_penguins_for_occupy >= source_iceberg.penguin_amount:
            return CANT_BE_OCCUPIED_SCORE, -1

        score = self.__max_price - min_penguins_for_occupy
        return score, min_penguins_for_occupy

    def __find_max_distance(self):
        """
        Find the max distance between icebergs.

        :rtype: int
        """
        game = self.__game
        max_distance = 0
        for iceberg1 in game.get_all_icebergs():  # type: Iceberg
            for iceberg2 in game.get_all_icebergs():  # type: Iceberg
                if not iceberg1.equals(iceberg2):
                    distance = iceberg1.get_turns_till_arrival(iceberg2)
                    if distance > max_distance:
                        max_distance = distance
        return max_distance

    def __find_max_price(self):
        """
        Find the max price of icebergs.

        :rtype: int
        """
        prices_map = map(
            lambda iceberg: iceberg.penguin_amount,
            self.__game.get_all_icebergs()
        )
        return max(prices_map)

    def __is_belong_to_me(self, iceberg):
        """Check whether the given iceberg belongs to me.

        :type iceberg: Iceberg
        :rtype: bool
        """
        return iceberg.owner.equals(self.__game.get_myself())
