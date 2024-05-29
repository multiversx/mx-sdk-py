import logging
from typing import Any, List, Optional

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.errors import (ErrInvalidGasLimitForInnerTransaction,
                                        ErrInvalidRelayerV2BuilderArguments)
from multiversx_sdk.core.interfaces import (IAddress, IGasLimit,
                                            INetworkConfig, INonce)
from multiversx_sdk.core.serializer import args_to_string
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transaction_payload import TransactionPayload

logger = logging.getLogger("RelayedTransactionV2Builder")


class RelayedTransactionV2Builder:
    def __init__(
            self, inner_transaction: Optional[Transaction] = None,
            inner_transaction_gas_limit: Optional[IGasLimit] = None,
            relayer_address: Optional[IAddress] = None,
            relayer_nonce: Optional[INonce] = None,
            network_config: Optional[INetworkConfig] = None) -> None:
        logger.warning("'RelayedTransactionV2Builder' is deprecated and will soon be removed. Please use 'RelayedTransactionsFactory' instead.")
        self.inner_transaction = inner_transaction
        self.inner_transaction_gas_limit = inner_transaction_gas_limit
        self.relayer_address = relayer_address
        self.relayer_nonce = relayer_nonce
        self.network_config = network_config

    def set_inner_transaction(self, transaction: Transaction) -> None:
        self.inner_transaction = transaction

    def set_inner_transaction_gas_limit(self, gas_limit: IGasLimit) -> None:
        self.inner_transaction_gas_limit = gas_limit

    def set_network_config(self, network_config: INetworkConfig) -> None:
        self.network_config = network_config

    def set_relayer_address(self, relayer_address: IAddress) -> None:
        self.relayer_address = relayer_address

    def set_relayer_nonce(self, relayer_nonce: INonce) -> None:
        self.relayer_nonce = relayer_nonce

    def build(self) -> Transaction:
        if (
            not self.inner_transaction
            or not self.network_config
            or not self.relayer_address
            or not self.inner_transaction.signature
            or not self.inner_transaction_gas_limit
        ):
            raise ErrInvalidRelayerV2BuilderArguments()

        if self.inner_transaction.gas_limit:
            raise ErrInvalidGasLimitForInnerTransaction()

        arguments: List[Any] = [
            Address.new_from_bech32(self.inner_transaction.receiver),
            self.inner_transaction.nonce,
            self.inner_transaction.data,
            self.inner_transaction.signature
        ]

        data = f"relayedTxV2@{args_to_string(arguments)}"
        payload = TransactionPayload.from_str(data)

        relayed_transaction = Transaction(
            sender=self.relayer_address.to_bech32(),
            receiver=self.inner_transaction.sender,
            value=0,
            gas_limit=self.inner_transaction_gas_limit + self.network_config.min_gas_limit + self.network_config.gas_per_data_byte * payload.length(),
            chain_id=self.network_config.chain_id,
            data=payload.data,
            version=self.inner_transaction.version,
            options=self.inner_transaction.options
        )

        if self.relayer_nonce:
            relayed_transaction.nonce = self.relayer_nonce

        return relayed_transaction
