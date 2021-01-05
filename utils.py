from penguin_game import *
from simulation import Simulation
from simulationsdata import SimulationsData, OWNER, ARE_GROUP_REMAIN, PENGUIN_AMOUNT

TURN_TO_START_PRINT_FROM = 0

__print_enable = False
game = ''  # type: Game


def is_me(game, owner):
    return owner.equals(game.get_myself())


def is_enemy(game, owner):
    return owner.equals(game.get_enemy())


def is_neutral(game, owner):
    return owner.equals(game.get_neutral())


def active_print(game_):
    """
    Enable prints
    """
    global __print_enable, game
    game = game_
    __print_enable = True


def disable_print():
    """
    Enable prints
    """
    global __print_enable
    __print_enable = False


def log(*args):
    """
    Print to log all params if print enabled.
    """
    global __print_enable, game
    if __print_enable and game.turn >= TURN_TO_START_PRINT_FROM:
        print ' '.join([str(x) for x in args])


def min_penguins_to_make_neutral(game, source_iceberg, destination_iceberg, simulation_data):
    """
    Calculate how much penguins need to be send
    so the source_iceberg will make the destination_iceberg neutral.
    Taking in account the level of the destination iceberg, the distance
    and the groups that in their way to the destination iceberg.

    :type game: Game
    :type source_iceberg: Iceberg
    :type destination_iceberg: Iceberg
    :rtype: int
    """
    # TODO: Think of another way to calculate min penguins to send, without another simulation.
    distance = source_iceberg.get_turns_till_arrival(destination_iceberg)
    log('distance', distance)
    penguins, owner, min_turns = get_penguins_in_x_turns(
        game, source_iceberg, destination_iceberg, distance, simulation_data)

    log('min penguins:', penguins, "owner:", owner)
    if not owner.equals(game.get_myself()):
        return penguins
    else:
        return 0


def get_penguins_in_x_turns(game, source_iceberg, destination_iceberg, min_turns, simulation_data):
    """
    Return how much penguins will be in the given iceberg after x turns, and in how much turns.

    :type game: Game
    :type destination_iceberg: Iceberg
    :type min_turns: int
    :type simulation_data: SimulationsData
    :rtype: (int, int)
    :return: (penguins, owner, turns)
    """
    # TODO: Think of another way to calculate min penguins to send, without another simulation.
    simulation = Simulation(game, destination_iceberg,
                            simulation_data.get_bonus_turns())

    iceberg_turns_data = simulation_data.get(destination_iceberg)
    iceberg_min_turns_data = iceberg_turns_data[min_turns]
    log(simulation)
    log(iceberg_min_turns_data)
    last_group_turns = turns_until_last_group_arrived(
        game, destination_iceberg)
    owner = destination_iceberg.owner
    new_owner = iceberg_min_turns_data[OWNER]
    penguin_amount = iceberg_min_turns_data[PENGUIN_AMOUNT]
    groups_sent = True
    not_finish_simulation = True
    if is_neutral(game, owner) and destination_iceberg.penguin_amount > 0:
        # Check what happen if we sent enough penguins to occupy.
        simulation.add_penguin_group(
            source_iceberg, destination_iceberg, penguin_amount + 1)
        simulation.simulate(min_turns)
        log(simulation)
        owner_after_sending = simulation.get_owner()
        if is_enemy(game, owner_after_sending):
            penguin_amount = destination_iceberg.penguin_amount
            simulation.reset_to_origin()
        else:
            simulation.simulate_until_last_group_arrived()
            log(simulation)
            new_penguin_amount = simulation.get_penguin_amount()
            owner_after_sending = simulation.get_owner()
            last_group_turns = simulation.get_turns_simulated()
            not_finish_simulation = False

    if not_finish_simulation:
        if not is_me(game, new_owner):
            # Check what happen if we sent enough penguins to occupy.
            simulation.add_penguin_group(
                source_iceberg, destination_iceberg, penguin_amount + 1)
            simulation.simulate_until_last_group_arrived()
            log(simulation)
            new_penguin_amount = simulation.get_penguin_amount()
            owner_after_sending = simulation.get_owner()
            last_group_turns = simulation.get_turns_simulated()
            log(simulation)
        else:
            groups_sent = False
            new_penguin_amount = iceberg_turns_data[last_group_turns][PENGUIN_AMOUNT]
            owner = iceberg_turns_data[last_group_turns][OWNER]

    if groups_sent:
        # In case we won't send penguins, the iceberg will belong to enemy.
        owner = game.get_enemy()
        if is_neutral(game, owner_after_sending):
            new_penguin_amount += penguin_amount + 1
        elif is_me(game, owner_after_sending):
            new_penguin_amount = penguin_amount
        else:
            new_penguin_amount += penguin_amount + 1

    return new_penguin_amount, owner, last_group_turns


def penguin_amount_after_all_groups_arrived(game, iceberg, penguins_amount_to_send=0, upgrade_cost=None,
                                            simulation_data=None):
    """
    Calculate how much penguins will be after all groups arrived to this iceberg.

    :type game: Game
    :param iceberg: Iceberg to calculate penguins amount for.
    :type iceberg: iceberg
    :param penguins_amount_to_send: How much penguins to reduce before simulation.
    :type penguins_amount_to_send: int
    :param upgrade_cost: If assigned, upgrade iceberg first.
    :type upgrade_cost: int
    :type simulation_data: SimulationsData
    :return: Penguins amount and owner.
    :rtype: int
    """
    if upgrade_cost is None and penguins_amount_to_send == 0:
        iceberg_turn_data = simulation_data.get(
            iceberg)[turns_until_last_group_arrived(game, iceberg)]
        penguins_amount = iceberg_turn_data[PENGUIN_AMOUNT]
        owner = iceberg_turn_data[OWNER]
        return penguins_amount, owner

    if simulation_data is None:
        bonus_turns_ls = []
    else:
        bonus_turns_ls = simulation_data.get_bonus_turns()
    simulation = Simulation(game, iceberg, bonus_turns_ls)
    if penguins_amount_to_send > 0:
        simulation.add_penguin_amount(game.get_enemy(),
                                      penguins_amount_to_send,
                                      is_sending=True)  # Treat as enemy so the penguins will reduce from the amount.
    elif upgrade_cost is not None and penguins_amount_to_send == 0:
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
    if type(iceberg) == BonusIceberg:
        return 0
    additional_penguins = iceberg.penguins_per_turn * turns
    if owner.equals(my_player):
        return additional_penguins
    elif owner.equals(enemy):
        return - 1 * additional_penguins
    return 0


def simulate_with_bridge(game, source_iceberg, destination_iceberg, simulation_data):
    """
    Build custom bridge between the iceberg and simulate until last group arrived.
    Return the owner of iceberg destination after all group arrived.

    :param source_iceberg: Iceberg the build the bridge.
    :type source_iceberg: Iceberg
    :param destination_iceberg: Destination of the bridge 
                                and the iceberg we going to active simulate on.
    :type destination_iceberg: Iceberg
    :type simulation_data: SimulationsData
    :return: Owner of destination after all group arrived.
    :rtype: Player
    """
    bonus_turns_ls = simulation_data.get_bonus_turns()
    simulation = Simulation(game, destination_iceberg, bonus_turns_ls)
    simulation.add_bridge(source_iceberg, source_iceberg.max_bridge_duration,
                          source_iceberg.bridge_speed_multiplier)
    simulation.simulate_until_last_group_arrived()
    return simulation.get_owner()


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
    return type(iceberg) == Iceberg and \
           iceberg.can_upgrade and \
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


__max_distance = -1


def find_max_distance(game):
    """
    Find the max distance between icebergs.
    :param game: Game status
    :type game: Game
    :return: max distance between two farthest icebergs.
    :rtype: int
    """
    global __max_distance
    if __max_distance < 0:
        max_distance = 0
        for iceberg1 in game.get_all_icebergs():  # type: Iceberg
            for iceberg2 in game.get_all_icebergs():  # type: Iceberg
                if not iceberg1.equals(iceberg2):
                    distance = iceberg1.get_turns_till_arrival(iceberg2)
                    if distance > max_distance:
                        max_distance = distance
        __max_distance = max_distance
    return __max_distance


def turns_until_last_group_arrived(game, destination_iceberg):
    """
    return the turns that the last group remain until arrive to destination iceberg.
    :param game: game status
    :type game: Game
    :param destination_iceberg:
    :type destination_iceberg: Iceberg
    :return:
    :rtype: int
    """
    penguin_groups = get_groups_way_to_iceberg(
        game, destination_iceberg)  # type: List[PenguinGroup]
    if is_empty(penguin_groups):
        return 0
    return max(penguin_groups, key=lambda group: group.turns_till_arrival).turns_till_arrival


def can_build_bridge(iceberg_source, iceberg_destination):
    """
    :type iceberg_source: Iceberg
    :type iceberg_destination: Iceberg
    """
    return iceberg_source.can_create_bridge(iceberg_destination) and \
           iceberg_source.penguin_amount >= iceberg_source.bridge_cost and \
           not has_bridge_between(iceberg_source, iceberg_destination)


def has_bridge_between(source_iceberg, destination_iceberg):
    """
    Check whether this iceberg has a bridge.
    :type source_iceberg: Iceberg
    :type destination_iceberg: Iceberg
    :rtype: bool
    """
    for bridge in source_iceberg.bridges:
        if destination_iceberg in bridge.get_edges():
            return True
    return False


def is_bonus_iceberg(game, iceberg):
    """
    Check whether this iceberg is a bonus.
    :rtype game: Game
    :rtype iceberg: Iceberg
    """
    return game.get_bonus_iceberg() is not None and game.get_bonus_iceberg().equals(iceberg)


def get_all_icebergs(game):
    """
    Get all icebergs, including bonus iceberg.
    :type game: Game
    """
    all_icebergs = []
    bonus_iceberg = game.get_bonus_iceberg()
    if bonus_iceberg is not None:
        all_icebergs.append(bonus_iceberg)
    all_icebergs += game.get_all_icebergs()
    return all_icebergs


def is_strong_enemy_close_to_me(game, my_iceberg):
    all_icebergs = game.get_all_icebergs()

    if type(my_iceberg) is not BonusIceberg:
        all_icebergs.remove(my_iceberg)
        closedIceberg = min(all_icebergs,
                            key=lambda iceberg: iceberg.get_turns_till_arrival(my_iceberg))  # type: my_iceberg
        if is_enemy(game,
                    closedIceberg.owner) and closedIceberg.penguin_amount >= my_iceberg.penguin_amount and closedIceberg.penguins_per_turn >= my_iceberg.penguins_per_turn:
            return closedIceberg

    return None


def get_real_distance_between_icebergs(source_iceberg, destination_iceberg):
    """
    Return the real distance between two icebergs, considering bridges.
    :type source_iceberg: Iceberg
    :type destination_iceberg: Iceberg
    """
    distance = source_iceberg.get_turns_till_arrival(destination_iceberg)
    bridges = [
        bridge
        for bridge in source_iceberg.bridges
        if destination_iceberg in bridge.get_edges()
    ]
    if is_empty(bridges):
        return distance
    bridge = max(bridges, key=lambda x: x.duration)
    if bridge.duration > distance:
        return distance // bridge.speed_multiplier
    else:
        return (distance - bridge.duration) + bridge.duration // bridge.speed_multiplier
