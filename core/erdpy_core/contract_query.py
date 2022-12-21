

from typing import List, Optional

from erdpy_core.interfaces import IAddress, ITransactionValue


class ContractQuery:
    def __init__(self,
                 contract: IAddress,
                 function: str,
                 encoded_arguments: List[str] = [],
                 value: Optional[ITransactionValue] = None,
                 caller: Optional[IAddress] = None) -> None:
        self.contract: IAddress = contract
        self.function: str = function
        self.encoded_arguments = encoded_arguments
        self.value: int = 0
        self.caller: Optional[IAddress] = caller
