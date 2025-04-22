from pathlib import Path
from typing import Optional, Union

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.base_controller import BaseController
from multiversx_sdk.core.interfaces import IAccount
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transactions_factory_config import TransactionsFactoryConfig
from multiversx_sdk.validators.validators_signers import ValidatorsSigners
from multiversx_sdk.validators.validators_transactions_factory import (
    ValidatorsTransactionsFactory,
)
from multiversx_sdk.wallet.validator_keys import ValidatorPublicKey


class ValidatorsController(BaseController):
    def __init__(self, chain_id: str) -> None:
        self.factory = ValidatorsTransactionsFactory(TransactionsFactoryConfig(chain_id))

    def create_transaction_for_staking(
        self,
        sender: IAccount,
        nonce: int,
        validators_file: Union[Path, ValidatorsSigners],
        amount: int,
        rewards_address: Optional[Address] = None,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_staking(
            sender=sender.address,
            validators_file=validators_file,
            amount=amount,
            rewards_address=rewards_address,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_topping_up(
        self,
        sender: IAccount,
        nonce: int,
        amount: int,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_topping_up(
            sender=sender.address,
            amount=amount,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_unstaking(
        self,
        sender: IAccount,
        nonce: int,
        public_keys: list[ValidatorPublicKey],
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_unstaking(
            sender=sender.address,
            public_keys=public_keys,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_unjailing(
        self,
        sender: IAccount,
        nonce: int,
        public_keys: list[ValidatorPublicKey],
        amount: int,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_unjailing(
            sender=sender.address,
            public_keys=public_keys,
            amount=amount,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_unbonding(
        self,
        sender: IAccount,
        nonce: int,
        public_keys: list[ValidatorPublicKey],
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_unbonding(
            sender=sender.address,
            public_keys=public_keys,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_changing_rewards_address(
        self,
        sender: IAccount,
        nonce: int,
        rewards_address: Address,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_changing_rewards_address(
            sender=sender.address,
            rewards_address=rewards_address,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_claiming(
        self,
        sender: IAccount,
        nonce: int,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_claiming(
            sender=sender.address,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_unstaking_nodes(
        self,
        sender: IAccount,
        nonce: int,
        public_keys: list[ValidatorPublicKey],
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_unstaking_nodes(
            sender=sender.address,
            public_keys=public_keys,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_unstaking_tokens(
        self,
        sender: IAccount,
        nonce: int,
        amount: int,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_unstaking_tokens(
            sender=sender.address,
            amount=amount,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_unbonding_nodes(
        self,
        sender: IAccount,
        nonce: int,
        public_keys: list[ValidatorPublicKey],
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_unbonding_nodes(
            sender=sender.address,
            public_keys=public_keys,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_unbonding_tokens(
        self,
        sender: IAccount,
        nonce: int,
        amount: int,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_unbonding_tokens(
            sender=sender.address,
            amount=amount,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_cleaning_registered_data(
        self,
        sender: IAccount,
        nonce: int,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_cleaning_registered_data(
            sender=sender.address,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_restaking_unstaked_nodes(
        self,
        sender: IAccount,
        nonce: int,
        public_keys: list[ValidatorPublicKey],
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_restaking_unstaked_nodes(
            sender=sender.address,
            public_keys=public_keys,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction
