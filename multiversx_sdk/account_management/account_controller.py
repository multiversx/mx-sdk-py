from typing import Optional

from multiversx_sdk.account_management.account_transactions_factory import (
    AccountTransactionsFactory,
)
from multiversx_sdk.core import Address, Transaction
from multiversx_sdk.core.base_controller import BaseController
from multiversx_sdk.core.interfaces import IAccount
from multiversx_sdk.core.transactions_factory_config import TransactionsFactoryConfig


class AccountController(BaseController):
    def __init__(self, chain_id: str) -> None:
        self.factory = AccountTransactionsFactory(TransactionsFactoryConfig(chain_id))

    def create_transaction_for_saving_key_value(
        self,
        sender: IAccount,
        nonce: int,
        key_value_pairs: dict[bytes, bytes],
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_saving_key_value(
            sender=sender.address, key_value_pairs=key_value_pairs
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_setting_guardian(
        self,
        sender: IAccount,
        nonce: int,
        guardian_address: Address,
        service_id: str,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_setting_guardian(
            sender=sender.address,
            guardian_address=guardian_address,
            service_id=service_id,
        )
        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_guarding_account(
        self,
        sender: IAccount,
        nonce: int,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_guarding_account(sender=sender.address)

        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_unguarding_account(
        self,
        sender: IAccount,
        nonce: int,
        guardian: Address,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_unguarding_account(sender=sender.address, guardian=guardian)

        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction
