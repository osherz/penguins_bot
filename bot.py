from penguin_game import Player, PenguinGroup, Iceberg
import utils
from scores import Scores
import math
from utils import log
from random import shuffle
from simulationsdata import SimulationsData, OWNER, ARE_GROUP_REMAIN, PENGUIN_AMOUNT
from scoredata import ScoreData

# import typing
# from typing import List

MIN_SCORE_FOR_SENDING = 0
TURNS_TO_CHECK = 15


def do_turn(game):
    """
    Makes the bot run a single turn.

    :param game: the current game state.
    :type game: Game
    """
    utils.active_print(game)
    # Go over all of my icebergs.
    log(game.turn, "/", game.max_turns)
    if game.turn == 1 and game.get_bonus_iceberg() is not None:
        log('max bonus turns', game.bonus_iceberg_max_turns_to_bonus, 'bonus', game.get_bonus_iceberg().penguin_bonus)
    occupy_close_icebergs(game)


def occupy_close_icebergs(game):
    """
    Occupy close icebergs (neutral and enemy's)
    :type game: Game
    """
    scores_for_my_icebergs = game.get_my_icebergs()[:]
    if game.get_my_bonus_iceberg() is not None:
        scores_for_my_icebergs.append(game.get_my_bonus_iceberg())
    shuffle(scores_for_my_icebergs)
    log('********************************* START ACTIONS **********************************')
    all_icebergs = game.get_all_icebergs()[:]  # type: list
    if game.get_bonus_iceberg() is not None:
        all_icebergs.append(game.get_bonus_iceberg())

    scores = Scores(game)
    simulation_data = SimulationsData(game)
    simulation_data.run_simulations()

    log('********************************* START ACTIONS **********************************')
    my_iceberg_cnt = 0
    standby_icebergs_score_data = {}
    for my_iceberg in scores_for_my_icebergs:  # type: Iceberg
        icebergs_to_update = []
        log('*************icebrg source', my_iceberg)
        log('Running time: ', game.get_max_turn_time(), ', ', game.get_time_remaining())
        my_iceberg_cnt += 1
        destination_scored_icebergs = get_scored_icebergs(scores, game, my_iceberg,
                                                          all_icebergs, simulation_data)  # type: list
        upgrade_score_for_my_iceberg = scores.score_upgrade(my_iceberg)

        log('upgrade score', upgrade_score_for_my_iceberg)
        continue_to_next_source = False
        if not utils.is_empty(destination_scored_icebergs) and upgrade_score_for_my_iceberg < \
                destination_scored_icebergs[0].get_score():
            while not utils.is_empty(destination_scored_icebergs) and not continue_to_next_source:
                icebergs_to_update = []
                if game.get_time_remaining() < 0:
                    log('time over')
                    break
                log('Running time: ', game.get_max_turn_time(), ', ', game.get_time_remaining())

                iceberg_score_data = destination_scored_icebergs[0]  # type: ScoreData
                dest_iceberg = iceberg_score_data.get_destination()  # type: Iceberg
                min_price = iceberg_score_data.get_min_penguins_for_occupy()
                max_penguins_can_be_sent = iceberg_score_data.get_max_penguins_can_be_sent()
                # If got so much scores but hasn't enough penguins we prefer to wait.
                if min_price > my_iceberg.penguin_amount or min_price > max_penguins_can_be_sent:
                    icebergs_to_update = try_to_send_from_multiple_icebergs(game, iceberg_score_data,
                                                                            standby_icebergs_score_data)
                    continue_to_next_source = True
                else:
                    send_penguins(my_iceberg, min_price, dest_iceberg)
                    icebergs_to_update = [my_iceberg, dest_iceberg]
                    continue_to_next_source = my_iceberg.penguin_amount <= 0

                if not continue_to_next_source:
                    icebergs_to_score = map(lambda iceberg: iceberg.get_destination(),
                                            destination_scored_icebergs[1:])
                    destination_scored_icebergs = get_scored_icebergs(scores, game, my_iceberg, icebergs_to_score,
                                                                      simulation_data)

        elif upgrade_score_for_my_iceberg > 0 and utils.can_be_upgrade(my_iceberg):
            my_iceberg.upgrade()
            icebergs_to_update = [my_iceberg]

        if game.get_time_remaining() < 0:
            log('time over')
            break

        if my_iceberg_cnt < len(game.get_my_icebergs()) or \
                (my_iceberg.penguin_amount > 0 and len(destination_scored_icebergs) > 1):
            simulation_data.update_iceberg_simulation(*icebergs_to_update)

            # if game.get_time_remaining() < 0:
            #    break


def get_scored_icebergs_for_all_my_icebergs(scores, game, simulation_data, source_icebergs=None):
    """
    scores icebergs for all source_icebergs.
    If source_icebergs is None, scores for all my icebergs.

    :type scores: Scores
    :param game: Game status
    :type game: Game
    :param source_icebergs: all source iceberg to score destinations for them
    :type source_icebergs: List[Iceberg]
    """
    if source_icebergs is None:
        source_icebergs = game.get_my_icebergs()
    scores_for_my_icebergs = []
    for my_iceberg in source_icebergs:
        destination_scored_icebergs = get_scored_icebergs(scores, game, my_iceberg,
                                                          game.get_all_icebergs(), simulation_data)  # type: list
        if utils.is_empty(destination_scored_icebergs):
            score = 0
        else:
            score = destination_scored_icebergs[0].get_score()
        scores_for_my_icebergs.append({
            'iceberg': my_iceberg,
            'score': score
        })

    scores_for_my_icebergs.sort(key=lambda iceberg_data: iceberg_data['score'], reverse=True)
    return [iceberg_data['iceberg'] for iceberg_data in scores_for_my_icebergs]


def get_scored_icebergs(scores, game, my_iceberg, icebergs, simulation_data):
    """
    :type icebergs : List[IceBuilding]
    """
    all_icebergs = icebergs[:]
    if my_iceberg in all_icebergs:
        all_icebergs.remove(my_iceberg)
    scored_icebergs = score_icebergs(game, scores, my_iceberg, all_icebergs, simulation_data)
    ret = []
    for iceberg in scored_icebergs:
        ret.append(iceberg)
    return ret


def score_icebergs(game, scores, source_iceberg, icebergs, simulation_data):
    """ Scores the given icebergs.
    Return list of the icebergs sorted by their scores, remove the icebergs with negative score.
    :type game:Game
    :type scores: Scores
    :type source_iceberg: Iceberg
    :type icebergs: List[Iceberg]
    :rtype: List[{Iceberg, int}]
    :return: List[{iceberg, min_price}]
    """

    def get_iceberg_data(iceberg):
        log('****start score', iceberg)
        score_data = score_iceberg(game, scores, source_iceberg, iceberg, simulation_data)
        return score_data

    scores_icebergs = map(lambda iceberg: get_iceberg_data(iceberg), icebergs)

    sort_icebergs_by_score(scores_icebergs)
    print_scores(scores_icebergs)

    scores_icebergs = remove_smalls_score_icebergs(scores_icebergs)

    return scores_icebergs


def print_scores(scores_icebergs):
    def str_data(score_data):
        """
        :type score_data: ScoreData
        """
        return 'iceberg: ' + str(score_data.get_destination()) + \
               ' score: ' + str(score_data.get_score()) + \
               ' min_price: ' + str(score_data.get_min_penguins_for_occupy()) + \
               ' max_penguins_can_be_sent ' + str(score_data.get_max_penguins_can_be_sent())

    log('******** scored icebergs *********')
    log('\n'.join(map(str_data, scores_icebergs)))


def sort_icebergs_by_score(scores_icebergs):
    """ Sort icebergs by score in descending order.

    :type scores_icebergs: list[ScoreData]
    :rtype: None
    """
    scores_icebergs.sort(
        key=lambda iceberg: iceberg.get_score(),
        reverse=True
    )


def remove_smalls_score_icebergs(scores_icebergs):
    """ Remove all icebergs with smalls scores or price <= 0.
    Not changing inplace.

    :type scores_icebergs: List[{Iceberg, int}]
    :rtype: List[{Iceberg, int}]
    :return: List[{Iceberg, score}]
    """
    ls = []
    for iceberg in scores_icebergs:
        if iceberg.get_score() >= MIN_SCORE_FOR_SENDING and iceberg.get_min_penguins_for_occupy() > 0:
            ls.append(iceberg)

    return ls


def score_iceberg(game, scores, source_iceberg, destination_iceberg, simulation_data):
    """ Score the given iceberg and gicen each one the.

    :param game:
    :type game: Game
    :type scores: Scores
    :type source_iceberg: Iceberg
    :type destination_iceberg: Iceberg
    :type simulation_data: SimulationsData
    :rtype: ScoreData
    :return: ScoreData
    """
    if type(destination_iceberg) is Iceberg:
        return scores.score(
            source_iceberg,
            destination_iceberg,
            simulation_data,
            score_by_iceberg_belogns=True,
            score_by_iceberg_level=True,
            score_by_iceberg_distance=True,
            score_by_iceberg_price=True,
            score_by_penguins_gaining=True,
            score_by_iceberg_bonus=False
        )
    else:
        return scores.score(
            source_iceberg,
            destination_iceberg,
            simulation_data,
            score_by_iceberg_belogns=True,
            score_by_iceberg_level=False,
            score_by_iceberg_distance=True,
            score_by_iceberg_price=True,
            score_by_iceberg_bonus=True
        )


def try_to_send_from_multiple_icebergs(game, current_iceberg_score_data, standby_icebergs_score_data):
    """
    Try to send penguins from multiple icebergs.
    :type current_iceberg_score_data: ScoreData
    :type standby_icebergs_score_data: {}
    """
    dest_iceberg = current_iceberg_score_data.get_destination()  # type: Iceberg
    unique_id = dest_iceberg.unique_id
    icebergs_to_update = []
    if unique_id in standby_icebergs_score_data:
        dest_score_data_ls = standby_icebergs_score_data[unique_id]
        dest_score_data_ls.append(current_iceberg_score_data)
        max_penguins_can_be_sent = sum([score_data.get_max_penguins_can_be_sent() for score_data in dest_score_data_ls])
        min_penguins_for_occupy = max([score_data.get_min_penguins_for_occupy() for score_data in dest_score_data_ls])
        if max_penguins_can_be_sent > min_penguins_for_occupy:
            log('Sending from multiple icebergs')
            log(min_penguins_for_occupy)
            icebergs_to_update.append(dest_iceberg)
            for iceberg_score_data in sorted(dest_score_data_ls, key=ScoreData.get_score,
                                             reverse=True):  # type: ScoreData
                source_iceberg = iceberg_score_data.get_source()  # type: Iceberg
                penguins_to_send = min(iceberg_score_data.get_max_penguins_can_be_sent(), min_penguins_for_occupy)
                source_iceberg.send_penguins(dest_iceberg, penguins_to_send)
                min_penguins_for_occupy -= penguins_to_send
                log(source_iceberg, dest_iceberg, penguins_to_send, min_penguins_for_occupy)
                icebergs_to_update.append(source_iceberg)
                if min_penguins_for_occupy <= 0:
                    break
            standby_icebergs_score_data.pop(unique_id)
    else:
        standby_icebergs_score_data[unique_id] = []
        standby_icebergs_score_data[unique_id].append(current_iceberg_score_data)

    return icebergs_to_update


def send_penguins(my_iceberg, destination_penguin_amount, destination):
    """
    Send penguins to destination
    :type my_iceberg: Iceberg
    :type destination_penguin_amount: int
    :type destination: Iceberg
    """
    log(my_iceberg, "sends", destination_penguin_amount, "penguins to", destination)
    my_iceberg.send_penguins(destination, destination_penguin_amount)


def send_penguins_groups(my_icebergs, destination_penguin_amount, destination):
    """
    Send groups of penguins from differrent sources to one destination
    :type my_icebergs: List[Iceberg]
    :type destination_penguin_amount: int
    :type destination: Iceberg
    """
    for iceberg in my_icebergs:
        send_penguins(iceberg, destination_penguin_amount, destination)
