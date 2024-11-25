from multiversx_sdk.account_management.account_transactions_factory import \
    AccountTransactionsFactory
from multiversx_sdk.core import Address, Transaction, TransactionComputer
from multiversx_sdk.core.interfaces import IAccount
from multiversx_sdk.core.transactions_factory_config import \
    TransactionsFactoryConfig


class AccountController:
    def __init__(self, chain_id: str) -> None:
        self.factory = AccountTransactionsFactory(TransactionsFactoryConfig(chain_id))
        self.tx_computer = TransactionComputer()

    def create_transaction_for_saving_key_value(self,
                                                sender: IAccount,
                                                nonce: int,
                                                key_value_pairs: dict[bytes, bytes]) -> Transaction:
        transaction = self.factory.create_transaction_for_saving_key_value(
            sender=sender.address,
            key_value_pairs=key_value_pairs
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_setting_guardian(self,
                                                sender: IAccount,
                                                nonce: int,
                                                guardian_address: Address,
                                                service_id: str) -> Transaction:
        transaction = self.factory.create_transaction_for_setting_guardian(
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
        transaction = self.factory.create_transaction_for_guarding_account(
            sender=sender.address
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(
            self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_unguarding_account(self,
                                                  sender: IAccount,
                                                  nonce: int) -> Transaction:
        transaction = self.factory.create_transaction_for_unguarding_account(
            sender=sender.address
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(
            self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction
