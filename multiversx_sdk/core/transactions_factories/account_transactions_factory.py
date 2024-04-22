from typing import Dict, List, Protocol

from multiversx_sdk.core.interfaces import IAddress
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transactions_factories.transaction_builder import \
    TransactionBuilder


class IConfig(Protocol):
    chain_id: str
    min_gas_limit: int
    gas_limit_per_byte: int
    gas_limit_save_key_value: int
    gas_limit_persist_per_byte: int
    gas_limit_store_per_byte: int
    gas_limit_set_guardian: int
    gas_limit_guard_account: int
    gas_limit_unguard_account: int


class AccountTransactionsFactory:
    def __init__(self, config: IConfig) -> None:
        self.config = config

    def create_transaction_for_saving_key_value(
        self,
        sender: IAddress,
        key_value_pairs: Dict[bytes, bytes]
    ) -> Transaction:
        function = "SaveKeyValue"

        extra_gas = self._compute_extra_gas_for_saving_key_value(key_value_pairs)
        data_parts = self._compute_data_parts_for_saving_key_value(key_value_pairs)

        data_parts.insert(0, function)

        return TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=sender,
            data_parts=data_parts,
            gas_limit=extra_gas,
            add_data_movement_gas=True
        ).build()

    def create_transaction_for_setting_guardian(
            self,
            sender: IAddress,
            guardian_address: IAddress,
            service_id: str
    ) -> Transaction:
        data_parts = [
            "SetGuardian",
            guardian_address.to_hex(),
            service_id.encode().hex()
        ]

        return TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=sender,
            data_parts=data_parts,
            gas_limit=self.config.gas_limit_set_guardian,
            add_data_movement_gas=True
        ).build()

    def create_transaction_for_guarding_account(self, sender: IAddress) -> Transaction:
        data_parts = ["GuardAccount"]

        return TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=sender,
            data_parts=data_parts,
            gas_limit=self.config.gas_limit_guard_account,
            add_data_movement_gas=True
        ).build()

    def create_transaction_for_unguarding_account(self, sender: IAddress) -> Transaction:
        data_parts = ["UnGuardAccount"]

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=sender,
            data_parts=data_parts,
            gas_limit=self.config.gas_limit_unguard_account,
            add_data_movement_gas=True
        ).build()
        transaction.options = 2

        return transaction

    def _compute_data_parts_for_saving_key_value(self, key_value_pairs: Dict[bytes, bytes]) -> List[str]:
        data_parts: List[str] = []

        for key, value in key_value_pairs.items():
            data_parts.extend([key.hex(), value.hex()])

        return data_parts

    def _compute_extra_gas_for_saving_key_value(self, key_value_pairs: Dict[bytes, bytes]) -> int:
        extra_gas = 0

        for key, value in key_value_pairs.items():
            extra_gas += self.config.gas_limit_persist_per_byte * (len(key) + len(value)) + self.config.gas_limit_store_per_byte * len(value)

        return extra_gas + self.config.gas_limit_save_key_value
