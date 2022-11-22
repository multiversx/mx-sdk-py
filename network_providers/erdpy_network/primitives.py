from interface import IAddress
from erdpy_network.utils import dec_to_padded_hex


class Address(IAddress):
    def __init__(self, adr: str):
        self.address = adr

    def bech32(self) -> str:
        return self.address


class Nonce:
    nonce: int

    def __init__(self, value: int):
        self.nonce = value

    def value_of(self):
        return self.nonce

    def hex(self):
        return dec_to_padded_hex(self.nonce)
