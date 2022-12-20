from typing import Any, Dict, List, Protocol, Union


class ISerializable(Protocol):
    def to_dictionary(self) -> Dict[str, Any]: ...


class IAddress(Protocol):
    def bech32(self) -> str: ...


class ITransaction(ISerializable, Protocol):
    def to_dictionary(self) -> Dict[str, Any]: ...


class IPagination(Protocol):
    def get_start(self) -> int: ...

    def get_size(self) -> int: ...


class IContractQuery(Protocol):
    contract: IAddress
    function: str
    value: int
    caller: Union[IAddress, None]
    encoded_arguments: List[str]
