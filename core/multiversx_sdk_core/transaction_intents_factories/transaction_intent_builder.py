from typing import List, Optional, Protocol

from multiversx_sdk_core.constants import ARGS_SEPARATOR
from multiversx_sdk_core.interfaces import IAddress, ITransactionPayload
from multiversx_sdk_core.transaction_intent import TransactionIntent
from multiversx_sdk_core.transaction_payload import TransactionPayload


class IConfig(Protocol):
    min_gas_limit: int
    gas_limit_per_byte: int


class TransactionIntentBuilder:
    def __init__(self,
                 config: IConfig,
                 sender: IAddress,
                 receiver: IAddress,
                 data_parts: List[str],
                 execution_gas_limit: int,
                 value: Optional[int] = None) -> None:
        self.config = config
        self.sender = sender
        self.receiver = receiver
        self.data_parts = data_parts
        self.execution_gas_limit = execution_gas_limit
        self.value = value

    def compute_gas_limit(self, payload: ITransactionPayload, execution_gas: int) -> int:
        data_movement_gas = self.config.min_gas_limit + self.config.gas_limit_per_byte * payload.length()
        gas = data_movement_gas + execution_gas

        return gas

    def build_transaction_payload(self, parts: List[str]) -> TransactionPayload:
        data = ARGS_SEPARATOR.join(parts)
        return TransactionPayload.from_str(data)

    def build(self) -> TransactionIntent:
        data = self.build_transaction_payload(self.data_parts)
        gas_limit = self.compute_gas_limit(data, self.execution_gas_limit)

        transaction_intent = TransactionIntent()

        transaction_intent.sender = self.sender.bech32()
        transaction_intent.receiver = self.receiver.bech32()
        transaction_intent.gas_limit = gas_limit
        transaction_intent.data = str(data).encode()
        transaction_intent.value = self.value if self.value else 0

        return transaction_intent
