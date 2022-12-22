

from typing import List, Optional, Sequence

from erdpy_core.interfaces import IAddress


class ContractQuery:
    def __init__(self,
                 contract: IAddress,
                 function: str,
                 encoded_arguments: List[str] = [],
                 value: Optional[int] = None,
                 caller: Optional[IAddress] = None) -> None:
        self.contract: IAddress = contract
        self.function: str = function
        self.encoded_arguments = encoded_arguments
        self.value: int = value or 0
        self.caller: Optional[IAddress] = caller

    def get_contract(self) -> IAddress:
        return self.contract

    def get_function(self) -> str:
        return self.function

    def get_encoded_arguments(self) -> Sequence[str]:
        return self.encoded_arguments

    def get_caller(self) -> Optional[IAddress]:
        return self.caller

    def get_value(self) -> int:
        return self.value
