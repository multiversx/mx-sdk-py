from enum import Enum


class ByteZero(Enum):
    Upgradeable = 1
    Reserved2 = 2
    Readable = 4


class ByteOne(Enum):
    Reserved1 = 1
    Payable = 2
    PayableByContract = 4


class CodeMetadata:
    def __init__(self, upgradeable: bool = True, readable: bool = True, payable: bool = False, payable_by_contract: bool = False):
        self.upgradeable = upgradeable
        self.readable = readable
        self.payable = payable
        self.payable_by_contract = payable_by_contract

    def serialize(self) -> bytes:
        data = bytearray([0, 0])

        if self.upgradeable:
            data[0] |= ByteZero.Upgradeable.value
        if self.readable:
            data[0] |= ByteZero.Readable.value
        if self.payable:
            data[1] |= ByteOne.Payable.value
        if self.payable_by_contract:
            data[1] |= ByteOne.PayableByContract.value

        return bytes(data)

    def __str__(self) -> str:
        return self.serialize().hex()
