from pathlib import Path
from typing import Any, Optional, Union, cast

from multiversx_sdk.abi.abi import Abi
from multiversx_sdk.abi.address_value import AddressValue
from multiversx_sdk.abi.biguint_value import BigUIntValue
from multiversx_sdk.abi.bytes_value import BytesValue
from multiversx_sdk.abi.code_metadata_value import CodeMetadataValue
from multiversx_sdk.abi.interface import ISingleValue
from multiversx_sdk.abi.list_value import ListValue
from multiversx_sdk.abi.multi_value import MultiValue
from multiversx_sdk.abi.option_value import OptionValue
from multiversx_sdk.abi.small_int_values import U32Value, U64Value
from multiversx_sdk.abi.string_value import StringValue
from multiversx_sdk.abi.variadic_values import VariadicValues
from multiversx_sdk.core.address import Address
from multiversx_sdk.core.code_metadata import CodeMetadata
from multiversx_sdk.core.tokens import TokenTransfer
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transactions_factory_config import TransactionsFactoryConfig
from multiversx_sdk.multisig.resources import (
    ProposeAsyncCallInput,
    ProposeSCDeployFromSourceInput,
    ProposeSCUpgradeFromSourceInput,
    ProposeTransferExecuteEsdtInput,
    ProposeTransferExecuteInput,
)
from multiversx_sdk.smart_contracts.smart_contract_transactions_factory import (
    SmartContractTransactionsFactory,
)


class MultisigTransactionsFactory:
    def __init__(self, config: TransactionsFactoryConfig, abi: Optional[Abi] = None) -> None:
        self._sc_factory = SmartContractTransactionsFactory(config, abi)

    def create_transaction_for_deploy(
        self,
        sender: Address,
        bytecode: Union[Path, bytes],
        quorum: int,
        board: list[Address],
        gas_limit: int,
        native_transfer_amount: int = 0,
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
            native_transfer_amount=native_transfer_amount,
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
        if not function:
            input = ProposeTransferExecuteInput.new_for_native_transfer(
                to=receiver,
                native_transfer_amount=native_token_amount,
                gas_limit=opt_gas_limit,
            )
        else:
            input = ProposeTransferExecuteInput.new_for_transfer_execute(
                to=receiver,
                native_transfer_amount=native_token_amount,
                function=function,
                arguments=arguments if arguments else [],
                gas_limit=opt_gas_limit,
                abi=abi,
            )

        function_call = input.function_call
        if all(isinstance(arg, bytes) for arg in input.function_call[1:]):
            function_call = [input.function_call[0]]
            for arg in input.function_call[1:]:
                arg = cast(bytes, arg)
                function_call.append(BytesValue(arg))

        function_call = cast(list[Union[ISingleValue, MultiValue]], function_call)

        return self._sc_factory.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function="proposeTransferExecute",
            gas_limit=gas_limit,
            arguments=[
                AddressValue.new_from_address(input.to),
                BigUIntValue(input.egld_amount),
                OptionValue(U64Value(input.opt_gas_limit or 0)),
                VariadicValues(items=function_call),
            ],
        )

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
        if not function:
            input = ProposeTransferExecuteEsdtInput.new_for_transfer(
                to=receiver,
                token_transfers=token_transfers,
                gas_limit=opt_gas_limit,
            )
        else:
            input = ProposeTransferExecuteEsdtInput.new_for_transfer_execute(
                to=receiver,
                token_transfers=token_transfers,
                function=function,
                arguments=arguments if arguments else [],
                gas_limit=opt_gas_limit,
                abi=abi,
            )

        tokens = cast(list[ISingleValue], input.tokens)
        return self._sc_factory.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function="proposeTransferExecuteEsdt",
            gas_limit=gas_limit,
            arguments=[
                AddressValue.new_from_address(input.to),
                ListValue(items=tokens),
                OptionValue(U64Value(input.opt_gas_limit or 0)),
                VariadicValues([StringValue(arg.hex()) for arg in input.function_call]),
            ],
        )

    def create_transaction_for_propose_async_call(
        self,
        sender: Address,
        contract: Address,
        receiver: Address,
        gas_limit: int,
        token_transfers: Optional[list[TokenTransfer]] = None,
        opt_gas_limit: Optional[int] = None,
        abi: Optional[Abi] = None,
        function: Optional[str] = None,
        arguments: Optional[list[Any]] = None,
    ) -> Transaction:
        token_transfers = token_transfers or []
        if not function:
            input = ProposeAsyncCallInput.new_for_transfer(
                to=receiver,
                token_transfers=token_transfers,
                gas_limit=opt_gas_limit,
            )
        else:
            input = ProposeAsyncCallInput.new_for_transfer_execute(
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
                BigUIntValue(),
                OptionValue(U64Value(input.opt_gas_limit or 0)),
                VariadicValues([StringValue(arg.decode()) for arg in input.function_call]),
            ],
        )

    def create_transaction_for_contract_deploy_from_source(
        self,
        sender: Address,
        contract: Address,
        gas_limit: int,
        contract_to_copy: Address,
        arguments: list[Any],
        native_token_amount: int,
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
        input = ProposeSCDeployFromSourceInput(
            native_transfer_amount=native_token_amount,
            contract_to_copy=contract_to_copy,
            code_metadata=code_metadata,
            arguments=arguments,
            abi=abi,
        )

        return self._sc_factory.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function="proposeSCDeployFromSource",
            gas_limit=gas_limit,
            arguments=[
                BigUIntValue(input.amount),
                AddressValue.new_from_address(input.source),
                CodeMetadataValue(input.code_metadata),
                VariadicValues(items=[BytesValue(value) for value in input.arguments]),
            ],
        )

    def create_transaction_for_contract_upgrade_from_source(
        self,
        sender: Address,
        contract: Address,
        contract_to_upgrade: Address,
        gas_limit: int,
        contract_to_copy: Address,
        arguments: list[Any],
        native_token_amount: int,
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
        input = ProposeSCUpgradeFromSourceInput(
            contract_to_upgrade=contract_to_upgrade,
            native_transfer_amount=native_token_amount,
            contract_to_copy=contract_to_copy,
            code_metadata=code_metadata,
            arguments=arguments,
            abi=abi,
        )

        return self._sc_factory.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function="proposeSCUpgradeFromSource",
            gas_limit=gas_limit,
            arguments=[
                AddressValue.new_from_address(contract_to_upgrade),
                BigUIntValue(input.amount),
                AddressValue.new_from_address(input.source),
                CodeMetadataValue(input.code_metadata),
                VariadicValues(items=[BytesValue(value) for value in input.arguments]),
            ],
        )

    def create_transaction_for_propose_batch(
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
