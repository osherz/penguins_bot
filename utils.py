from penguin_game import *
from simulation import Simulation


def min_penguins_for_occupy(game, iceberg):
    """ 
    Return the minimum of penguins require to occupy iceberg
    taking in account penguins groups

    :type game: Game
    :type iceberg: Iceberg
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
    distance = source_iceberg.get_turns_till_arrival(destination_iceberg)
    penguins, min_turns = get_penguins_in_x_turns(
        game, destination_iceberg, distance)

    print 'min penguins:', penguins
    if penguins == 0:
        return 1

    if penguins > 0:
        return 0

    return abs(penguins) + 1


def get_penguins_in_x_turns(game, iceberg, min_turns):
    """
    Return how much penguins will be in the given iceberg after x turns, and in howmuch turns.
    Negative = enemy/neutral penguins,
    Positive = my player penguins

    :type game: Game
    :type iceberg: Iceberg
    :type min_turns: int
    :rtype: (int, int)
    :return: (penguins, turns)
    """
    simulation = Simulation(game, iceberg)
    simulation.simulate(min_turns)
    cost = 0
    if not simulation.is_belong_to_me():
        cost = simulation.get_cost()
        # Check what happen if we sent enough penguins to occupy.
        simulation.add_penguin_amount(False, cost + 1)

    # Continue simulate
    if simulation.are_group_remains():
        simulation.simulate_until_last_group_arrived()

    penguin_amount = simulation.get_penguin_amount()
    if simulation.is_belong_to_neutral():
        penguin_amount = -1 * simulation.get_cost_if_neutral()
    penguin_amount += cost
    return penguin_amount, simulation.get_turns_simulated()


def get_groups_way_to_iceberg(game, iceberg):
    """
    Get all the penguins group in their way to the given iceberg.

    :param game: Game status
    :type game: Game
    :param iceberg: Destination iceberg
    :type iceberg: iceberg
    :return: Penguins group in their way to the iceberg.
    :rtype: List[PenguinGroup]
    """
    groups = [
        group for group in game.get_all_penguin_groups()
        if group.destination.equals(iceberg)
    ]
    if len(groups) > 0:
        print 'groups to iceberg', iceberg, ':', groups
        print game.get_all_penguin_groups()
    return groups


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


def can_be_upgrade(iceberg):
    """
    Return whether given iceberg can be upgrade.
    :type iceberg: Iceberg
    """
    return iceberg.can_upgrade and \
           iceberg.upgrade_level_limit > iceberg.level and \
           not iceberg.already_acted and \
           iceberg.penguin_amount > iceberg.upgrade_cost
