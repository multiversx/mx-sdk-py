
from typing import Any, List

from erdpy_core.args_serializer import args_to_string
from erdpy_core.constants import ARGUMENTS_SEPARATOR
from erdpy_core.transaction_payload import TransactionPayload


class FunctionCallBuilder:
    """
    A builder for TransactionPayload objects, to be used for Smart Contract calls or built-in function calls.
    """

    def __init__(self) -> None:
        self.function_name = ""
        self.arguments: List[Any] = []

    def set_function(self, function_name: str) -> 'FunctionCallBuilder':
        self.function_name = function_name
        return self

    def add_argument(self, arg: Any) -> 'FunctionCallBuilder':
        self.arguments.append(arg)
        return self

    def set_arguments(self, args: List[Any]) -> 'FunctionCallBuilder':
        self.arguments = args
        return self

    def build(self) -> TransactionPayload:
        data = self.function_name

        if self.arguments:
            data = f"{data}{ARGUMENTS_SEPARATOR}{args_to_string(self.arguments)}"

        return TransactionPayload.from_str(data)
