from penguin_game import PenguinGroup, Game, Iceberg


class IcebergSimulate:
    """
    Penguin group data staructure for simulation.
    """

    def __init__(self, game, iceberg):
        """
        Initialize data by penguin_group
        If penguin_group not assigned then create custom group from the other params.
        penguin_group or all others must be assigned.

        :param game: Game status.
        :type game: Game
        :type iceberg: Iceberg
        """
        self.__source_iceberg = iceberg
        self.reset_to_origin()

    def reset_to_origin(self):
        """
        Reset the data to the penguin_group origin data.
        :return:
        """
        iceberg = self.__source_iceberg
        self.__penguin_amount = iceberg.penguin_amount
        self.__owner = iceberg.owner
        self.__level = iceberg.level
        self.__penguins_per_turn = iceberg.penguins_per_turn

    def get_owner(self):
        """
        :rtype: Player
        """
        return self.__owner

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
