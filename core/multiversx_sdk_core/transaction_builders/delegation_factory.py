from typing import Any, List, Optional, Protocol, Tuple

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
from multiversx_sdk_core.serializer import args_to_string
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
            data=data,
            execution_gas_limit=MetaChainSystemSCsCost.DELEGATION_MANAGER_OPS,
            gas_limit_hint=gas_limit,
            gas_price=gas_price,
            nonce=transaction_nonce,
            value=value
        )

        return transaction

    def _prepare_data_for_create_new_delegation_contract(self, total_delegation_cap: int, service_fee: int) -> TransactionPayload:
        function = "createNewDelegationContract"
        args_list: List[Any] = [total_delegation_cap, service_fee]
        data = ARGS_SEPARATOR.join([function, args_to_string(args_list)])
        return TransactionPayload.from_str(data)

    def add_nodes(self,
                  sender: IAddress,
                  delegation_contract: IAddress,
                  public_keys: List[IValidatorPublicKey],
                  signed_messages: List[ISignature],
                  value: ITransactionValue,
                  transaction_nonce: Optional[INonce] = None,
                  gas_price: Optional[IGasPrice] = None,
                  gas_limit: Optional[IGasLimit] = None) -> Transaction:
        data = self._prepare_data_for_add_nodes(public_keys, signed_messages)

        transaction = self.create_transaction(
            sender=sender,
            receiver=delegation_contract,
            data=data,
            execution_gas_limit=MetaChainSystemSCsCost.DELEGATION_OPS,
            gas_limit_hint=gas_limit,
            gas_price=gas_price,
            nonce=transaction_nonce,
            value=value
        )
        return transaction

    def _prepare_data_for_add_nodes(self, public_keys: List[IValidatorPublicKey], signed_messages: List[ISignature]) -> TransactionPayload:
        if len(public_keys) != len(signed_messages):
            raise ErrListsLengthDoNotMatch("The number of public keys should match the number of signed messages")

        add_nodes_data = "addNodes"
        for i in range(len(public_keys)):
            add_nodes_data += f"@{public_keys[i].hex()}@{signed_messages[i].hex()}"

        return TransactionPayload.from_str(add_nodes_data)

    def remove_nodes(self,
                     sender: IAddress,
                     delegation_contract: IAddress,
                     bls_keys: List[str],
                     value: ITransactionValue,
                     transaction_nonce: Optional[INonce] = None,
                     gas_price: Optional[IGasPrice] = None,
                     gas_limit: Optional[IGasLimit] = None):
        parsed_keys, _ = self._parse_keys(bls_keys)
        data = TransactionPayload.from_str("removeNodes" + parsed_keys)

        transaction = self.create_transaction(
            sender=sender,
            receiver=delegation_contract,
            data=data,
            execution_gas_limit=MetaChainSystemSCsCost.DELEGATION_OPS,
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
            data: ITransactionPayload,
            execution_gas_limit: IGasLimit,
            gas_limit_hint: Optional[IGasLimit],
            gas_price: Optional[IGasPrice],
            nonce: Optional[INonce],
            value: Optional[ITransactionValue]
    ) -> Transaction:
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
