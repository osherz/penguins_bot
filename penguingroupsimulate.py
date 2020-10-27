from penguin_game import PenguinGroup, Game, Iceberg


class PenguinGroupSimulate:
    """
    Penguin group data staructure for simulation.
    """

    def __init__(self, penguin_group, game):
        """
        Initialize data by penguin_group
        :param penguin_group: Penguin group to attach to.
        :type penguin_group: PenguinGroup
        :param game: Game status.
        :type game: Game
        """
        self.__is_custom = False
        self.__penguin_group = penguin_group
        self.__is_enemy = penguin_group.owner.equals(game.get_enemy())
        self.reset_to_origin()

    def __init__(self, source_iceberg, destination_iceberg, penguin_amount, game):
        """
        Initialize data by penguin_group

        :param source_iceberg: Iceberg to send penguin from it
        :type source_iceberg: Iceberg
        :param destination_iceberg: Iceberg to send penguin to it
        :type destination_iceberg: Iceberg
        :param penguin_amount: How much penguin to send.
        :type penguin_amount: iny
        :param game: Game status.
        :type game: Game
        """
        self.__is_custom = True
        self.__source_iceberg = source_iceberg
        self.__destination_iceberg = destination_iceberg
        self.__origin_penguin_amount = penguin_amount
        self.__is_enemy = source_iceberg.owner.equals(game.get_enemy())
        self.reset_to_origin()

    def is_enemy(self):
        """
        Is group belong to enemy
        :return: bool
        """
        return self.__is_enemy

    def is_mine(self):
        """
        Is group belong to us.
        :return: bool
        """
        return not self.is_enemy()

    def get_penguin_amount(self):
        """
        Get penguin amount.
        :return:
        """
        return self.__penguin_amount

    def reset_to_origin(self):
        """
        Reset the data to the penguin_group origin data.
        :return:
        """
        if self.__is_custom:
            self.__penguin_amount = self.__origin_penguin_amount
            self.turns_till_arrival = self.__source_iceberg.get_turns_till_arrival(self.__destination_iceberg)
        else:
            penguin_group = self.__penguin_group
            self.__penguin_amount = penguin_group.penguin_amount
            self.turns_till_arrival = penguin_group.turns_till_arrival
