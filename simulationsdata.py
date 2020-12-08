from penguin_game import *
import utils
from utils import log
from simulation import Simulation


class SimulationsData:
    def __init__(self, game):
        self.__icebergs_simulations = {}

    def get(self, iceberg):
        """
        Return list of simulations data, where each index represents turn number.
        :param iceberg: Iceberg to get it simulations.
        :type iceberg: Iceberg
        :return: List[(penguin_amount,owner,are_group_remains)]
        :rtype: List[(int,Player, bool)]
        """
        return self.__icebergs_simulations[iceberg]

    def __run_simulations(self, icebergs_ls):
        """
        :type icebergs_ls: List[Iceberg]
        """
        for iceberg in icebergs_ls:
            simulation = Simulation(self.__game, iceberg)
            for i in range(max_turns):
                simulation.simulate(1)
                data = self.__get_simulation_data(simulation)
                self.__icebergs_simulations.append(data)

    def __get_simulation_data(self, simulation):
        """
        :type simulation: Simulation
        :return: (penguin_amount,owner,are_group_remains)
        :rtype: (int,Player, bool)
        """
        return ()
