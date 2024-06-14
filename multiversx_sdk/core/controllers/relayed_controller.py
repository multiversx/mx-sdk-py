from typing import List, Protocol, Union

from multiversx_sdk.core.interfaces import IAddress, ITransaction
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transaction_computer import TransactionComputer
from multiversx_sdk.core.transactions_factories.relayed_transactions_factory import \
    RelayedTransactionsFactory
from multiversx_sdk.core.transactions_factories.transactions_factory_config import \
    TransactionsFactoryConfig


class INetworkConfig(Protocol):
    chain_id: str


class INetworkProvider(Protocol):
    def get_network_config(self) -> INetworkConfig:
        ...


class IAccount(Protocol):
    address: IAddress

    def sign(self, data: bytes) -> bytes:
        ...


class RelayedController:
    """The transactions are created from the perspective of the relayer. The 'sender' represents the relayer."""

    def __init__(self, network_provider: INetworkProvider) -> None:
        self.chain_id: Union[str, None] = None
        self.factory: Union[RelayedTransactionsFactory, None] = None
        self.provider = network_provider
        self.tx_computer = TransactionComputer()

    def create_relayed_v1_transaction(self,
                                      sender: IAccount,
                                      nonce: int,
                                      inner_transaction: ITransaction) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_relayed_v1_transaction(  # type: ignore
            inner_transaction=inner_transaction,
            relayer_address=sender.address
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_relayed_v2_transaction(self,
                                      sender: IAccount,
                                      nonce: int,
                                      inner_transaction: ITransaction,
                                      inner_transaction_gas_limit: int) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_relayed_v2_transaction(  # type: ignore
            inner_transaction=inner_transaction,
            inner_transaction_gas_limit=inner_transaction_gas_limit,
            relayer_address=sender.address
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_relayed_v3_transaction(self,
                                      sender: IAccount,
                                      nonce: int,
                                      inner_transactions: List[ITransaction]) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_relayed_v3_transaction(  # type: ignore
            inner_transactions=inner_transactions,
            relayer_address=sender.address
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def _ensure_factory_is_initialized(self):
        if self.factory is None:
            self.chain_id = self.provider.get_network_config().chain_id
            config = TransactionsFactoryConfig(self.chain_id)
            self.factory = RelayedTransactionsFactory(config)
