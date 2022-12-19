from typing import Any, Dict


class GenericResponse:
    def __init__(self, data: Any) -> None:
        self.__dict__.update(data)

    def get(self, key: str, default: Any = None) -> Any:
        return self.__dict__.get(key, default)

    def to_dictionary(self) -> Dict[str, Any]:
        return self.__dict__


class EmptyAddress:
    def bech32(self) -> str:
        return ""
