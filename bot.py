from penguin_game import Player, PenguinGroup, Iceberg
from IcebergsInRisk import *
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
    icebergs_in_risk = get_icebergs_in_risk(
        game, my_player)  # type: IcebergsInRisk
    icebergs_keys_in_risk = sorted(icebergs_in_risk.get_icebergs(
    ), key=lambda iceberg: iceberg.level, reverse=True)  # type: List[Iceberg]
    icebergs_not_in_risk = get_icebergs_not_in(
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
            if are_all_has_enough_penguins(icebergs_can_to_help, penguins_each_iceberg_send):
                print "rescu: ", iceberg
                send_penguins_groups(icebergs_can_to_help,
                                     penguins_each_iceberg_send, iceberg)


def are_all_has_enough_penguins(icebergs, penguins):
    """
    Are all icebergs has more penguined that the given
    :type icebergs: Iceberg
    :type penguins: int
    """
    for iceberg in icebergs:  # type: Iceberg
        if iceberg.penguin_amount <= penguins:
            return False
    return True


def get_icebergs_in_risk(game, my_player):
    """
    Check which enemy groups put my icebergs in danger.
    :type game: Game
    :type myPlayer: Player
    :return: List[Iceberg]
    """
    icbergs_in_risk = IcebergsInRisk()
    enemy_groups = game.get_enemy_penguin_groups()  # List[Iceberg]
    for my_iceberg in game.get_my_icebergs():
        penguins, turns = get_penguins_in_x_turns(game, my_iceberg)
        if penguins <= 0:
            icbergs_in_risk.append(my_iceberg, abs(penguins), turns)

    return icbergs_in_risk


def get_icebergs_not_in(all_icebergs, icebergs):
    """
    Return icebergs that exists in all_icebergs but not in icebergs
    :type all_icebergs: List[Iceberg]
    :type icebergs: List[Iceberg]
    :return: List[Iceberg]
    """
    icebergs_to_return = [
        iceberg for iceberg in all_icebergs if iceberg not in icebergs]
    return icebergs_to_return


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
            future_pengiuins_in_dest, turns_to_dest = get_penguins_in_x_turns(game,
                                                                              dest_iceberg, turns_to_dest)
            if future_pengiuins_in_dest <= 0:
                penguins_to_send = abs(future_pengiuins_in_dest)+1
                if my_iceberg.penguin_amount + 1 > penguins_to_send:
                    send_penguins(my_iceberg, penguins_to_send, dest_iceberg)


def min_penguins_for_occupy(game, iceberg):
    """ 
    Return the minimum of penguins require to occupy iceberg
    taking in account penguins groups

    :type game: Game
    :type iceberg: Iceberg
    :type my_player: Player
    """
    min_penguins = iceberg.penguin_amount

    for enemy_group in game.get_enemy_penguin_groups():  # type: PenguinGroup
        if enemy_group.destination.equal(iceberg):
            min_penguins += enemy_group.penguin_amount

    for my_group in game.get_my_penguin_groups():  # type: PenguinGroup
        if my_group.destination.equal(iceberg):
            min_penguins -= my_group.penguin_amount

    return min_penguins


def get_penguins_in_x_turns(game, iceberg, turns=0):
    """
    Return how much penguins will be in the given iceberg after x turns, and in howmuch turns.
    Negative = enemy/neutral penguins,
    Positive = my player penguins
    :type game: Game
    :type iceberg: Iceberg
    :type turns: int
    :return: (int, int)
    """
    def get_additional_pengions_in_x_turns(iceberg, owner, turns, my_player, enemy):
        """
        Return how much penguins will added in x turns, taking in account only this owner
        """
        additional_penguins = iceberg.penguins_per_turn * turns
        if owner.equals(my_player):
            return additional_penguins
        elif owner.equals(enemy):
            return - 1 * additional_penguins
        return 0

    my_player = game.get_myself()  # type: Player
    enemy = game.get_enemy()  # type: Player

    group_to_this_iceberg = [
        group for group in game.get_all_penguin_groups()
        if group.destination.equals(iceberg)
        and (turns <= 0 or group.‎turns_till_arrival <= turns)
    ]
    group_to_this_iceberg = sorted(group_to_this_iceberg, key=lambda group: group.‎turns_till_arrival)

    penguins = iceberg.penguin_amount
    owner = iceberg.owner
    if not owner.equals(my_player):
        penguins *= -1

    turns_since_start = 0
    for group in group_to_this_iceberg:  # type: PenguinGroup
        # Add penguins that the iceberg invreasing
        penguins += get_additional_pengions_in_x_turns(
            iceberg, owner, group.turns_till_arrival - turns_since_start, my_player, enemy)
        turns_since_start += group.turns_till_arrival

        # Add penguins that arrival from outside
        if group.equals(enemy):
            penguins -= group.penguin_amount
        elif group.equals(my_player):
            penguins += group.penguin_amount

        # update owner
        if penguins > 0:
            owner = my_player
        elif penguins < 0:
            owner = enemy
        else:
            owner = game.get_neutral()

    if turns > turns_since_start:
        penguins += get_additional_pengions_in_x_turns(
            iceberg, owner, turns - turns_since_start, my_player, enemy)
        turns_since_start = turns

    print 'In ', iceberg, ' in ', turns_since_start, ' turns will be ', penguins, ' penguins.'
    return penguins, turns_since_start


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
