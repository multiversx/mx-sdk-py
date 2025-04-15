from typing import Any, Optional, Union

from multiversx_sdk.abi.abi import Abi
from multiversx_sdk.abi.biguint_value import BigUIntValue
from multiversx_sdk.abi.fields import Field
from multiversx_sdk.abi.interface import ISingleValue
from multiversx_sdk.abi.multi_value import MultiValue
from multiversx_sdk.abi.small_int_values import U64Value
from multiversx_sdk.abi.string_value import StringValue
from multiversx_sdk.abi.struct_value import StructValue
from multiversx_sdk.core.address import Address
from multiversx_sdk.core.code_metadata import CodeMetadata
from multiversx_sdk.core.constants import ARGS_SEPARATOR
from multiversx_sdk.core.tokens import TokenTransfer
from multiversx_sdk.core.transactions_factory_config import TransactionsFactoryConfig
from multiversx_sdk.smart_contracts.smart_contract_transactions_factory import (
    SmartContractTransactionsFactory,
)
from multiversx_sdk.transfers.transfer_transactions_factory import (
    TransferTransactionsFactory,
)


class ProposeTransferExecuteInput:
    def __init__(
        self,
        to: Address,
        native_transfer_amount: int,
        function_call: Union[list[bytes], list[Union[ISingleValue, MultiValue]]],
        opt_gas_limit: Optional[int] = None,
    ) -> None:
        self.to = to
        self.egld_amount = native_transfer_amount
        self.function_call = function_call
        self.opt_gas_limit = opt_gas_limit

    @classmethod
    def new_for_native_transfer(cls, to: Address, native_transfer_amount: int, gas_limit: Optional[int] = None):
        return cls(to, native_transfer_amount, [], gas_limit)

    @classmethod
    def new_for_transfer_execute(
        cls,
        to: Address,
        native_transfer_amount: int,
        function: str,
        arguments: list[Any],
        gas_limit: Optional[int] = None,
        abi: Optional[Abi] = None,
    ):
        arguments = abi.encode_endpoint_input_parameters(function, arguments) if abi else arguments
        function_call: list[Any] = [StringValue(function), *arguments]
        return cls(to, native_transfer_amount, function_call, gas_limit)


class ProposeTransferExecuteEsdtInput:
    def __init__(
        self,
        to: Address,
        tokens: list["EsdtTokenPayment"],
        function_call: list[bytes],
        opt_gas_limit: Optional[int] = None,
    ) -> None:
        self.to = to
        self.tokens = tokens
        self.function_call = function_call
        self.opt_gas_limit = opt_gas_limit

    @classmethod
    def new_for_transfer(
        cls,
        to: Address,
        token_transfers: list[TokenTransfer],
        gas_limit: Optional[int] = None,
    ):
        tokens = [
            EsdtTokenPayment(token.token.identifier, token.token.nonce, token.amount) for token in token_transfers
        ]
        return cls(to, tokens, [], gas_limit)

    @classmethod
    def new_for_transfer_execute(
        cls,
        to: Address,
        token_transfers: list[TokenTransfer],
        function: str,
        arguments: list[Any],
        gas_limit: Optional[int] = None,
        abi: Optional[Abi] = None,
    ):
        # Since multisig requires the execution (but not the transfers) to be encoded as variadic<bytes> in "function_call",
        # we leverage the transactions factory to achieve this (followed by splitting the data).
        transactions_factory = SmartContractTransactionsFactory(TransactionsFactoryConfig(""), abi=abi)
        transaction = transactions_factory.create_transaction_for_execute(
            sender=Address.empty(),
            contract=Address.empty(),
            function=function,
            gas_limit=0,
            arguments=arguments,
        )

        tokens = [
            EsdtTokenPayment(token.token.identifier, token.token.nonce, token.amount) for token in token_transfers
        ]
        function_call_parts = transaction.data.split(ARGS_SEPARATOR.encode())
        function_name = function_call_parts[0]
        function_arguments = [bytes.fromhex(item.decode()) for item in function_call_parts[1:]]
        function_call = [function_name, *function_arguments]
        return cls(to, tokens, function_call, gas_limit)


class ProposeAsyncCallInput:
    def __init__(
        self,
        to: Address,
        function_call: list[bytes],
        opt_gas_limit: Optional[int] = None,
    ) -> None:
        self.to = to
        self.function_call = function_call
        self.opt_gas_limit = opt_gas_limit

    @classmethod
    def new_for_transfer(
        cls,
        to: Address,
        token_transfers: list[TokenTransfer],
        gas_limit: Optional[int] = None,
    ):
        # Since multisig requires the transfer to be encoded as variadic<bytes> in "function_call",
        # we leverage the transactions factory to achieve this (followed by splitting the data).
        transactions_factory = TransferTransactionsFactory(TransactionsFactoryConfig(""))
        transaction = transactions_factory.create_transaction_for_transfer(
            sender=Address.empty(),
            receiver=Address.empty(),
            # Multisig wasn't designed to work with EGLD within MultiESDTNFT.
            native_amount=0,
            token_transfers=token_transfers,
        )

        function_call_parts = transaction.data.split(ARGS_SEPARATOR.encode())
        function_name = function_call_parts[0]
        function_arguments = [bytes.fromhex(item.decode()) for item in function_call_parts[1:]]
        function_call = [function_name, *function_arguments]
        return cls(to, function_call, gas_limit)

    @classmethod
    def new_for_transfer_execute(
        cls,
        to: Address,
        token_transfers: list[TokenTransfer],
        function: str,
        arguments: list[Any],
        gas_limit: Optional[int] = None,
        abi: Optional[Abi] = None,
    ):
        # Since multisig requires the transfer & execute to be encoded as variadic<bytes> in "function_call",
        # we leverage the transactions factory to achieve this (followed by splitting the data).
        transactions_factory = SmartContractTransactionsFactory(TransactionsFactoryConfig(""), abi=abi)
        transaction = transactions_factory.create_transaction_for_execute(
            sender=Address.empty(),
            contract=Address.empty(),
            function=function,
            gas_limit=0,
            arguments=arguments,
            native_transfer_amount=0,
            token_transfers=token_transfers,
        )

        function_call_parts = transaction.data.split(ARGS_SEPARATOR.encode())
        function_name = function_call_parts[0]
        function_arguments = [bytes.fromhex(item.decode()) for item in function_call_parts[1:]]
        function_call = [function_name, *function_arguments]
        return cls(to, function_call, gas_limit)


class ProposeSyncCallInput(ProposeAsyncCallInput):
    pass


class EsdtTokenPayment(StructValue):
    def __init__(self, token_identifier: str, token_nonce: int, amount: int) -> None:
        super().__init__(
            [
                Field("token_identifier", StringValue(token_identifier)),
                Field("token_nonce", U64Value(token_nonce)),
                Field("amount", BigUIntValue(amount)),
            ],
        )


class ProposeSCDeployFromSourceInput:
    def __init__(
        self,
        native_transfer_amount: int,
        contract_to_copy: Address,
        code_metadata: CodeMetadata,
        arguments: list[Any],
        abi: Optional[Abi] = None,
    ) -> None:
        self.amount = native_transfer_amount
        self.source = contract_to_copy
        self.code_metadata = code_metadata.serialize()
        self.arguments = abi.encode_constructor_input_parameters(arguments) if abi else arguments


class ProposeSCUpgradeFromSourceInput:
    def __init__(
        self,
        contract_to_upgrade: Address,
        native_transfer_amount: int,
        contract_to_copy: Address,
        code_metadata: CodeMetadata,
        arguments: list[Any],
        abi: Optional[Abi] = None,
    ) -> None:
        self.sc_address = contract_to_upgrade
        self.amount = native_transfer_amount
        self.source = contract_to_copy
        self.code_metadata = code_metadata.serialize()
        self.arguments = abi.encode_upgrade_constructor_input_parameters(arguments) if abi else arguments


class Action:
    discriminant: int

    def __init__(self) -> None:
        pass

    def __repr__(self) -> str:
        return self.__class__.__name__
