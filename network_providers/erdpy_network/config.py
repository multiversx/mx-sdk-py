from erdpy_network.interface import IPagination
from erdpy_core import Address

ESDT_CONTRACT_ADDRESS = Address.from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u")


class DefaultPagination(IPagination):
    def __init__(self):
        self.start = 0
        self.size = 100

    def get_start(self) -> int:
        return self.start

    def get_size(self) -> int:
        return self.size
