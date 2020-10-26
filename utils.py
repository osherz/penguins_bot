from penguin_game import *


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


def min_penguins_for_occupy(game, source_iceberg, destination_iceberg):
    """
    Calculate how much penguins need to be send 
    so the source_iceberg will occupy the destination_iceberg.
    Taking in account the level of the destination iceberg, the distance 
    and the groups that in their way to the destination iceberg.

    :type game: Game
    :type source_iceberg: Iceberg
    :type destination_iceberg: Iceberg
    :rtype: int
    """
    distance = destination_iceberg.get_turns_till_arrival(source_iceberg)
    penguins, min_turns = get_penguins_in_x_turns(
        game, destination_iceberg, distance)

    if penguins == 0:
        return 1

    if penguins > 0:
        return 0

    return abs(penguins) + 1


def get_penguins_in_x_turns(game, iceberg, turns=0):
    """
    Return how much penguins will be in the given iceberg after x turns, and in howmuch turns.
    Negative = enemy/neutral penguins,
    Positive = my player penguins

    :type game: Game
    :type iceberg: Iceberg
    :type turns: int
    :rtype: (int, int)
    :return: (penguins, turns)
    """
    my_player = game.get_myself()  # type: Player
    enemy = game.get_enemy()  # type: Player

    group_to_this_iceberg = [
        group for group in game.get_all_penguin_groups()
        if group.destination.equals(iceberg) and (turns <= 0 or group.turns_till_arrival <= turns)
    ]
    group_to_this_iceberg = sorted(group_to_this_iceberg, key=lambda group: group.turns_till_arrival)

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


def get_icebergs_not_in(all_icebergs, icebergs):
    """
    Return icebergs that exists in all_icebergs but not in icebergs
    :type all_icebergs: List[Iceberg]
    :type icebergs: List[Iceberg]
    :rtype: List[Iceberg]
    """
    icebergs_to_return = [
        iceberg for iceberg in all_icebergs if iceberg not in icebergs]
    return icebergs_to_return


def get_icebergs_in_risk(game, my_player):
    """
    Check which enemy groups put my icebergs in danger.
    :type game: Game
    :type myPlayer: Player
    :rtype: List[Iceberg]
    """
    icbergs_in_risk = []
    for my_iceberg in game.get_my_icebergs():
        penguins, turns = get_penguins_in_x_turns(game, my_iceberg)
        if penguins <= 0:
            icbergs_in_risk.append(my_iceberg, abs(penguins), turns)

    return icbergs_in_risk


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


def is_empty(ls):
    """
    Check is the given list is empty
    :param ls: List to checl
    :type ls: list
    :return: Is empty
    :rtype: bool
    """
    return len(ls) == 0