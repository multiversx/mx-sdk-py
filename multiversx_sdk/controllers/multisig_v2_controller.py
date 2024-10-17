from pathlib import Path
from typing import Any, List, Optional, Protocol, Sequence, Union

from multiversx_sdk.controllers.interfaces import IAbi, IAccount
from multiversx_sdk.controllers.smart_contract_controller import \
    INetworkProvider
from multiversx_sdk.core.interfaces import IAddress
from multiversx_sdk.core.smart_contract_queries_controller import \
    SmartContractQueriesController
from multiversx_sdk.core.tokens import TokenTransfer
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transaction_computer import TransactionComputer
from multiversx_sdk.core.transaction_on_network import TransactionOnNetwork
from multiversx_sdk.core.transactions_factories import (
    SmartContractTransactionsFactory, TransactionsFactoryConfig)
from multiversx_sdk.core.transactions_outcome_parsers import (
    SmartContractDeployOutcome, SmartContractTransactionsOutcomeParser)
from multiversx_sdk.core.transactions_outcome_parsers.smart_contract_transactions_outcome_parser_types import \
    ParsedSmartContractCallOutcome


class MultisigV2Controller:
    def __init__(self, chain_id: str, network_provider: INetworkProvider, abi: IAbi) -> None:
        self.network_provider = network_provider
        self.factory = SmartContractTransactionsFactory(TransactionsFactoryConfig(chain_id), abi=abi)
        self.parser = SmartContractTransactionsOutcomeParser(abi=abi)
        self.transaction_computer = TransactionComputer()
        self.query_controller = SmartContractQueriesController(
            network_provider=network_provider,
            abi=abi
        )

    def create_transaction_for_deploy(self,
                                      sender: IAccount,
                                      nonce: int,
                                      bytecode: Union[Path, bytes],
                                      gas_limit: int,
                                      quorum: int,
                                      board: list[IAddress],
                                      is_upgradeable: bool = True,
                                      is_readable: bool = True,
                                      is_payable: bool = False,
                                      is_payable_by_contract: bool = True) -> Transaction:
        transaction = self.factory.create_transaction_for_deploy(
            sender=sender.address,
            bytecode=bytecode,
            gas_limit=gas_limit,
            arguments=[quorum, board],
            is_upgradeable=is_upgradeable,
            is_readable=is_readable,
            is_payable=is_payable,
            is_payable_by_sc=is_payable_by_contract,
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_deploy(self, transaction_on_network: TransactionOnNetwork) -> SmartContractDeployOutcome:
        return self.parser.parse_deploy(transaction_on_network)

    def await_completed_deploy(self, tx_hash: str) -> SmartContractDeployOutcome:
        transaction = self.network_provider.await_transaction_completed(tx_hash)
        return self.parse_deploy(transaction)

    def create_transaction_for_deposit(self,
                                       sender: IAccount,
                                       nonce: int,
                                       contract: IAddress,
                                       gas_limit: int,
                                       native_transfer_amount: int = 0,
                                       token_transfers: Optional[List[TokenTransfer]] = None) -> Transaction:
        transaction = self.factory.create_transaction_for_execute(
            sender=sender.address,
            contract=contract,
            function="deposit",
            gas_limit=gas_limit,
            arguments=[],
            native_transfer_amount=native_transfer_amount,
            token_transfers=token_transfers or []
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_discard_action(self,
                                              sender: IAccount,
                                              nonce: int,
                                              contract: IAddress,
                                              gas_limit: int,
                                              action_id: int) -> Transaction:
        transaction = self.factory.create_transaction_for_execute(
            sender=sender.address,
            contract=contract,
            function="discardAction",
            gas_limit=gas_limit,
            arguments=[action_id],
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_discard_batch(self,
                                             sender: IAccount,
                                             nonce: int,
                                             contract: IAddress,
                                             gas_limit: int,
                                             actions_ids: list[int]) -> Transaction:
        transaction = self.factory.create_transaction_for_execute(
            sender=sender.address,
            contract=contract,
            function="discardBatch",
            gas_limit=gas_limit,
            arguments=[actions_ids],
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        return transaction

    def get_quorum(self, contract: IAddress) -> int:
        [value] = self.query_controller.query(
            contract=contract.to_bech32(),
            function="getQuorum",
            arguments=[],
        )

        return value

    def get_num_board_members(self, contract: IAddress) -> int:
        [value] = self.query_controller.query(
            contract=contract.to_bech32(),
            function="getNumBoardMembers",
            arguments=[],
        )

        return value

    def get_num_groups(self, contract: IAddress) -> int:
        [value] = self.query_controller.query(
            contract=contract.to_bech32(),
            function="getNumGroups",
            arguments=[],
        )

        return value

    def get_num_proposers(self, contract: IAddress) -> int:
        [value] = self.query_controller.query(
            contract=contract.to_bech32(),
            function="getNumProposers",
            arguments=[],
        )

        return value

    def get_action_group(self, contract: IAddress, group_id: int) -> list[int]:
        values = self.query_controller.query(
            contract=contract.to_bech32(),
            function="getActionGroup",
            arguments=[group_id],
        )

        return values

    def get_last_group_action_id(self, contract: IAddress) -> int:
        [value] = self.query_controller.query(
            contract=contract.to_bech32(),
            function="getLastGroupActionId",
            arguments=[],
        )

        return value

    def get_action_last_index(self, contract: IAddress) -> int:
        [value] = self.query_controller.query(
            contract=contract.to_bech32(),
            function="getActionLastIndex",
            arguments=[],
        )

        return value

    def create_transaction_for_propose_add_board_member(self,
                                                        sender: IAccount,
                                                        nonce: int,
                                                        contract: IAddress,
                                                        gas_limit: int,
                                                        board_member: IAddress,) -> Transaction:
        transaction = self.factory.create_transaction_for_execute(
            sender=sender.address,
            contract=contract,
            function="proposeAddBoardMember",
            gas_limit=gas_limit,
            arguments=[board_member],
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_execute_propose_add_board_member(self, transaction_on_network: TransactionOnNetwork, function: Optional[str] = None) -> int:
        outcome = self.parser.parse_execute(transaction_on_network)
        self._raise_for_return_code_in_outcome(outcome)
        return outcome.values[0]

    def await_completed_execute_add_board_member(self, tx_hash: str) -> int:
        transaction = self.network_provider.await_transaction_completed(tx_hash)
        return self.parse_execute_propose_add_board_member(transaction)

    def create_transaction_for_propose_add_proposer(self,
                                                    sender: IAccount,
                                                    nonce: int,
                                                    contract: IAddress,
                                                    gas_limit: int,
                                                    proposer: IAddress) -> Transaction:
        transaction = self.factory.create_transaction_for_execute(
            sender=sender.address,
            contract=contract,
            function="proposeAddProposer",
            gas_limit=gas_limit,
            arguments=[proposer],
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_execute_propose_add_proposer(self, transaction_on_network: TransactionOnNetwork, function: Optional[str] = None) -> int:
        outcome = self.parser.parse_execute(transaction_on_network)
        self._raise_for_return_code_in_outcome(outcome)
        return outcome.values[0]

    def await_completed_execute_add_proposer(self, tx_hash: str) -> int:
        transaction = self.network_provider.await_transaction_completed(tx_hash)
        return self.parse_execute_propose_add_proposer(transaction)

    def create_transaction_for_propose_remove_user(self,
                                                   sender: IAccount,
                                                   nonce: int,
                                                   contract: IAddress,
                                                   gas_limit: int,
                                                   user: IAddress) -> Transaction:
        transaction = self.factory.create_transaction_for_execute(
            sender=sender.address,
            contract=contract,
            function="proposeRemoveUser",
            gas_limit=gas_limit,
            arguments=[user],
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_execute_propose_remove_user(self, transaction_on_network: TransactionOnNetwork, function: Optional[str] = None) -> int:
        outcome = self.parser.parse_execute(transaction_on_network)
        self._raise_for_return_code_in_outcome(outcome)
        return outcome.values[0]

    def await_completed_execute_propose_remove_user(self, tx_hash: str) -> int:
        transaction = self.network_provider.await_transaction_completed(tx_hash)
        return self.parse_execute_propose_remove_user(transaction)

    def create_transaction_for_propose_change_quorum(self,
                                                     sender: IAccount,
                                                     nonce: int,
                                                     contract: IAddress,
                                                     gas_limit: int,
                                                     new_quorum: int) -> Transaction:
        transaction = self.factory.create_transaction_for_execute(
            sender=sender.address,
            contract=contract,
            function="proposeChangeQuorum",
            gas_limit=gas_limit,
            arguments=[new_quorum],
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_execute_propose_change_quorum(self, transaction_on_network: TransactionOnNetwork, function: Optional[str] = None) -> int:
        outcome = self.parser.parse_execute(transaction_on_network)
        self._raise_for_return_code_in_outcome(outcome)
        return outcome.values[0]

    def await_completed_execute_propose_change_quorum(self, tx_hash: str) -> int:
        transaction = self.network_provider.await_transaction_completed(tx_hash)
        return self.parse_execute_propose_change_quorum(transaction)

    # TODO: maybe move to the generic outcome parser, just like we did in the query controller?
    def _raise_for_return_code_in_outcome(self, outcome: ParsedSmartContractCallOutcome):
        is_ok = outcome.return_code == "ok"
        if not is_ok:
            raise Exception(outcome.return_code, outcome.return_message)
