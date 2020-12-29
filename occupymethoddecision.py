from penguin_game import *
from simulationsdata import SimulationsData

SEND_PENGUINS = 'send_penguins'
BUILD_BRIDGE = 'build_bridge'


class OccupyMethodData:
    """
    Handle data that important for occupy.
    """

    def __init__(self, min_penguins_for_occupy, min_penguins_for_neutral, recommended_penguins_for_occupy, method):
        """
        :param method: SEND_PENGUINS or BUILD_BRIDGE
        :type method: str
        """
        self.min_penguins_for_occupy = min_penguins_for_occupy
        self.min_penguins_for_neutral = min_penguins_for_neutral
        self.recommended_penguins_for_occupy = recommended_penguins_for_occupy
        self.method = method


class OccupyMethodDecision:
    """
    Making the decision of which method to choose for occupy and how much penguins need to be use.
    """

    def __init__(self, game, simulation_data):
        self.__game = game
        self.__simulation_data = simulation_data

    def pick_occupy_method(self, source_iceberg, destination_iceberg):
        """
        Decide how to occupy the destination iceberg by the source_iceberg
        and how much penguins to use.
        """
        return OccupyMethodData()

    def __clac_min_penguins_to_send(self, source_iceberg, destination_iceberg, simulation_data):
        """
        Calculate the number of minimum penguin the need to be send to make the destination with 0 penguins
        and who will be the owner of the destination if no penguins are send.

        :return: (min_penguins_for_occupy, owner)
        :rtype: (int, Player)
        """
        return min_penguins_for_occupy, owner

    def __is_bridge_prefer(self, source_iceberg, destination_iceberg, simulation_data, min_penguins_to_send_for_occupy):
        """
        Check whether the bridge is prefer over sending penguins.
        Return whether the bridge is prefer, how much penguins need to be use
        and who will be the owner of the destination if no penguins are send.
        :return: (is_bridge_prefer, penguins_to_use, owner)
        :rtype: (bool, int, Player)
        """
        return is_bridge_prefer, penguins_to_use, owner
