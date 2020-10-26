from penguin_game import Player, PenguinGroup, Iceberg
from IcebergsInRisk import *
import utils
from scores import Scores
import math
# import typing
# from typing import List

MIN_SCORE_FOR_SENDING = 20


def do_turn(game):
    """
    Makes the bot run a single turn.

    :param game: the current game state.
    :type game: Game
    """

    # TODO: Check which icebergs are in real danger.
    # TODO: Occupy close icbergs & check whether the enemy want to occupt them too.
    # TODO: Upgrades.

    # Go over all of my icebergs.
    print game.turn, "/", game.get_max_turn_time()
    scores = Scores(game)
    my_player = game.get_myself()  # type: Player
    # rescu_icebers_in_risk(game, my_player)

    occupy_close_icebergs(scores, game)
    upgrade_icebergs(game)


def occupy_close_icebergs(scores, game):
    """
    Occupy close icebergs (neutral and enemy's)
    :type game: Game
    """
    for my_iceberg in game.get_my_icebergs():  # type: Iceberg
        icebergs = score_icebergs(scores, my_iceberg, game.get_all_icebergs())
        for iceberg in icebergs:  # type: (Iceberg, int)
            dest_iceberg, min_price = iceberg['iceberg'], iceberg['min_price']
            print dest_iceberg, min_price
            send_penguins(my_iceberg, min_price, dest_iceberg)


def score_icebergs(scores, source_iceberg, icebergs):
    """ Scores the given icebergs.
    Return list of the icebergs sorted by their scores, remove the icebergs with negative score.
    :type scores: Scores
    :type source_iceberg: Iceberg
    :type icebergs: List[Iceberg]
    :rtype: List[{Iceberg, int}]
    :return: List[{iceberg, min_price}]
    """
    def get_iceberg_data(iceberg):
        score, min_price = score_iceberg(
            scores, source_iceberg, iceberg)
        return {
            "iceberg": iceberg,
            "score": score,
            "min_price": min_price
        }

    scores_icebergs = map(
        lambda iceberg: get_iceberg_data(iceberg),
        icebergs
    )

    scores_icebergs = remove_smalls_score_icebergs(scores_icebergs)
    sort_icebergs_by_score(scores_icebergs)

    print '******** scored icebergs *********'
    print '\n'.join(map(str, scores_icebergs))

    scores_icebergs = map(
        lambda iceberg: {
            'iceberg': iceberg['iceberg'],
            'min_price': iceberg['min_price']
        },
        scores_icebergs
    )

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
    print scores_icebergs
    ls = []
    for iceberg in scores_icebergs:
        if iceberg['score'] >= MIN_SCORE_FOR_SENDING:
            ls.append(iceberg)

    return ls


def score_iceberg(scores, source_iceberg, destination_iceberg):
    """ Score the given iceberg and gicen each one the.

    :type scores: Scores
    :type source_iceberg: Iceberg
    :type destination_iceberg: Iceberg
    :rtype: (int, int)
    :return: score, min_penguins_for_occupy)
    """
    min_penguins_for_occupy_score, min_penguins_for_occupy = scores.score_by_iceberg_price(
        source_iceberg, destination_iceberg)

    score = scores.score_by_iceberg_belogns(destination_iceberg) + \
        scores.score_by_iceberg_distance(source_iceberg, destination_iceberg) + \
        scores.score_by_iceberg_level(destination_iceberg) + \
        min_penguins_for_occupy_score

    print 'source', source_iceberg, 'destination', destination_iceberg, 'score', score, 'min_penguins_for_occupy', min_penguins_for_occupy
    return score, min_penguins_for_occupy


def send_penguins(my_iceberg, destination_penguin_amount, destination):
    """
    Send penguins to destination
    :type my_iceberg: Iceberg
    :type destination_penguin_amount: int
    :type destination: Iceberg
    """
    print my_iceberg, "sends", destination_penguin_amount, "penguins to", destination
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


def upgrade_icebergs(game):
    """
    Upgrade all icebergs that can be upgraded and didn't do any action.
    :type game: Game
    """
    for iceberg in game.get_my_icebergs():  # type: Iceberg
        if can_be_upgrade(iceberg):
            print "upgrade: ", iceberg, "penguins: ", iceberg.penguin_amount, "for update: ", iceberg.upgrade_cost
            iceberg.upgrade()


def can_be_upgrade(iceberg):
    """
    Return whether given iceberg can be upgrade.
    :type iceberg: Iceberg
    """
    print 'upgrade enable status for ', iceberg, ': ', iceberg.penguin_amount, '/', iceberg.upgrade_cost, 'for level', iceberg.level+1
    return iceberg.can_upgrade and \
        iceberg.upgrade_level_limit > iceberg.level and \
        not iceberg.already_acted and \
        iceberg.penguin_amount > iceberg.upgrade_cost


def rescu_icebers_in_risk(game, my_player):
    """
    Rescu icbergs in risk
    :type game: Game
    :type my_player: Player
    """
    icebergs_in_risk = utlis.get_icebergs_in_risk(
        game, my_player)  # type: IcebergsInRisk
    icebergs_keys_in_risk = sorted(icebergs_in_risk.get_icebergs(
    ), key=lambda iceberg: iceberg.level, reverse=True)  # type: List[Iceberg]
    icebergs_not_in_risk = utlis.get_icebergs_not_in(
        game.get_my_icebergs(), icebergs_in_risk.get_icebergs())  # List[Iceberg]
    for iceberg in icebergs_keys_in_risk:  # type: Iceberg
        # type: IcebergInRisk
        iceberg_in_risk = icebergs_in_risk.icebergs[iceberg]
        turns = iceberg_in_risk.turns_until_arrival
        penguins = iceberg_in_risk.penguins_in_arrival
        icebergs_can_to_help = [
            iceberg_option for iceberg_option in icebergs_not_in_risk
            if iceberg_option.get_turns_till_arrival(iceberg) <= turns
        ]

        # Whether there are any icebergs can to help
        if len(icebergs_can_to_help) > 0:
            penguins_each_iceberg_send = int(math.ceil(
                penguins / len(icebergs_can_to_help)))
            if utlis.are_all_has_enough_penguins(icebergs_can_to_help, penguins_each_iceberg_send):
                print "rescu: ", iceberg
                send_penguins_groups(icebergs_can_to_help,
                                     penguins_each_iceberg_send, iceberg)
