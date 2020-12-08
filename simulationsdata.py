from penguin_game import *
import utils
from simulation import Simulation

PENGUIN_AMOUNT="penguin_amount"
OWNER = "owner"
ARE_GROUP_REMAIN = "are_group_remains"


class SimulationsData:
    def __init__(self, game):
        self.__game = game  # type: Game
        self.__icebergs_simulations = {}
        self.__max_turn = utils.find_max_distance(game)

    def get(self, iceberg):
        """
        Return list of simulations data, where each index represents turn number.
        :param iceberg: Iceberg to get it simulations.
        :type iceberg: Iceberg
        :return: List[(penguin_amount,owner,are_group_remains)]
        :rtype: List[(int,Player, bool)]
        """
        key = self.__get_iceberg_key(iceberg)
        return self.__icebergs_simulations[key]

    def run_simulations(self):
        """
        :type icebergs_ls: List[Iceberg]
        """
        icebergs_ls = self.__game.get_all_icebergs()
        #icebergs_ls.append(self.__game.get_bonus_iceberg())
        for iceberg in icebergs_ls:
            self.update_iceberg_simulation(iceberg)

    def update_iceberg_simulation(self, *icebergs):
        """
        Resimulate all turns of the given iceberg
        :param iceberg:
        :type iceberg:
        """
        for iceberg in icebergs:
            key = self.__get_iceberg_key(iceberg)
            simulation_data = self.__run_simulation(iceberg)
            self.__icebergs_simulations[key] = simulation_data

    def __run_simulation(self, iceberg):
        """
        Run simulation for current iceberg.
        :param iceberg: iceberg to simulate
        :type iceberg: Iceberg
        :return: list of the iceberg status for all turns. list[(penguin_amount,owner,are_group_remains)].
        :rtype: list[(int,Player, bool)]
        """
        simulation = Simulation(self.__game, iceberg)
        simulation.simulate(0)
        iceberg_simulation_turn = [self.__get_simulation_data(simulation)]
        turns_to_run = utils.find_max_distance(self.__game)
        for i in range(turns_to_run):
            simulation.simulate(1)
            data = self.__get_simulation_data(simulation)
            iceberg_simulation_turn.append(data)
        return iceberg_simulation_turn

    def __get_simulation_data(self, simulation):
        """
        Return the data from the simulation that we want to store for each turn.
        :type simulation: Simulation
        :return: (penguin_amount,owner,are_group_remains)
        :rtype: (int,Player, bool)
        """
        iceberg_turn_data = {
            PENGUIN_AMOUNT: simulation.get_penguin_amount(),
            OWNER: simulation.get_owner(),
            ARE_GROUP_REMAIN: simulation.are_group_remains()
        }
        return iceberg_turn_data

    def __get_iceberg_key(self, iceberg):
        """
        return the iceberg key
        :param iceberg:
        :type iceberg: Iceberg
        :return:
        :rtype:
        """
        return iceberg.id, iceberg.owner.id
