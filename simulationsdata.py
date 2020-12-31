from penguin_game import *
import utils
from simulation import Simulation
from bonusturndata import BonusTurnData

PENGUIN_AMOUNT = "penguin_amount"
OWNER = "owner"
ARE_GROUP_REMAIN = "are_group_remains"
TURNS_UNTIL_BONUS = "turns_until_bonus"
GET_BONUS = "get_bonus"
OURS_AVG_DISTANCE = "ours_avg_distance"
ENEMY_AVG_DISTANCE = "enemy_avg_distance"


class SimulationsData:
    def __init__(self, game):
        self.__game = game  # type: Game
        self.__icebergs_simulations = {}
        self.__icebergs_last_group_turns = {}
        self.__icebergs_avg_distance = {}
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

    def get_avg_distance_from_players(self, iceberg):
        """
        Return average distance of the given iceberg from enemy and our icebergs.
        :type iceberg: Iceberg
        :return: (ours_avg_distance,enemy_avg_distance)
        :rtype: (float, float)
        """
        key = self.__get_iceberg_key(iceberg)
        distances = self.__icebergs_avg_distance[key]
        return distances[OURS_AVG_DISTANCE], distances[ENEMY_AVG_DISTANCE]

    def get_bonus_turns(self):
        """
        Return list of turns that icebergs supposed to get bonus.
        """
        return self.__bonus_turns_ls

    def get_last_group_turn(self, iceberg):
        """
        Return how much turns take for the last group to come.
        """
        key = self.__get_iceberg_key(iceberg)
        return self.__icebergs_last_group_turns[key]

    def run_simulations(self):
        """
        Run simulations for all icebergs.
        """
        icebergs_ls = utils.get_all_icebergs(self.__game)
        for iceberg in icebergs_ls:
            self.update_iceberg_simulation(iceberg)

        for iceberg in icebergs_ls:
            self.__calc_avg_distances(iceberg)

    def update_iceberg_simulation(self, *icebergs):
        """
        Resimulate all turns of the given iceberg
        :param iceberg:
        :type iceberg:
        """
        for iceberg in icebergs:
            if utils.is_bonus_iceberg(self.__game, iceberg):
                self.__bonus_turns_ls = []
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
        simulation = Simulation(game, iceberg, self.get_bonus_turns())
        simulation.simulate(0)
        iceberg_simulation_turn = [self.__get_simulation_data(simulation, iceberg)]
        turns_to_run = utils.find_max_distance(game)
        for i in range(turns_to_run):
            simulation.simulate(1)
            data = self.__get_simulation_data(simulation, iceberg, iceberg_simulation_turn[-1])
            iceberg_simulation_turn.append(data)
            if not simulation.are_group_remains():
                self.__all_groups_arrived(iceberg, simulation.get_owner() ,i)
        return iceberg_simulation_turn

    def __all_groups_arrived(self, iceberg, owner, turn):
        """
        Do some action after all groups have arrived.
        """
        self.__set_last_group_turn(iceberg, turn)

    def __set_last_group_turn(self, iceberg, last_group_turn):
        """
        Set the last group turn for this iceberg.
        """
        key = self.__get_iceberg_key(iceberg)
        self.__icebergs_last_group_turns[key] = last_group_turn

    def __get_simulation_data(self, simulation, iceberg, last_simulation_data=None):
        """
        Return the data from the simulation that we want to store for each turn.
        Return different data depending on iceberg type.
        :rtype: {}
        """
        if utils.is_bonus_iceberg(self.__game, iceberg):
            return self.__get_bonus_simulation_data(simulation, last_simulation_data)
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

    def __get_bonus_simulation_data(self, simulation, last_simulation_data=None):
        """
        Return the data from the simulation of the bonus iceberg that we want to store for each turn.
        :type simulation: Simulation
        :return: {penguin_amount,owner,are_group_remains,turns_until_bonus, get_bonus}
        :rtype: {}
        """
        game = self.__game  # type: Game
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

    def __calculate_average_distance_from_enemy(self, iceberg):
        """
        Calculate the distance average between the given iceberg and the enemy icebergs.

        :param iceberg: Iceberg to calculate the distance from him.
        :type iceberg: Iceberg
        :return: distance average
        :rtype: float
        """
        enemy_icebergs = self.__game.get_enemy_icebergs()
        if len(enemy_icebergs) == 0:
            return 0
        enemy_distance = map(
            lambda enemy_iceberg: enemy_iceberg.get_turns_till_arrival(iceberg),
            enemy_icebergs
        )
        return sum(enemy_distance) / len(enemy_distance)

    def __calculate_average_distance_from_ours(self, iceberg):
        """
        Calculate the distance average between the given iceberg and ours icebergs.

        :param iceberg: Iceberg to calculate the distance from him.
        :type iceberg: Iceberg
        :return: distance average
        :rtype: float
        """
        ours_icebergs = self.__game.get_my_icebergs()
        if len(ours_icebergs) == 0:
            return 0
        ours_distance = map(
            lambda our_iceberg: our_iceberg.get_turns_till_arrival(iceberg),
            ours_icebergs
        )
        return sum(ours_distance) / len(ours_distance)

    def __calc_avg_distances(self, iceberg):
        key = self.__get_iceberg_key(iceberg)
        self.__icebergs_avg_distance[key] = {
            OURS_AVG_DISTANCE: self.__calculate_average_distance_from_ours(iceberg),
            ENEMY_AVG_DISTANCE: self.__calculate_average_distance_from_enemy(iceberg)
        }
