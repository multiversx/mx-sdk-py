from typing import Any, Dict, Optional, Protocol, Sequence


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
    encoded_arguments: Sequence[str]
    caller: Optional[IAddress]
    value: int
