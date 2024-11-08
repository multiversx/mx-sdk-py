from pathlib import Path
from typing import Any, List, Optional, Sequence, Union

from multiversx_sdk.controllers.interfaces import (IAbi, IAccount,
                                                   INetworkProvider)
from multiversx_sdk.core.address import Address
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


class SmartContractController:
    def __init__(self, chain_id: str, network_provider: INetworkProvider, abi: Optional[IAbi] = None) -> None:
        self.abi = abi
        self.factory = SmartContractTransactionsFactory(
            TransactionsFactoryConfig(chain_id), abi=self.abi)
        self.parser = SmartContractTransactionsOutcomeParser()
        self.query_controller = SmartContractQueriesController(
            network_provider=network_provider,
            abi=self.abi
        )
        self.network_provider = network_provider
        self.tx_computer = TransactionComputer()

    def create_transaction_for_deploy(self,
                                      sender: IAccount,
                                      nonce: int,
                                      bytecode: Union[Path, bytes],
                                      gas_limit: int,
                                      arguments: Sequence[Any] = [],
                                      native_transfer_amount: int = 0,
                                      is_upgradeable: bool = True,
                                      is_readable: bool = True,
                                      is_payable: bool = False,
                                      is_payable_by_sc: bool = True) -> Transaction:
        transaction = self.factory.create_transaction_for_deploy(
            sender=sender.address,
            bytecode=bytecode,
            gas_limit=gas_limit,
            arguments=arguments,
            native_transfer_amount=native_transfer_amount,
            is_upgradeable=is_upgradeable,
            is_readable=is_readable,
            is_payable=is_payable,
            is_payable_by_sc=is_payable_by_sc
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_deploy(self, transaction_on_network: TransactionOnNetwork) -> SmartContractDeployOutcome:
        return self.parser.parse_deploy(transaction_on_network)

    def await_completed_deploy(self, transaction_hash: Union[str, bytes]) -> SmartContractDeployOutcome:
        transaction = self.network_provider.await_transaction_completed(
            transaction_hash)
        return self.parse_deploy(transaction)

    def create_transaction_for_upgrade(self,
                                       sender: IAccount,
                                       nonce: int,
                                       contract: Address,
                                       bytecode: Union[Path, bytes],
                                       gas_limit: int,
                                       arguments: Sequence[Any] = [],
                                       native_transfer_amount: int = 0,
                                       is_upgradeable: bool = True,
                                       is_readable: bool = True,
                                       is_payable: bool = False,
                                       is_payable_by_sc: bool = True) -> Transaction:
        transaction = self.factory.create_transaction_for_upgrade(
            sender=sender.address,
            contract=contract,
            bytecode=bytecode,
            gas_limit=gas_limit,
            arguments=arguments,
            native_transfer_amount=native_transfer_amount,
            is_upgradeable=is_upgradeable,
            is_readable=is_readable,
            is_payable=is_payable,
            is_payable_by_sc=is_payable_by_sc
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_execute(self,
                                       sender: IAccount,
                                       nonce: int,
                                       contract: Address,
                                       gas_limit: int,
                                       function: str,
                                       arguments: Sequence[Any] = [],
                                       native_transfer_amount: int = 0,
                                       token_transfers: List[TokenTransfer] = []) -> Transaction:
        transaction = self.factory.create_transaction_for_execute(
            sender=sender.address,
            contract=contract,
            gas_limit=gas_limit,
            function=function,
            arguments=arguments,
            native_transfer_amount=native_transfer_amount,
            token_transfers=token_transfers
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_execute(self, transaction_on_network: TransactionOnNetwork, function: Optional[str] = None) -> List[Any]:
        raise NotImplementedError("This method is not yet implemented")

    def await_completed_execute(self, transaction_hash: Union[str, bytes]) -> List[Any]:
        raise NotImplementedError("This feature is not yet implemented")

    def query_contract(self,
                       contract: Address,
                       function: str,
                       arguments: List[Any],
                       caller: Optional[Address] = None,
                       value: Optional[int] = None) -> List[Any]:
        return self.query_controller.query(
            contract=contract.to_bech32(),
            function=function,
            arguments=arguments,
            caller=caller.to_bech32() if caller else None,
            value=value
        )
