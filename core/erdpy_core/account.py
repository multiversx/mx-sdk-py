
from erdpy_core.interfaces import IAddress, INonce


class AccountNonceHolder():
    """
    An abstraction representing an account (user or Smart Contract) on the Network.
    """

    def __init__(self, address: IAddress):
        self.address = address
        self.nonce: INonce = 0

    def get_nonce_then_increment(self) -> INonce:
        nonce = self.nonce
        self.increment_nonce()
        return nonce

    def increment_nonce(self):
        self.nonce += 1
