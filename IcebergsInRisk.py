from penguin_game import *
# from typing import List, Dict


class IcebergsInRisk:
    def __init__(self):
        self.icebergs = {}  # type Dict[Iceberg, IcebergInRisk]

    def append(self, iceberg, penguins_in_arrival, turns_until_arrival):
        """
        Add another iceberg in danger.
        If iceberg already exists - penguins_in_arrival is increase 
        and taking the max between turns_until_arrivals.
        :type iceberg: Iceberg
        :type penguins_in_arrival: int
        :type turns_until_arrival: int
        """
        if self.icebergs.has_key(iceberg):
            self.icebergs[iceberg].append(
                penguins_in_arrival, turns_until_arrival)
        else:
            self.icebergs[iceberg] = IcebergInRisk(
                iceberg, penguins_in_arrival, turns_until_arrival)

    def get_icebergs(self):
        """
        :return: Icebergs in danger
        """
        return self.icebergs.keys()


class IcebergInRisk:

    def __init__(self, iceberg, penguins_in_arrival=0, turns_until_arrival=0):
        self.iceberg = iceberg
        self.penguins_in_arrival = penguins_in_arrival
        self.turns_until_arrival = turns_until_arrival

    def append(self, penguins_in_arrival, turns_until_arrival):
        """
        Add another risk group to this iceberg..
        :type penguins_in_arrival: int
        :type turns_until_arrival: int
        """
        self.penguins_in_arrival += penguins_in_arrival
        self.turns_until_arrival = max(
            self.turns_until_arrival, turns_until_arrival)
