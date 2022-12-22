
from erdpy_core.interfaces import INonce


class AccountNonceHolder():
    """
    An abstraction representing an account (user or Smart Contract) on the Network.
    """

    def __init__(self, initial_nonce: INonce = 0):
        self.nonce: INonce = initial_nonce

    def get_nonce_then_increment(self) -> INonce:
        nonce = self.nonce
        self.increment_nonce()
        return nonce

    def increment_nonce(self):
        self.nonce += 1
