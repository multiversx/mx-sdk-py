from typing import List, Optional, Protocol

from erdpy_core.constants import (ARGS_SEPARATOR, TRANSACTION_OPTIONS_DEFAULT,
                                  TRANSACTION_VERSION_DEFAULT)
from erdpy_core.interfaces import (IAddress, IChainID, IGasLimit, IGasPrice,
                                   INonce, ITransactionOptions,
                                   ITransactionPayload, ITransactionValue,
                                   ITransactionVersion)
from erdpy_core.transaction import Transaction
from erdpy_core.transaction_payload import TransactionPayload


class ITransactionBuilderConfiguration(Protocol):
    chain_id: IChainID
    min_gas_price: IGasPrice
    min_gas_limit: IGasLimit
    gas_limit_per_byte: IGasLimit


class TransactionBuilder:
    """
    Not intended to be used directly; should be derived and specialized.
    """

    def __init__(self,
                 config: ITransactionBuilderConfiguration,
                 nonce: Optional[INonce] = None,
                 value: Optional[ITransactionValue] = None,
                 gas_limit: Optional[IGasLimit] = None,
                 gas_price: Optional[IGasPrice] = None) -> None:
        self.chain_id = config.chain_id
        self.min_gas_price = config.min_gas_price
        self.min_gas_limit = config.min_gas_limit
        self.gas_limit_per_byte = config.gas_limit_per_byte

        self.nonce = nonce
        self.value = value
        self.gas_limit = gas_limit
        self.gas_price = gas_price or config.min_gas_price
        self.sender: Optional[IAddress] = None
        self.receiver: Optional[IAddress] = None

    def build(self) -> Transaction:
        chain_id = self.chain_id
        sender = self._get_sender()
        receiver = self._get_receiver()
        data = self.build_payload()
        gas_limit = self._get_gas_limit(data)
        gas_price = self.gas_price
        nonce = self.nonce or 0
        value = self._get_value()
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
        parts = self._build_payload_parts()
        data = ARGS_SEPARATOR.join(parts)
        payload = TransactionPayload.from_str(data)
        return payload

    def _build_payload_parts(self) -> List[str]:
        raise NotImplementedError()

    def _get_sender(self) -> IAddress:
        assert self.sender is not None, "sender isn't set"
        return self.sender

    def _get_receiver(self) -> IAddress:
        assert self.receiver is not None, "receiver isn't set"
        return self.receiver

    def _get_value(self) -> ITransactionValue:
        return self.value or 0

    def _get_gas_limit(self, payload: ITransactionPayload) -> IGasLimit:
        if self.gas_limit:
            return self.gas_limit

        gas_limit = self._compute_data_movement_gas(payload) + self._estimate_execution_gas()
        return gas_limit

    def _compute_data_movement_gas(self, payload: ITransactionPayload) -> IGasLimit:
        return self.min_gas_limit + self.gas_limit_per_byte * payload.length()

    def _estimate_execution_gas(self) -> IGasLimit:
        raise NotImplementedError()

    def _get_transaction_version(self) -> ITransactionVersion:
        return TRANSACTION_VERSION_DEFAULT

    def _get_transaction_options(self) -> ITransactionOptions:
        return TRANSACTION_OPTIONS_DEFAULT
