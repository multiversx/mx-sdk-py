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
    min_gas_price: IGasPrice
    min_gas_limit: IGasLimit
    gas_limit_per_byte: IGasLimit
    stake = 5000000
    unstake = 5000000
    unbond = 5000000
    claim = 5000000
    get = 5000000
    change_reward_address = 5000000
    change_validator_keys = 5000000
    unjail = 5000000
    delegation_manager_ops = 50000000
    delegation_ops = 1000000
    unstake_tokens = 5000000
    unbond_tokens = 5000000
    additional_gas_limit_per_node = 6000000
    additional_gas_for_operations = 10000000


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
            execution_gas_limit=self.config.delegation_manager_ops + self.config.additional_gas_for_operations,
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
            execution_gas_limit=self.config.delegation_ops + num_nodes * self.config.additional_gas_limit_per_node,
            gas_limit_hint=gas_limit,
            gas_price=gas_price,
            nonce=transaction_nonce,
            value=value
        )
        return transaction

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
            execution_gas_limit=self.config.delegation_ops + num_nodes * self.config.additional_gas_limit_per_node,
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
            execution_gas_limit=self.config.delegation_ops + self.config.stake + num_nodes * self.config.additional_gas_limit_per_node,
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
            execution_gas_limit=self.config.delegation_ops + self.config.unbond + num_nodes * self.config.additional_gas_limit_per_node,
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
            execution_gas_limit=self.config.delegation_ops + self.config.unstake + num_nodes * self.config.additional_gas_limit_per_node,
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
            execution_gas_limit=self.config.delegation_ops + num_nodes * self.config.additional_gas_limit_per_node,
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
            execution_gas_limit=self.config.delegation_ops + self.config.additional_gas_for_operations,
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
            execution_gas_limit=self.config.delegation_ops + self.config.additional_gas_for_operations,
            gas_limit_hint=gas_limit,
            gas_price=gas_price,
            nonce=transaction_nonce,
            value=value
        )

        return transaction

    def automatic_activation(self,
                             sender: IAddress,
                             delegation_contract: IAddress,
                             set: bool,
                             unset: bool,
                             value: ITransactionValue,
                             transaction_nonce: Optional[INonce] = None,
                             gas_price: Optional[IGasPrice] = None,
                             gas_limit: Optional[IGasLimit] = None) -> Transaction:
        parts = ["setAutomaticActivation"]

        if set:
            parts.append(arg_to_string('true'))

        if unset:
            parts.append(arg_to_string('false'))

        transaction = self.create_transaction(
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            execution_gas_limit=self.config.delegation_ops + self.config.additional_gas_for_operations,
            gas_limit_hint=gas_limit,
            gas_price=gas_price,
            nonce=transaction_nonce,
            value=value
        )

        return transaction

    def redelegate_cap(self,
                       sender: IAddress,
                       delegation_contract: IAddress,
                       set: bool,
                       unset: bool,
                       value: ITransactionValue,
                       transaction_nonce: Optional[INonce] = None,
                       gas_price: Optional[IGasPrice] = None,
                       gas_limit: Optional[IGasLimit] = None) -> Transaction:
        parts = ["setCheckCapOnReDelegateRewards"]

        if set:
            parts.append(arg_to_string('true'))

        if unset:
            parts.append(arg_to_string('false'))

        transaction = self.create_transaction(
            sender=sender,
            receiver=delegation_contract,
            data_parts=parts,
            execution_gas_limit=self.config.delegation_ops + self.config.additional_gas_for_operations,
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
            execution_gas_limit=self.config.delegation_ops + self.config.additional_gas_for_operations,
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
