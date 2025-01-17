from typing import Optional

from multiversx_sdk.core import Address, Transaction
from multiversx_sdk.core.constants import ARGS_SEPARATOR
from multiversx_sdk.core.transactions_factory_config import TransactionsFactoryConfig


class TransactionBuilder:
    """
    **FOR INTERNAL USE ONLY.**
    Used for the transactions factories.
    """

    def __init__(
        self,
        config: TransactionsFactoryConfig,
        sender: Address,
        receiver: Address,
        data_parts: list[str],
        gas_limit: int,
        add_data_movement_gas: bool,
        amount: Optional[int] = None,
    ) -> None:
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

    def build_transaction_payload(self, parts: list[str]) -> bytes:
        data = ARGS_SEPARATOR.join(parts)
        return data.encode("utf-8")

    def build(self) -> Transaction:
        data = self.build_transaction_payload(self.data_parts)
        gas_limit = self.compute_gas_limit(data)

        transaction = Transaction(
            sender=self.sender,
            receiver=self.receiver,
            gas_limit=gas_limit,
            chain_id=self.config.chain_id,
            data=data,
            value=self.amount,
        )

        return transaction
