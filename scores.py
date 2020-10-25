from penguin_game import *


class Scores:
    __init__(self, game):
        self.__game = game

    def score_by_iceberg_belogns(self, iceberg_to_score):
        """
        Scoring by the belongs of the iceberg (my, enemy, neutrial)

        :type iceberg_to_score: Iceberg
        :rtype: float
        """
        pass

    def score_by_iceberg_level(self, iceberg_to_score):
        """
        Scoring by the iceberg level.

        :type iceberg_to_score: Iceberg
        :rtype: float
        """
        pass

    def score_by_iceberg_distance(self, source_iceberg, destination_iceberg_to_score):
        """
        Scoring by the distance between source iceberg to the destination iceberg.

        :type source_iceberg: Iceberg
        :type destination_iceberg_to_score: Iceberg
        :rtype: float:
        """
        pass

    def score_by_iceberg_min_price(self, source_iceberg, destination_iceberg_to_score):
        """
        Scoring by the min price  of the destination iceberg.
        Taking in account the number of the penguins when the penguins-group from the source iceberg will arrive.
        If there is not enoght penguins in the source iceberg, the score is negative.
        :type source_iceberg: Iceberg
        :type destination_iceberg_to_score: Iceberg
        :rtype: float
        """
        pass
