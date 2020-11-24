from penguin_game import Game, Iceberg
from penguingroupsimulate import PenguinGroupSimulate
import utils
import itertools


class Simulation:
    """
    Simulation of the game.
    """

    def __init__(self, game, iceberg_to_simulate):
        """
        :param game: Game current status
        :type game: Game
        :param iceberg_to_simulate: Iceberg to simulate his penguins amount.
        :type iceberg_to_simulate: Iceberg
        """
        self.__game = game
        self.__iceberg_to_simulate = iceberg_to_simulate
        self.reset_to_origin()

    def reset_to_origin(self):
        """
        Reset all data to game status.
        :return:
        """
        game = self.__game
        self.__is_simulate_started = False
        self.__current_turn = 0

        iceberg_to_simulate = self.__iceberg_to_simulate
        self.__iceberg_owner = iceberg_to_simulate.owner
        self.__iceberg_level = iceberg_to_simulate.level
        self.__penguin_amount = iceberg_to_simulate.penguin_amount
        # TODO: use penguins_per_turn instead of level
        self.__all_groups = map(
            lambda group: PenguinGroupSimulate(game, penguin_group=group),
            game.get_all_penguin_groups()
        )

    def get_penguin_amount(self):
        """
        Get penguin amount.

        :return: Penguin amount.
        :rtype: int
        """
        return self.__penguin_amount

    def simulate(self, turns_to_simulate):
        """
        Start/continue simulation on the iceberg to check how much penguins will be in it in X turns
        :param turns_to_simulate: How much turns to simulate.
        :type turns_to_simulate: int
        """
        self.__init_groups_to_iceberg()

        print "turns: ", turns_to_simulate
        for turn in range(turns_to_simulate):
            self.__current_turn += 1
            self.__move_groups_to_destination()
            self.__treat_iceberg_by_turns(1)
            self.__treat_groups_arrived_destination()

    def simulate_until_last_group_arrived(self):
        """
        Start/continue to simulate until the last group arrival to destination.

        :return:
        """
        self.__init_groups_to_iceberg()
        if len(self.__groups_to_iceberg) > 0:
            sorted_groups_by_turns = sorted(
                self.__groups_to_iceberg,
                key=lambda group: group.get_turns_till_arrival()
            )
            last_group = sorted_groups_by_turns[-1]
            turns = last_group.get_turns_till_arrival()
            self.simulate(turns)

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
            raise NotImplementedError("You can't add groups after simulate started. Please reset and try again")
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

    def add_penguin_amount(self, owner, penguin_amount):
        """
        Add penguin amount to the iceberg, appropriate the owner of the penguins.
        Changed the owner if needed.

        :type owner: Player
        :param penguin_amount: Penguins to add.
        :type penguin_amount: int
        """
        self.__treat_group_arrived_destination(owner, penguin_amount)

    def upgrade_iceberg(self, cost):
        """
        Upgrade the iceberg.
        Assume that the iceberg can be upgrade.
        Check only are there enough penguins.
        """
        if cost < self.get_penguin_amount():
            self.__penguin_amount -= cost
            self.__iceberg_level += 1

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

    def is_belong_to_me(self):
        return self.__iceberg_owner.equals(self.__game.get_myself())

    def is_belong_to_enemy(self):
        return self.__iceberg_owner.equals(self.__game.get_enemy())

    def is_belong_to_neutral(self):
        return self.__iceberg_owner.equals(self.__game.get_neutral())

    def __init_groups_to_iceberg(self):
        if not self.__is_simulate_started:
            self.__is_simulate_started = True
            self.__groups_to_iceberg = utils.get_groups_way_to_iceberg(
                self.__game,
                self.__iceberg_to_simulate,
                groups_to_check=self.__all_groups
            )
            self.__treat_groups_coming_each_other()

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
        iceberg_level = self.__iceberg_level
        penguins_to_add = turns * iceberg_level
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
            self.__treat_group_arrived_destination(group.get_owner(), group.get_penguin_amount())
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
            self.__treat_group_arrived_iceberg_not_neutral(owner, penguin_amount)

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
            self.__treat_group_arrived_iceberg_not_neutral(owner, penguin_amount)

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
        groups_from_destination.sort(key=lambda group: group.get_turns_till_arrival())

        # Check for collision for each group send from destination.
        for source, groups_from_iceberg in itertools.groupby(groups_from_destination,
                                                             lambda x: x.get_destination()):
            groups_from_iceberg = list(groups_from_iceberg)
            groups_from_iceberg.sort(key=lambda group: group.get_turns_till_arrival())

            groups_from_source = [group for group in self.__groups_to_iceberg if group.get_source().equals(source)]
            groups_from_source.sort(key=lambda group: group.get_turns_till_arrival)

            for group_from_iceberg in groups_from_iceberg:  # type: PenguinGroupSimulate
                if group_from_iceberg.get_penguin_amount() > 0:
                    for group_from_source in groups_from_source:  # type: PenguinGroupSimulate
                        if group_from_iceberg.get_penguin_amount() <= 0:
                            break
                        if group_from_source.get_penguin_amount() > 0:
                            group_from_iceberg.collision_with(group_from_source)

        # Remove groups that not has penguins
        self.__groups_to_iceberg = [group for group in self.__groups_to_iceberg if group.get_penguin_amount() > 0]

    def __str__(self):
        return 'Simulation: penguin amount ' + str(self.get_penguin_amount()) + ', owner ' + str(
            self.__iceberg_owner) + ', level ' + str(self.__iceberg_level)


def valid_instance_of_penguin_group_simulate(penguin_group_simulate):
    """
    Check whether the given penguin_group is isinstance of PenguinGroupSimulate.
    If not, raise ValueError.
    :param penguin_group_simulate:
    """
    if not isinstance(penguin_group_simulate, PenguinGroupSimulate):
        raise ValueError("penguin_group_simulate not instance of PenguinGroupSimulate")
