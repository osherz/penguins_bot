from penguin_game import Game, Iceberg, BonusIceberg, IceBuilding
from penguingroupsimulate import PenguinGroupSimulate
from bonusturndata import BonusTurnData
from bridgesimulation import BridgeSimulation

import math
import utils
import itertools

MAX_ACTIONS = 10


class Simulation:
    """
    Simulation of the game.
    """

    def __init__(self, game, iceberg_to_simulate, bonus_turns_ls):
        """
        :param game: Game current status
        :type game: Game
        :param iceberg_to_simulate: Iceberg to simulate his penguins amount.
        :type iceberg_to_simulate: IceBuilding
        :type bonus_turns_ls: List[int]
        """
        self.__game = game
        self.__iceberg_to_simulate = iceberg_to_simulate
        self.__bonus_turns_ls = bonus_turns_ls
        self.reset_to_origin()

    def reset_to_origin(self):
        """
        Reset all data to game status.
        :return:
        """
        game = self.__game
        self.__is_simulate_started = False
        self.__current_turn = 0
        self.__bonus_turn_index = 0

        iceberg_to_simulate = self.__iceberg_to_simulate  # type: Iceberg
        self.__iceberg_owner = iceberg_to_simulate.owner
        self.__penguin_amount = iceberg_to_simulate.penguin_amount
        if type(iceberg_to_simulate) == Iceberg:
            self.__iceberg_level = iceberg_to_simulate.level
            self.__penguins_per_turn = iceberg_to_simulate.penguins_per_turn
        # TODO: use penguins_per_turn instead of level

        self.__all_groups = map(
            lambda group: PenguinGroupSimulate(game, penguin_group=group),
            game.get_all_penguin_groups()
        )
        # type: List[Bridge]
        # type: List[Bridge]
        self.__custom_bridges_to_iceberg = {}

    def get_penguin_amount(self):
        """
        Get penguin amount.

        :return: Penguin amount.
        :rtype: int
        """
        return self.__penguin_amount

    def __simulate(self, turns_to_simulate, max_actions=99):
        """
        Start/continue simulation on the iceberg to check how much penguins will be in it in X turns
        Call after you inits akk groups to iceberg.
        :param turns_to_simulate: How much turns to simulate.
        :type turns_to_simulate: int
        """
        turn = 1
        if self.are_group_remains():
            turn = self.__calculate_how_much_turns_to_continue(
                turn, turns_to_simulate)
        turns_to_continue = turn
        actions = 0
        while turn <= turns_to_simulate:
            self.__current_turn += turns_to_continue
            self.__move_groups_to_destination(turns_to_continue)
            self.__treat_iceberg_by_turns(turns_to_continue)
            self.__treat_bonus()
            self.__treat_groups_arrived_destination()

            # Calculate how much turns to continue
            turns_to_continue = self.__calculate_how_much_turns_to_continue(
                turn, turns_to_simulate)
            turn += turns_to_continue
            actions += -1
            if actions >= max_actions:
                break

    def simulate(self, turns_to_simulate):
        """
        Start/continue simulation on the iceberg to check how much penguins will be in it in X turns
        :param turns_to_simulate: How much turns to simulate.
        :type turns_to_simulate: int
        """
        self.__init_groups_to_iceberg()
        self.__simulate(turns_to_simulate)

    def simulate_until_last_group_arrived(self):
        """
        Start/continue to simulate until the last group arrival to destination.

        :return:
        """
        self.__init_groups_to_iceberg()
        if len(self.__groups_to_iceberg) > 0:
            turns = self.get_last_group_distance()
            self.__simulate(turns, MAX_ACTIONS)

    def are_group_remains(self):
        """
        Return whether there are any groups to the destination remains.
        :return:
        :rtype: bool
        """
        return len(self.__groups_to_iceberg) > 0

    def add_penguin_group_simulate(self, penguin_group_simulate):
        """
        Add custom penguin group.

        :param penguin_group_simulate: Custom penguin group.
        :type penguin_group_simulate: PenguinGroupSimulate.
        """
        valid_instance_of_penguin_group_simulate(penguin_group_simulate)
        if self.__is_simulate_started:
            raise NotImplementedError(
                "You can't add groups after simulate started. Please reset and try again")
        else:
            self.__all_groups.append(penguin_group_simulate)

    def add_penguin_group(self, source_iceberg, destination_iceberg, penguin_amount):
        """
        Add custom penguin group.

        :param source_iceberg: Iceberg to send group from.
        :type source_iceberg: Iceberg
        :param destination_iceberg: Iceberg to send group to.
        :type destination_iceberg: Iceberg
        :param penguin_amount: How much penguins to send.
        :type penguin_amount: int
        :return: The custom PenguinGroupSimulate that created and added to the groups.
        :rtype: PenguinGroupSimulate
        """
        penguin_group_simulate = PenguinGroupSimulate(self.__game,
                                                      source_iceberg=source_iceberg,
                                                      destination_iceberg=destination_iceberg,
                                                      penguin_amount=penguin_amount)
        self.add_penguin_group_simulate(penguin_group_simulate)
        return penguin_group_simulate

    def add_bridge(source_iceberg, duration, speed_multiplier):
        """Add custom bridge.

        :type bridge: Bridge
        """
        custom_bridge = BridgeSimulation(
            source_iceberg,
            self.__iceberg_to_simulate,
            duration,
            speed_multiplier
        )
        key = self.__get_iceberg_key(source_iceberg)
        self.__custom_bridges_to_iceberg[key] = custom_bridge

    def add_penguin_amount(self, owner=None, penguin_amount=0, is_sending=False):
        """
        Add penguin amount to the iceberg, appropriate the owner of the penguins.
        Changed the owner if needed.

        :type owner: Player
        :param penguin_amount: Penguins to add.
        :type penguin_amount: int
        """
        if is_sending:
            if self.__penguin_amount - penguin_amount >= 0:
                self.__penguin_amount -= penguin_amount
            else:
                raise ValueError(
                    'Simulation: You can\'t send more penguins then you have: send' + str(penguin_amount) + ' has:' + str(
                        self.__penguin_amount))
        else:
            self.__treat_group_arrived_destination(owner, penguin_amount)

    def upgrade_iceberg(self, cost):
        """
        Upgrade the iceberg.
        Assume that the iceberg can be upgrade.
        Check only are there enough penguins.
        """
        if type(self.__iceberg_to_simulate) == BonusIceberg:
            raise ValueError(
                'You cant upgrade BonusIceberg')
        elif cost <= self.get_penguin_amount():
            self.__penguin_amount -= cost
            self.__iceberg_level += 1
        else:
            raise ValueError(
                'You cant upgrade, you have only:' + str(self.__penguin_amount) + ' while cost is:' + str(cost))

    def remove_penguin_group(self, penguin_group_simulate):
        """
        Remove custom group.
        :type penguin_group_simulate: PenguinGroupSimulate
        """
        valid_instance_of_penguin_group_simulate(penguin_group_simulate)
        self.__groups_to_iceberg.remove(penguin_group_simulate)

    def get_turns_simulated(self):
        """
        :return: How much turns already simulated.
        :rtype: int
        """
        return self.__current_turn

    def get_owner(self):
        """
        Get the current owner of the iceberg.

        :rtype: Player
        """
        return self.__iceberg_owner

    def get_last_group_distance(self):
        if self.are_group_remains():
            return self.__groups_to_iceberg[-1].get_turns_till_arrival()
        else:
            return 0

    def is_belong_to_me(self):
        return self.__iceberg_owner.equals(self.__game.get_myself())

    def is_belong_to_enemy(self):
        return self.__iceberg_owner.equals(self.__game.get_enemy())

    def is_belong_to_neutral(self):
        return self.__iceberg_owner.equals(self.__game.get_neutral())

    def __calculate_how_much_turns_to_continue(self, current_simulate_turn, turns_to_simulate):
        """
        Calculate how much turns need the closest group to arrive.
        If its bigger than the turns remind, return the turns remind.
        """
        turns_to_continue = 1
        if self.are_group_remains() and current_simulate_turn < turns_to_simulate:
            turns_to_continue = self.__groups_to_iceberg[0].get_turns_till_arrival(
            )
            if current_simulate_turn + turns_to_continue > turns_to_simulate:
                turns_to_continue = turns_to_simulate - current_simulate_turn
        return turns_to_continue
        # Calculate turns for next bonus

    def __sort_groups_by_distance(self):
        """
        Sort groups by their distance from destination.
        """
        self.__groups_to_iceberg.sort(
            key=lambda group: group.get_turns_till_arrival())

    def __init_groups_to_iceberg(self):
        """
        Initialize the groups and their amount that in their way to the iceberg.
        Taking in account groups that colliding with each other.
        :return:
        :rtype:
        """
        if not self.__is_simulate_started:
            self.__is_simulate_started = True
            self.__groups_to_iceberg = utils.get_groups_way_to_iceberg(
                self.__game,
                self.__iceberg_to_simulate,
                groups_to_check=self.__all_groups
            )
            if not utils.is_empty(self.__groups_to_iceberg):
                self.__analyze_groups_distance()
                self.__sort_groups_by_distance()
                self.__treat_groups_coming_each_other()

    def __analyze_groups_distance(self):
        """
        Analyze real group distance.
        Take in account the bridges.
        """
        for group in self.__groups_to_iceberg:  # type: PenguinGroupSimulate
            source_iceberg = group.get_source()
            bridges = source_iceberg.bridges  # type: List[Bridge]

            # Check whether there is custom bridge going out from this source_iceberg
            source_key = self.__get_iceberg_key(source_iceberg)
            if source_iceberg in self.__custom_bridges_to_iceberg:
                bridges.append(self.__custom_bridges_to_iceberg[source_key])
            # Type: bridge
            for bridge in bridges.sort(key=lambda b: b.duration, reverse=True):
                if group.get_destination() in bridge.get_edges():
                    turns_forward_until_bridge_gone = bridge.speed_multiplier * bridge.duration
                    turns_till_arrival = group.get_turns_till_arrival()
                    if turns_forward_until_bridge_gone >= turns_till_arrival:
                        turns = math.ceil(
                            turns_till_arrival / bridge.speed_multiplier)
                    else:
                        turns = bridge.duration + \
                            (turns_till_arrival - turns_forward_until_bridge_gone)
                    group.move_toward_destination(turns_till_arrival - turns)

    def __move_groups_to_destination(self, turns_to_move=1):
        """
        Move all penguins groups toward destination.

        :param turns_to_move: Number of turns to move.
        :type turns_to_move: int
        """
        for group in self.__groups_to_iceberg:
            group.move_toward_destination(turns_to_move)

    def __treat_iceberg_by_turns(self, turns):
        """
        Add penguins to the iceberg if it's not neutral.

        :param turns: How much turns to simulate on the iceberg.
        :type turns: int
        """
        if type(self.__iceberg_to_simulate) == Iceberg:
            penguins_per_turn = self.__penguins_per_turn
            penguins_to_add = turns * penguins_per_turn
            if not self.is_belong_to_neutral():
                self.__penguin_amount += penguins_to_add

    def __treat_groups_arrived_destination(self):
        """
        Treat each groups arrived destination.
        If enemy, reduce number of penguins.
        If our, append the number of penguins.
        """

        groups_arrived = [
            penguin_group for penguin_group in self.__groups_to_iceberg
            if penguin_group.is_arrived()
        ]

        groups_arrived.sort(
            key=lambda group: group.get_owner().id)  # If number of groups arrived, treat ours as arrived first

        for group in groups_arrived:  # type: PenguinGroupSimulate
            self.__treat_group_arrived_destination(
                group.get_owner(), group.get_penguin_amount())
            self.__groups_to_iceberg.remove(group)

    def __treat_group_arrived_destination(self, owner, penguin_amount):
        """
        Treat group as arrived destination.
        If enemy, reduce number of penguins.
        If our, append the number of penguins.
        :type owner: Player
        :type penguin_amount: int
        :return:
        """
        if self.is_belong_to_neutral():
            self.__treat_group_arrived_iceberg_neutral(owner, penguin_amount)
        else:
            self.__treat_group_arrived_iceberg_not_neutral(
                owner, penguin_amount)

    def __treat_group_arrived_iceberg_neutral(self, owner, penguin_amount):
        """
        Treat group as iceberg belong to enemy or to us.

        :type owner: Player
        :type penguin_amount: int
        """
        if self.__penguin_amount > penguin_amount:
            self.__penguin_amount -= penguin_amount
        else:
            penguin_amount -= self.__penguin_amount
            self.__iceberg_owner = owner
            self.__penguin_amount = 0
            self.__treat_group_arrived_iceberg_not_neutral(
                owner, penguin_amount)

    def __treat_group_arrived_iceberg_not_neutral(self, owner, penguin_amount):
        """
        Treat group as iceberg belong to enemy or to us.

        :type owner: Player
        :param penguin_amount: Amount of penguins in group.
        :type penguin_amount: int
        """
        if self.__iceberg_owner.equals(owner):
            self.__penguin_amount += penguin_amount
        else:
            self.__penguin_amount -= penguin_amount
            if self.__penguin_amount < 0:
                self.__iceberg_owner = owner
                self.__penguin_amount = abs(self.__penguin_amount)
            elif self.__penguin_amount == 0:
                self.__iceberg_owner = self.__game.get_neutral()

    def __treat_groups_coming_each_other(self):
        """
        Check if there is ant group that sent from destination to any source of any penguin-groups.
        If there are, reduce the small from the big.
        """
        groups_from_destination = [
            penguin_group
            for penguin_group in self.__all_groups
            if penguin_group.get_source().equals(self.__iceberg_to_simulate)
        ]
        groups_from_destination.sort(
            key=lambda group: group.get_turns_till_arrival())

        # Check for collision for each group send from destination.
        for source, groups_from_iceberg in itertools.groupby(groups_from_destination,
                                                             lambda x: x.get_destination()):
            groups_from_iceberg = list(groups_from_iceberg)
            groups_from_iceberg.sort(
                key=lambda group: group.get_turns_till_arrival())

            groups_from_source = [
                group for group in self.__groups_to_iceberg if group.get_source().equals(source)]
            groups_from_source.sort(
                key=lambda group: group.get_turns_till_arrival)

            for group_from_iceberg in groups_from_iceberg:  # type: PenguinGroupSimulate
                if group_from_iceberg.get_penguin_amount() > 0:
                    for group_from_source in groups_from_source:  # type: PenguinGroupSimulate
                        if group_from_iceberg.get_penguin_amount() <= 0:
                            break
                        if group_from_source.get_penguin_amount() > 0:
                            group_from_iceberg.collision_with(
                                group_from_source)

        # Remove groups that not has penguins
        self.__groups_to_iceberg = [
            group for group in self.__groups_to_iceberg if group.get_penguin_amount() > 0]

    def __treat_bonus(self):
        bonus_iceberg = self.__game.get_bonus_iceberg()  # type:BonusIceberg
        if bonus_iceberg is not None and not utils.is_bonus_iceberg(self.__game, self.__iceberg_to_simulate):
            bonus_turns_ls = self.__bonus_turns_ls
            index = self.__bonus_turn_index
            while index < len(bonus_turns_ls) and \
                    bonus_turns_ls[index].get_turn() <= self.__current_turn:
                bonus_data = bonus_turns_ls[index]  # type:BonusTurnData
                if self.__iceberg_owner.equals(bonus_data.get_owner()):
                    self.__penguin_amount += bonus_data.get_pengion_bonus()
                index += 1
            self.__bonus_turn_index = index

    def __belong_to(self):
        """
        Return string to whom the iceberg is belong to.
        :rtype: str
        """
        game = self.__game
        owner = self.__iceberg_owner
        if utils.is_neutral(game, owner):
            return 'Netural'
        if utils.is_enemy(game, owner):
            return 'Enemy'
        if utils.is_me(game, owner):
            return 'Me'

    def __get_iceberg_key(self, iceberg):
        return iceberg.unique_id

    def __str__(self):
        num_of_groups_to_iceberg = 0
        if self.__is_simulate_started:
            num_of_groups_to_iceberg = len(self.__groups_to_iceberg)
        ret = 'Simulation: is started:' + str(self.__is_simulate_started) + ', penguin amount ' + str(
            self.get_penguin_amount()) + ', owner ' + self.__belong_to() + ' ' + str(
            self.__iceberg_owner)

        if type(self.__iceberg_to_simulate) == Iceberg:
            ret += ', level ' + str(self.__iceberg_level)

        ret += ', groups: ' + str(num_of_groups_to_iceberg)
        return ret


def valid_instance_of_penguin_group_simulate(penguin_group_simulate):
    """
    Check whether the given penguin_group is isinstance of PenguinGroupSimulate.
    If not, raise ValueError.
    :param penguin_group_simulate:
    """
    if not isinstance(penguin_group_simulate, PenguinGroupSimulate):
        raise ValueError(
            "penguin_group_simulate not instance of PenguinGroupSimulate")
