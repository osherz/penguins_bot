from penguin_game import *
import utils
from simulation import Simulation
from bonusturndata import BonusTurnData

PENGUIN_AMOUNT = "penguin_amount"
OWNER = "owner"
ARE_GROUP_REMAIN = "are_group_remains"
TURNS_UNTIL_BONUS = "turns_until_bonus"
GET_BONUS = "get_bonus"


class SimulationsData:
    def __init__(self, game):
        self.__game = game  # type: Game
        self.__icebergs_simulations = {}
        self.__max_turn = utils.find_max_distance(game)
        self.__bonus_turns_ls = []

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

    def get_bonus_turns(self):
        """
        Return list of turns that icebergs supposed to get bonus.
        """
        return self.__bonus_turns_ls

    def run_simulations(self):
        """
        Run simulations for all icebergs.
        """
        icebergs_ls = utils.get_all_icebergs(self.__game)
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
        game = self.__game
        simulation = Simulation(game, iceberg)
        simulation.simulate(0)
        iceberg_simulation_turn = [self.__get_simulation_data(simulation)]
        turns_to_run = utils.find_max_distance(game)
        for i in range(turns_to_run):
            simulation.simulate(1)
            data = self.__get_simulation_data(simulation)
            iceberg_simulation_turn.append(data)
        return iceberg_simulation_turn

    def __get_simulation_data(self, simulation, iceberg, last_simulation_data= None):
        """
        Return the data from the simulation that we want to store for each turn.
        Return different data depending on iceberg type.
        :rtype: {}
        """
        if utils.is_bonus_iceberg(self.__game, iceberg):
            return self.__get_bonus_simulation_data(simulation,last_simulation_data)
        else:
            return self.__get_non_bonus_simulation_data(simulation)

    def __get_non_bonus_simulation_data(self, simulation):
        """
        Return the data from the simulation that we want to store for each turn.
        :type simulation: Simulation
        :return: {penguin_amount,owner,are_group_remains}
        :rtype: {}
        """
        iceberg_turn_data = {
            PENGUIN_AMOUNT: simulation.get_penguin_amount(),
            OWNER: simulation.get_owner(),
            ARE_GROUP_REMAIN: simulation.are_group_remains()
        }
        return iceberg_turn_data

    def __get_bonus_simulation_data(self, simulation, last_simulation_data = None):
        """
        Return the data from the simulation of the bonus iceberg that we want to store for each turn.
        :type simulation: Simulation
        :return: {penguin_amount,owner,are_group_remains,turns_until_bonus, get_bonus}
        :rtype: {}
        """
        game = self.__game # type: Game
        iceberg_turn_data = self.__get_non_bonus_simulation_data(simulation)
        iceberg_turn_data[GET_BONUS] = False
        new_owner = simulation.get_owner()
        if last_simulation_data is None:
            iceberg_turn_data[TURNS_UNTIL_BONUS] = game.get_bonus_iceberg().turns_left_to_bonus
            return iceberg_turn_data

        old_owner = last_simulation_data[OWNER]
        neutral = game.get_neutral()
        if not old_owner.equals(new_owner) or old_owner.equals(neutral) or new_owner.equals(neutral):
            turns_until_bonus = self.__game.bonus_iceberg_max_turns_to_bonus
        else:
            turns_until_bonus = last_simulation_data[TURNS_UNTIL_BONUS] - 1
            if turns_until_bonus == 0:
                iceberg_turn_data[GET_BONUS] = True
                turns_until_bonus = game.bonus_iceberg_max_turns_to_bonus
                self.__bonus_turns_ls.append(
                    BonusTurnData(
                        simulation.get_turns_simulated(),
                        new_owner,
                        game.bonus_iceberg_penguin_bonus
                    )
                )
        iceberg_turn_data[TURNS_UNTIL_BONUS] = turns_until_bonus
        return iceberg_turn_data

    def __get_iceberg_key(self, iceberg):
        """
        return the iceberg key
        :param iceberg:
        :type iceberg: Iceberg
        :return:
        :rtype:
        """
        return iceberg.unique_id
