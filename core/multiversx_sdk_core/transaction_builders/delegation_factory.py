from typing import Any, List, Optional, Protocol, Sequence, Tuple

from multiversx_sdk_core import TransactionPayload
from multiversx_sdk_core.constants import (ARGS_SEPARATOR,
                                           TRANSACTION_OPTIONS_DEFAULT,
                                           TRANSACTION_VERSION_DEFAULT)
from multiversx_sdk_core.errors import ErrListsLengthDoNotMatch
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


class MetaChainSystemSCsCost:
    STAKE = 5000000
    UNSTAKE = 5000000
    UNBOND = 5000000
    CLAIM = 5000000
    GET = 5000000
    CHANGE_REWARD_ADDRESS = 5000000
    CHANGE_VALIDATOR_KEYS = 5000000
    UNJAIL = 5000000
    DELEGATION_MANAGER_OPS = 50000000
    DELEGATION_OPS = 1000000
    UNSTAKE_TOKENS = 5000000
    UNBOND_TOKENS = 5000000


ADDITIONAL_GAS_LIMIT_PER_NODE = 6000000
ADDITIONAL_GAS_FOR_OPERATIONS = 10000000


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
        data = self._prepare_data_for_create_new_delegation_contract(total_delegation_cap, service_fee)

        transaction = self.create_transaction(
            sender=sender,
            receiver=receiver,
            data_parts=data,
            execution_gas_limit=MetaChainSystemSCsCost.DELEGATION_MANAGER_OPS + ADDITIONAL_GAS_FOR_OPERATIONS,
            gas_limit_hint=gas_limit,
            gas_price=gas_price,
            nonce=transaction_nonce,
            value=value
        )

        return transaction

    def _prepare_data_for_create_new_delegation_contract(self, total_delegation_cap: int, service_fee: int) -> List[str]:
        function = "createNewDelegationContract"
        args_list: List[Any] = [
            function,
            arg_to_string(total_delegation_cap),
            arg_to_string(service_fee)
        ]
        return args_list

    def add_nodes(self,
                  sender: IAddress,
                  delegation_contract: IAddress,
                  public_keys: Sequence[IValidatorPublicKey],
                  signed_messages: List[ISignature],
                  value: ITransactionValue,
                  transaction_nonce: Optional[INonce] = None,
                  gas_price: Optional[IGasPrice] = None,
                  gas_limit: Optional[IGasLimit] = None) -> Transaction:
        data = self._prepare_data_for_add_nodes(public_keys, signed_messages)
        num_nodes = len(public_keys)

        transaction = self.create_transaction(
            sender=sender,
            receiver=delegation_contract,
            data_parts=data,
            execution_gas_limit=MetaChainSystemSCsCost.DELEGATION_OPS + num_nodes * ADDITIONAL_GAS_LIMIT_PER_NODE,
            gas_limit_hint=gas_limit,
            gas_price=gas_price,
            nonce=transaction_nonce,
            value=value
        )
        return transaction

    def _prepare_data_for_add_nodes(self, public_keys: Sequence[IValidatorPublicKey], signed_messages: List[ISignature]) -> List[str]:
        if len(public_keys) != len(signed_messages):
            raise ErrListsLengthDoNotMatch("The number of public keys should match the number of signed messages")

        function = "addNodes"
        args: List[str] = [function]

        for i in range(len(public_keys)):
            args.append(public_keys[i].hex())
            args.append(signed_messages[i].hex())

        return args

    def remove_nodes(self,
                     sender: IAddress,
                     delegation_contract: IAddress,
                     bls_keys: List[str],
                     value: ITransactionValue,
                     transaction_nonce: Optional[INonce] = None,
                     gas_price: Optional[IGasPrice] = None,
                     gas_limit: Optional[IGasLimit] = None) -> Transaction:
        num_nodes = len(bls_keys)

        data: List[str] = ["removeNodes"]
        data.extend(bls_keys)

        transaction = self.create_transaction(
            sender=sender,
            receiver=delegation_contract,
            data_parts=data,
            execution_gas_limit=MetaChainSystemSCsCost.DELEGATION_OPS + num_nodes * ADDITIONAL_GAS_LIMIT_PER_NODE,
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

        data = ["stakeNodes"]
        data.extend(bls_keys)

        transaction = self.create_transaction(
            sender=sender,
            receiver=delegation_contract,
            data_parts=data,
            execution_gas_limit=(MetaChainSystemSCsCost.DELEGATION_OPS + MetaChainSystemSCsCost.STAKE) + num_nodes * ADDITIONAL_GAS_LIMIT_PER_NODE,
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

        data = ["unBondNodes"]
        data.extend(bls_keys)

        transaction = self.create_transaction(
            sender=sender,
            receiver=delegation_contract,
            data_parts=data,
            execution_gas_limit=(MetaChainSystemSCsCost.DELEGATION_OPS + MetaChainSystemSCsCost.UNBOND) + num_nodes * ADDITIONAL_GAS_LIMIT_PER_NODE,
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

        data = ["unStakeNodes"]
        data.extend(bls_keys)

        transaction = self.create_transaction(
            sender=sender,
            receiver=delegation_contract,
            data_parts=data,
            execution_gas_limit=(MetaChainSystemSCsCost.DELEGATION_OPS + MetaChainSystemSCsCost.UNSTAKE) + num_nodes * ADDITIONAL_GAS_LIMIT_PER_NODE,
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

        data = ["unJailNodes"]
        data.extend(bls_keys)

        transaction = self.create_transaction(
            sender=sender,
            receiver=delegation_contract,
            data_parts=data,
            execution_gas_limit=MetaChainSystemSCsCost.DELEGATION_OPS + num_nodes * ADDITIONAL_GAS_LIMIT_PER_NODE,
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
        data = [
            "changeServiceFee",
            arg_to_string(service_fee)
        ]

        transaction = self.create_transaction(
            sender=sender,
            receiver=delegation_contract,
            data_parts=data,
            execution_gas_limit=MetaChainSystemSCsCost.DELEGATION_OPS + ADDITIONAL_GAS_FOR_OPERATIONS,
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
        data = [
            "modifyTotalDelegationCap",
            arg_to_string(delegation_cap)
        ]

        transaction = self.create_transaction(
            sender=sender,
            receiver=delegation_contract,
            data_parts=data,
            execution_gas_limit=MetaChainSystemSCsCost.DELEGATION_OPS + ADDITIONAL_GAS_FOR_OPERATIONS,
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
        data = ["setAutomaticActivation"]

        if set:
            data.append(arg_to_string('true'))

        if unset:
            data.append(arg_to_string('false'))

        transaction = self.create_transaction(
            sender=sender,
            receiver=delegation_contract,
            data_parts=data,
            execution_gas_limit=MetaChainSystemSCsCost.DELEGATION_OPS + ADDITIONAL_GAS_FOR_OPERATIONS,
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
        data = ["setCheckCapOnReDelegateRewards"]

        if set:
            data.append(arg_to_string('true'))

        if unset:
            data.append(arg_to_string('false'))

        transaction = self.create_transaction(
            sender=sender,
            receiver=delegation_contract,
            data_parts=data,
            execution_gas_limit=MetaChainSystemSCsCost.DELEGATION_OPS + ADDITIONAL_GAS_FOR_OPERATIONS,
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
        data = [
            "setMetaData",
            arg_to_string(name),
            arg_to_string(website),
            arg_to_string(identifier)
        ]

        transaction = self.create_transaction(
            sender=sender,
            receiver=delegation_contract,
            data_parts=data,
            execution_gas_limit=MetaChainSystemSCsCost.DELEGATION_OPS + ADDITIONAL_GAS_FOR_OPERATIONS,
            gas_limit_hint=gas_limit,
            gas_price=gas_price,
            nonce=transaction_nonce,
            value=value
        )

        return transaction

    def _compute_gas_limit(self, payload: ITransactionPayload, execution_gas: IGasLimit) -> IGasLimit:
        data_movement_gas = self.config.min_gas_limit + self.config.gas_limit_per_byte * payload.length()
        return data_movement_gas + execution_gas

    def _parse_keys(self, keys: List[str]) -> Tuple[str, int]:
        parsed_keys = ''
        for key in keys:
            parsed_keys += '@' + key
        return parsed_keys, len(keys)

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
