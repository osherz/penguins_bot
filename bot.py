from penguin_game import Player, PenguinGroup, Iceberg
from IcebergsInRisk import *
from utils import * as utils
import math
# import typing
# from typing import List


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

    my_player = game.get_myself()  # type: Player
    # rescu_icebers_in_risk(game, my_player)

    occupy_close_icebergs(game)
    upgrade_icebergs(game)


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


def occupy_close_icebergs(game):
    """
    Occupy close icebergs (neutral and enemy's)
    :type game: Game
    """
    for my_iceberg in game.get_my_icebergs():  # type: Iceberg
        icebergs = game.get_neutral_icebergs(
        ) + game.get_enemy_icebergs()  # type: List[Iceberg]
        icebergs = sorted(
            icebergs, key=my_iceberg.get_turns_till_arrival)
        for dest_iceberg in icebergs:  # type: Iceberg
            turns_to_dest = my_iceberg.get_turns_till_arrival(dest_iceberg)
            future_pengiuins_in_dest, turns_to_dest = utlis.get_penguins_in_x_turns(game,
                                                                                    dest_iceberg, turns_to_dest)
            if future_pengiuins_in_dest <= 0:
                penguins_to_send = abs(future_pengiuins_in_dest)+1
                if my_iceberg.penguin_amount + 1 > penguins_to_send:
                    send_penguins(my_iceberg, penguins_to_send, dest_iceberg)


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
