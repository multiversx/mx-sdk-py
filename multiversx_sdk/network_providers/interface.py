from typing import Any, Dict, Optional, Protocol, Sequence


class ISerializable(Protocol):
    def to_dictionary(self) -> Dict[str, Any]:
        ...


class IAddress(Protocol):
    def to_bech32(self) -> str:
        ...

    def to_hex(self) -> str:
        ...


class IPagination(Protocol):
    def get_start(self) -> int:
        ...

    def get_size(self) -> int:
        ...


class IContractQuery(Protocol):
    def get_contract(self) -> IAddress:
        ...

    def get_function(self) -> str:
        ...

    def get_encoded_arguments(self) -> Sequence[str]:
        ...

    def get_caller(self) -> Optional[IAddress]:
        ...

    def get_value(self) -> int:
        ...
