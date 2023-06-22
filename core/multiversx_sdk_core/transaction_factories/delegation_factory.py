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


class DelegationFactory:
    def __init__(self, config: IConfig) -> None:
        self.config = config

    def create_new_delegation_contract(self,
                                       sender: IAddress,
                                       receiver: IAddress,
                                       total_delegation_cap: int,
                                       service_fee: int,
                                       value: ITransactionValue,
                                       transaction_nonce: Optional[INonce] = None,
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
            value=value
        )

        return transaction

    def add_nodes(self,
                  sender: IAddress,
                  delegation_contract: IAddress,
                  public_keys: Sequence[IValidatorPublicKey],
                  signed_messages: Sequence[ISignature],
                  value: ITransactionValue,
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
            value=value
        )
        return transaction

    def _compute_execution_gas_limit_for_nodes_management(self, num_nodes: int) -> IGasLimit:
        return self.config.gas_limit_delegation_operations + num_nodes * self.config.additional_gas_limit_per_validator_node

    def remove_nodes(self,
                     sender: IAddress,
                     delegation_contract: IAddress,
                     bls_keys: List[str],
                     value: ITransactionValue,
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
            value=value
        )

        return transaction

    def stake_nodes(self,
                    sender: IAddress,
                    delegation_contract: IAddress,
                    bls_keys: List[str],
                    value: ITransactionValue,
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
            value=value
        )

        return transaction

    def unbond_nodes(self,
                     sender: IAddress,
                     delegation_contract: IAddress,
                     bls_keys: List[str],
                     value: ITransactionValue,
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
            value=value
        )

        return transaction

    def unstake_nodes(self,
                      sender: IAddress,
                      delegation_contract: IAddress,
                      bls_keys: List[str],
                      value: ITransactionValue,
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
            value=value
        )

        return transaction

    def unjail_nodes(self,
                     sender: IAddress,
                     delegation_contract: IAddress,
                     bls_keys: List[str],
                     value: ITransactionValue,
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
            value=value
        )

        return transaction

    def change_service_fee(self,
                           sender: IAddress,
                           delegation_contract: IAddress,
                           service_fee: int,
                           value: ITransactionValue,
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
            value=value
        )

        return transaction

    def modify_delegation_cap(self,
                              sender: IAddress,
                              delegation_contract: IAddress,
                              delegation_cap: int,
                              value: ITransactionValue,
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
            value=value
        )

        return transaction

    def set_automatic_activation(self,
                                 sender: IAddress,
                                 delegation_contract: IAddress,
                                 value: ITransactionValue,
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
            value=value
        )

        return transaction

    def unset_automatic_activation(self,
                                   sender: IAddress,
                                   delegation_contract: IAddress,
                                   value: ITransactionValue,
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
            value=value
        )

        return transaction

    def set_redelegate_cap(self,
                           sender: IAddress,
                           delegation_contract: IAddress,
                           value: ITransactionValue,
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
            value=value
        )

        return transaction

    def unset_redelegate_cap(self,
                             sender: IAddress,
                             delegation_contract: IAddress,
                             value: ITransactionValue,
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
            value=value
        )

        return transaction

    def set_metadata(self,
                     sender: IAddress,
                     delegation_contract: IAddress,
                     name: str,
                     website: str,
                     identifier: str,
                     value: ITransactionValue,
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
            value=value
        )

        return transaction

    def _compute_gas_limit(self, payload: ITransactionPayload, execution_gas: IGasLimit) -> IGasLimit:
        data_movement_gas = self.config.min_gas_limit + self.config.gas_limit_per_byte * payload.length()
        return data_movement_gas + execution_gas

    def create_transaction(
            self,
            sender: IAddress,
            receiver: IAddress,
            data_parts: List[str],
            execution_gas_limit: IGasLimit,
            gas_limit_hint: Optional[IGasLimit],
            gas_price: Optional[IGasPrice],
            nonce: Optional[INonce],
            value: Optional[ITransactionValue]
    ) -> Transaction:
        data = self._build_transaction_payload(data_parts)
        gas_limit = gas_limit_hint or self._compute_gas_limit(data, execution_gas_limit)
        version = TRANSACTION_VERSION_DEFAULT
        options = TRANSACTION_OPTIONS_DEFAULT

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
            options=options
        )

    def _build_transaction_payload(self, parts: List[str]) -> TransactionPayload:
        data = ARGS_SEPARATOR.join(parts)
        return TransactionPayload.from_str(data)
