from penguin_game import *
import utils

ENEMY_BELONGS_SCORE = 4
NEUTRAL_BELONGS_SCORE = 2
MY_BELONGS_SCORE = 0
NEED_PROTECTED = 10
CANT_DO_ACTION_SCORE = -9999
UPGRADE_TURNS_TO_CHECK = 20


class Scores:
    def __init__(self, game):
        """
        :type game: Game
        """

        self.update_game(game)
        self.__max_distance = self.__find_max_distance()
        self.__average_distance = self.__calculate_average_distance()

    def update_game(self, game):
        """
        Update the game.
        Active every new turn.

        :type game: Game
        """
        self.__game = game
        self.__max_price = self.__find_max_price()

    def score_by_iceberg_belogns(self, source_iceberg, iceberg_to_score):
        """
        Scoring by the belongs of the iceberg (my, enemy, neutrial)

        :type source_iceberg: Iceberg
        :type iceberg_to_score: Iceberg
        :rtype: float
        """
        game = self.__game
        iceberg_owner = iceberg_to_score.owner
        if iceberg_owner.equals(game.get_enemy()):
            return ENEMY_BELONGS_SCORE

        if self.__is_belong_to_me(iceberg_to_score):

            if self.__is_destination_closest_to_enemy(source_iceberg, iceberg_to_score):
                return self.__max_distance - source_iceberg.get_turns_till_arrival(iceberg_to_score)
            else:
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

        print
        source_iceberg, destination_iceberg_to_score, min_penguins_for_occupy
        if min_penguins_for_occupy == 0:
            return MY_BELONGS_SCORE, 0

        if min_penguins_for_occupy >= source_iceberg.penguin_amount:
            return CANT_DO_ACTION_SCORE, -1

        score = self.__max_price - min_penguins_for_occupy
        return score, min_penguins_for_occupy

    def score_upgrade(self, iceberg_to_score):
        """
        Score the upgrade action of iceberg_to_score.

        :param iceberg_to_score: Iceberg to score the upgrade action.
        :type iceberg_to_score: Iceberg
        :return: Score
        :rtype: float
        """

        if not utils.can_be_upgrade(iceberg_to_score):
            return CANT_DO_ACTION_SCORE

        upgrade_cost = iceberg_to_score.upgrade_cost
        next_level = iceberg_to_score.level + 1
        return self.__max_price - upgrade_cost + next_level * UPGRADE_TURNS_TO_CHECK

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

    def __calculate_average_distance(self):
        """
        Calculate the average distance between all icebergs.
        :return: The average distance.
        :rtype: float
        """
        game = self.__game  # type: Game
        all_icebergs = game.get_all_icebergs()
        all_icebergs_pairs = zip(all_icebergs, all_icebergs)
        distances = map(
            lambda (iceberg1, iceberg2): iceberg1.get_turns_till_arrival(iceberg2),
            all_icebergs_pairs
        )
        sum_of_icebergs = len(all_icebergs)
        sum_distances = sum(distances)
        return sum_distances / (sum_of_icebergs * (sum_of_icebergs - 1) / 2)

    def __calculate_average_distance_from_enemy(self, iceberg):
        """
        Calculate the distance average between the given iceberg and the enemy icebergs.

        :param iceberg: Iceberg to calculate the distance from him.
        :type iceberg: Iceberg
        :return: distance average
        :rtype: float
        """
        enemy_icebergs = self.__game.get_enemy_icebergs()
        enemy_distance = map(
            lambda enemy_iceberg: enemy_iceberg.get_turns_till_arrival(iceberg),
            enemy_icebergs
        )
        return sum(enemy_distance) / len(enemy_distance)

    def __is_destination_closest_to_enemy(self, source_iceberg, destination_iceberg):
        """
        Check is the source closest to the enemy than the destination.
        :param source_iceberg:
        :param destination_iceberg:
        :return: Whether source closest
        """
        source_avg_distance = self.__calculate_average_distance_from_enemy(source_iceberg)
        destination_avg_distance = self.__calculate_average_distance_from_enemy(destination_iceberg)
        return destination_avg_distance < self.__average_distance < source_avg_distance
