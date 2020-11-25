from penguin_game import PenguinGroup, Game, Iceberg
from penguingroupsimulate import PenguinGroupSimulate
from utils import print_enabled


class IcebergSimulate:
    """
    Penguin group data staructure for simulation.
    """

    def __init__(self, game, iceberg):
        """
        Initialize data by given iceberg.

        :param game: Game status.
        :type game: Game
        :type iceberg: Iceberg
        """
        self.__source_iceberg = iceberg

        self.__cost_factor = iceberg.cost_factor
        self.__upgrade_cost = iceberg.upgrade_cost
        self.__upgrade_level_limit = iceberg.upgrade_level_limit

        self.__origin_level = iceberg.level
        self.__origin_penguin_amount = iceberg.penguin_amount
        self.__origin_penguins_per_turn = iceberg.penguins_per_turn
        self.__origin_owner = iceberg.owner

        self.reset_to_origin()

    def reset_to_origin(self):
        """
        Reset the data to the iceberg origin data.
        :return:
        """
        iceberg = self.__source_iceberg  # type: Iceberg
        self.__owner = iceberg.owner
        self.__penguin_amount = iceberg.penguin_amount
        self.__level = iceberg.level
        self.__penguins_per_turn = iceberg.penguins_per_turn

    def get_owner(self):
        """
        :return: the current iceberg owners
        :rtype: Player
        """
        return self.__owner

    def get_penguin_amount(self):
        """
        :return: iceberg current penguin amount.
        :rtype: int
        """
        return self.__penguin_amount

    def get_level(self):
        """
        :return: current iceberg level
        :rtype: int
        """
        return self.__level

    def get_penguins_per_turn(self):
        """
        :return: iceberg penguins produce per turn
        :rtype: int
        """
        return self.__penguins_per_turn

    def can_send_penguins(self, destination, penguin_amount):
        """
        :param destination: the iceberg to send the penguins to
        :type destination: Iceberg
        :param penguin_amount: amount of penguins to send
        :type penguin_amount: int
        :return: whether the current iceberg can send the penguins or not
        :rtype: bool
        """
        return self.__source_iceberg.can_send_penguins(destination, penguin_amount)

    def can_upgrade(self):
        """
        :return: whether the iceberg can upgrade itself
        :rtype: bool
        """
        return self.__source_iceberg.can_upgrade()

    def get_turns_till_arrival(self, destination):
        """
        :param destination: the iceberg which we calculate the distance to
        :type destination: Iceberg
        :return: the distance from current iceberg to destination
        :rtype: int
        """
        return self.__source_iceberg.get_turns_till_arrival(destination)

    def create_penguins_to_send(self, destination, penguin_amount):
        """
        :param destination: iceberg to send penguins group to
        :type destination: Iceberg
        :param penguin_amount: amount of penguins to send
        :type penguin_amount: int
        """
        #:TODO to make sure that this iceberg have enough penguins to send.
        if self.can_send_penguins(penguin_amount):
            self.__penguin_amount -= penguin_amount
            return PenguinGroupSimulate(self.__game, source_iceberg=self.__source_iceberg,
                                        destination_iceberg=destination,
                                        penguin_amount=penguin_amount)
        else:
            return None

    def upgrade(self):
        #:TODO make sure that this iceberg have enough penguins for upgrade.
        if self.can_upgrade():
            self.__penguin_amount -= self.__upgrade_cost
            self.__level += 1
        else:
            return None

    def penguin_group_arrival(self, penguin_groups):
        """
        Treat groups as arrived destination.
        If enemy, reduce number of penguins.
        If our, append the number of penguins.

        if this iceberg is neutral sort the penguin groups by amount.

        :param penguin_groups:
        :type penguin_groups: PenguinGroupSimulate
        """

        if self.is_belong_to_neutral():
            penguin_groups = penguin_groups.sort(key=lambda group: group.penguin_amount)

        for penguin_group in penguin_groups:  # type: PenguinGroupSimulate
            if self.is_belong_to_neutral():
                self.__treat_group_arrived_iceberg_neutral(penguin_group.owner, penguin_group.penguin_amount)
            else:
                self.__treat_group_arrived_iceberg_not_neutral(penguin_group.owner, penguin_group.penguin_amount)

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
            self.__owner = owner
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
                self.__owner = owner
                self.__penguin_amount = abs(self.__penguin_amount)
            elif self.__penguin_amount == 0:
                self.__owner = self.__game.get_neutral()

    def is_belong_to_me(self):
        return self.__owner.equals(self.__game.get_myself())

    def is_belong_to_enemy(self):
        return self.__owner.equals(self.__game.get_enemy())

    def is_belong_to_neutral(self):
        return self.__owner.equals(self.__game.get_neutral())
