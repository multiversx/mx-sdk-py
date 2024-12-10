from typing import Protocol


class IRandomness(Protocol):
    salt: bytes
    iv: bytes
    id: str
