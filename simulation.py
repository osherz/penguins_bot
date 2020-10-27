from penguin_game import Game, Iceberg
from penguingroupsimulate import PenguinGroupSimulate


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
        self.__iceberg_owner = iceberg_to_simulate.owner
        self.reset_to_origin()

    def reset_to_origin(self):
        """
        Reset all data to game status.
        :return:
        """
        game = self.__game
        self.__penguin_groups = map(PenguinGroupSimulate, game.get_all_penguin_groups())
        self.__turns_to_simualte = 0
        self.__current_turn = 0

        iceberg_to_simulate = self.__iceberg_to_simulate
        self.__cost_if_neutral = 0
        self.__penguin_amount = 0
        if self.is_belong_to_neutral():
            self.__cost_if_neutral = iceberg_to_simulate.penguin_amount
        else:
            self.__penguin_amount = iceberg_to_simulate.penguin_amount
        if self.is_belong_to_enemy():
            self.__penguin_amount *= -1

    def get_penguin_amount(self):
        """
        Get penguin amount.
        If positive: The iceberg belong to us.
        If negative: The iceberg belong to enemy.
        If is neutral return 0 in any case so tou need to go to get_cose_if_neutral() to know the amount.
        :return: Penguin amount.
        :rtype: int
        """
        if self.is_belong_to_neutral():
            return 0
        else:
            return self.__penguin_amount

    def add_penguin_group(self, penguin_group_simulate):
        """
        Add custom penguin group.

        :param penguin_group_simulate: Custom penguin group.
        :type penguin_group_simulate: PenguinGroupSimulate
        :return:
        """
        self.__valid_instance_of_penguin_group_simulate(penguin_group_simulate)
        self.__penguin_groups.append(penguin_group_simulate)

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
        penguin_group_simulate = PenguinGroupSimulate(source_iceberg, destination_iceberg, penguin_amount, self.__game)
        self.add_penguin_group(penguin_group_simulate)
        return penguin_group_simulate

    def remove_penguin_group(self, penguin_group_simulate):
        """
        Remove custom group.
        :param penguin_group:
        :return:
        """
        self.__valid_instance_of_penguin_group_simulate(penguin_group_simulate)
        self.__penguin_groups.remove(penguin_group_simulate)

    def is_belong_to_me(self):
        return self.__iceberg_owner.equals(self.__game.get_myself())

    def is_belong_to_enemy(self):
        return self.__iceberg_owner.equals(self.__game.get_enemy())

    def is_belong_to_neutral(self):
        return self.__iceberg_owner.equals(self.__game.get_neutral())

    def __valid_instance_of_penguin_group_simulate(self, penguin_group_simulate):
        """
        Check whether the given penguin_group is isinstance of PenguinGroupSimulate.
        If not, raise ValueError.
        :param penguin_group_simulate:
        """
        if not isinstance(penguin_group_simulate):
            raise ValueError("penguin_group_simulate not instance of PenguinGroupSimulate")
