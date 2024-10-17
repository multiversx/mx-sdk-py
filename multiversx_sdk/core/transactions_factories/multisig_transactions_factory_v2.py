
from pathlib import Path
from typing import Optional, Union

from multiversx_sdk.core.interfaces import IAddress
from multiversx_sdk.core.tokens import TokenTransfer
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transactions_factories.smart_contract_transactions_factory import (
    IAbi, IConfig, SmartContractTransactionsFactory)


class MultisigTransactionsFactoryV2:
    def __init__(self, config: IConfig, multisig_abi: IAbi) -> None:
        self.factory_for_any = SmartContractTransactionsFactory(config)
        self.factory_for_multisig = SmartContractTransactionsFactory(config, abi=multisig_abi)

    def create_transaction_for_deploy(
        self,
        sender: IAddress,
        bytecode: Union[Path, bytes],
        quorum: int,
        board: list[IAddress],
        is_upgradeable=True,
        is_readable=True,
        is_payable=False,
        is_payable_by_contract=True,
        gas_limit=0,
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
        native_transfer_amount=0,
        token_transfers: Optional[list[TokenTransfer]] = None,
        gas_limit=0,
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
        action_id: int,
        gas_limit=0,
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
        actions_ids: list[int],
        gas_limit=0,
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
        board_member: IAddress,
        gas_limit=0,
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
        proposer: IAddress,
        gas_limit=0,
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
        user: IAddress,
        gas_limit=0,
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
        new_quorum: int,
        gas_limit=0,
    ) -> Transaction:
        return self.factory_for_multisig.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function="proposeChangeQuorum",
            gas_limit=gas_limit,
            arguments=[new_quorum],
        )
