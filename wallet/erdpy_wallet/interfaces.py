
from typing import Protocol

ISignature = bytes


class ISignable(Protocol):
    def serialize_for_signing(self) -> ISignature:
        return bytes()
