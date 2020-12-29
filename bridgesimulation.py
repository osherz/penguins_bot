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

    def __str__(self):
        return 'edges: ' + str(self.__edges) + ' duration: ' + str(self.duration) + ' speed_multiplier: ' + str(
            self.speed_multiplier)
