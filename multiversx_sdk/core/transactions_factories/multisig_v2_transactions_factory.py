
from pathlib import Path
from typing import Optional, Union

from multiversx_sdk.core.interfaces import IAddress
from multiversx_sdk.core.tokens import TokenTransfer
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transactions_factories.smart_contract_transactions_factory import (
    IAbi, IConfig, SmartContractTransactionsFactory)


class MultisigV2TransactionsFactory:
    def __init__(self, config: IConfig, multisig_abi: IAbi) -> None:
        self.factory_for_any = SmartContractTransactionsFactory(config)
        self.factory_for_multisig = SmartContractTransactionsFactory(config, abi=multisig_abi)

    def create_transaction_for_deploy(
        self,
        sender: IAddress,
        bytecode: Union[Path, bytes],
        gas_limit: int,
        quorum: int,
        board: list[IAddress],
        is_upgradeable=True,
        is_readable=True,
        is_payable=False,
        is_payable_by_contract=True,
    ) -> Transaction:
        return self.factory_for_multisig.create_transaction_for_deploy(
            sender=sender,
            bytecode=bytecode,
            gas_limit=gas_limit,
            arguments=[quorum, board],
            is_upgradeable=is_upgradeable,
            is_readable=is_readable,
            is_payable=is_payable,
            is_payable_by_sc=is_payable_by_contract,
        )

    def create_transaction_for_deposit(
        self,
        sender: IAddress,
        contract: IAddress,
        gas_limit: int,
        native_transfer_amount: int = 0,
        token_transfers: Optional[list[TokenTransfer]] = None,
    ) -> Transaction:
        return self.factory_for_multisig.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function="deposit",
            gas_limit=gas_limit,
            arguments=[],
            native_transfer_amount=native_transfer_amount,
            token_transfers=token_transfers or []
        )

    def create_transaction_for_discard_action(
        self,
        sender: IAddress,
        contract: IAddress,
        gas_limit: int,
        action_id: int
    ) -> Transaction:
        return self.factory_for_multisig.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function="discardAction",
            gas_limit=gas_limit,
            arguments=[action_id],
        )

    def create_transaction_for_discard_batch(
        self,
        sender: IAddress,
        contract: IAddress,
        gas_limit: int,
        actions_ids: list[int],
    ) -> Transaction:
        return self.factory_for_multisig.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function="discardBatch",
            gas_limit=gas_limit,
            arguments=[actions_ids],
        )

    def create_transaction_for_propose_add_board_member(
        self,
        sender: IAddress,
        contract: IAddress,
        gas_limit: int,
        board_member: IAddress,
    ) -> Transaction:
        return self.factory_for_multisig.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function="proposeAddBoardMember",
            gas_limit=gas_limit,
            arguments=[board_member],
        )

    def create_transaction_for_propose_add_proposer(
        self,
        sender: IAddress,
        contract: IAddress,
        gas_limit: int,
        proposer: IAddress,
    ) -> Transaction:
        return self.factory_for_multisig.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function="proposeAddProposer",
            gas_limit=gas_limit,
            arguments=[proposer],
        )

    def create_transaction_for_propose_remove_user(
        self,
        sender: IAddress,
        contract: IAddress,
        gas_limit: int,
        user: IAddress,
    ) -> Transaction:
        return self.factory_for_multisig.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function="proposeRemoveUser",
            gas_limit=gas_limit,
            arguments=[user],
        )

    def create_transaction_for_propose_change_quorum(
        self,
        sender: IAddress,
        contract: IAddress,
        gas_limit: int,
        new_quorum: int,
    ) -> Transaction:
        return self.factory_for_multisig.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function="proposeChangeQuorum",
            gas_limit=gas_limit,
            arguments=[new_quorum],
        )
