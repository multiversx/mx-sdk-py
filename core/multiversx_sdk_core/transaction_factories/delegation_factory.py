from typing import List, Optional, Protocol, Sequence

from multiversx_sdk_core import TransactionPayload
from multiversx_sdk_core.constants import (ARGS_SEPARATOR,
                                           TRANSACTION_OPTIONS_DEFAULT,
                                           TRANSACTION_VERSION_DEFAULT)
from multiversx_sdk_core.errors import ErrListsLengthMismatch
from multiversx_sdk_core.interfaces import (IAddress, IChainID, IGasLimit,
                                            IGasPrice, INonce, ISignature,
                                            ITransactionPayload,
                                            ITransactionValue,
                                            IValidatorPublicKey)
from multiversx_sdk_core.serializer import arg_to_string
from multiversx_sdk_core.transaction import Transaction


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

    def create_new_delegation_contract_transaction(self,
                                                   sender: IAddress,
                                                   receiver: IAddress,
                                                   total_delegation_cap: int,
                                                   service_fee: int,
                                                   value: ITransactionValue,
                                                   transaction_nonce: Optional[INonce] = None,
                                                   guardian: Optional[IAddress] = None,
                                                   gas_price: Optional[IGasPrice] = None,
                                                   gas_limit: Optional[IGasLimit] = None) -> Transaction:
        parts = [
            "createNewDelegationContract",
            arg_to_string(total_delegation_cap),
            arg_to_string(service_fee)
        ]

        transaction = self.create_transaction(
            sender=sender,
            receiver=receiver,
            data_parts=parts,
            execution_gas_limit=self.config.gas_limit_create_delegation_contract + self.config.additional_gas_for_delegation_operations,
            gas_limit_hint=gas_limit,
            gas_price=gas_price,
            nonce=transaction_nonce,
            value=value,
            guardian=guardian
        )

        return transaction

    def create_add_nodes_transaction(self,
                                     sender: IAddress,
                                     delegation_contract: IAddress,
                                     public_keys: Sequence[IValidatorPublicKey],
                                     signed_messages: Sequence[ISignature],
                                     value: Optional[ITransactionValue] = None,
                                     guardian: Optional[IAddress] = None,
                                     transaction_nonce: Optional[INonce] = None,
                                     gas_price: Optional[IGasPrice] = None,
                                     gas_limit: Optional[IGasLimit] = None) -> Transaction:
        if len(public_keys) != len(signed_messages):
            raise ErrListsLengthMismatch("The number of public keys should match the number of signed messages")

        parts = ["addNodes"]
        for i in range(len(public_keys)):
            parts.append(public_keys[i].hex())
            parts.append(signed_messages[i].hex())

        num_nodes = len(public_keys)

        transaction = self.create_transaction(
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            execution_gas_limit=self._compute_execution_gas_limit_for_nodes_management(num_nodes),
            gas_limit_hint=gas_limit,
            gas_price=gas_price,
            nonce=transaction_nonce,
            value=value,
            guardian=guardian
        )
        return transaction

    def _compute_execution_gas_limit_for_nodes_management(self, num_nodes: int) -> IGasLimit:
        return self.config.gas_limit_delegation_operations + num_nodes * self.config.additional_gas_limit_per_validator_node

    def create_remove_nodes_transaction(self,
                                        sender: IAddress,
                                        delegation_contract: IAddress,
                                        bls_keys: List[str],
                                        value: Optional[ITransactionValue] = None,
                                        guardian: Optional[IAddress] = None,
                                        transaction_nonce: Optional[INonce] = None,
                                        gas_price: Optional[IGasPrice] = None,
                                        gas_limit: Optional[IGasLimit] = None) -> Transaction:
        num_nodes = len(bls_keys)

        parts: List[str] = ["removeNodes"]
        parts.extend(bls_keys)

        transaction = self.create_transaction(
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            execution_gas_limit=self._compute_execution_gas_limit_for_nodes_management(num_nodes),
            gas_limit_hint=gas_limit,
            gas_price=gas_price,
            nonce=transaction_nonce,
            value=value,
            guardian=guardian
        )

        return transaction

    def create_stake_nodes_transaction(self,
                                       sender: IAddress,
                                       delegation_contract: IAddress,
                                       bls_keys: List[str],
                                       value: Optional[ITransactionValue] = None,
                                       guardian: Optional[IAddress] = None,
                                       transaction_nonce: Optional[INonce] = None,
                                       gas_price: Optional[IGasPrice] = None,
                                       gas_limit: Optional[IGasLimit] = None) -> Transaction:
        num_nodes = len(bls_keys)

        parts = ["stakeNodes"]
        parts.extend(bls_keys)

        transaction = self.create_transaction(
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            execution_gas_limit=self.config.gas_limit_delegation_operations + self.config.gas_limit_stake + num_nodes * self.config.additional_gas_limit_per_validator_node,
            gas_limit_hint=gas_limit,
            gas_price=gas_price,
            nonce=transaction_nonce,
            value=value,
            guardian=guardian
        )

        return transaction

    def create_unbond_nodes_transaction(self,
                                        sender: IAddress,
                                        delegation_contract: IAddress,
                                        bls_keys: List[str],
                                        value: Optional[ITransactionValue] = None,
                                        guardian: Optional[IAddress] = None,
                                        transaction_nonce: Optional[INonce] = None,
                                        gas_price: Optional[IGasPrice] = None,
                                        gas_limit: Optional[IGasLimit] = None) -> Transaction:
        num_nodes = len(bls_keys)

        parts = ["unBondNodes"]
        parts.extend(bls_keys)

        transaction = self.create_transaction(
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            execution_gas_limit=self.config.gas_limit_delegation_operations + self.config.gas_limit_unbond + num_nodes * self.config.additional_gas_limit_per_validator_node,
            gas_limit_hint=gas_limit,
            gas_price=gas_price,
            nonce=transaction_nonce,
            value=value,
            guardian=guardian
        )

        return transaction

    def create_unstake_nodes_transaction(self,
                                         sender: IAddress,
                                         delegation_contract: IAddress,
                                         bls_keys: List[str],
                                         value: Optional[ITransactionValue] = None,
                                         guardian: Optional[IAddress] = None,
                                         transaction_nonce: Optional[INonce] = None,
                                         gas_price: Optional[IGasPrice] = None,
                                         gas_limit: Optional[IGasLimit] = None) -> Transaction:
        num_nodes = len(bls_keys)

        parts = ["unStakeNodes"]
        parts.extend(bls_keys)

        transaction = self.create_transaction(
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            execution_gas_limit=self.config.gas_limit_delegation_operations + self.config.gas_limit_unstake + num_nodes * self.config.additional_gas_limit_per_validator_node,
            gas_limit_hint=gas_limit,
            gas_price=gas_price,
            nonce=transaction_nonce,
            value=value,
            guardian=guardian
        )

        return transaction

    def create_unjail_nodes_transaction(self,
                                        sender: IAddress,
                                        delegation_contract: IAddress,
                                        bls_keys: List[str],
                                        value: Optional[ITransactionValue] = None,
                                        guardian: Optional[IAddress] = None,
                                        transaction_nonce: Optional[INonce] = None,
                                        gas_price: Optional[IGasPrice] = None,
                                        gas_limit: Optional[IGasLimit] = None) -> Transaction:
        num_nodes = len(bls_keys)

        parts = ["unJailNodes"]
        parts.extend(bls_keys)

        transaction = self.create_transaction(
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            execution_gas_limit=self._compute_execution_gas_limit_for_nodes_management(num_nodes),
            gas_limit_hint=gas_limit,
            gas_price=gas_price,
            nonce=transaction_nonce,
            value=value,
            guardian=guardian
        )

        return transaction

    def create_change_service_fee_transaction(self,
                                              sender: IAddress,
                                              delegation_contract: IAddress,
                                              service_fee: int,
                                              value: Optional[ITransactionValue] = None,
                                              guardian: Optional[IAddress] = None,
                                              transaction_nonce: Optional[INonce] = None,
                                              gas_price: Optional[IGasPrice] = None,
                                              gas_limit: Optional[IGasLimit] = None) -> Transaction:
        parts = [
            "changeServiceFee",
            arg_to_string(service_fee)
        ]

        transaction = self.create_transaction(
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            execution_gas_limit=self.config.gas_limit_delegation_operations + self.config.additional_gas_for_delegation_operations,
            gas_limit_hint=gas_limit,
            gas_price=gas_price,
            nonce=transaction_nonce,
            value=value,
            guardian=guardian
        )

        return transaction

    def create_modify_delegation_cap_transaction(self,
                                                 sender: IAddress,
                                                 delegation_contract: IAddress,
                                                 delegation_cap: int,
                                                 value: Optional[ITransactionValue] = None,
                                                 guardian: Optional[IAddress] = None,
                                                 transaction_nonce: Optional[INonce] = None,
                                                 gas_price: Optional[IGasPrice] = None,
                                                 gas_limit: Optional[IGasLimit] = None) -> Transaction:
        parts = [
            "modifyTotalDelegationCap",
            arg_to_string(delegation_cap)
        ]

        transaction = self.create_transaction(
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            execution_gas_limit=self.config.gas_limit_delegation_operations + self.config.additional_gas_for_delegation_operations,
            gas_limit_hint=gas_limit,
            gas_price=gas_price,
            nonce=transaction_nonce,
            value=value,
            guardian=guardian
        )

        return transaction

    def create_set_automatic_activation_transaction(self,
                                                    sender: IAddress,
                                                    delegation_contract: IAddress,
                                                    value: Optional[ITransactionValue] = None,
                                                    guardian: Optional[IAddress] = None,
                                                    transaction_nonce: Optional[INonce] = None,
                                                    gas_price: Optional[IGasPrice] = None,
                                                    gas_limit: Optional[IGasLimit] = None) -> Transaction:
        parts = [
            "setAutomaticActivation",
            arg_to_string('true')
        ]

        transaction = self.create_transaction(
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            execution_gas_limit=self.config.gas_limit_delegation_operations + self.config.additional_gas_for_delegation_operations,
            gas_limit_hint=gas_limit,
            gas_price=gas_price,
            nonce=transaction_nonce,
            value=value,
            guardian=guardian
        )

        return transaction

    def create_unset_automatic_activation_transaction(self,
                                                      sender: IAddress,
                                                      delegation_contract: IAddress,
                                                      value: Optional[ITransactionValue] = None,
                                                      guardian: Optional[IAddress] = None,
                                                      transaction_nonce: Optional[INonce] = None,
                                                      gas_price: Optional[IGasPrice] = None,
                                                      gas_limit: Optional[IGasLimit] = None) -> Transaction:
        parts = [
            "setAutomaticActivation",
            arg_to_string('false')
        ]

        transaction = self.create_transaction(
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            execution_gas_limit=self.config.gas_limit_delegation_operations + self.config.additional_gas_for_delegation_operations,
            gas_limit_hint=gas_limit,
            gas_price=gas_price,
            nonce=transaction_nonce,
            value=value,
            guardian=guardian
        )

        return transaction

    def create_set_redelegate_cap_transaction(self,
                                              sender: IAddress,
                                              delegation_contract: IAddress,
                                              value: Optional[ITransactionValue] = None,
                                              guardian: Optional[IAddress] = None,
                                              transaction_nonce: Optional[INonce] = None,
                                              gas_price: Optional[IGasPrice] = None,
                                              gas_limit: Optional[IGasLimit] = None) -> Transaction:
        parts = [
            "setCheckCapOnReDelegateRewards",
            arg_to_string('true')
        ]

        transaction = self.create_transaction(
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            execution_gas_limit=self.config.gas_limit_delegation_operations + self.config.additional_gas_for_delegation_operations,
            gas_limit_hint=gas_limit,
            gas_price=gas_price,
            nonce=transaction_nonce,
            value=value,
            guardian=guardian
        )

        return transaction

    def create_unset_redelegate_cap_transaction(self,
                                                sender: IAddress,
                                                delegation_contract: IAddress,
                                                value: Optional[ITransactionValue] = None,
                                                guardian: Optional[IAddress] = None,
                                                transaction_nonce: Optional[INonce] = None,
                                                gas_price: Optional[IGasPrice] = None,
                                                gas_limit: Optional[IGasLimit] = None) -> Transaction:
        parts = [
            "setCheckCapOnReDelegateRewards",
            arg_to_string('false')
        ]

        transaction = self.create_transaction(
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            execution_gas_limit=self.config.gas_limit_delegation_operations + self.config.additional_gas_for_delegation_operations,
            gas_limit_hint=gas_limit,
            gas_price=gas_price,
            nonce=transaction_nonce,
            value=value,
            guardian=guardian
        )

        return transaction

    def create_set_metadata_transaction(self,
                                        sender: IAddress,
                                        delegation_contract: IAddress,
                                        name: str,
                                        website: str,
                                        identifier: str,
                                        value: Optional[ITransactionValue] = None,
                                        guardian: Optional[IAddress] = None,
                                        transaction_nonce: Optional[INonce] = None,
                                        gas_price: Optional[IGasPrice] = None,
                                        gas_limit: Optional[IGasLimit] = None) -> Transaction:
        parts = [
            "setMetaData",
            arg_to_string(name),
            arg_to_string(website),
            arg_to_string(identifier)
        ]

        transaction = self.create_transaction(
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            execution_gas_limit=self.config.gas_limit_delegation_operations + self.config.additional_gas_for_delegation_operations,
            gas_limit_hint=gas_limit,
            gas_price=gas_price,
            nonce=transaction_nonce,
            value=value,
            guardian=guardian
        )

        return transaction

    def _compute_gas_limit(self, payload: ITransactionPayload, execution_gas: IGasLimit, has_guardian: bool) -> IGasLimit:
        data_movement_gas = self.config.min_gas_limit + self.config.gas_limit_per_byte * payload.length()
        gas = data_movement_gas + execution_gas

        if has_guardian:
            gas += self.config.extra_gas_limit_for_guarded_transactions

        return gas

    def create_transaction(
            self,
            sender: IAddress,
            receiver: IAddress,
            data_parts: List[str],
            execution_gas_limit: IGasLimit,
            gas_limit_hint: Optional[IGasLimit],
            gas_price: Optional[IGasPrice],
            nonce: Optional[INonce],
            value: Optional[ITransactionValue],
            guardian: Optional[IAddress]) -> Transaction:
        data = self._build_transaction_payload(data_parts)
        version = TRANSACTION_VERSION_DEFAULT
        options = TRANSACTION_OPTIONS_DEFAULT

        has_guardian = True if guardian else False
        gas_limit = gas_limit_hint or self._compute_gas_limit(data, execution_gas_limit, has_guardian)

        return Transaction(
            chain_id=self.config.chain_id,
            sender=sender,
            receiver=receiver,
            gas_limit=gas_limit,
            gas_price=gas_price,
            value=value,
            nonce=nonce,
            data=data,
            version=version,
            options=options,
            guardian=guardian
        )

    def _build_transaction_payload(self, parts: List[str]) -> TransactionPayload:
        data = ARGS_SEPARATOR.join(parts)
        return TransactionPayload.from_str(data)
