class AccountNonceHolder():
    """An abstraction representing an account's nonce on the Network."""

    def __init__(self, initial_nonce: int = 0):
        """Creates an acount nonce holder object from an initial nonce.

        Args:
            initial_nonce (int): the current nonce of the account"""
        self.nonce = initial_nonce

    def get_nonce_then_increment(self) -> int:
        """Returns the current nonce then increments it

        Returns:
            int: the current nonce"""
        nonce = self.nonce
        self.increment_nonce()
        return nonce

    def increment_nonce(self):
        """Increments the current nonce"""
        self.nonce += 1
