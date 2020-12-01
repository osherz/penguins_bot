from penguin_game import *
from simulation import Simulation

__print = False


def active_print():
    """
    Enable prints
    """
    global __print
    __print = True


def disable_print():
    """
    Enable prints
    """
    global __print
    __print = False


def print_enabled():
    global __print
    return __print


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
    penguins, owner, min_turns = get_penguins_in_x_turns(
        game, source_iceberg, destination_iceberg, distance)

    if print_enabled():
        print 'min penguins:', penguins, "owner:", owner
    if not owner.equals(game.get_myself()):
        return penguins + 1
    else:
        return 0


def get_penguins_in_x_turns(game, source_iceberg, destination_iceberg, min_turns):
    """
    Return how much penguins will be in the given iceberg after x turns, and in how much turns.

    :type game: Game
    :type destination_iceberg: Iceberg
    :type min_turns: int
    :rtype: (int, int)
    :return: (penguins, owner, turns)
    """
    simulation = Simulation(game, destination_iceberg)
    simulation.simulate(min_turns)
    if print_enabled():
        print simulation
    penguin_amount = 0
    owner = game.get_myself()
    if not simulation.is_belong_to_me():
        penguin_amount = simulation.get_penguin_amount()
        owner = simulation.get_owner()
        # Check what happen if we sent enough penguins to occupy.
        simulation.reset_to_origin()
        simulation.add_penguin_group(source_iceberg, destination_iceberg, penguin_amount + 1)
    simulation.simulate_until_last_group_arrived()
    if print_enabled():
        print simulation

    new_penguin_amount = simulation.get_penguin_amount()
    if simulation.is_belong_to_neutral():
        new_penguin_amount += penguin_amount
        owner = game.get_enemy()  # In case we won't send penguins, the iceberg will belong to enemy.
    elif simulation.is_belong_to_me():
        new_penguin_amount = penguin_amount
    else:
        new_penguin_amount += penguin_amount
        owner = game.get_enemy()  # In case we won't send penguins, the iceberg will belong to enemy.

    return new_penguin_amount, owner, simulation.get_turns_simulated()


def penguin_amount_after_all_groups_arrived(game, iceberg, penguins_amount_to_send=0, upgrade_cost=None):
    """
    Calculate how much penguins will be after all groups arrived to this iceberg.

    :type game: Game
    :param iceberg: Iceberg to calculate penguins amount for.
    :type iceberg: iceberg
    :param penguins_amount_to_reduce: How much penguins to reduce before simulation.
    :type penguins_amount_to_reduce: int
    :param upgrade_cost: If assigned, upgrade iceberg first.
    :type upgrade_cost: int
    :return: Penguins amount and owner.
    :rtype: int
    """
    simulation = Simulation(game, iceberg)
    if penguins_amount_to_send > 0:
        simulation.add_penguin_amount(game.get_enemy(),
                                      penguins_amount_to_send,
                                      is_sending=True)  # Treat as enemy so the penguins will reduce from the amount.
    if upgrade_cost is not None and penguins_amount_to_send == 0:
        simulation.upgrade_iceberg(upgrade_cost)
    simulation.simulate_until_last_group_arrived()

    return simulation.get_penguin_amount(), simulation.get_owner()


def get_groups_way_to_iceberg(game, iceberg, groups_to_check=None):
    """
    Get all the penguins group in their way to the given iceberg.

    :param game: Game status
    :type game: Game
    :param iceberg: Destination iceberg
    :type iceberg: iceberg
    :param groups_to_check: optional. You can decide which groups to check or leave it None to check all groups.
    :type groups_to_check: List[PenguinGroup]
    :return: Penguins group in their way to the iceberg. If groups_to_check is list of PenguinGroupSimulate,
             so the return will be list of PenguinGroupSimulate.
    :rtype: List[PenguinGroup]
    """
    if groups_to_check is None:
        groups_to_check = game.get_all_penguin_groups()
    groups = [
        group for group in groups_to_check
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
           iceberg.penguin_amount >= iceberg.upgrade_cost


def get_actual_penguin_amount(game, iceberg):
    """
    Calculate the actual penguin amount including the additional penguin amount getting in this turn.

    :type game: Game
    :type iceberg: Iceberg
    """
    if iceberg.owner.equals(game.get_neutral()):
        return iceberg.penguin_amount
    return iceberg.penguin_amount
