from penguin_game import *
import utils
from utils import log
from scoredata import ScoreData
from occupymethoddecision import OccupyMethodData, SEND_PENGUINS, BUILD_BRIDGE
from simulationsdata import SimulationsData, OWNER
from mapchecker import MapChecker

ENEMY_BELONGS_SCORE = 27
NEUTRAL_BELONGS_SCORE = 17
MY_BELONGS_SCORE = 0
CANT_DO_ACTION_SCORE = -10
UPGRADE_TURNS_TO_CHECK = 15
OUR_SOURCE_ICEBERG_IN_DANGER_SCORE = -9999
OUR_UPGRADE_ICEBERG_IN_DANGER_SCORE = -9999
UNUPGRADEABLE_ICEBERG_SCORE = -9999
DONT_DO_ACTION_SCORE = -9999
LAST_ENEMY_ICEBERG_THAT_CAN_BE_OCCUPIED = 100
OUR_DESTINATION_ICEBERG_IN_DANGER_SCORE = 200
MIN_PENGUINS_AMOUNT_AVG_PERCENT = 0
IRREVERSIBLE_SCORE = -1000
BONUS_SCORE = 0
SOURCE_LEVEL_SMALL_THAN_DESTINATION_SCORE = 0
MIN_LEVEL_FOR_ACTION = 1
OUR_DESTINATION_ICEBERG_FAR_FROM_ENEMY_SCORE = -80

# Factors
DISTANCE_FACTOR_SCORE = -35
PRICE_FACTOR_SCORE = -5
LEVEL_FACTOR_SCORE = 4
UPDATE_FACTOR_SCORE = 1.4
AVG_DISTANCE_FROM_PLAYERS_FACTOR_SCORE = 0.3
SUPPORT_SCORE_FACTOR = 1.2

OUR_BONUS_FACTOR_SCORE = 0.1
ENEMY_BONUS_FACTOR_SCORE = 1.2
NATURAL_BONUS_FACTOR_SCORE = 1.1

PENGUINS_GAINING_SCORE_FACTOR = 0.2

STRONG_ENEMY_CLOSE = 0


class Scores:
    def __init__(self, game, simulation_data):
        """
        :type game: Game
        """
        self.__change_score_by_map()
        self.__game = game
        self.__simulation_data = simulation_data
        self.__max_price = self.__find_max_price()
        self.__max_distance = self.__find_max_distance()
        log('Max distance:', self.__max_distance)
        self.__average_distance = self.__calculate_average_distance()
        log('Average distance:', self.__average_distance)
        self.__average_penguins_in_our_icebergs = self.__calculate_average_penguins_in_our_icebergs()
        self.__min_penguins_amount = int(
            MIN_PENGUINS_AMOUNT_AVG_PERCENT * self.__average_penguins_in_our_icebergs)

    def score(self, source_iceberg, destination_iceberg_to_score, occupy_method_data,
              score_by_iceberg_belogns=False,
              score_by_iceberg_level=False,
              score_by_iceberg_distance=False,
              score_by_iceberg_price=False,
              score_by_penguins_gaining=False,
              score_by_iceberg_bonus=False,
              score_by_avg_distance_from_players=False):
        """
        Score the iceberg by the scores specified.
        :type occupy_method_data: OccupyMethodData
        :return: ScoreData
        :rtype: ScoreData
        """
        scores = []
        simulation_data = self.__simulation_data
        max_penguins_can_be_use = occupy_method_data.max_penguins_can_be_use
        min_penguins_for_occupy_score = self.__score_by_iceberg_price(
            source_iceberg, destination_iceberg_to_score, simulation_data, occupy_method_data)
        if score_by_iceberg_price:
            scores.append(min_penguins_for_occupy_score)
        if utils.is_bonus_iceberg(self.__game, source_iceberg) or source_iceberg.level < MIN_LEVEL_FOR_ACTION:
            scores.append(DONT_DO_ACTION_SCORE)
        # if the score will not be positive, return score.
        if sum(scores) >= IRREVERSIBLE_SCORE:
            log('penguin_amount_after_all_groups_arrived')
            iceberg_owner_after_all_groups_arrived = simulation_data.get(destination_iceberg_to_score)[-1][OWNER]

            if score_by_iceberg_belogns:
                scores.append(self.__score_by_iceberg_belogns(source_iceberg, destination_iceberg_to_score,
                                                              iceberg_owner_after_all_groups_arrived))

            if score_by_penguins_gaining:
                scores.append(self.__score_by_penguins_gaining(source_iceberg, destination_iceberg_to_score,
                                                               iceberg_owner_after_all_groups_arrived))

            if score_by_iceberg_distance:
                scores.append(
                    self.__score_by_iceberg_distance(
                        source_iceberg, destination_iceberg_to_score)
                )

            if score_by_iceberg_level:
                scores.append(self.__score_by_iceberg_level(source_iceberg,
                                                            destination_iceberg_to_score,
                                                            iceberg_owner_after_all_groups_arrived))

            if score_by_avg_distance_from_players:
                scores.append(self.__score_by_avg_distance_from_players(source_iceberg,
                                                                        destination_iceberg_to_score, simulation_data))

            if score_by_iceberg_bonus:
                bonus_iceberg_score = self.__score_by_iceberg_bonus(
                    destination_iceberg_to_score, occupy_method_data.owner)
                scores.append(bonus_iceberg_score)
        log('score:', scores)
        # TODO: change "scores" to integer variabel.

        action = occupy_method_data.method
        return ScoreData(source_iceberg,
                         destination_iceberg_to_score,
                         occupy_method_data.min_penguins_for_occupy,
                         max_penguins_can_be_use,
                         occupy_method_data.spare_penguins,
                         sum(scores),
                         send_penguins=action == SEND_PENGUINS,
                         build_bridge=action == BUILD_BRIDGE)

    def score_upgrade(self, iceberg_to_score):
        """
        Score the upgrade action of iceberg_to_score.

        :param iceberg_to_score: Iceberg to score the upgrade action.
        :type iceberg_to_score: Iceberg
        :return: Score
        :rtype: float
        """
        game = self.__game
        if utils.is_bonus_iceberg(game, iceberg_to_score):
            return UNUPGRADEABLE_ICEBERG_SCORE
        score = 0
        upgrade_cost = iceberg_to_score.upgrade_cost
        if not utils.can_be_upgrade(iceberg_to_score):
            if utils.is_bonus_iceberg(game,
                                      iceberg_to_score) or iceberg_to_score.level >= iceberg_to_score.upgrade_level_limit:
                return UNUPGRADEABLE_ICEBERG_SCORE
            score += CANT_DO_ACTION_SCORE
        else:
            owner = self.__simulation_data.get(iceberg_to_score)[-1][OWNER]

            if not game.get_myself().equals(owner):
                score += OUR_UPGRADE_ICEBERG_IN_DANGER_SCORE

        next_level = iceberg_to_score.level + 1
        score += - upgrade_cost + (next_level * UPGRADE_TURNS_TO_CHECK)

        ret = UPDATE_FACTOR_SCORE * score

        ret += self.__score_by_strong_enemy_close_to_me(iceberg_to_score)
        return ret

    def __score_by_avg_distance_from_players(self, source_iceberg, iceberg_to_score, simulation_data):
        """
        Scoring by the relation between the average distance from enemy and ours.
        """
        ours_avg_distance, enemy_avg_distance = simulation_data.get_avg_distance_from_players(
            iceberg_to_score)

        score = (enemy_avg_distance - ours_avg_distance) * AVG_DISTANCE_FROM_PLAYERS_FACTOR_SCORE
        score += self.__score_by_strong_enemy_close_to_me(source_iceberg)
        return score

    def __score_by_strong_enemy_close_to_me(self, source_iceberg):
        if utils.is_strong_enemy_close_to_me(self.__game, source_iceberg):
            return STRONG_ENEMY_CLOSE
        return 0

    def __score_by_penguins_gaining(self, source_iceberg, destination_iceberg_to_score,
                                    iceberg_owner_after_all_groups_arrived):
        """
        Score by how much penguins will gain if occupy

        :type source_iceberg: Iceberg
        :type destination_iceberg_to_score: Iceberg
        """
        if iceberg_owner_after_all_groups_arrived.equals(self.__game.get_myself()):
            return 0
        turns_to_check = self.__max_distance - \
                         source_iceberg.get_turns_till_arrival(destination_iceberg_to_score)
        return turns_to_check * destination_iceberg_to_score.penguins_per_turn * PENGUINS_GAINING_SCORE_FACTOR

    def __score_by_iceberg_bonus(self, destination_iceberg_to_score, owner_if_no_action_will_made):
        game = self.__game
        if game.get_bonus_iceberg() is None:
            return 0

        if utils.is_neutral(game, owner_if_no_action_will_made) and destination_iceberg_to_score.penguin_amount > 0:
            return DONT_DO_ACTION_SCORE

        penguin_bonus = destination_iceberg_to_score.penguin_bonus
        bonus_score = (
                destination_iceberg_to_score.max_turns_to_bonus - destination_iceberg_to_score.turns_left_to_bonus)
        # check if the bonus iceberg will be ours.
        if utils.is_me(game, owner_if_no_action_will_made):
            return BONUS_SCORE + bonus_score * len(
                self.__game.get_my_icebergs()) * penguin_bonus * OUR_BONUS_FACTOR_SCORE
        # check if the bonus iceberg belongs to the enemy.
        elif utils.is_enemy(game, owner_if_no_action_will_made):
            return BONUS_SCORE + bonus_score * len(
                self.__game.get_enemy_icebergs()) * penguin_bonus * ENEMY_BONUS_FACTOR_SCORE
        # if the bonus iceberg is netural.
        else:
            return BONUS_SCORE + NATURAL_BONUS_FACTOR_SCORE * len(
                self.__game.get_enemy_icebergs()) * penguin_bonus

    def __score_by_iceberg_belogns(self, source_iceberg, iceberg_to_score, iceberg_to_score_owner):
        """
        Scoring by the belongs of the iceberg (my, enemy, neutral)

        :type source_iceberg: Iceberg
        :type iceberg_to_score: Iceberg
        :rtype: float
        """
        game = self.__game
        if iceberg_to_score_owner.equals(game.get_enemy()):
            return ENEMY_BELONGS_SCORE

        if iceberg_to_score_owner.equals(game.get_myself()):
            return MY_BELONGS_SCORE

        return NEUTRAL_BELONGS_SCORE

    def __score_by_support(self, source_iceberg, iceberg_to_score, iceberg_to_score_owner, simulation_data):
        """
        Score the destination based on his need for support.
        Taking in account his penguins amount and his distance from enemy.

        :type source_iceberg: Iceberg
        :type iceberg_to_score: Iceberg
        :rtype: int
        """
        game = self.__game
        is_belong_to_me = iceberg_to_score_owner.equals(game.get_myself())
        score = 0
        is_closest_to_enemy, avr_distance_from_enemy = self.__is_destination_closest_to_enemy(source_iceberg,
                                                                                              iceberg_to_score,
                                                                                              simulation_data)
        if is_belong_to_me and is_closest_to_enemy:
            if not iceberg_to_score is game.get_bonus_iceberg():
                score += (self.__max_distance - avr_distance_from_enemy) * SUPPORT_SCORE_FACTOR
            else:
                score += CANT_DO_ACTION_SCORE
        elif is_belong_to_me:
            score += OUR_DESTINATION_ICEBERG_FAR_FROM_ENEMY_SCORE
        return score

    def __score_by_iceberg_level(self, source_iceberg, iceberg_to_score, iceberg_owner_after_all_groups_arrived):
        """
        Scoring by the iceberg level.

        :type source_iceberg: Iceberg
        :type iceberg_to_score: Iceberg
        :rtype: float
        """
        if utils.is_me(self.__game, iceberg_owner_after_all_groups_arrived):
            if source_iceberg.level <= iceberg_to_score.level:
                return SOURCE_LEVEL_SMALL_THAN_DESTINATION_SCORE
            if iceberg_to_score.level < iceberg_to_score.upgrade_level_limit:
                return LEVEL_FACTOR_SCORE ** iceberg_to_score.penguins_per_turn
        elif utils.is_neutral(self.__game, iceberg_owner_after_all_groups_arrived):
            if MapChecker.get().is_tricky_map() or MapChecker.get().is_extra_far_treasure() or MapChecker.get().is_extra_far():
                return LEVEL_FACTOR_SCORE * iceberg_to_score.penguins_per_turn
            else:
                return LEVEL_FACTOR_SCORE ** iceberg_to_score.penguins_per_turn
        return iceberg_to_score.penguins_per_turn

    def __score_by_iceberg_distance(self, source_iceberg, destination_iceberg_to_score):
        """
        Scoring by the distance between source iceberg to the destination iceberg.

        :type source_iceberg: Iceberg
        :type destination_iceberg_to_score: Iceberg
        :rtype: float:
        """

        distance = utils.get_real_distance_between_icebergs(source_iceberg, destination_iceberg_to_score)

        return DISTANCE_FACTOR_SCORE * (float(distance) / float(self.__max_distance))

    def __score_by_iceberg_price(self, source_iceberg, destination_iceberg_to_score, simulation_data,
                                 occupy_method_data):
        """
        Scoring by the price of the destination iceberg.
        Taking in account the number of the penguins when the penguins-group from the source iceberg will arrive.
        If there is not enough penguins in the source iceberg return (-999, -1).
        If the iceberg belong or will belong to us, return (0,0).
        :type source_iceberg: Iceberg
        :type destination_iceberg_to_score: Iceberg
        :type occupy_method_data: OccupyMethodData
        :rtype: float
        :return: score
        """
        score = 0
        game = self.__game
        min_penguins_for_occupy = occupy_method_data.min_penguins_for_occupy

        log(occupy_method_data)
        if utils.is_me(game, occupy_method_data.owner):  # In the end, the iceberg belongs to us.
            score += self.__score_by_support(source_iceberg, destination_iceberg_to_score, game.get_myself(),
                                             simulation_data)
        elif destination_iceberg_to_score.owner.equals(game.get_myself()):
            # We want to protect out iceberg if it gonna to be occupied.
            score += OUR_DESTINATION_ICEBERG_IN_DANGER_SCORE

        # Max penguins can be used
        max_penguins_can_be_use = occupy_method_data.max_penguins_can_be_use

        # Is source has enough penguins to send
        if max_penguins_can_be_use - min_penguins_for_occupy < self.__min_penguins_amount:
            score += CANT_DO_ACTION_SCORE

        # Score by price
        score += PRICE_FACTOR_SCORE * (float(min_penguins_for_occupy) / self.__max_price)

        if utils.is_enemy(game, destination_iceberg_to_score.owner) \
                and (min_penguins_for_occupy <= max_penguins_can_be_use or utils.is_empty(game.get_neutral_icebergs())) \
                and len(game.get_enemy_icebergs()) == 1:
            score += LAST_ENEMY_ICEBERG_THAT_CAN_BE_OCCUPIED

        # Check whether source will be in danger if send the penguins.
        iceberg_simulation_data = simulation_data.get(source_iceberg)
        owner = iceberg_simulation_data[-1][OWNER]
        if not self.__game.get_myself().equals(owner):
            score += OUR_SOURCE_ICEBERG_IN_DANGER_SCORE
        return score

    def __find_max_distance(self):
        """
        Find the max distance between icebergs.

        :rtype: int
        """
        return utils.find_max_distance(self.__game)

    def __find_max_price(self):
        """
        Find the max price of icebergs.

        :rtype: int
        """
        prices_map = map(
            lambda iceberg: utils.get_actual_penguin_amount(
                self.__game, iceberg),
            self.__game.get_all_icebergs()
        )
        return max(prices_map)

    def __is_belong_to_me(self, iceberg):
        """Check whether the given iceberg belongs to me.

        :type iceberg: Iceberg
        :rtype: bool
        """
        return iceberg.owner.equals(self.__game.get_myself())

    def __calculate_average_penguins_in_our_icebergs(self):
        """
        :return: The average penguins in my icebergs.
        :rtype: int
        """
        sum_penguins = 0
        all_my_icebergs = self.__game.get_my_icebergs()
        for iceberg in all_my_icebergs:  # type: PenguinGroup
            sum_penguins += iceberg.penguin_amount
        return sum_penguins / len(all_my_icebergs)

    def __calculate_average_distance(self):
        """
        Calculate the average distance between all icebergs.
        :return: The average distance.
        :rtype: float
        """
        game = self.__game  # type: Game
        all_icebergs = game.get_all_icebergs()
        all_icebergs_length = len(all_icebergs)
        sum_distances = 0
        for i in range(all_icebergs_length):
            for j in range(i + 1, all_icebergs_length):
                iceberg1 = all_icebergs[i]
                iceberg2 = all_icebergs[j]
                sum_distances += iceberg1.get_turns_till_arrival(iceberg2)

        return sum_distances / (all_icebergs_length * (all_icebergs_length - 1) / 2)

    def __calculate_average_distance_from_enemy(self, iceberg, simulation_data):
        """
        Calculate the distance average between the given iceberg and the enemy icebergs.

        :param iceberg: Iceberg to calculate the distance from him.
        :type iceberg: Iceberg
        :type simulation_data: simulationdata.SimulationData
        :return: distance average
        :rtype: float
        """
        return simulation_data.get_avg_distance_from_players(iceberg)[1]

    def __is_destination_closest_to_enemy(self, source_iceberg, destination_iceberg, simulation_data):
        """
        Check is the source closest to the enemy than the destination.
        :param source_iceberg:
        :param destination_iceberg:
        :return: Whether source closest
        """
        source_avg_distance = self.__calculate_average_distance_from_enemy(
            source_iceberg, simulation_data)
        destination_avg_distance = self.__calculate_average_distance_from_enemy(
            destination_iceberg, simulation_data)
        # TODO: maybe to return int value for more accurate score for distance from enemy.
        return destination_avg_distance < source_avg_distance, destination_avg_distance

    def __calculate_min_penguins_for_support(self, destination_iceberg_to_score):
        """
        calculate the penguins amount to support the destination,
        taking in account the average penguins amount.

        :param destination_iceberg_to_score: Iceberg to support.
        :type destination_iceberg_to_score: Iceberg.
        """
        min_penguins_amount = self.__min_penguins_amount
        if destination_iceberg_to_score.penguin_amount < min_penguins_amount:
            penguins_to_send = min_penguins_amount - \
                               destination_iceberg_to_score.penguin_amount
            return penguins_to_send
        return 0

    def __change_score_by_map(self):
        """
        Change scores by map
        """
        global ENEMY_BELONGS_SCORE, UPDATE_FACTOR_SCORE, UPGRADE_TURNS_TO_CHECK
        map_checker = MapChecker.get()  # type: MapChecker
        if map_checker.is_2X2_map():
            ENEMY_BELONGS_SCORE = 127
        elif map_checker.is_2020_map():
            UPDATE_FACTOR_SCORE = 1.45
            ENEMY_BELONGS_SCORE = 23
        elif map_checker.is_circles():
            UPGRADE_TURNS_TO_CHECK = 20
            ENEMY_BELONGS_SCORE = 40
