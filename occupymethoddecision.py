from penguin_game import *

SEND_PENGUINS = 'send_penguins'
BUILD_BRIDGE = 'build_bridge'

class OccupyMethodData:
    """
    Handle data that important for occupy.
    """

    def __init__(self, min_penguins_for_occupy, min_penguins_for_netural, recommended_penguins_for_occupy, method):
        """
        :param method: SEND_PENGUINS or BUILD_BRIDGE
        :type method: str
        """
        self.min_penguins_for_occupy = min_penguins_for_occupy
        self.min_penguins_for_netural = min_penguins_for_netural
        self.recommended_penguins_for_occupy = recommended_penguins_for_occupy
        self.method = method

