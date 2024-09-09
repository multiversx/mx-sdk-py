from typing import Protocol

from multiversx_sdk.core.interfaces import IAddress


class IAccount(Protocol):
    @property
    def address(self) -> IAddress:
        ...

    def sign(self, data: bytes) -> bytes:
        ...
