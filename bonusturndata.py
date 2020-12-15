class BonusTurnData:
    """
    Store data of turn that bonus should be given.
    """

    def __init__(self, turn, owner, penguins_bonus):
        self.__turn = turn
        self.__owner = owner
        self.__pengiun_bonus = penguins_bonus

    def get_turn(self):
        return self.__turn

    def get_owner(self):
        return self.__owner

    def get_pengion_bonus(self):
        return self.__pengiun_bonus