from erdpy_network.interface import IPagination


class DefaultPagination(IPagination):
    def __init__(self):
        self.start = 0
        self.size = 100

    def get_start(self) -> int:
        return self.start

    def get_size(self) -> int:
        return self.size
