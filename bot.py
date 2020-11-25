from penguin_game import Player, PenguinGroup, Iceberg
import utils
from scores import Scores
import math

# import typing
# from typing import List

MIN_SCORE_FOR_SENDING = 0
TURNS_TO_CHECK = 15
PENGUINS_FOR_HELP = 0

def do_turn(game):
    """
    Makes the bot run a single turn.

    :param game: the current game state.
    :type game: Game
    """

    # Go over all of my icebergs.
    print
    game.turn, "/", game.get_max_turn_time()
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
    for my_iceberg in game.get_my_icebergs():  # type: Iceberg
        print '*************icebrg source', my_iceberg

        icebergs_to_score = [iceberg for iceberg in game.get_all_icebergs() if not iceberg.equals(my_iceberg)]
        destination_scored_icebergs = get_scored_icebergs(scores, game, my_iceberg, icebergs_to_score)  # type: list
        upgrade_score_for_my_iceberg = scores.score_upgrade(my_iceberg)

        print 'upgrade score', upgrade_score_for_my_iceberg

        if not utils.is_empty(destination_scored_icebergs) and upgrade_score_for_my_iceberg < \
                destination_scored_icebergs[0]['score']:
            while not utils.is_empty(destination_scored_icebergs):
                iceberg = destination_scored_icebergs[0]
                # type: (Iceberg, int)
                dest_iceberg, min_price = iceberg['iceberg'], iceberg['min_price']
                send_penguins(my_iceberg, min_price, dest_iceberg)

                icebergs_to_score = map(lambda iceberg: iceberg['iceberg'], destination_scored_icebergs[1:])
                destination_scored_icebergs = get_scored_icebergs(scores, game, my_iceberg, icebergs_to_score)

        elif upgrade_score_for_my_iceberg > 0:
            my_iceberg.upgrade()


def get_scored_icebergs(scores, game, my_iceberg, icebergs):
    all_icebergs = icebergs
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
        print '****start score', iceberg
        score, min_price = score_iceberg(game, scores, source_iceberg, iceberg)
        if min_price == 0:
            min_price = PENGUINS_FOR_HELP
        return {
            "iceberg": iceberg,
            "score": score,
            "min_price": min_price
        }

    scores_icebergs = map(lambda iceberg: get_iceberg_data(iceberg), icebergs)

    sort_icebergs_by_score(scores_icebergs)
    print '******** scored icebergs *********'
    print 'source iceberg:', source_iceberg
    print '\n'.join(map(str, scores_icebergs))
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
    """ Remove all icebergs with smalls scors.
    Not changing inplace.

    :type scores_icebergs: List[{Iceberg, int}]
    :rtype: List[{Iceberg, int}]
    :return: List[{Iceberg, score}]
    """
    ls = []
    for iceberg in scores_icebergs:
        if iceberg['score'] >= MIN_SCORE_FOR_SENDING:
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
    min_penguins_for_occupy_score, min_penguins_for_occupy = scores.score_by_iceberg_price(
        source_iceberg, destination_iceberg)

    print 'scores for:', destination_iceberg, scores.score_by_iceberg_belogns(source_iceberg,
                                                                                           destination_iceberg), \
        scores.score_by_iceberg_distance(source_iceberg, destination_iceberg), \
        scores.score_by_iceberg_level(destination_iceberg), \
        min_penguins_for_occupy_score
    score = scores.score_by_iceberg_belogns(source_iceberg, destination_iceberg) + \
            scores.score_by_iceberg_distance(source_iceberg, destination_iceberg) + \
            scores.score_by_iceberg_level(destination_iceberg) + \
            min_penguins_for_occupy_score

    return score, min_penguins_for_occupy


def send_penguins(my_iceberg, destination_penguin_amount, destination):
    """
    Send penguins to destination
    :type my_iceberg: Iceberg
    :type destination_penguin_amount: int
    :type destination: Iceberg
    """
    print
    my_iceberg, "sends", destination_penguin_amount, "penguins to", destination
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
