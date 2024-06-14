from typing import Dict, Protocol, Union

from multiversx_sdk.core.interfaces import IAddress
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transaction_computer import TransactionComputer
from multiversx_sdk.core.transactions_factories.account_transactions_factory import \
    AccountTransactionsFactory
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


class AccountController:
    def __init__(self, network_provider: INetworkProvider) -> None:
        self.chain_id: Union[str, None] = None
        self.factory: Union[AccountTransactionsFactory, None] = None
        self.provider = network_provider
        self.tx_computer = TransactionComputer()

    def create_transaction_for_saving_key_value(self,
                                                sender: IAccount,
                                                nonce: int,
                                                key_value_pairs: Dict[bytes, bytes]) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_saving_key_value(  # type: ignore
            sender=sender.address,
            key_value_pairs=key_value_pairs
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_setting_guardian(self,
                                                sender: IAccount,
                                                nonce: int,
                                                guardian_address: IAddress,
                                                service_id: str) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_setting_guardian(  # type: ignore
            sender=sender.address,
            guardian_address=guardian_address,
            service_id=service_id
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_guarding_account(self,
                                                sender: IAccount,
                                                nonce: int) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_guarding_account(  # type: ignore
            sender=sender.address
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_unguarding_account(self,
                                                  sender: IAccount,
                                                  nonce: int) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_unguarding_account(  # type: ignore
            sender=sender.address
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def _ensure_factory_is_initialized(self):
        if self.factory is None:
            self.chain_id = self.provider.get_network_config().chain_id
            config = TransactionsFactoryConfig(self.chain_id)
            self.factory = AccountTransactionsFactory(config)
