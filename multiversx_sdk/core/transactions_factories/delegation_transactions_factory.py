from typing import Protocol, Sequence

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.constants import DELEGATION_MANAGER_SC_ADDRESS
from multiversx_sdk.core.errors import ErrListsLengthMismatch
from multiversx_sdk.core.interfaces import IAddress, IValidatorPublicKey
from multiversx_sdk.core.serializer import arg_to_string
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transactions_factories.transaction_builder import \
    TransactionBuilder


class IConfig(Protocol):
    chain_id: str
    min_gas_limit: int
    gas_limit_per_byte: int
    gas_limit_stake: int
    gas_limit_unstake: int
    gas_limit_unbond: int
    gas_limit_create_delegation_contract: int
    gas_limit_delegation_operations: int
    additional_gas_limit_per_validator_node: int
    additional_gas_for_delegation_operations: int


class DelegationTransactionsFactory:
    def __init__(self, config: IConfig) -> None:
        self.config = config

    def create_transaction_for_new_delegation_contract(self,
                                                       sender: IAddress,
                                                       total_delegation_cap: int,
                                                       service_fee: int,
                                                       amount: int) -> Transaction:
        parts = [
            "createNewDelegationContract",
            arg_to_string(total_delegation_cap),
            arg_to_string(service_fee)
        ]

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=Address.new_from_bech32(DELEGATION_MANAGER_SC_ADDRESS),
            data_parts=parts,
            gas_limit=self.config.gas_limit_create_delegation_contract + self.config.additional_gas_for_delegation_operations,
            add_data_movement_gas=True,
            amount=amount
        ).build()

        return transaction

    def create_transaction_for_adding_nodes(self,
                                            sender: IAddress,
                                            delegation_contract: IAddress,
                                            public_keys: Sequence[IValidatorPublicKey],
                                            signed_messages: Sequence[bytes]) -> Transaction:
        if len(public_keys) != len(signed_messages):
            raise ErrListsLengthMismatch("The number of public keys should match the number of signed messages")

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
            add_data_movement_gas=True
        ).build()

        return transaction

    def _compute_execution_gas_limit_for_nodes_management(self, num_nodes: int) -> int:
        return self.config.gas_limit_delegation_operations + num_nodes * self.config.additional_gas_limit_per_validator_node

    def create_transaction_for_removing_nodes(self,
                                              sender: IAddress,
                                              delegation_contract: IAddress,
                                              public_keys: Sequence[IValidatorPublicKey]) -> Transaction:
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
            add_data_movement_gas=True
        ).build()

        return transaction

    def create_transaction_for_staking_nodes(self,
                                             sender: IAddress,
                                             delegation_contract: IAddress,
                                             public_keys: Sequence[IValidatorPublicKey]) -> Transaction:
        num_nodes = len(public_keys)

        parts = ["stakeNodes"]
        for public_key in public_keys:
            parts.append(public_key.hex())

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            gas_limit=self.config.gas_limit_delegation_operations + self.config.gas_limit_stake + num_nodes * self.config.additional_gas_limit_per_validator_node,
            add_data_movement_gas=True
        ).build()

        return transaction

    def create_transaction_for_unbonding_nodes(self,
                                               sender: IAddress,
                                               delegation_contract: IAddress,
                                               public_keys: Sequence[IValidatorPublicKey]) -> Transaction:
        num_nodes = len(public_keys)

        parts = ["unBondNodes"]
        for public_key in public_keys:
            parts.append(public_key.hex())

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            gas_limit=self.config.gas_limit_delegation_operations + self.config.gas_limit_unbond + num_nodes * self.config.additional_gas_limit_per_validator_node,
            add_data_movement_gas=True
        ).build()

        return transaction

    def create_transaction_for_unstaking_nodes(self,
                                               sender: IAddress,
                                               delegation_contract: IAddress,
                                               public_keys: Sequence[IValidatorPublicKey]) -> Transaction:
        num_nodes = len(public_keys)

        parts = ["unStakeNodes"]
        for public_key in public_keys:
            parts.append(public_key.hex())

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            gas_limit=self.config.gas_limit_delegation_operations + self.config.gas_limit_unstake + num_nodes * self.config.additional_gas_limit_per_validator_node,
            add_data_movement_gas=True
        ).build()

        return transaction

    def create_transaction_for_unjailing_nodes(self,
                                               sender: IAddress,
                                               delegation_contract: IAddress,
                                               public_keys: Sequence[IValidatorPublicKey],
                                               amount: int) -> Transaction:
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
            amount=amount
        ).build()

        return transaction

    def create_transaction_for_changing_service_fee(self,
                                                    sender: IAddress,
                                                    delegation_contract: IAddress,
                                                    service_fee: int) -> Transaction:
        parts = [
            "changeServiceFee",
            arg_to_string(service_fee)
        ]

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            gas_limit=self.config.gas_limit_delegation_operations + self.config.additional_gas_for_delegation_operations,
            add_data_movement_gas=True
        ).build()

        return transaction

    def create_transaction_for_modifying_delegation_cap(self,
                                                        sender: IAddress,
                                                        delegation_contract: IAddress,
                                                        delegation_cap: int) -> Transaction:
        parts = [
            "modifyTotalDelegationCap",
            arg_to_string(delegation_cap)
        ]

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            gas_limit=self.config.gas_limit_delegation_operations + self.config.additional_gas_for_delegation_operations,
            add_data_movement_gas=True
        ).build()

        return transaction

    def create_transaction_for_setting_automatic_activation(self,
                                                            sender: IAddress,
                                                            delegation_contract: IAddress) -> Transaction:
        parts = [
            "setAutomaticActivation",
            arg_to_string('true')
        ]

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            gas_limit=self.config.gas_limit_delegation_operations + self.config.additional_gas_for_delegation_operations,
            add_data_movement_gas=True
        ).build()

        return transaction

    def create_transaction_for_unsetting_automatic_activation(self,
                                                              sender: IAddress,
                                                              delegation_contract: IAddress) -> Transaction:
        parts = [
            "setAutomaticActivation",
            arg_to_string('false')
        ]

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            gas_limit=self.config.gas_limit_delegation_operations + self.config.additional_gas_for_delegation_operations,
            add_data_movement_gas=True
        ).build()

        return transaction

    def create_transaction_for_setting_cap_check_on_redelegate_rewards(self,
                                                                       sender: IAddress,
                                                                       delegation_contract: IAddress) -> Transaction:
        parts = [
            "setCheckCapOnReDelegateRewards",
            arg_to_string('true')
        ]

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            gas_limit=self.config.gas_limit_delegation_operations + self.config.additional_gas_for_delegation_operations,
            add_data_movement_gas=True
        ).build()

        return transaction

    def create_transaction_for_unsetting_cap_check_on_redelegate_rewards(self,
                                                                         sender: IAddress,
                                                                         delegation_contract: IAddress) -> Transaction:
        parts = [
            "setCheckCapOnReDelegateRewards",
            arg_to_string('false')
        ]

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            gas_limit=self.config.gas_limit_delegation_operations + self.config.additional_gas_for_delegation_operations,
            add_data_movement_gas=True
        ).build()

        return transaction

    def create_transaction_for_setting_metadata(self,
                                                sender: IAddress,
                                                delegation_contract: IAddress,
                                                name: str,
                                                website: str,
                                                identifier: str) -> Transaction:
        parts = [
            "setMetaData",
            arg_to_string(name),
            arg_to_string(website),
            arg_to_string(identifier)
        ]

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            gas_limit=self.config.gas_limit_delegation_operations + self.config.additional_gas_for_delegation_operations,
            add_data_movement_gas=True
        ).build()

        return transaction

    def create_transaction_for_delegating(self,
                                          sender: IAddress,
                                          delegation_contract: IAddress,
                                          amount: int) -> Transaction:
        return TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=delegation_contract,
            data_parts=["delegate"],
            gas_limit=12000000,
            add_data_movement_gas=False,
            amount=amount
        ).build()

    def create_transaction_for_claiming_rewards(self,
                                                sender: IAddress,
                                                delegation_contract: IAddress) -> Transaction:
        return TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=delegation_contract,
            data_parts=["claimRewards"],
            gas_limit=6000000,
            add_data_movement_gas=False,
            amount=0
        ).build()

    def create_transaction_for_redelegating_rewards(self,
                                                    sender: IAddress,
                                                    delegation_contract: IAddress) -> Transaction:
        return TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=delegation_contract,
            data_parts=["reDelegateRewards"],
            gas_limit=12000000,
            add_data_movement_gas=False,
            amount=0
        ).build()

    def create_transaction_for_undelegating(self,
                                            sender: IAddress,
                                            delegation_contract: IAddress,
                                            amount: int) -> Transaction:
        return TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=delegation_contract,
            data_parts=["unDelegate", arg_to_string(amount)],
            gas_limit=12000000,
            add_data_movement_gas=False,
            amount=0
        ).build()

    def create_transaction_for_withdrawing(self,
                                           sender: IAddress,
                                           delegation_contract: IAddress) -> Transaction:
        return TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=delegation_contract,
            data_parts=["withdraw"],
            gas_limit=12000000,
            add_data_movement_gas=False,
            amount=0
        ).build()
