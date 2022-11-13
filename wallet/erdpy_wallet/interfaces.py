
from typing import Protocol

ISignature = bytes


class ISignable(Protocol):
    def serialize_for_signing(self) -> ISignature:
        return bytes()

    def apply_signature(self, signature: ISignature):
        pass
