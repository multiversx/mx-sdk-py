from typing import List, Optional, Protocol, Sequence, Union

from multiversx_sdk_core.address import Address
from multiversx_sdk_core.constants import (
    ARGS_SEPARATOR, DEFAULT_EXTRA_GAS_LIMIT_FOR_GUARDED_TRANSACTION,
    DELEGATION_MANAGER_SC_ADDRESS)
from multiversx_sdk_core.errors import ErrListsLengthMismatch
from multiversx_sdk_core.interfaces import (IAddress, IChainID, IGasLimit,
                                            ITransactionPayload,
                                            IValidatorPublicKey)
from multiversx_sdk_core.serializer import arg_to_string
from multiversx_sdk_core.transaction_intent import TransactionIntent
from multiversx_sdk_core.transaction_payload import TransactionPayload


class IConfig(Protocol):
    chain_id: IChainID
    min_gas_limit: IGasLimit
    gas_limit_per_byte: IGasLimit
    gas_limit_stake: IGasLimit
    gas_limit_unstake: IGasLimit
    gas_limit_unbond: IGasLimit
    gas_limit_create_delegation_contract: IGasLimit
    gas_limit_delegation_operations: IGasLimit
    additional_gas_limit_per_validator_node: IGasLimit
    additional_gas_for_delegation_operations: IGasLimit
    extra_gas_limit_for_guarded_transactions: IGasLimit


class DelegationFactory:
    def __init__(self, config: IConfig) -> None:
        self.config = config

    def create_transaction_intent_for_new_delegation_contract(self,
                                                              sender: IAddress,
                                                              total_delegation_cap: int,
                                                              service_fee: int,
                                                              value: Union[str, int]) -> TransactionIntent:
        parts = [
            "createNewDelegationContract",
            arg_to_string(total_delegation_cap),
            arg_to_string(service_fee)
        ]

        transaction = self._create_transaction_intent(
            sender=sender,
            receiver=Address.from_bech32(DELEGATION_MANAGER_SC_ADDRESS),
            data_parts=parts,
            execution_gas_limit=self.config.gas_limit_create_delegation_contract + self.config.additional_gas_for_delegation_operations,
            value=value
        )

        return transaction

    def create_transaction_intent_for_adding_nodes(self,
                                                   sender: IAddress,
                                                   delegation_contract: IAddress,
                                                   public_keys: Sequence[IValidatorPublicKey],
                                                   signed_messages: List[bytes]) -> TransactionIntent:
        if len(public_keys) != len(signed_messages):
            raise ErrListsLengthMismatch("The number of public keys should match the number of signed messages")

        parts = ["addNodes"]
        for i in range(len(public_keys)):
            parts.append(public_keys[i].hex())
            parts.append(signed_messages[i].hex())

        num_nodes = len(public_keys)

        transaction = self._create_transaction_intent(
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            execution_gas_limit=self._compute_execution_gas_limit_for_nodes_management(num_nodes)
        )
        return transaction

    def _compute_execution_gas_limit_for_nodes_management(self, num_nodes: int) -> IGasLimit:
        return self.config.gas_limit_delegation_operations + num_nodes * self.config.additional_gas_limit_per_validator_node

    def create_transaction_intent_for_removing_nodes(self,
                                                     sender: IAddress,
                                                     delegation_contract: IAddress,
                                                     public_keys: Sequence[IValidatorPublicKey]) -> TransactionIntent:
        num_nodes = len(public_keys)

        parts: List[str] = ["removeNodes"]
        for public_key in public_keys:
            parts.append(public_key.hex())

        transaction = self._create_transaction_intent(
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            execution_gas_limit=self._compute_execution_gas_limit_for_nodes_management(num_nodes)
        )

        return transaction

    def create_transaction_intent_for_staking_nodes(self,
                                                    sender: IAddress,
                                                    delegation_contract: IAddress,
                                                    public_keys: Sequence[IValidatorPublicKey]) -> TransactionIntent:
        num_nodes = len(public_keys)

        parts = ["stakeNodes"]
        for public_key in public_keys:
            parts.append(public_key.hex())

        transaction = self._create_transaction_intent(
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            execution_gas_limit=self.config.gas_limit_delegation_operations + self.config.gas_limit_stake + num_nodes * self.config.additional_gas_limit_per_validator_node
        )

        return transaction

    def create_transaction_intent_for_unbonding_nodes(self,
                                                      sender: IAddress,
                                                      delegation_contract: IAddress,
                                                      public_keys: Sequence[IValidatorPublicKey]) -> TransactionIntent:
        num_nodes = len(public_keys)

        parts = ["unBondNodes"]
        for public_key in public_keys:
            parts.append(public_key.hex())

        transaction = self._create_transaction_intent(
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            execution_gas_limit=self.config.gas_limit_delegation_operations + self.config.gas_limit_unbond + num_nodes * self.config.additional_gas_limit_per_validator_node
        )

        return transaction

    def create_transaction_intent_for_unstaking_nodes(self,
                                                      sender: IAddress,
                                                      delegation_contract: IAddress,
                                                      public_keys: Sequence[IValidatorPublicKey]) -> TransactionIntent:
        num_nodes = len(public_keys)

        parts = ["unStakeNodes"]
        for public_key in public_keys:
            parts.append(public_key.hex())

        transaction = self._create_transaction_intent(
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            execution_gas_limit=self.config.gas_limit_delegation_operations + self.config.gas_limit_unstake + num_nodes * self.config.additional_gas_limit_per_validator_node
        )

        return transaction

    def create_transaction_intent_for_unjailing_nodes(self,
                                                      sender: IAddress,
                                                      delegation_contract: IAddress,
                                                      public_keys: Sequence[IValidatorPublicKey]) -> TransactionIntent:
        num_nodes = len(public_keys)

        parts = ["unJailNodes"]
        for public_key in public_keys:
            parts.append(public_key.hex())

        transaction = self._create_transaction_intent(
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            execution_gas_limit=self._compute_execution_gas_limit_for_nodes_management(num_nodes)
        )

        return transaction

    def create_transaction_intent_for_changing_service_fee(self,
                                                           sender: IAddress,
                                                           delegation_contract: IAddress,
                                                           service_fee: int) -> TransactionIntent:
        parts = [
            "changeServiceFee",
            arg_to_string(service_fee)
        ]

        transaction = self._create_transaction_intent(
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            execution_gas_limit=self.config.gas_limit_delegation_operations + self.config.additional_gas_for_delegation_operations
        )

        return transaction

    def create_transaction_intent_for_modifying_delegation_cap(self,
                                                               sender: IAddress,
                                                               delegation_contract: IAddress,
                                                               delegation_cap: int) -> TransactionIntent:
        parts = [
            "modifyTotalDelegationCap",
            arg_to_string(delegation_cap)
        ]

        transaction = self._create_transaction_intent(
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            execution_gas_limit=self.config.gas_limit_delegation_operations + self.config.additional_gas_for_delegation_operations
        )

        return transaction

    def create_transaction_intent_for_setting_automatic_activation(self,
                                                                   sender: IAddress,
                                                                   delegation_contract: IAddress) -> TransactionIntent:
        parts = [
            "setAutomaticActivation",
            arg_to_string('true')
        ]

        transaction = self._create_transaction_intent(
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            execution_gas_limit=self.config.gas_limit_delegation_operations + self.config.additional_gas_for_delegation_operations
        )

        return transaction

    def create_transaction_intent_for_unsetting_automatic_activation(self,
                                                                     sender: IAddress,
                                                                     delegation_contract: IAddress) -> TransactionIntent:
        parts = [
            "setAutomaticActivation",
            arg_to_string('false')
        ]

        transaction = self._create_transaction_intent(
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            execution_gas_limit=self.config.gas_limit_delegation_operations + self.config.additional_gas_for_delegation_operations
        )

        return transaction

    def create_transaction_intent_for_setting_cap_check_on_redelegate_rewards(self,
                                                                              sender: IAddress,
                                                                              delegation_contract: IAddress) -> TransactionIntent:
        parts = [
            "setCheckCapOnReDelegateRewards",
            arg_to_string('true')
        ]

        transaction = self._create_transaction_intent(
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            execution_gas_limit=self.config.gas_limit_delegation_operations + self.config.additional_gas_for_delegation_operations
        )

        return transaction

    def create_transaction_intent_for_unsetting_cap_check_on_redelegate_rewards(self,
                                                                                sender: IAddress,
                                                                                delegation_contract: IAddress) -> TransactionIntent:
        parts = [
            "setCheckCapOnReDelegateRewards",
            arg_to_string('false')
        ]

        transaction = self._create_transaction_intent(
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            execution_gas_limit=self.config.gas_limit_delegation_operations + self.config.additional_gas_for_delegation_operations
        )

        return transaction

    def create_transaction_intent_for_setting_metadata(self,
                                                       sender: IAddress,
                                                       delegation_contract: IAddress,
                                                       name: str,
                                                       website: str,
                                                       identifier: str) -> TransactionIntent:
        parts = [
            "setMetaData",
            arg_to_string(name),
            arg_to_string(website),
            arg_to_string(identifier)
        ]

        transaction = self._create_transaction_intent(
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            execution_gas_limit=self.config.gas_limit_delegation_operations + self.config.additional_gas_for_delegation_operations
        )

        return transaction

    def _compute_gas_limit(self, payload: ITransactionPayload, execution_gas: IGasLimit) -> IGasLimit:
        data_movement_gas = self.config.min_gas_limit + self.config.gas_limit_per_byte * payload.length()
        gas = data_movement_gas + execution_gas

        # add by default extra gas for guarded transactions
        gas += DEFAULT_EXTRA_GAS_LIMIT_FOR_GUARDED_TRANSACTION

        return gas

    def _create_transaction_intent(
            self,
            sender: IAddress,
            receiver: IAddress,
            data_parts: List[str],
            execution_gas_limit: IGasLimit,
            value: Optional[Union[str, int]] = None) -> TransactionIntent:
        data = self._build_transaction_payload(data_parts)
        gas_limit = self._compute_gas_limit(data, execution_gas_limit)

        transaction_intent = TransactionIntent()

        transaction_intent.sender = sender.bech32()
        transaction_intent.receiver = receiver.bech32()
        transaction_intent.gas_limit = gas_limit
        transaction_intent.data = str(data).encode()
        transaction_intent.value = str(value) if value else "0"

        return transaction_intent

    def _build_transaction_payload(self, parts: List[str]) -> TransactionPayload:
        data = ARGS_SEPARATOR.join(parts)
        return TransactionPayload.from_str(data)
