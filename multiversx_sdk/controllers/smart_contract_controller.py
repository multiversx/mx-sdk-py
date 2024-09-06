from pathlib import Path
from typing import Any, List, Optional, Protocol, Sequence, Union

from multiversx_sdk.adapters.query_runner_adapter import QueryRunnerAdapter
from multiversx_sdk.controllers.interfaces import IAccount
from multiversx_sdk.controllers.network_provider_wrapper import ProviderWrapper
from multiversx_sdk.converters.transactions_converter import \
    TransactionsConverter
from multiversx_sdk.core.interfaces import IAddress
from multiversx_sdk.core.smart_contract_queries_controller import \
    SmartContractQueriesController
from multiversx_sdk.core.tokens import TokenTransfer
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transaction_computer import TransactionComputer
from multiversx_sdk.core.transactions_factories import (
    SmartContractTransactionsFactory, TransactionsFactoryConfig)
from multiversx_sdk.core.transactions_outcome_parsers import (
    SmartContractDeployOutcome, SmartContractTransactionsOutcomeParser)
from multiversx_sdk.network_providers.transaction_awaiter import \
    TransactionAwaiter
from multiversx_sdk.network_providers.transactions import TransactionOnNetwork


class IQuery(Protocol):
    def get_contract(self) -> IAddress:
        ...

    def get_function(self) -> str:
        ...

    def get_encoded_arguments(self) -> Sequence[str]:
        ...

    def get_caller(self) -> Optional[IAddress]:
        ...

    def get_value(self) -> int:
        ...


class IQueryResponse(Protocol):
    return_data: List[str]
    return_code: str
    return_message: str
    gas_used: int

    def get_return_data_parts(self) -> List[bytes]:
        ...


class INetworkProvider(Protocol):
    def query_contract(self, query: IQuery) -> IQueryResponse:
        ...


class IAbi(Protocol):
    def encode_endpoint_input_parameters(self, endpoint_name: str, values: List[Any]) -> List[bytes]:
        ...

    def encode_constructor_input_parameters(self, values: List[Any]) -> List[bytes]:
        ...

    def encode_upgrade_constructor_input_parameters(self, values: List[Any]) -> List[bytes]:
        ...

    def decode_endpoint_output_parameters(self, endpoint_name: str, encoded_values: List[bytes]) -> List[Any]:
        ...


class SmartContractController:
    def __init__(self, chain_id: str, network_provider: INetworkProvider, abi: Optional[IAbi] = None) -> None:
        self.provider = network_provider
        self.abi = abi
        self.factory = SmartContractTransactionsFactory(TransactionsFactoryConfig(chain_id))
        self.parser = SmartContractTransactionsOutcomeParser()
        self.query_controller = SmartContractQueriesController(
            query_runner=QueryRunnerAdapter(self.provider),
            abi=self.abi
        )
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
        tx_converter = TransactionsConverter()
        tx_outcome = tx_converter.transaction_on_network_to_outcome(transaction_on_network)

        return self.parser.parse_deploy(tx_outcome)

    def await_completed_deploy(self, tx_hash: str) -> SmartContractDeployOutcome:
        provider = ProviderWrapper(self.provider)
        transaction_awaiter = TransactionAwaiter(provider)
        transaction = transaction_awaiter.await_completed(tx_hash)
        return self.parse_deploy(transaction)

    def create_transaction_for_upgrade(self,
                                       sender: IAccount,
                                       nonce: int,
                                       contract: IAddress,
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
                                       contract: IAddress,
                                       gas_limit: int,
                                       function: str,
                                       arguments: Sequence[Any] = [],
                                       native_transfer_amount: int = 0,
                                       token_transfers: Sequence[TokenTransfer] = []) -> Transaction:
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

    def await_completed_execute(self, tx_hash: str) -> List[Any]:
        raise NotImplementedError("This feature is not yet implemented")

    def query_contract(self,
                       contract: IAddress,
                       function: str,
                       arguments: List[Any],
                       caller: Optional[IAddress] = None,
                       value: Optional[int] = None) -> List[Any]:
        return self.query_controller.query(
            contract=contract.to_bech32(),
            function=function,
            arguments=arguments,
            caller=caller.to_bech32() if caller else None,
            value=value
        )
