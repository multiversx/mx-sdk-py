
from typing import Any, List

from erdpy_core.constants import ARGUMENTS_SEPARATOR, VM_TYPE_WASM_VM
from erdpy_core.interfaces import ICodeMetadata
from erdpy_core.serializer import args_to_string
from erdpy_core.transaction_payload import TransactionPayload


class FunctionCallBuilder:
    """
    A builder for TransactionPayload objects, to be used for Smart Contract calls or built-in function calls.
    """

    def __init__(self, function_name: str, arguments: List[Any] = []) -> None:
        self.function_name = function_name
        self.arguments: List[Any] = arguments

    def build(self) -> TransactionPayload:
        data = self.function_name

        if self.arguments:
            data = f"{data}{ARGUMENTS_SEPARATOR}{args_to_string(self.arguments)}"

        return TransactionPayload.from_str(data)


class ContractDeployBuilder:
    """
    A builder for TransactionPayload objects, to be used for Smart Contract deployments.
    """

    def __init__(self, code: bytes, code_metadata: ICodeMetadata, arguments: List[Any] = []) -> None:
        self.code: bytes = code
        self.code_metadata: bytes = code_metadata.serialize()
        self.arguments: List[Any] = arguments

    def build(self) -> TransactionPayload:
        data = f"{self.code.hex()}{ARGUMENTS_SEPARATOR}{VM_TYPE_WASM_VM}{ARGUMENTS_SEPARATOR}{self.code_metadata.hex()}"

        if self.arguments:
            data = f"{data}{ARGUMENTS_SEPARATOR}{args_to_string(self.arguments)}"

        return TransactionPayload.from_str(data)


class ContractUpgradeBuilder:
    """
    A builder for TransactionPayload objects, to be used for Smart Contract upgrades.
    """

    def __init__(self, code: bytes, code_metadata: ICodeMetadata, arguments: List[Any] = []) -> None:
        self.code: bytes = code
        self.code_metadata: bytes = code_metadata.serialize()
        self.arguments: List[Any] = arguments

    def build(self) -> TransactionPayload:
        data = f"upgradeContract{ARGUMENTS_SEPARATOR}{self.code.hex()}{ARGUMENTS_SEPARATOR}{self.code_metadata.hex()}"

        if self.arguments:
            data = f"{data}{ARGUMENTS_SEPARATOR}{args_to_string(self.arguments)}"

        return TransactionPayload.from_str(data)
