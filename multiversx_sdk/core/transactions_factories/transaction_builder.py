from typing import List, Optional, Protocol

from multiversx_sdk.core.constants import ARGS_SEPARATOR
from multiversx_sdk.core.interfaces import IAddress
from multiversx_sdk.core.transaction import Transaction


class IConfig(Protocol):
    chain_id: str
    min_gas_limit: int
    gas_limit_per_byte: int


class TransactionBuilder:
    def __init__(self,
                 config: IConfig,
                 sender: IAddress,
                 receiver: IAddress,
                 data_parts: List[str],
                 gas_limit: int,
                 add_data_movement_gas: bool,
                 amount: Optional[int] = None) -> None:
        self.config = config
        self.sender = sender
        self.receiver = receiver
        self.data_parts = data_parts
        self.provided_gas_limit = gas_limit
        self.add_data_movement_gas = add_data_movement_gas
        self.amount = amount

    def compute_gas_limit(self, payload: bytes) -> int:
        if not self.add_data_movement_gas:
            return self.provided_gas_limit

        data_movement_gas = self.config.min_gas_limit + self.config.gas_limit_per_byte * len(payload)
        gas = data_movement_gas + self.provided_gas_limit

        return gas

    def build_transaction_payload(self, parts: List[str]) -> bytes:
        data = ARGS_SEPARATOR.join(parts)
        return data.encode("utf-8")

    def build(self) -> Transaction:
        data = self.build_transaction_payload(self.data_parts)
        gas_limit = self.compute_gas_limit(data)

        transaction = Transaction(
            sender=self.sender.to_bech32(),
            receiver=self.receiver.to_bech32(),
            gas_limit=gas_limit,
            chain_id=self.config.chain_id,
            data=data,
            value=self.amount
        )

        return transaction
