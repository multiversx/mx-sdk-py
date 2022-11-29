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


class IPagination(Protocol):
    def get_start(self) -> int:
        return 0

    def get_size(self) -> int:
        return 0


class IContractQuery(Protocol):
    def get_encoded_arguments(self):
        return []

    def get_function(self) -> str:
        return ''

    def get_value(self) -> int:
        return 0

    def get_address(self) -> IAddress:
        return IAddress()

    def get_caller(self) -> Union[IAddress, None]:
        return None
