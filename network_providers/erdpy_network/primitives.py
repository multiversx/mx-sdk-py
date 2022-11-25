from erdpy_network.utils import decimal_to_padded_hex


class Nonce:
    def __init__(self, value: int):
        self.nonce = value

    def hex(self):
        return decimal_to_padded_hex(self.nonce)
