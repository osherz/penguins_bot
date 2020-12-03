from penguin_game import Player, PenguinGroup, Iceberg
import utils
from scores import Scores
import math
from utils import log
from random import shuffle

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
    scores = Scores(game)
    my_player = game.get_myself()  # type: Player
    # rescu_icebers_in_risk(game, my_player)

    occupy_close_icebergs(scores, game)


def occupy_close_icebergs(scores, game):
    """
    Occupy close icebergs (neutral and enemy's)
    :param scores:
    :type scores:
    :type game: Game
    """
    # scores_for_my_icebergs = get_scored_icebergs_for_all_my_icebergs(scores, game, game.get_my_icebergs())
    scores_for_my_icebergs = game.get_my_icebergs()[:]
    shuffle(scores_for_my_icebergs)

    log('********************************* START ACTIONS **********************************')
    all_icebergs = game.get_all_icebergs()  # type: list
    all_icebergs.append(game.get_bonus_iceberg())
    log(all_icebergs)
    for my_iceberg in scores_for_my_icebergs:  # type: Iceberg
        log('*************icebrg source', my_iceberg)
        log('Running time: ', game.get_max_turn_time(), ', ', game.get_time_remaining())
        destination_scored_icebergs = get_scored_icebergs(scores, game, my_iceberg,
                                                          all_icebergs)  # type: list
        upgrade_score_for_my_iceberg = scores.score_upgrade(my_iceberg)

        log('upgrade score', upgrade_score_for_my_iceberg)

        if not utils.is_empty(destination_scored_icebergs) and upgrade_score_for_my_iceberg < \
                destination_scored_icebergs[0]['score']:
            while not utils.is_empty(destination_scored_icebergs) and my_iceberg.penguin_amount > 0:
                iceberg = destination_scored_icebergs[0]  # type: (Iceberg, int)
                dest_iceberg, min_price = iceberg['iceberg'], iceberg['min_price']
                send_penguins(my_iceberg, min_price, dest_iceberg)

                icebergs_to_score = map(lambda iceberg: iceberg['iceberg'], destination_scored_icebergs[1:])
                destination_scored_icebergs = get_scored_icebergs(scores, game, my_iceberg, icebergs_to_score)

        elif upgrade_score_for_my_iceberg > 0:
            my_iceberg.upgrade()
        if game.get_time_remaining() < 0:
            break


def get_scored_icebergs_for_all_my_icebergs(scores, game, source_icebergs=None):
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
                                                          game.get_all_icebergs())  # type: list
        if utils.is_empty(destination_scored_icebergs):
            score = 0
        else:
            score = destination_scored_icebergs[0]['score']
        scores_for_my_icebergs.append({
            'iceberg': my_iceberg,
            'score': score
        })

    scores_for_my_icebergs.sort(key=lambda iceberg_data: iceberg_data['score'], reverse=True)
    return [iceberg_data['iceberg'] for iceberg_data in scores_for_my_icebergs]


def get_scored_icebergs(scores, game, my_iceberg, icebergs):
    """
    :type icebergs : List[IceBuilding]
    """
    all_icebergs = icebergs[:]
    if my_iceberg in all_icebergs:
        all_icebergs.remove(my_iceberg)
    scored_icebergs = score_icebergs(game, scores, my_iceberg, all_icebergs)
    ret = []
    for iceberg in scored_icebergs:
        if iceberg['min_price'] > 0:
            ret.append(iceberg)
        elif iceberg['min_price'] == 0:
            pass
            # TODO: to decide waht to do with our iceberg that needs penguins from some reason
    return ret


def score_icebergs(game, scores, source_iceberg, icebergs):
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
        score, min_price = score_iceberg(game, scores, source_iceberg, iceberg)
        return {
            "iceberg": iceberg,
            "score": score,
            "min_price": min_price
        }

    scores_icebergs = map(lambda iceberg: get_iceberg_data(iceberg), icebergs)

    sort_icebergs_by_score(scores_icebergs)
    log('******** scored icebergs *********')
    log('\n'.join(map(str, scores_icebergs)))
    scores_icebergs = remove_smalls_score_icebergs(scores_icebergs)

    return scores_icebergs


def sort_icebergs_by_score(scores_icebergs):
    """ Sort icebergs by score in descending order.

    :type scores_icebergs: list[{Iceberg, int}]
    :rtype: None
    """
    scores_icebergs.sort(
        key=lambda iceberg: iceberg['score'],
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
        if iceberg['score'] >= MIN_SCORE_FOR_SENDING or iceberg['min_price'] <= 0:
            ls.append(iceberg)

    return ls


def score_iceberg(game, scores, source_iceberg, destination_iceberg):
    """ Score the given iceberg and gicen each one the.

    :param game:
    :type game: Game
    :type scores: Scores
    :type source_iceberg: Iceberg
    :type destination_iceberg: Iceberg
    :rtype: (int, int)
    :return: score, min_penguins_for_occupy)
    """
    if type(destination_iceberg) is Iceberg:
        return scores.score(
            source_iceberg,
            destination_iceberg,
            score_by_iceberg_belogns=True,
            score_by_iceberg_level=True,
            score_by_iceberg_distance=True,
            score_by_iceberg_price=True,
            score_by_iceberg_bonus=False
        )
    else:
        return scores.score(
            source_iceberg,
            destination_iceberg,
            score_by_iceberg_belogns=True,
            score_by_iceberg_level=False,
            score_by_iceberg_distance=True,
            score_by_iceberg_price=False,
            score_by_iceberg_bonus=True
        )



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
