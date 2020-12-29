from penguin_game import *
from simulationsdata import SimulationsData
import utils

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
        min_penguins_to_send_for_occupy, owner = self.__clac_min_penguins_to_send(
            source_iceberg,
            destination_iceberg
        )

        is_bridge_prefer = False
        if utils.is_enemy(self.__game, owner):
            is_bridge_prefer, penguins_to_use = self.__is_bridge_prefer(
                source_iceberg,
                destination_iceberg,
                min_penguins_to_send_for_occupy
            )

        if is_bridge_prefer:
            occupy_method_data = OccupyMethodData(
                penguins_to_use,
                penguins_to_use,
                penguins_to_use,
                BUILD_BRIDGE
            )
        else:
            occupy_method_data = OccupyMethodData(
                min_penguins_to_send_for_occupy,
                min_penguins_to_send_for_occupy,
                min_penguins_to_send_for_occupy,
                SEND_PENGUINS
            )

        return occupy_method_data

    def __clac_min_penguins_to_send(self, source_iceberg, destination_iceberg):
        """
        Calculate the number of minimum penguin the need to be send for occupy
        and who will be the owner of the destination if no penguins are send.

        :return: (min_penguins_for_occupy, owner)
        :rtype: (int, Player)
        """
        return min_penguins_for_occupy, owner

    def __is_bridge_prefer(self, source_iceberg, destination_iceberg, min_penguins_to_send_for_occupy):
        """
        Check whether the bridge is prefer over sending penguins.
        Return whether the bridge is prefer, how much penguins need to be use.
        :return: (is_bridge_prefer, penguins_to_use)
        :rtype: (bool, int)
        """
        return is_bridge_prefer, penguins_to_use
