from penguin_game import *
from simulationsdata import SimulationsData, OWNER
import utils

SEND_PENGUINS = 'send_penguins'
BUILD_BRIDGE = 'build_bridge'

MIN_ADDITIONAL_PENGUINS_FOR_OCCUPY = 1
MIN_PENGUIN_BONUS_ICEBERG_FACTOR = 1.8


class OccupyMethodData:
    """
    Handle data that important for occupy.
    """

    def __init__(self, min_penguins_for_occupy, min_penguins_for_neutral, recommended_penguins_for_occupy, method,
                 owner):
        """
        :param method: SEND_PENGUINS or BUILD_BRIDGE
        :type method: str
        :param owner: The owner of destination if no action will made.
        """
        self.min_penguins_for_occupy = min_penguins_for_occupy
        self.min_penguins_for_neutral = min_penguins_for_neutral
        self.recommended_penguins_for_occupy = recommended_penguins_for_occupy
        self.method = method
        self.owner = owner


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
        game = self.__game

        min_penguins_to_make_neutral, owner_if_no_action_will_made = self.__calc_min_penguins_to_send(
            source_iceberg,
            destination_iceberg
        )

        is_bridge_prefer = False
        if not utils.is_me(game, owner_if_no_action_will_made):
            min_penguins_to_send_for_occupy = min_penguins_to_make_neutral + MIN_ADDITIONAL_PENGUINS_FOR_OCCUPY

            if utils.is_enemy(game, owner_if_no_action_will_made):
                # Only if the destination iceberg will belong to enemy
                # we want to think about bridge building.
                is_bridge_prefer, penguins_to_use = self.__is_bridge_prefer(
                    source_iceberg,
                    destination_iceberg,
                    min_penguins_to_send_for_occupy
                )

            elif utils.is_neutral(game, owner_if_no_action_will_made) and utils.is_bonus_iceberg(game,
                                                                                                 destination_iceberg):
                # If the destination iceberg will belong to neutral and its bonus, we want to send addition penguins.
                min_penguins_to_send_for_occupy = int(min_penguins_to_make_neutral * MIN_PENGUIN_BONUS_ICEBERG_FACTOR)

        else:
            # If the iceberg will belong ot me,
            # we want to think about sending some support.
            min_penguins_to_send_for_occupy = self.__calc_penguins_to_send_for_support(source_iceberg)

        if is_bridge_prefer:
            occupy_method_data = OccupyMethodData(
                penguins_to_use,
                penguins_to_use,
                penguins_to_use,
                BUILD_BRIDGE,
                owner_if_no_action_will_made
            )
        else:
            occupy_method_data = OccupyMethodData(
                min_penguins_to_send_for_occupy,
                min_penguins_to_make_neutral,
                min_penguins_to_send_for_occupy,
                SEND_PENGUINS,
                owner_if_no_action_will_made
            )

        return occupy_method_data

    def __calc_min_penguins_to_send(self, source_iceberg, destination_iceberg):
        """
        Calculate the number of minimum penguin the need to be send to make destination neutral
        and who will be the owner of the destination if no penguins are send.

        :return: (min_penguins_for_occupy, owner)
        :rtype: (int, Player)
        """
        min_penguins_to_make_neutral = utils.min_penguins_to_make_neutral(
            self.__game, source_iceberg, destination_iceberg, self.__simulation_data)

        simulation_data_turns = self.__simulation_data.get(destination_iceberg)
        owner = simulation_data_turns[-1][OWNER]
        return min_penguins_to_make_neutral, owner

    def __is_bridge_prefer(self, source_iceberg, destination_iceberg, min_penguins_to_send_for_occupy):
        """
        Check whether the bridge is prefer over sending penguins.
        Return whether the bridge is prefer, how much penguins need to be use.
        :return: (is_bridge_prefer, penguins_to_use)
        :rtype: (bool, int)
        """
        game = self.__game
        simulation_data = self.__simulation_data

        is_bridge_prefer = False

        penguins_to_use = source_iceberg.bridge_cost
        if penguins_to_use < min_penguins_to_send_for_occupy and utils.can_build_bridge(source_iceberg,
                                                                                        destination_iceberg):
            new_owner = utils.simulate_with_bridge(
                game, source_iceberg, destination_iceberg, simulation_data)
            if utils.is_me(game, new_owner):
                is_bridge_prefer = True

        return is_bridge_prefer, penguins_to_use

    def __calc_penguins_to_send_for_support(self, source_iceberg):
        """
        Calculate how much penguins to send to destination for support
        when destination belongs me.
        """
        if type(source_iceberg) == Iceberg:
            penguins_per_turn = source_iceberg.penguins_per_turn
            penguin_amount_to_send = source_iceberg.penguin_amount
        else:
            penguins_per_turn = 0
            penguin_amount_to_send = source_iceberg.penguin_amount - 1

        return min(penguin_amount_to_send, penguins_per_turn)
