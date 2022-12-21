

from typing import Any, Optional, Sequence

from erdpy_core.contract_query import ContractQuery
from erdpy_core.interfaces import IAddress
from erdpy_core.serializer import args_to_strings


class ContractQueryBuilder():
    def __init__(self,
                 contract: IAddress,
                 function: str,
                 call_arguments: Sequence[Any] = [],
                 caller: Optional[IAddress] = None,
                 value: Optional[int] = None,
                 ) -> None:
        self.contract = contract
        self.function_name = function
        self.call_arguments = call_arguments
        self.caller = caller
        self.value = value

    def build(self) -> ContractQuery:
        query = ContractQuery(
            contract=self.contract,
            function=self.function_name,
            encoded_arguments=args_to_strings(self.call_arguments),
            caller=self.caller,
            value=self.value
        )

        return query
