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
        game,source_iceberg, destination_iceberg, distance)

    print 'min penguins:', penguins
    if penguins == 0:
        return 1

    if penguins > 0:
        return 0

    return abs(penguins) + 1


def get_penguins_in_x_turns(game, source_iceberg, destination_iceberg, min_turns):
    """
    Return how much penguins will be in the given iceberg after x turns, and in howmuch turns.
    Negative = enemy/neutral penguins,
    Positive = my player penguins

    :type game: Game
    :type destination_iceberg: Iceberg
    :type min_turns: int
    :rtype: (int, int)
    :return: (penguins, turns)
    """
    simulation = Simulation(game, destination_iceberg)
    simulation.simulate(min_turns)
    print simulation
    cost = 0
    if not simulation.is_belong_to_me():
        cost = simulation.get_cost()
        # Check what happen if we sent enough penguins to occupy.
        simulation.reset_to_origin()
        simulation.add_penguin_group(source_iceberg,destination_iceberg, cost+1)
        simulation.simulate_until_last_group_arrived()
        print simulation

    penguin_amount = simulation.get_penguin_amount()
    if simulation.is_belong_to_neutral():
        penguin_amount = -1 * simulation.get_cost_if_neutral()
        penguin_amount += -cost
    elif simulation.is_belong_to_me() and cost > 0:
        penguin_amount = -cost
    else:
        penguin_amount -= cost
    return penguin_amount, simulation.get_turns_simulated()

def penguin_amount_after_all_groups_arrived(game, iceberg, penguins_amount_to_reduce=0, upgrade_cost=None):
    """
    Calculate how much penguins will be after all groups arrived to this iceberg.

    :type game: Game
    :param iceberg: Iceberg to calculate penguins amount for.
    :type iceberg: iceberg
    :param penguins_amount_to_reduce: How much penguins to reduce befure simulation.
    :type penguins_amount_to_reduce: int
    :param upgrade_cost: If assigned, upgrade iceberg first.
    :type upgrade_cost: int
    :return: Penguins amount. If negative belong to enemy, if positive belong to me else neutral.
    :rtype: int
    """
    simulation = Simulation(game, iceberg)
    print '1. Simulate source:', simulation
    simulation.add_penguin_amount(True, penguins_amount_to_reduce) # Treat as enemy so the penguins will reduce from the amount.
    if upgrade_cost is not None:
        simulation.upgrade_iceberg(upgrade_cost)
    print '2. Simulate source:', simulation
    simulation.simulate_until_last_group_arrived()
    print '3. Simulate source:', simulation
    if simulation.is_belong_to_neutral():
        return simulation.get_cost()
    else:
        return simulation.get_penguin_amount()

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
    :type icebergs: List[Iceberg]
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

def get_actual_penguin_amount(game, iceberg):
    """
    Calculate the actual penguin amount including the additional penguin amount getting in this turn.

    :type game: Game
    :type iceberg: Iceberg
    """
    if iceberg.owner.equals(game.get_neutral()):
        return iceberg.penguin_amount
    return iceberg.penguin_amount + iceberg.penguins_per_turn