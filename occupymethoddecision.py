from penguin_game import *
from simulationsdata import SimulationsData, OWNER
import utils

SEND_PENGUINS = 'send_penguins'
BUILD_BRIDGE = 'build_bridge'

MIN_ADDITIONAL_PENGUINS_FOR_OCCUPY = 1
MIN_PENGUIN_BONUS_ICEBERG_FACTOR = 1.8
MIN_DISTANCE_TO_CHECK = 90
MIN_PENGUINS_GROUP_FOR_BRIDGE_BUILDING_TO_OURS = 15


class OccupyMethodData:
    """
    Handle data that important for occupy.
    """

    def __init__(self, min_penguins_for_occupy, min_penguins_for_neutral, recommended_penguins_for_occupy,
                 max_penguins_can_be_use, method,
                 owner):
        """
        :param method: SEND_PENGUINS or BUILD_BRIDGE
        :type method: str
        :param owner: The owner of destination if no action will made.
        """
        self.min_penguins_for_occupy = min_penguins_for_occupy
        self.min_penguins_for_neutral = min_penguins_for_neutral
        self.recommended_penguins_for_occupy = recommended_penguins_for_occupy
        self.max_penguins_can_be_use = max_penguins_can_be_use
        self.method = method
        self.owner = owner

    def __str__(self):
        return 'self.min_penguins_for_occupy=' + str(self.min_penguins_for_occupy) + \
               ' self.min_penguins_for_neutral=' + str(self.min_penguins_for_neutral) + \
               ' self.recommended_penguins_for_occupy=' + str(self.recommended_penguins_for_occupy) + \
               ' self.method=' + str(self.method) + \
               ' self.owner=' + str(self.owner)


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
            is_bridge_prefer, penguins_to_use = self.__is_bridge_to_our_prefer(destination_iceberg, source_iceberg)
            if not is_bridge_prefer:
                min_penguins_to_send_for_occupy = self.__calc_penguins_to_send_for_support(source_iceberg)

        max_penguins_can_be_use = self.__calc_max_penguins_can_be_use_consider_close_enemy_icebergs(source_iceberg)
        if is_bridge_prefer:
            occupy_method_data = OccupyMethodData(
                penguins_to_use,
                penguins_to_use,
                penguins_to_use,
                max_penguins_can_be_use,
                BUILD_BRIDGE,
                owner_if_no_action_will_made
            )
        else:
            occupy_method_data = OccupyMethodData(
                min_penguins_to_send_for_occupy,
                min_penguins_to_make_neutral,
                min_penguins_to_send_for_occupy,
                max_penguins_can_be_use,
                SEND_PENGUINS,
                owner_if_no_action_will_made
            )

        return occupy_method_data

    def __calc_max_penguins_can_be_use_consider_close_enemy_icebergs(self, source_iceberg):
        max_penguins_can_be_use = self.__simulation_data.get_max_penguins_can_be_use(source_iceberg)
        penguins_of_close_iceberg, max_distance = self.__calc_penguins_of_close_iceberg_and_max_distance(source_iceberg)
        penguins_per_turn = 0 if utils.is_bonus_iceberg(self.__game,
                                                        source_iceberg) else source_iceberg.penguins_per_turn
        distance_with_bridge = max_distance / self.__game.iceberg_bridge_speed_multiplier
        reduce_penguins = int(max(0, penguins_of_close_iceberg - distance_with_bridge * penguins_per_turn))
        max_penguins_can_be_use = max(0, max_penguins_can_be_use - reduce_penguins)
        return max_penguins_can_be_use

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
        is_bridge_prefer = False

        penguins_to_use = source_iceberg.bridge_cost
        # If destination or source are bonus - we can't build bridge.
        if utils.is_bonus_iceberg(self.__game, source_iceberg) or \
                utils.is_bonus_iceberg(self.__game, destination_iceberg):
            return False, penguins_to_use

        if penguins_to_use < min_penguins_to_send_for_occupy and utils.can_build_bridge(source_iceberg,
                                                                                        destination_iceberg):
            is_bridge_prefer = self.__is_ours_after_bridge_creating(destination_iceberg, source_iceberg)

        return is_bridge_prefer, penguins_to_use

    def __is_bridge_to_our_prefer(self, destination_iceberg, source_iceberg):
        game = self.__game
        simulation_data = self.__simulation_data

        is_bridge_prefer = False
        if utils.can_build_bridge(source_iceberg, destination_iceberg):
            is_ours_after_bridge_creating = self.__is_ours_after_bridge_creating(destination_iceberg, source_iceberg)

            our_penguin_groups_amount = self.__calc_amount_of_our_penguins_to_destination(destination_iceberg, game,
                                                                                          source_iceberg)
            if is_ours_after_bridge_creating and our_penguin_groups_amount > MIN_PENGUINS_GROUP_FOR_BRIDGE_BUILDING_TO_OURS:
                is_bridge_prefer = True
        return is_bridge_prefer, game.iceberg_bridge_cost

    def __is_ours_after_bridge_creating(self, destination_iceberg, source_iceberg):
        game = self.__game
        simulation_data = self.__simulation_data

        new_owner = utils.simulate_with_bridge(
            game, source_iceberg, destination_iceberg, simulation_data)
        return utils.is_me(game, new_owner)

    def __calc_amount_of_our_penguins_to_destination(self, destination_iceberg, game, source_iceberg):
        ours_groups = utils.get_groups_way_to_iceberg(game, destination_iceberg, [
            group
            for group in game.get_my_penguin_groups()
            if group.source.equals(source_iceberg)
        ])
        our_penguin_groups_amount = sum(map(lambda x: x.penguin_amount, ours_groups))
        return our_penguin_groups_amount

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

    def __calc_penguins_of_close_iceberg_and_max_distance(self, iceberg):
        """
        Calculate how much penguins has the close enemies icebergs.
        """
        ours_avg_distance, enemy_avg_distance = self.__simulation_data.get_avg_distance_from_players(iceberg)
        if ours_avg_distance <= 0:
            max_distance_to_check = MIN_DISTANCE_TO_CHECK
        else:
            max_distance_to_check = ours_avg_distance
        close_icebergs = [
            enemy_iceberg
            for enemy_iceberg in self.__game.get_enemy_icebergs()
            if utils.get_real_distance_between_icebergs(iceberg, enemy_iceberg) <= max_distance_to_check
        ]
        if utils.is_empty(close_icebergs):
            return 0, 0
        return sum(map(lambda x: x.penguin_amount, close_icebergs)), \
               max(close_icebergs, key=lambda x: x.get_turns_till_arrival(iceberg)).get_turns_till_arrival(iceberg)
