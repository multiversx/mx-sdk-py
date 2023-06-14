from typing import Any, List, Optional, Protocol

from multiversx_sdk_core import TransactionPayload
from multiversx_sdk_core.address import Address
from multiversx_sdk_core.constants import (ARGS_SEPARATOR,
                                           DELEGATION_MANAGER_SC_ADDRESS)
from multiversx_sdk_core.interfaces import (IAddress, IChainID, IGasLimit,
                                            IGasPrice, INonce,
                                            ITransactionPayload,
                                            ITransactionValue)
from multiversx_sdk_core.serializer import args_to_string
from multiversx_sdk_core.transaction import Transaction


class IConfig(Protocol):
    chain_id: IChainID
    min_gas_price: IGasPrice
    min_gas_limit: IGasLimit
    gas_limit_per_byte: IGasLimit


class IBaseArgs(Protocol):
    transaction_nonce: Optional[INonce]
    value: Optional[ITransactionValue]
    gas_price: Optional[IGasPrice]
    gas_limit: Optional[IGasLimit]


class ICreateNewDelegationContractArgs(IBaseArgs, Protocol):
    sender: IAddress
    receiver: IAddress = Address.from_bech32(DELEGATION_MANAGER_SC_ADDRESS)
    total_delegation_cap: int
    service_fee: int
    data: Optional[ITransactionPayload]


class MetaChainSystemSCsCost:
    DELEGATION_MANAGER_OPS = 50000000
    DELEGATION_OPS = 1000000


class DelegationFactory:
    def __init__(self, config: IConfig) -> None:
        self.config = config

    def create_new_delegation_contract(self, args: ICreateNewDelegationContractArgs) -> Transaction:
        if not args.data:
            args.data = self._prepare_data_for_create_new_delegation_contract(args)

        if not args.gas_limit:
            args.gas_limit = self._estimate_system_sc_call(args.data.length(), MetaChainSystemSCsCost.DELEGATION_MANAGER_OPS, 2)

        transaction = self.create_transaction(
            args.sender,
            args.receiver,
            args.gas_limit,
            args.data,
            args.gas_price,
            args.transaction_nonce,
            args.value
        )

        return transaction

    def _prepare_data_for_create_new_delegation_contract(self, args: ICreateNewDelegationContractArgs) -> TransactionPayload:
        function = "createNewDelegationContract"
        args_list: List[Any] = [args.total_delegation_cap, args.service_fee]
        data = ARGS_SEPARATOR.join([function, args_to_string(args_list)])
        return TransactionPayload.from_str(data)

    def _estimate_system_sc_call(self, data_length: int, base_cost: int, factor: int = 1) -> int:
        gas_limit = self.config.min_gas_limit + data_length * self.config.gas_limit_per_byte
        gas_limit += factor * base_cost
        return gas_limit

    def create_transaction(
            self,
            sender: IAddress,
            receiver: IAddress,
            gas_limit: IGasLimit,
            data: ITransactionPayload,
            gas_price: Optional[IGasPrice],
            nonce: Optional[INonce],
            value: Optional[ITransactionValue]
    ) -> Transaction:
        return Transaction(
            chain_id=self.config.chain_id,
            sender=sender,
            receiver=receiver,
            gas_limit=gas_limit,
            gas_price=gas_price,
            value=value,
            nonce=nonce,
            data=data
        )
