from penguin_game import Bridge


class BridgeSimulation:
    def __init__(self, source_iceberg, destination_iceberg, duration, speed_multiplier):
        self.__edges = [
            source_iceberg,
            destination_iceberg
        ]
        self.duration = duration
        self.speed_multiplier = speed_multiplier

    def get_edges(self):
        return self.__edges
