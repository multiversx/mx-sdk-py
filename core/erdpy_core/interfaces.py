
from typing import Protocol


class IAddress(Protocol):
    def bech32(self) -> str: ...


INonce = int
IGasPrice = int
IGasLimit = int
IChainID = str
ITransactionVersion = int
ITransactionOptions = int
ISignature = bytes
ITokenIdentifier = str


class ITransactionValue(Protocol):
    def __str__(self) -> str: ...


class ITransactionPayload(Protocol):
    def encoded(self) -> str: ...


class ICodeMetadata(Protocol):
    def serialize(self) -> bytes: ...
