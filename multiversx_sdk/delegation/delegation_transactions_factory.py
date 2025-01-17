from typing import Sequence

from multiversx_sdk.abi import Serializer
from multiversx_sdk.abi.biguint_value import BigUIntValue
from multiversx_sdk.abi.string_value import StringValue
from multiversx_sdk.builders.transaction_builder import TransactionBuilder
from multiversx_sdk.core import Address, Transaction
from multiversx_sdk.core.constants import DELEGATION_MANAGER_SC_ADDRESS_HEX
from multiversx_sdk.core.transactions_factory_config import TransactionsFactoryConfig
from multiversx_sdk.delegation.errors import ListsLengthMismatchError
from multiversx_sdk.wallet.validator_keys import ValidatorPublicKey


class DelegationTransactionsFactory:
    def __init__(self, config: TransactionsFactoryConfig) -> None:
        self.config = config
        self.serializer = Serializer()

    def create_transaction_for_new_delegation_contract(
        self, sender: Address, total_delegation_cap: int, service_fee: int, amount: int
    ) -> Transaction:
        parts = ["createNewDelegationContract"]

        serialized_parts = self.serializer.serialize_to_parts(
            [BigUIntValue(total_delegation_cap), BigUIntValue(service_fee)]
        )

        parts.extend([part.hex() for part in serialized_parts])

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=Address.new_from_hex(DELEGATION_MANAGER_SC_ADDRESS_HEX),
            data_parts=parts,
            gas_limit=self.config.gas_limit_create_delegation_contract
            + self.config.additional_gas_for_delegation_operations,
            add_data_movement_gas=True,
            amount=amount,
        ).build()

        return transaction

    def create_transaction_for_adding_nodes(
        self,
        sender: Address,
        delegation_contract: Address,
        public_keys: Sequence[ValidatorPublicKey],
        signed_messages: Sequence[bytes],
    ) -> Transaction:
        if len(public_keys) != len(signed_messages):
            raise ListsLengthMismatchError("The number of public keys should match the number of signed messages")

        parts = ["addNodes"]
        for i in range(len(public_keys)):
            parts.append(public_keys[i].hex())
            parts.append(signed_messages[i].hex())

        num_nodes = len(public_keys)

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            gas_limit=self._compute_execution_gas_limit_for_nodes_management(num_nodes),
            add_data_movement_gas=True,
        ).build()

        return transaction

    def _compute_execution_gas_limit_for_nodes_management(self, num_nodes: int) -> int:
        return (
            self.config.gas_limit_delegation_operations
            + num_nodes * self.config.additional_gas_limit_per_validator_node
        )

    def create_transaction_for_removing_nodes(
        self,
        sender: Address,
        delegation_contract: Address,
        public_keys: Sequence[ValidatorPublicKey],
    ) -> Transaction:
        num_nodes = len(public_keys)

        parts = ["removeNodes"]
        for public_key in public_keys:
            parts.append(public_key.hex())

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            gas_limit=self._compute_execution_gas_limit_for_nodes_management(num_nodes),
            add_data_movement_gas=True,
        ).build()

        return transaction

    def create_transaction_for_staking_nodes(
        self,
        sender: Address,
        delegation_contract: Address,
        public_keys: Sequence[ValidatorPublicKey],
    ) -> Transaction:
        num_nodes = len(public_keys)

        parts = ["stakeNodes"]
        for public_key in public_keys:
            parts.append(public_key.hex())

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            gas_limit=self.config.gas_limit_delegation_operations
            + self.config.gas_limit_stake
            + num_nodes * self.config.additional_gas_limit_per_validator_node,
            add_data_movement_gas=True,
        ).build()

        return transaction

    def create_transaction_for_unbonding_nodes(
        self,
        sender: Address,
        delegation_contract: Address,
        public_keys: Sequence[ValidatorPublicKey],
    ) -> Transaction:
        num_nodes = len(public_keys)

        parts = ["unBondNodes"]
        for public_key in public_keys:
            parts.append(public_key.hex())

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            gas_limit=self.config.gas_limit_delegation_operations
            + self.config.gas_limit_unbond
            + num_nodes * self.config.additional_gas_limit_per_validator_node,
            add_data_movement_gas=True,
        ).build()

        return transaction

    def create_transaction_for_unstaking_nodes(
        self,
        sender: Address,
        delegation_contract: Address,
        public_keys: Sequence[ValidatorPublicKey],
    ) -> Transaction:
        num_nodes = len(public_keys)

        parts = ["unStakeNodes"]
        for public_key in public_keys:
            parts.append(public_key.hex())

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            gas_limit=self.config.gas_limit_delegation_operations
            + self.config.gas_limit_unstake
            + num_nodes * self.config.additional_gas_limit_per_validator_node,
            add_data_movement_gas=True,
        ).build()

        return transaction

    def create_transaction_for_unjailing_nodes(
        self,
        sender: Address,
        delegation_contract: Address,
        public_keys: Sequence[ValidatorPublicKey],
        amount: int,
    ) -> Transaction:
        num_nodes = len(public_keys)

        parts = ["unJailNodes"]
        for public_key in public_keys:
            parts.append(public_key.hex())

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            gas_limit=self._compute_execution_gas_limit_for_nodes_management(num_nodes),
            add_data_movement_gas=True,
            amount=amount,
        ).build()

        return transaction

    def create_transaction_for_changing_service_fee(
        self, sender: Address, delegation_contract: Address, service_fee: int
    ) -> Transaction:
        parts = [
            "changeServiceFee",
            self.serializer.serialize([BigUIntValue(service_fee)]),
        ]

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            gas_limit=self.config.gas_limit_delegation_operations
            + self.config.additional_gas_for_delegation_operations,
            add_data_movement_gas=True,
        ).build()

        return transaction

    def create_transaction_for_modifying_delegation_cap(
        self, sender: Address, delegation_contract: Address, delegation_cap: int
    ) -> Transaction:
        parts = [
            "modifyTotalDelegationCap",
            self.serializer.serialize([BigUIntValue(delegation_cap)]),
        ]

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            gas_limit=self.config.gas_limit_delegation_operations
            + self.config.additional_gas_for_delegation_operations,
            add_data_movement_gas=True,
        ).build()

        return transaction

    def create_transaction_for_setting_automatic_activation(
        self, sender: Address, delegation_contract: Address
    ) -> Transaction:
        parts = [
            "setAutomaticActivation",
            self.serializer.serialize([StringValue("true")]),
        ]

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            gas_limit=self.config.gas_limit_delegation_operations
            + self.config.additional_gas_for_delegation_operations,
            add_data_movement_gas=True,
        ).build()

        return transaction

    def create_transaction_for_unsetting_automatic_activation(
        self, sender: Address, delegation_contract: Address
    ) -> Transaction:
        parts = [
            "setAutomaticActivation",
            self.serializer.serialize([StringValue("false")]),
        ]

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            gas_limit=self.config.gas_limit_delegation_operations
            + self.config.additional_gas_for_delegation_operations,
            add_data_movement_gas=True,
        ).build()

        return transaction

    def create_transaction_for_setting_cap_check_on_redelegate_rewards(
        self, sender: Address, delegation_contract: Address
    ) -> Transaction:
        parts = [
            "setCheckCapOnReDelegateRewards",
            self.serializer.serialize([StringValue("true")]),
        ]

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            gas_limit=self.config.gas_limit_delegation_operations
            + self.config.additional_gas_for_delegation_operations,
            add_data_movement_gas=True,
        ).build()

        return transaction

    def create_transaction_for_unsetting_cap_check_on_redelegate_rewards(
        self, sender: Address, delegation_contract: Address
    ) -> Transaction:
        parts = [
            "setCheckCapOnReDelegateRewards",
            self.serializer.serialize([StringValue("false")]),
        ]

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            gas_limit=self.config.gas_limit_delegation_operations
            + self.config.additional_gas_for_delegation_operations,
            add_data_movement_gas=True,
        ).build()

        return transaction

    def create_transaction_for_setting_metadata(
        self,
        sender: Address,
        delegation_contract: Address,
        name: str,
        website: str,
        identifier: str,
    ) -> Transaction:
        parts = ["setMetaData"]

        serialized_parts = self.serializer.serialize_to_parts(
            [StringValue(name), StringValue(website), StringValue(identifier)]
        )

        parts.extend([part.hex() for part in serialized_parts])

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            gas_limit=self.config.gas_limit_delegation_operations
            + self.config.additional_gas_for_delegation_operations,
            add_data_movement_gas=True,
        ).build()

        return transaction

    def create_transaction_for_delegating(
        self, sender: Address, delegation_contract: Address, amount: int
    ) -> Transaction:
        return TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=delegation_contract,
            data_parts=["delegate"],
            gas_limit=12000000,
            add_data_movement_gas=False,
            amount=amount,
        ).build()

    def create_transaction_for_claiming_rewards(self, sender: Address, delegation_contract: Address) -> Transaction:
        return TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=delegation_contract,
            data_parts=["claimRewards"],
            gas_limit=6000000,
            add_data_movement_gas=False,
            amount=0,
        ).build()

    def create_transaction_for_redelegating_rewards(self, sender: Address, delegation_contract: Address) -> Transaction:
        return TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=delegation_contract,
            data_parts=["reDelegateRewards"],
            gas_limit=12000000,
            add_data_movement_gas=False,
            amount=0,
        ).build()

    def create_transaction_for_undelegating(
        self, sender: Address, delegation_contract: Address, amount: int
    ) -> Transaction:
        return TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=delegation_contract,
            data_parts=[
                "unDelegate",
                self.serializer.serialize([BigUIntValue(amount)]),
            ],
            gas_limit=12000000,
            add_data_movement_gas=False,
            amount=0,
        ).build()

    def create_transaction_for_withdrawing(self, sender: Address, delegation_contract: Address) -> Transaction:
        return TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=delegation_contract,
            data_parts=["withdraw"],
            gas_limit=12000000,
            add_data_movement_gas=False,
            amount=0,
        ).build()
