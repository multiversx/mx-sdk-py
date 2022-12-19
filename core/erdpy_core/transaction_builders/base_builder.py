from typing import Optional

from erdpy_core.interfaces import (IAddress, IChainID, IGasLimit, IGasPrice,
                                   INonce, ITransactionOptions,
                                   ITransactionValue, ITransactionVersion)
from erdpy_core.transaction import Transaction
from erdpy_core.transaction_builders.configuration import Configuration
from erdpy_core.transaction_payload import TransactionPayload


class BaseBuilder:
    def __init__(self,
                 chain_id: IChainID,
                 nonce: Optional[INonce] = None,
                 value: Optional[ITransactionValue] = None,
                 gas_limit: Optional[IGasLimit] = None,
                 gas_price: Optional[IGasPrice] = None) -> None:
        self.chain_id = chain_id
        self.nonce = nonce
        self.value = value
        self.gas_limit = gas_limit
        self.gas_price = gas_price
        self.configuration = Configuration()

    def build_transaction(self) -> Transaction:
        chain_id = self.chain_id
        sender = self._get_sender()
        receiver = self._get_receiver()
        gas_limit = self._get_gas_limit()
        gas_price = self._get_gas_price()
        nonce = self.nonce or 0
        value = self._get_value()
        data = self.build_payload()
        version = self._get_transaction_version()
        options = self._get_transaction_options()

        return Transaction(
            chain_id=chain_id,
            sender=sender,
            receiver=receiver,
            gas_limit=gas_limit,
            gas_price=gas_price,
            nonce=nonce,
            value=value,
            data=data,
            version=version,
            options=options
        )

    def build_payload(self) -> TransactionPayload:
        raise NotImplementedError()

    def _get_sender(self) -> IAddress:
        raise NotImplementedError()

    def _get_receiver(self) -> IAddress:
        raise NotImplementedError()

    def _get_value(self) -> ITransactionValue:
        return self.value or 0

    def _get_gas_limit(self) -> IGasLimit:
        assert self.gas_limit, "gas_limit isn't set, nor computed"
        return self.gas_limit

    def _get_gas_price(self) -> IGasPrice:
        return self.gas_price or self.configuration.gas_price

    def _get_transaction_version(self) -> ITransactionVersion:
        return self.configuration.transaction_version

    def _get_transaction_options(self) -> ITransactionOptions:
        return self.configuration.transaction_options
