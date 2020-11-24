from penguin_game import PenguinGroup, Game, Iceberg


class PenguinGroupSimulate:
    """
    Penguin group data staructure for simulation.
    """

    def __init__(self, game, penguin_group = None, source_iceberg = None, destination_iceberg=None, penguin_amount=None):
        """
        Initialize data by penguin_group
        If penguin_group not assigned then create custom group from the other params.
        penguin_group or all others must be assigned.

        :param game: Game status.
        :type game: Game
        :param penguin_group: Penguin group to attach to.
        :type penguin_group: PenguinGroup
        :param source_iceberg: Iceberg to send penguin from it
        :type source_iceberg: Iceberg
        :param destination_iceberg: Iceberg to send penguin to it
        :type destination_iceberg: Iceberg
        :param penguin_amount: How much penguin to send.
        :type penguin_amount: iny
        """
        if penguin_group is None:
            self.__source_iceberg = source_iceberg
            self.__destination_iceberg = destination_iceberg
            self.__origin_penguin_amount = penguin_amount
            self.__origin_turns_till_arrival = self.__source_iceberg.get_turns_till_arrival(self.__destination_iceberg)
            self.__is_enemy = source_iceberg.owner.equals(game.get_enemy())
        else:
            self.__source_iceberg = penguin_group.source
            self.__destination_iceberg = penguin_group.destination
            self.__origin_penguin_amount = penguin_group.penguin_amount
            self.__origin_turns_till_arrival = penguin_group.turns_till_arrival
            self.__is_enemy = penguin_group.source.owner.equals(game.get_enemy())

        self.__owner = self.__source_iceberg.owner
        self.reset_to_origin()

    def reset_to_origin(self):
        """
        Reset the data to the penguin_group origin data.
        :return:
        """
        self.__penguin_amount = self.__origin_penguin_amount
        self.__turns_till_arrival = self.__origin_turns_till_arrival

    def get_destination(self):
        """
        Get the destination iceberg.

        :rtype: Iceberg
        """
        return self.__destination_iceberg

    def get_source(self):
        """
        Get the source iceberg.

        :rtype: Iceberg
        """
        return self.__source_iceberg

    def get_owner(self):
        """
        :rtype: Player
        """
        return self.__owner

    def is_enemy(self):
        """
        :return: Is group belong to enemy
        :rtype: bool
        """
        return self.__is_enemy

    def is_mine(self):
        """
        :return: Is group belong to us.
        :rtype: bool
        """
        return not self.is_enemy()

    def get_penguin_amount(self):
        """
        :return: Penguin amount.
        :rtype: int
        """
        return self.__penguin_amount

    def get_turns_till_arrival(self):
        """
        :return: Turns till arrival.
        :rtype: int
        """
        return self.__turns_till_arrival

    def move_toward_destination(self, turns = 1):
        """
        Move on to destination by number of turns.
        If turns is too much raise exception.
        If after that turns the group is arrive his destination return True, else return False.

        :param turns: How much turns to move on.
        :type turns: int
        :return: Is arrived
        :rtype: bool
        """
        if self.__turns_till_arrival - turns >= 0:
            self.__turns_till_arrival-=turns
            return self.is_arrived()
        else:
            raise ValueError("Turns bigger than turns-till-arrival")

    def is_arrived(self):
        """
        Is arrived to destination.

        :return: Is arrived.
        :rtype: bool
        """
        return self.__turns_till_arrival == 0

    def collision_with(self, other_penguin_group):
        """
        Make a collision with other penguin group.
        Check which of the groups win the collision and how much penguins left to him.
        Update the penguins remains in each of the group.

        :type other_penguin_group: PenguinGroupSimulate
        """
        if other_penguin_group.get_penguin_amount() > self.get_penguin_amount():
            other_penguin_group.__penguin_amount -= self.get_penguin_amount()
            self.__penguin_amount = 0
        else:
            self.__penguin_amount -= other_penguin_group.get_penguin_amount()
            other_penguin_group.__penguin_amount = 0

    def __eq__(self, other):
        """

        :param other:
        :type other: PenguinGroupSimulate
        :return:
        """
        if not isinstance(other, PenguinGroupSimulate):
            return False

        return other.__source_iceberg.equals(self.__source_iceberg) and \
               other.__destination_iceberg.equals(self.__destination_iceberg) and \
               other.__penguin_amount == self.__penguin_amount


    def __ne__(self, other):
        return not self.__eq__(other)
