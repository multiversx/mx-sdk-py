
from typing import Any, Optional

from multiversx_sdk.controllers.interfaces import IAbi
from multiversx_sdk.core.address import EmptyAddress
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
                 gas_limit: Optional[int] = None,
                 function: Optional[str] = None,
                 arguments: Optional[list[Any]] = None,
                 abi: Optional[IAbi] = None) -> None:
        arguments = arguments or []

        self.to = to
        self.egld_amount = native_transfer_amount
        self.opt_gas_limit = gas_limit

        if function:
            if abi:
                self.function_call = abi.encode_endpoint_input_parameters(function, arguments)
            else:
                self.function_call = [function, *arguments]
        else:
            self.function_call = []


class ProposeTransferExecuteEsdtInput:
    def __init__(self,
                 to: IAddress,
                 token_transfers: list[TokenTransfer],
                 gas_limit: Optional[int] = None,
                 function: Optional[str] = None,
                 arguments: Optional[list[Any]] = None,
                 abi: Optional[IAbi] = None) -> None:
        arguments = arguments or []

        self.to = to
        self.tokens = [EsdtTokenPayment(token.token.identifier, token.token.nonce, token.amount) for token in token_transfers]
        self.opt_gas_limit = gas_limit

        if function:
            if abi:
                self.function_call = abi.encode_endpoint_input_parameters(function, arguments)
            else:
                self.function_call = [function, *arguments]
        else:
            self.function_call = []


class ProposeAsyncCallInput:
    def __init__(self,
                 to: IAddress,
                 native_transfer_amount: int,
                 token_transfers: list[TokenTransfer],
                 gas_limit: Optional[int] = None,
                 function: Optional[str] = None,
                 arguments: Optional[list[Any]] = None,
                 abi: Optional[IAbi] = None) -> None:
        arguments = arguments or []

        self.to = to
        self.egld_amount = native_transfer_amount
        self.opt_gas_limit = gas_limit

        if function:
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

            self.function_call = transaction.data.split(ARGS_SEPARATOR.encode())
        else:
            # Since multisig requires the transfer to be encoded as variadic<bytes> in "function_call",
            # we leverage the transactions factory to achieve this (followed by splitting the data).
            transactions_factory = TransferTransactionsFactory(TransactionsFactoryConfig(""))
            transaction = transactions_factory.create_transaction_for_transfer(
                sender=EmptyAddress(),
                receiver=EmptyAddress(),
                # Multisig wasn't designed to work with EGLD within MultiESDTNFT.
                native_amount=0,
                token_transfers=token_transfers)

            self.function_call = transaction.data.split(ARGS_SEPARATOR.encode())


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

        if abi:
            self.arguments = abi.encode_constructor_input_parameters(arguments)
        else:
            self.arguments = arguments


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

        if abi:
            self.arguments = abi.encode_upgrade_constructor_input_parameters(arguments)
        else:
            self.arguments = arguments
