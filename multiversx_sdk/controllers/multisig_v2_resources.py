
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Union

from multiversx_sdk.controllers.interfaces import IAbi
from multiversx_sdk.core.address import Address, EmptyAddress
from multiversx_sdk.core.code_metadata import CodeMetadata
from multiversx_sdk.core.constants import ARGS_SEPARATOR
from multiversx_sdk.core.interfaces import IAddress
from multiversx_sdk.core.tokens import TokenTransfer
from multiversx_sdk.core.transactions_factories import (
    SmartContractTransactionsFactory, TransactionsFactoryConfig)
from multiversx_sdk.core.transactions_factories.transfer_transactions_factory import \
    TransferTransactionsFactory


class ProposeTransferExecuteInput:
    def __init__(self,
                 to: IAddress,
                 native_transfer_amount: int,
                 function_call: list[bytes],
                 opt_gas_limit: Optional[int] = None,) -> None:

        self.to = to
        self.egld_amount = native_transfer_amount
        self.function_call = function_call
        self.opt_gas_limit = opt_gas_limit

    @classmethod
    def new_for_native_transfer(cls,
                                to: IAddress,
                                native_transfer_amount: int,
                                gas_limit: Optional[int] = None):
        return cls(to, native_transfer_amount, [], gas_limit)

    @classmethod
    def new_for_transfer_execute(cls,
                                 to: IAddress,
                                 native_transfer_amount: int,
                                 function: str,
                                 arguments: list[Any],
                                 gas_limit: Optional[int] = None,
                                 abi: Optional[IAbi] = None):
        arguments = abi.encode_endpoint_input_parameters(function, arguments) if abi else arguments
        function_call = [function, *arguments]
        return cls(to, native_transfer_amount, function_call, gas_limit)


class ProposeTransferExecuteEsdtInput:
    def __init__(self,
                 to: IAddress,
                 tokens: list['EsdtTokenPayment'],
                 function_call: list[bytes],
                 opt_gas_limit: Optional[int] = None) -> None:
        self.to = to
        self.tokens = tokens
        self.function_call = function_call
        self.opt_gas_limit = opt_gas_limit

    @classmethod
    def new_for_transfer(cls,
                         to: IAddress,
                         token_transfers: list[TokenTransfer],
                         gas_limit: Optional[int] = None):
        tokens = [EsdtTokenPayment(token.token.identifier, token.token.nonce, token.amount) for token in token_transfers]
        return cls(to, tokens, [], gas_limit)

    @classmethod
    def new_for_transfer_execute(cls,
                                 to: IAddress,
                                 token_transfers: list[TokenTransfer],
                                 function: str,
                                 arguments: list[Any],
                                 gas_limit: Optional[int] = None,
                                 abi: Optional[IAbi] = None):
        # Since multisig requires the execution (but not the transfers) to be encoded as variadic<bytes> in "function_call",
        # we leverage the transactions factory to achieve this (followed by splitting the data).
        transactions_factory = SmartContractTransactionsFactory(TransactionsFactoryConfig(""), abi=abi)
        transaction = transactions_factory.create_transaction_for_execute(
            sender=EmptyAddress(),
            contract=EmptyAddress(),
            function=function,
            gas_limit=0,
            arguments=arguments)

        tokens = [EsdtTokenPayment(token.token.identifier, token.token.nonce, token.amount) for token in token_transfers]
        function_call_parts = transaction.data.split(ARGS_SEPARATOR.encode())
        function_name = function_call_parts[0]
        function_arguments = [bytes.fromhex(item.decode()) for item in function_call_parts[1:]]
        function_call = [function_name, *function_arguments]
        return cls(to, tokens, function_call, gas_limit)


class ProposeAsyncCallInput:
    def __init__(self,
                 to: IAddress,
                 egld_amount: int,
                 function_call: list[bytes],
                 opt_gas_limit: Optional[int] = None) -> None:
        self.to = to
        self.egld_amount = egld_amount
        self.function_call = function_call
        self.opt_gas_limit = opt_gas_limit

    @classmethod
    def new_for_transfer(cls,
                         to: IAddress,
                         token_transfers: list[TokenTransfer],
                         gas_limit: Optional[int] = None):
        # Since multisig requires the transfer to be encoded as variadic<bytes> in "function_call",
        # we leverage the transactions factory to achieve this (followed by splitting the data).
        transactions_factory = TransferTransactionsFactory(TransactionsFactoryConfig(""))
        transaction = transactions_factory.create_transaction_for_transfer(
            sender=EmptyAddress(),
            receiver=EmptyAddress(),
            # Multisig wasn't designed to work with EGLD within MultiESDTNFT.
            native_amount=0,
            token_transfers=token_transfers)

        function_call_parts = transaction.data.split(ARGS_SEPARATOR.encode())
        function_name = function_call_parts[0]
        function_arguments = [bytes.fromhex(item.decode()) for item in function_call_parts[1:]]
        function_call = [function_name, *function_arguments]
        return cls(to, 0, function_call, gas_limit)

    @classmethod
    def new_for_transfer_execute(cls,
                                 to: IAddress,
                                 native_transfer_amount: int,
                                 token_transfers: list[TokenTransfer],
                                 function: str,
                                 arguments: list[Any],
                                 gas_limit: Optional[int] = None,
                                 abi: Optional[IAbi] = None):
        # Since multisig requires the transfer & execute to be encoded as variadic<bytes> in "function_call",
        # we leverage the transactions factory to achieve this (followed by splitting the data).
        transactions_factory = SmartContractTransactionsFactory(TransactionsFactoryConfig(""), abi=abi)
        transaction = transactions_factory.create_transaction_for_execute(
            sender=EmptyAddress(),
            contract=EmptyAddress(),
            function=function,
            gas_limit=0,
            arguments=arguments,
            # Multisig wasn't designed to work with EGLD within MultiESDTNFT.
            native_transfer_amount=0,
            token_transfers=token_transfers)

        function_call_parts = transaction.data.split(ARGS_SEPARATOR.encode())
        function_name = function_call_parts[0]
        function_arguments = [bytes.fromhex(item.decode()) for item in function_call_parts[1:]]
        function_call = [function_name, *function_arguments]
        return cls(to, native_transfer_amount, function_call, gas_limit)


class EsdtTokenPayment:
    def __init__(self, token_identifier: str, token_nonce: int, amount: int) -> None:
        self.token_identifier = token_identifier
        self.token_nonce = token_nonce
        self.amount = amount


class ProposeSCDeployFromSourceInput:
    def __init__(self,
                 native_transfer_amount: int,
                 contract_to_copy: IAddress,
                 code_metadata: CodeMetadata,
                 arguments: list[Any],
                 abi: Optional[IAbi] = None) -> None:
        self.amount = native_transfer_amount
        self.source = contract_to_copy
        self.code_metadata = code_metadata.serialize()
        self.arguments = abi.encode_constructor_input_parameters(arguments) if abi else arguments


class ProposeSCUpgradeFromSourceInput:
    def __init__(self,
                 contract_to_upgrade: IAddress,
                 native_transfer_amount: int,
                 contract_to_copy: IAddress,
                 code_metadata: CodeMetadata,
                 arguments: list[Any],
                 abi: Optional[IAbi] = None) -> None:
        self.sc_address = contract_to_upgrade
        self.amount = native_transfer_amount
        self.source = contract_to_copy
        self.code_metadata = code_metadata.serialize()
        self.arguments = abi.encode_constructor_input_parameters(arguments) if abi else arguments


class UserRole(Enum):
    NONE = 0
    PROPOSER = 1
    BOARD_MEMBER = 2
