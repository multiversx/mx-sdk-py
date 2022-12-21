

from typing import List, Optional

from erdpy_core.interfaces import IAddress, ITransactionValue


class ContractQuery:
    def __init__(self,
                 contract: IAddress,
                 function: str,
                 encoded_arguments: List[str] = [],
                 value: Optional[ITransactionValue] = None,
                 caller: Optional[IAddress] = None) -> None:
        self.contract = contract
        self.function = function
        self.encoded_arguments = encoded_arguments
        self.value = value
        self.caller = caller
