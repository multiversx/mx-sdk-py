
from typing import Any, List

from erdpy_core.constants import ARGS_SEPARATOR, VM_TYPE_WASM_VM
from erdpy_core.interfaces import IAddress, ICodeMetadata, ITokenPayment
from erdpy_core.serializer import arg_to_string, args_to_string
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
            data = f"{data}{ARGS_SEPARATOR}{args_to_string(self.arguments)}"

        return TransactionPayload.from_str(data)


class ContractDeploymentBuilder:
    """
    A builder for TransactionPayload objects, to be used for Smart Contract deployments.
    """

    def __init__(self, code: bytes, code_metadata: ICodeMetadata, arguments: List[Any] = []) -> None:
        self.code: bytes = code
        self.code_metadata: bytes = code_metadata.serialize()
        self.arguments: List[Any] = arguments

    def build(self) -> TransactionPayload:
        data = f"{self.code.hex()}{ARGS_SEPARATOR}{VM_TYPE_WASM_VM.hex()}{ARGS_SEPARATOR}{self.code_metadata.hex()}"

        if self.arguments:
            data = f"{data}{ARGS_SEPARATOR}{args_to_string(self.arguments)}"

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
        data = f"upgradeContract{ARGS_SEPARATOR}{self.code.hex()}{ARGS_SEPARATOR}{self.code_metadata.hex()}"

        if self.arguments:
            data = f"{data}{ARGS_SEPARATOR}{args_to_string(self.arguments)}"

        return TransactionPayload.from_str(data)


class ESDTTransferBuilder:
    """
    A builder for TransactionPayload objects, to be used for token transfers.
    """

    def __init__(self, payment: ITokenPayment) -> None:
        self.payment: ITokenPayment = payment

    def build(self) -> TransactionPayload:
        data = ARGS_SEPARATOR.join([
            "ESDTTransfer",
            arg_to_string(self.payment.token_identifier),
            arg_to_string(self.payment.amount_as_integer)
        ])

        return TransactionPayload.from_str(data)


class ESDTNFTTransferBuilder:
    """
    A builder for TransactionPayload objects, to be used for token transfers.
    """

    def __init__(self, payment: ITokenPayment, destination: IAddress) -> None:
        self.payment: ITokenPayment = payment
        self.destination: IAddress = destination

    def build(self) -> TransactionPayload:
        data = ARGS_SEPARATOR.join([
            "ESDTNFTTransfer",
            arg_to_string(self.payment.token_identifier),
            arg_to_string(self.payment.token_nonce),
            arg_to_string(self.payment.amount_as_integer),
            arg_to_string(self.destination)
        ])

        return TransactionPayload.from_str(data)


class MultiESDTNFTTransferBuilder:
    """
    A builder for TransactionPayload objects, to be used for token transfers.
    """

    def __init__(self, payments: List[ITokenPayment], destination: IAddress) -> None:
        self.payments: List[ITokenPayment] = payments
        self.destination: IAddress = destination

    def build(self) -> TransactionPayload:
        data_parts = [
            "MultiESDTNFTTransfer",
            arg_to_string(self.destination),
            arg_to_string(len(self.payments))
        ]

        for payment in self.payments:
            data_parts.extend([
                arg_to_string(payment.token_identifier),
                arg_to_string(payment.token_nonce),
                arg_to_string(payment.amount_as_integer)
            ])

        data = ARGS_SEPARATOR.join(data_parts)
        return TransactionPayload.from_str(data)
