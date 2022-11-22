from typing import Any, Dict, Protocol, Union


class ISerializable(Protocol):
    def to_dictionary(self) -> Dict[str, Any]:
        return self.__dict__


class IAddress(Protocol):
    def bech32(self) -> str:
        return ""


class ITransaction(ISerializable, Protocol):
    def to_dictionary(self) -> Dict[str, Any]:
        return {}

    def get_hash(self) -> str:
        return ""


class ISimulateResponse(ISerializable):
    pass


class ISimulateCostResponse(ISerializable):
    pass


class IPagination(Protocol):
    start: int = 0
    size: int = 100

    def get_start(self) -> int:
        return 0

    def get_size(self) -> int:
        return 0


class IContractQuery(Protocol):
    address: IAddress
    caller: Union[IAddress, None]
    function: str
    value: str

    def get_encoded_arguments(self):
        return []

    def get_function(self) -> str:
        return ''

    def get_value(self) -> int:
        return 0
