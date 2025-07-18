from typing import Optional

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.base_factory import BaseFactory
from multiversx_sdk.core.constants import TRANSACTION_OPTIONS_TX_GUARDED
from multiversx_sdk.core.interfaces import IGasLimitEstimator
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transactions_factory_config import TransactionsFactoryConfig


class AccountTransactionsFactory(BaseFactory):
    def __init__(
        self,
        config: TransactionsFactoryConfig,
        gas_limit_estimator: Optional[IGasLimitEstimator] = None,
    ) -> None:
        super().__init__(config, gas_limit_estimator)
        self.config = config

    def create_transaction_for_saving_key_value(
        self, sender: Address, key_value_pairs: dict[bytes, bytes]
    ) -> Transaction:
        function = "SaveKeyValue"

        extra_gas = self._compute_extra_gas_for_saving_key_value(key_value_pairs)
        data_parts = self._compute_data_parts_for_saving_key_value(key_value_pairs)

        data_parts.insert(0, function)

        transaction = Transaction(
            sender=sender,
            receiver=sender,
            gas_limit=0,
            chain_id=self.config.chain_id,
        )

        self.set_payload(transaction, data_parts)
        self.set_gas_limit(transaction=transaction, config_gas_limit=extra_gas)

        return transaction

    def create_transaction_for_setting_guardian(
        self, sender: Address, guardian_address: Address, service_id: str
    ) -> Transaction:
        data_parts = [
            "SetGuardian",
            guardian_address.to_hex(),
            service_id.encode().hex(),
        ]

        transaction = Transaction(
            sender=sender,
            receiver=sender,
            gas_limit=0,
            chain_id=self.config.chain_id,
        )

        self.set_payload(transaction, data_parts)
        self.set_gas_limit(transaction=transaction, config_gas_limit=self.config.gas_limit_set_guardian)

        return transaction

    def create_transaction_for_guarding_account(self, sender: Address) -> Transaction:
        data_parts = ["GuardAccount"]

        transaction = Transaction(
            sender=sender,
            receiver=sender,
            gas_limit=0,
            chain_id=self.config.chain_id,
        )

        self.set_payload(transaction, data_parts)
        self.set_gas_limit(transaction=transaction, config_gas_limit=self.config.gas_limit_guard_account)

        return transaction

    def create_transaction_for_unguarding_account(
        self,
        sender: Address,
        guardian: Optional[Address] = None,
    ) -> Transaction:
        data_parts = ["UnGuardAccount"]

        transaction = Transaction(
            sender=sender,
            receiver=sender,
            gas_limit=0,
            chain_id=self.config.chain_id,
        )

        if guardian:
            transaction.guardian = guardian
            transaction.options = TRANSACTION_OPTIONS_TX_GUARDED

        self.set_payload(transaction, data_parts)
        self.set_gas_limit(transaction=transaction, config_gas_limit=self.config.gas_limit_unguard_account)

        return transaction

    def _compute_data_parts_for_saving_key_value(self, key_value_pairs: dict[bytes, bytes]) -> list[str]:
        data_parts: list[str] = []

        for key, value in key_value_pairs.items():
            data_parts.extend([key.hex(), value.hex()])

        return data_parts

    def _compute_extra_gas_for_saving_key_value(self, key_value_pairs: dict[bytes, bytes]) -> int:
        extra_gas = 0

        for key, value in key_value_pairs.items():
            extra_gas += self.config.gas_limit_persist_per_byte * (
                len(key) + len(value)
            ) + self.config.gas_limit_store_per_byte * len(value)

        return extra_gas + self.config.gas_limit_save_key_value
