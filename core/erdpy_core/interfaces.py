
from typing import Protocol


class IAddress(Protocol):
    def bech32(self) -> str:
        return ""


INonce = int
ITransactionValue = str
IGasPrice = int
IGasLimit = int
IChainID = str
ITransactionVersion = int
ITransactionOptions = int
ISignature = bytes


class ITransactionPayload(Protocol):
    def encoded(self) -> str:
        return ""
