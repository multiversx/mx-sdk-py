from typing import Protocol


class IAddressAsOutput(Protocol):
    def bech32(self) -> str:
        return ""

    def pubkey(self) -> bytes:
        return bytes()
