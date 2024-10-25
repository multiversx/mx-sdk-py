
from enum import Enum
from typing import Any, Optional

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
from multiversx_sdk.network_providers.constants import DEFAULT_ADDRESS_HRP


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
        self.arguments = abi.encode_upgrade_constructor_input_parameters(arguments) if abi else arguments


class UserRole(Enum):
    NONE = 0
    PROPOSER = 1
    BOARD_MEMBER = 2


class ActionFullInfo:
    def __init__(self,
                 action_id: int,
                 group_id: int,
                 action_data: 'Action',
                 signers: list[Address]) -> None:
        self.action_id = action_id
        self.group_id = group_id
        self.action_data = action_data
        self.signers = signers

    @classmethod
    def new_from_object(cls, object: Any) -> 'ActionFullInfo':
        signers = [Address(value, DEFAULT_ADDRESS_HRP) for value in object.signers]
        action_data = create_action_from_object(object.action_data)
        return cls(object.action_id, object.group_id, action_data, signers)

    def __repr__(self) -> str:
        return f"ActionFullInfo(action_id={self.action_id}, group_id={self.group_id}, action_data={self.action_data}, signers={self.signers})"


def create_action_from_object(object: Any) -> 'Action':
    discriminant = int(object)

    if discriminant == AddBoardMember.discriminant:
        return AddBoardMember.new_from_object(object)
    elif discriminant == AddProposer.discriminant:
        return AddProposer.new_from_object(object)
    elif discriminant == RemoveUser.discriminant:
        return RemoveUser.new_from_object(object)
    elif discriminant == ChangeQuorum.discriminant:
        return ChangeQuorum.new_from_object(object)
    elif discriminant == SendTransferExecuteEgld.discriminant:
        return SendTransferExecuteEgld.new_from_object(object)
    elif discriminant == SendTransferExecuteEsdt.discriminant:
        return SendTransferExecuteEsdt.new_from_object(object)
    elif discriminant == SendAsyncCall.discriminant:
        return SendAsyncCall.new_from_object(object)
    elif discriminant == SCDeployFromSource.discriminant:
        return SCDeployFromSource.new_from_object(object)
    elif discriminant == SCUpgradeFromSource.discriminant:
        return SCUpgradeFromSource.new_from_object(object)
    else:
        raise ValueError(f"Unknown action discriminant: {discriminant}")


class Action:
    discriminant: int

    def __init__(self) -> None:
        pass

    def __repr__(self) -> str:
        return self.__class__.__name__


class AddBoardMember(Action):
    discriminant = 1

    def __init__(self, address: IAddress) -> None:
        self.address = address

    @classmethod
    def new_from_object(cls, object: Any) -> 'AddBoardMember':
        field_0 = getattr(object, "0")
        public_key = field_0
        address = Address(public_key, DEFAULT_ADDRESS_HRP)
        return cls(address)


class AddProposer(Action):
    discriminant = 2

    def __init__(self, address: IAddress) -> None:
        self.address = address

    @classmethod
    def new_from_object(cls, object: Any) -> 'AddProposer':
        field_0 = getattr(object, "0")
        public_key = field_0
        address = Address(public_key, DEFAULT_ADDRESS_HRP)
        return cls(address)


class RemoveUser(Action):
    discriminant = 3

    def __init__(self, address: IAddress) -> None:
        self.address = address

    @classmethod
    def new_from_object(cls, object: Any) -> 'RemoveUser':
        field_0 = getattr(object, "0")
        public_key = field_0
        address = Address(public_key, DEFAULT_ADDRESS_HRP)
        return cls(address)


class ChangeQuorum(Action):
    discriminant = 4

    def __init__(self, quorum: int) -> None:
        self.quorum = quorum

    @classmethod
    def new_from_object(cls, object: Any) -> 'ChangeQuorum':
        field_0 = getattr(object, "0")
        quorum = field_0
        return cls(quorum)


class SendTransferExecuteEgld(Action):
    discriminant = 5

    def __init__(self, data: 'CallActionData') -> None:
        self.data = data

    @classmethod
    def new_from_object(cls, object: Any) -> 'SendTransferExecuteEgld':
        field_0 = getattr(object, "0")
        data = CallActionData.new_from_object(field_0)
        return cls(data)


class CallActionData:
    def __init__(self,
                 to: Address,
                 egld_amount: int,
                 endpoint_name: str,
                 arguments: list[bytes],
                 opt_gas_limit: Optional[int] = None):
        self.to = to
        self.egld_amount = egld_amount
        self.endpoint_name = endpoint_name
        self.arguments = arguments
        self.opt_gas_limit = opt_gas_limit

    @classmethod
    def new_from_object(cls, object: Any) -> 'CallActionData':
        to = Address(object.to, DEFAULT_ADDRESS_HRP)
        egld_amount = object.egld_amount
        endpoint_name = object.endpoint_name
        arguments = object.arguments
        opt_gas_limit = object.opt_gas_limit
        return cls(to, egld_amount, endpoint_name, arguments, opt_gas_limit)


class SendTransferExecuteEsdt(Action):
    discriminant = 6

    def __init__(self, data: 'EsdtTransferExecuteData') -> None:
        self.data = data

    @classmethod
    def new_from_object(cls, object: Any) -> 'SendTransferExecuteEsdt':
        field_0 = getattr(object, "0")
        data = EsdtTransferExecuteData.new_from_object(field_0)
        return cls(data)


class EsdtTransferExecuteData:
    def __init__(self,
                 to: Address,
                 tokens: list[EsdtTokenPayment],
                 opt_gas_limit: Optional[int],
                 endpoint_name: bytes,
                 arguments: list[bytes]) -> None:
        self.to = to
        self.tokens = tokens
        self.opt_gas_limit = opt_gas_limit
        self.endpoint_name = endpoint_name
        self.arguments = arguments

    @classmethod
    def new_from_object(cls, object: Any) -> 'EsdtTransferExecuteData':
        to = Address(object.to, DEFAULT_ADDRESS_HRP)
        tokens = [EsdtTokenPayment(token.token_identifier, token.token_nonce, token.amount) for token in object.tokens]
        opt_gas_limit = object.opt_gas_limit
        endpoint_name = object.endpoint_name
        arguments = object.arguments
        return cls(to, tokens, opt_gas_limit, endpoint_name, arguments)


class SendAsyncCall(Action):
    discriminant = 7

    def __init__(self, data: 'CallActionData') -> None:
        self.data = data

    @classmethod
    def new_from_object(cls, object: Any) -> 'SendAsyncCall':
        field_0 = getattr(object, "0")
        data = CallActionData.new_from_object(field_0)
        return cls(data)


class SCDeployFromSource(Action):
    discriminant = 8

    def __init__(self, amount: int, source: Address, code_metadata: bytes, arguments: list[bytes]) -> None:
        self.amount = amount
        self.source = source
        self.code_metadata = code_metadata
        self.arguments = arguments

    @classmethod
    def new_from_object(cls, object: Any) -> 'SCDeployFromSource':
        amount = object.amount
        source = Address(object.source, DEFAULT_ADDRESS_HRP)
        code_metadata = object.code_metadata
        arguments = object.arguments
        return cls(amount, source, code_metadata, arguments)


class SCUpgradeFromSource(Action):
    discriminant = 9

    def __init__(self, sc_address: Address, amount: int, source: Address, code_metadata: bytes, arguments: list[bytes]) -> None:
        self.sc_address = sc_address
        self.amount = amount
        self.source = source
        self.code_metadata = code_metadata
        self.arguments = arguments

    @classmethod
    def new_from_object(cls, object: Any) -> 'SCUpgradeFromSource':
        sc_address = Address(object.sc_address, DEFAULT_ADDRESS_HRP)
        amount = object.amount
        source = Address(object.source, DEFAULT_ADDRESS_HRP)
        code_metadata = object.code_metadata
        arguments = object.arguments
        return cls(sc_address, amount, source, code_metadata, arguments)
