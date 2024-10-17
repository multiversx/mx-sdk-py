from pathlib import Path
from typing import Any, List, Optional, Protocol, Sequence, Union

from multiversx_sdk.controllers.interfaces import IAbi, IAccount
from multiversx_sdk.controllers.smart_contract_controller import \
    INetworkProvider
from multiversx_sdk.core.interfaces import IAddress
from multiversx_sdk.core.smart_contract_queries_controller import \
    SmartContractQueriesController
from multiversx_sdk.core.smart_contract_query import (
    SmartContractQuery, SmartContractQueryResponse)
from multiversx_sdk.core.tokens import TokenTransfer
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transaction_computer import TransactionComputer
from multiversx_sdk.core.transaction_on_network import TransactionOnNetwork
from multiversx_sdk.core.transactions_factories import (
    SmartContractTransactionsFactory, TransactionsFactoryConfig)
from multiversx_sdk.core.transactions_factories.multisig_v2_transactions_factory import \
    MultisigV2TransactionsFactory
from multiversx_sdk.core.transactions_outcome_parsers import (
    SmartContractDeployOutcome, SmartContractTransactionsOutcomeParser)
from multiversx_sdk.network_providers.resources import AwaitingOptions


class MultisigV2Controller:
    def __init__(self, chain_id: str, network_provider: INetworkProvider, multisig_abi: IAbi) -> None:
        self.network_provider = network_provider
        self.factory = MultisigV2TransactionsFactory(TransactionsFactoryConfig(chain_id), multisig_abi=multisig_abi)
        self.transaction_computer = TransactionComputer()
        self.query_controller = SmartContractQueriesController(
            network_provider=network_provider,
            abi=multisig_abi
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
            quorum=quorum,
            board=board,
            is_upgradeable=is_upgradeable,
            is_readable=is_readable,
            is_payable=is_payable,
            is_payable_by_contract=is_payable_by_contract
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_deposit(self,
                                       sender: IAccount,
                                       nonce: int,
                                       contract: IAddress,
                                       gas_limit: int,
                                       native_transfer_amount: int = 0,
                                       token_transfers: Optional[List[TokenTransfer]] = None) -> Transaction:
        transaction = self.factory.create_transaction_for_deposit(
            sender=sender.address,
            contract=contract,
            gas_limit=gas_limit,
            native_transfer_amount=native_transfer_amount,
            token_transfers=token_transfers,
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
        transaction = self.factory.create_transaction_for_discard_action(
            sender=sender.address,
            contract=contract,
            gas_limit=gas_limit,
            action_id=action_id,
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
        transaction = self.factory.create_transaction_for_discard_batch(
            sender=sender.address,
            contract=contract,
            gas_limit=gas_limit,
            actions_ids=actions_ids,
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        return transaction

    def get_quorum(self, contract: IAddress) -> int:
        [quorum] = self.query_controller.query(
            contract=contract.to_bech32(),
            function="getQuorum",
            arguments=[],
        )

        return quorum

    def get_num_board_members(self, contract: IAddress) -> int:
        [num] = self.query_controller.query(
            contract=contract.to_bech32(),
            function="getNumBoardMembers",
            arguments=[],
        )

        return num

    def get_num_groups(self, contract: IAddress) -> int:
        [num] = self.query_controller.query(
            contract=contract.to_bech32(),
            function="getNumGroups",
            arguments=[],
        )

        return num

    def get_num_proposers(self, contract: IAddress) -> int:
        [num] = self.query_controller.query(
            contract=contract.to_bech32(),
            function="getNumProposers",
            arguments=[],
        )

        return num

    def get_action_group(self, contract: IAddress, group_id: int) -> list[int]:
        ids = self.query_controller.query(
            contract=contract.to_bech32(),
            function="getActionGroup",
            arguments=[group_id],
        )

        return ids
