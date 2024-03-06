from typing import Protocol


class IAccountOnNetwork(Protocol):
    nonce: int
    balance: int
