from pathlib import Path
from typing import Any, Optional, Union

from multiversx_sdk.abi.abi import Abi
from multiversx_sdk.abi.address_value import AddressValue
from multiversx_sdk.abi.biguint_value import BigUIntValue
from multiversx_sdk.abi.bytes_value import BytesValue
from multiversx_sdk.abi.code_metadata_value import CodeMetadataValue
from multiversx_sdk.abi.list_value import ListValue
from multiversx_sdk.abi.option_value import OptionValue
from multiversx_sdk.abi.serializer import Serializer
from multiversx_sdk.abi.small_int_values import U32Value, U64Value
from multiversx_sdk.abi.string_value import StringValue
from multiversx_sdk.abi.typesystem import is_list_of_typed_values
from multiversx_sdk.abi.variadic_values import VariadicValues
from multiversx_sdk.core.address import Address
from multiversx_sdk.core.code_metadata import CodeMetadata
from multiversx_sdk.core.constants import ARGS_SEPARATOR
from multiversx_sdk.core.tokens import TokenTransfer
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transactions_factory_config import TransactionsFactoryConfig
from multiversx_sdk.multisig.resources import (
    Action,
    EsdtTokenPayment,
    ProposeAsyncCallInput,
    ProposeTransferExecuteEsdtInput,
)
from multiversx_sdk.smart_contracts.errors import ArgumentSerializationError
from multiversx_sdk.smart_contracts.smart_contract_transactions_factory import (
    SmartContractTransactionsFactory,
)
from multiversx_sdk.transfers.transfer_transactions_factory import (
    TransferTransactionsFactory,
)


class MultisigTransactionsFactory:
    def __init__(self, config: TransactionsFactoryConfig, abi: Abi) -> None:
        self._sc_factory = SmartContractTransactionsFactory(config, abi)
        self._serializer = Serializer()

    def create_transaction_for_deploy(
        self,
        sender: Address,
        bytecode: Union[Path, bytes],
        quorum: int,
        board: list[Address],
        gas_limit: int,
        is_upgradeable: bool = True,
        is_readable: bool = True,
        is_payable: bool = False,
        is_payable_by_sc: bool = True,
    ) -> Transaction:
        board_members = [AddressValue.new_from_address(address) for address in board]
        args = [U32Value(quorum), VariadicValues(items=board_members)]

        return self._sc_factory.create_transaction_for_deploy(
            sender=sender,
            bytecode=bytecode,
            arguments=args,
            gas_limit=gas_limit,
            is_upgradeable=is_upgradeable,
            is_readable=is_readable,
            is_payable=is_payable,
            is_payable_by_sc=is_payable_by_sc,
        )

    def create_transaction_for_deposit(
        self,
        sender: Address,
        contract: Address,
        gas_limit: int,
        native_token_amount: Optional[int] = None,
        token_transfers: Optional[list[TokenTransfer]] = None,
    ) -> Transaction:
        if not native_token_amount and not token_transfers:
            raise Exception("No native token amount or token transfers provided")

        return self._sc_factory.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function="deposit",
            gas_limit=gas_limit,
            arguments=[],
            native_transfer_amount=native_token_amount if native_token_amount else 0,
            token_transfers=token_transfers if token_transfers else [],
        )

    def create_transaction_for_discard_action(
        self,
        sender: Address,
        contract: Address,
        action_id: int,
        gas_limit: int,
    ) -> Transaction:
        return self._sc_factory.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function="discardAction",
            gas_limit=gas_limit,
            arguments=[U32Value(action_id)],
        )

    def create_transaction_for_discard_batch(
        self,
        sender: Address,
        contract: Address,
        action_ids: list[int],
        gas_limit: int,
    ) -> Transaction:
        return self._sc_factory.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function="discardBatch",
            gas_limit=gas_limit,
            arguments=[VariadicValues(items=[U32Value(id) for id in action_ids])],
        )

    def create_transaction_for_propose_add_board_member(
        self,
        sender: Address,
        contract: Address,
        board_member: Address,
        gas_limit: int,
    ) -> Transaction:
        return self._sc_factory.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function="proposeAddBoardMember",
            gas_limit=gas_limit,
            arguments=[AddressValue.new_from_address(board_member)],
        )

    def create_transaction_for_propose_add_proposer(
        self,
        sender: Address,
        contract: Address,
        proposer: Address,
        gas_limit: int,
    ) -> Transaction:
        return self._sc_factory.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function="proposeAddProposer",
            gas_limit=gas_limit,
            arguments=[AddressValue.new_from_address(proposer)],
        )

    def create_transaction_for_propose_remove_user(
        self,
        sender: Address,
        contract: Address,
        user: Address,
        gas_limit: int,
    ) -> Transaction:
        return self._sc_factory.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function="proposeRemoveUser",
            gas_limit=gas_limit,
            arguments=[AddressValue.new_from_address(user)],
        )

    def create_transaction_for_propose_change_quorum(
        self,
        sender: Address,
        contract: Address,
        quorum: int,
        gas_limit: int,
    ) -> Transaction:
        return self._sc_factory.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function="proposeChangeQuorum",
            gas_limit=gas_limit,
            arguments=[U32Value(quorum)],
        )

    def create_transaction_for_propose_transfer_execute(
        self,
        sender: Address,
        contract: Address,
        receiver: Address,
        native_token_amount: int,
        gas_limit: int,
        opt_gas_limit: Optional[int] = None,
        abi: Optional[Abi] = None,
        function: Optional[str] = None,
        arguments: Optional[list[Any]] = None,
    ) -> Transaction:
        function_call: list[bytes] = []
        if function:
            arguments = arguments or []

            function_call: list[bytes] = self._serializer.serialize_to_parts([StringValue(function)])
            if abi:
                arguments = abi.encode_endpoint_input_parameters(function, arguments)
            else:
                arguments = self._serialize_arguments(arguments)

            function_call.extend(self._serialize_arguments(arguments))

        return self._sc_factory.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function="proposeTransferExecute",
            gas_limit=gas_limit,
            arguments=[
                AddressValue.new_from_address(receiver),
                BigUIntValue(native_token_amount),
                OptionValue(U64Value(opt_gas_limit) if opt_gas_limit else None),
                VariadicValues(items=[BytesValue(item) for item in function_call]),
            ],
        )

    def _serialize_arguments(self, arguments: list[Any]) -> list[bytes]:
        if is_list_of_typed_values(arguments):
            return self._serializer.serialize_to_parts(arguments)

        if all(isinstance(arg, bytes) for arg in arguments):
            return arguments

        raise ArgumentSerializationError()

    def create_transaction_for_propose_transfer_esdt_execute(
        self,
        sender: Address,
        contract: Address,
        receiver: Address,
        token_transfers: list[TokenTransfer],
        gas_limit: int,
        opt_gas_limit: Optional[int] = None,
        abi: Optional[Abi] = None,
        function: Optional[str] = None,
        arguments: Optional[list[Any]] = None,
    ) -> Transaction:
        input = self._prepare_transfer_execute_esdt_input(
            to=receiver,
            token_transfers=token_transfers,
            function=function,
            arguments=arguments,
            gas_limit=opt_gas_limit,
            abi=abi,
        )

        return self._sc_factory.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function="proposeTransferExecuteEsdt",
            gas_limit=gas_limit,
            arguments=[
                AddressValue.new_from_address(input.to),
                ListValue(items=input.tokens),
                OptionValue(U64Value(input.opt_gas_limit or 0)),
                VariadicValues([StringValue(arg.hex()) for arg in input.function_call]),
            ],
        )

    def _prepare_transfer_execute_esdt_input(
        self,
        to: Address,
        token_transfers: list[TokenTransfer],
        function: Optional[str] = None,
        arguments: Optional[list[Any]] = None,
        gas_limit: Optional[int] = None,
        abi: Optional[Abi] = None,
    ) -> ProposeTransferExecuteEsdtInput:
        tokens = [
            EsdtTokenPayment(token.token.identifier, token.token.nonce, token.amount) for token in token_transfers
        ]

        if not function:
            return ProposeTransferExecuteEsdtInput(
                to=to,
                tokens=tokens,
                function_call=[],
                opt_gas_limit=gas_limit,
            )

        arguments = arguments or []
        function_call: list[bytes] = self._serializer.serialize_to_parts([StringValue(function)])

        if abi:
            arguments = abi.encode_endpoint_input_parameters(function, arguments)
        else:
            arguments = self._serialize_arguments(arguments)

        function_call.extend(self._serialize_arguments(arguments))

        return ProposeTransferExecuteEsdtInput(
            to=to,
            tokens=tokens,
            function_call=function_call,
            opt_gas_limit=gas_limit,
        )

    def create_transaction_for_propose_async_call(
        self,
        sender: Address,
        contract: Address,
        receiver: Address,
        gas_limit: int,
        native_token_amount: int = 0,
        token_transfers: Optional[list[TokenTransfer]] = None,
        opt_gas_limit: Optional[int] = None,
        abi: Optional[Abi] = None,
        function: Optional[str] = None,
        arguments: Optional[list[Any]] = None,
    ) -> Transaction:
        token_transfers = token_transfers or []
        if not function:
            input = self._prepare_async_call_input_for_transfer(
                to=receiver,
                token_transfers=token_transfers,
                gas_limit=opt_gas_limit,
            )
        else:
            input = self._prepare_async_call_input_for_transfer_execute(
                to=receiver,
                token_transfers=token_transfers,
                function=function,
                arguments=arguments if arguments else [],
                gas_limit=opt_gas_limit,
                abi=abi,
            )

        return self._sc_factory.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function="proposeAsyncCall",
            gas_limit=gas_limit,
            arguments=[
                AddressValue.new_from_address(input.to),
                BigUIntValue(native_token_amount or 0),
                OptionValue(U64Value(input.opt_gas_limit)),
                VariadicValues([StringValue(arg.decode()) for arg in input.function_call]),
            ],
        )

    def _prepare_async_call_input_for_transfer(
        self,
        to: Address,
        token_transfers: list[TokenTransfer],
        gas_limit: Optional[int] = None,
    ) -> ProposeAsyncCallInput:
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
        return ProposeAsyncCallInput(to, function_call, gas_limit)

    def _prepare_async_call_input_for_transfer_execute(
        self,
        to: Address,
        token_transfers: list[TokenTransfer],
        function: str,
        arguments: list[Any],
        gas_limit: Optional[int] = None,
        abi: Optional[Abi] = None,
    ) -> ProposeAsyncCallInput:
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
        return ProposeAsyncCallInput(to, function_call, gas_limit)

    def create_transaction_for_propose_contract_deploy_from_source(
        self,
        sender: Address,
        contract: Address,
        gas_limit: int,
        contract_to_copy: Address,
        native_token_amount: int = 0,
        arguments: Optional[list[Any]] = None,
        is_upgradeable: bool = True,
        is_readable: bool = True,
        is_payable: bool = False,
        is_payable_by_sc: bool = True,
        abi: Optional[Abi] = None,
    ) -> Transaction:
        code_metadata = CodeMetadata(
            upgradeable=is_upgradeable,
            readable=is_readable,
            payable=is_payable,
            payable_by_contract=is_payable_by_sc,
        )
        arguments = arguments or []
        if abi:
            arguments = abi.encode_constructor_input_parameters(arguments)
        else:
            arguments = self._serialize_arguments(arguments)

        return self._sc_factory.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function="proposeSCDeployFromSource",
            gas_limit=gas_limit,
            arguments=[
                BigUIntValue(native_token_amount),
                AddressValue.new_from_address(contract_to_copy),
                CodeMetadataValue(code_metadata.serialize()),
                VariadicValues(items=[BytesValue(value) for value in arguments]),
            ],
        )

    def create_transaction_for_propose_contract_upgrade_from_source(
        self,
        sender: Address,
        contract: Address,
        contract_to_upgrade: Address,
        contract_to_copy: Address,
        gas_limit: int,
        arguments: Optional[list[Any]] = None,
        native_token_amount: int = 0,
        is_upgradeable: bool = True,
        is_readable: bool = True,
        is_payable: bool = False,
        is_payable_by_sc: bool = True,
        abi: Optional[Abi] = None,
    ) -> Transaction:
        code_metadata = CodeMetadata(
            upgradeable=is_upgradeable,
            readable=is_readable,
            payable=is_payable,
            payable_by_contract=is_payable_by_sc,
        )
        arguments = arguments or []
        if abi:
            arguments = abi.encode_upgrade_constructor_input_parameters(arguments)
        else:
            arguments = self._serialize_arguments(arguments)

        return self._sc_factory.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function="proposeSCUpgradeFromSource",
            gas_limit=gas_limit,
            arguments=[
                AddressValue.new_from_address(contract_to_upgrade),
                BigUIntValue(native_token_amount),
                AddressValue.new_from_address(contract_to_copy),
                CodeMetadataValue(code_metadata.serialize()),
                VariadicValues(items=[BytesValue(value) for value in arguments]),
            ],
        )

    def create_transaction_for_propose_batch(
        self,
        sender: Address,
        contract: Address,
        actions: list[Action],
        gas_limit: int,
    ) -> Transaction:
        raise NotImplementedError("proposeBatch was not implemented")

    def create_transaction_for_sign_action(
        self,
        sender: Address,
        contract: Address,
        action_id: int,
        gas_limit: int,
    ) -> Transaction:
        return self._sc_factory.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function="sign",
            gas_limit=gas_limit,
            arguments=[U32Value(action_id)],
        )

    def create_transaction_for_sign_batch(
        self,
        sender: Address,
        contract: Address,
        batch_id: int,
        gas_limit: int,
    ) -> Transaction:
        return self._sc_factory.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function="signBatch",
            gas_limit=gas_limit,
            arguments=[U32Value(batch_id)],
        )

    def create_transaction_for_sign_and_perform(
        self,
        sender: Address,
        contract: Address,
        action_id: int,
        gas_limit: int,
    ) -> Transaction:
        return self._sc_factory.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function="signAndPerform",
            gas_limit=gas_limit,
            arguments=[U32Value(action_id)],
        )

    def create_transaction_for_sign_batch_and_perform(
        self,
        sender: Address,
        contract: Address,
        batch_id: int,
        gas_limit: int,
    ) -> Transaction:
        return self._sc_factory.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function="signBatchAndPerform",
            gas_limit=gas_limit,
            arguments=[U32Value(batch_id)],
        )

    def create_transaction_for_unsign_action(
        self,
        sender: Address,
        contract: Address,
        action_id: int,
        gas_limit: int,
    ) -> Transaction:
        return self._sc_factory.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function="unsign",
            gas_limit=gas_limit,
            arguments=[U32Value(action_id)],
        )

    def create_transaction_for_unsign_batch(
        self,
        sender: Address,
        contract: Address,
        batch_id: int,
        gas_limit: int,
    ) -> Transaction:
        return self._sc_factory.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function="unsignBatch",
            gas_limit=gas_limit,
            arguments=[U32Value(batch_id)],
        )

    def create_transaction_for_unsign_for_outdated_board_members(
        self,
        sender: Address,
        contract: Address,
        action_id: int,
        outdated_board_members: list[int],
        gas_limit: int,
    ) -> Transaction:
        return self._sc_factory.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function="unsignForOutdatedBoardMembers",
            gas_limit=gas_limit,
            arguments=[
                U32Value(action_id),
                VariadicValues(items=[U32Value(member) for member in outdated_board_members]),
            ],
        )

    def create_transaction_for_perform_action(
        self,
        sender: Address,
        contract: Address,
        action_id: int,
        gas_limit: int,
    ) -> Transaction:
        return self._sc_factory.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function="performAction",
            gas_limit=gas_limit,
            arguments=[U32Value(action_id)],
        )

    def create_transaction_for_perform_batch(
        self,
        sender: Address,
        contract: Address,
        batch_id: int,
        gas_limit: int,
    ) -> Transaction:
        return self._sc_factory.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function="performBatch",
            gas_limit=gas_limit,
            arguments=[U32Value(batch_id)],
        )

    def create_transaction_for_execute(
        self,
        sender: Address,
        contract: Address,
        function: str,
        gas_limit: int,
        arguments: list[Any] = [],
        native_transfer_amount: int = 0,
        token_transfers: list[TokenTransfer] = [],
    ) -> Transaction:
        return self._sc_factory.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function=function,
            gas_limit=gas_limit,
            arguments=arguments,
            native_transfer_amount=native_transfer_amount,
            token_transfers=token_transfers,
        )
