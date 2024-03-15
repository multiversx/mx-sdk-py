import pytest

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.errors import (ErrInvalidGasLimitForInnerTransaction,
                                        ErrInvalidRelayerV2BuilderArguments)
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transaction_builders.relayed_v2_builder import \
    RelayedTransactionV2Builder
from multiversx_sdk.core.transaction_computer import TransactionComputer
from multiversx_sdk.testutils.wallets import load_wallets


class NetworkConfig:
    def __init__(self) -> None:
        self.min_gas_limit = 50_000
        self.gas_per_data_byte = 1_500
        self.gas_price_modifier = 0.01
        self.chain_id = "T"


class TestRelayedV2Builder:
    wallets = load_wallets()
    alice = wallets["alice"]
    bob = wallets["bob"]

    def test_without_arguments(self):
        relayed_builder = RelayedTransactionV2Builder()

        with pytest.raises(ErrInvalidRelayerV2BuilderArguments):
            relayed_builder.build()

    def test_with_inner_tx_gas_limit(self):
        builder = RelayedTransactionV2Builder()
        network_config = NetworkConfig()
        transaction_computer = TransactionComputer()

        inner_tx = Transaction(
            chain_id=network_config.chain_id,
            sender=self.alice.label,
            receiver="erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u",
            gas_limit=10,
            nonce=15,
            data=b"getContractConfig"
        )
        inner_tx.signature = self.alice.secret_key.sign(transaction_computer.compute_bytes_for_signing(inner_tx))

        builder.set_network_config(network_config)
        builder.set_inner_transaction_gas_limit(10)
        builder.set_inner_transaction(inner_tx)
        builder.set_relayer_address(Address.new_from_bech32(self.alice.label))

        with pytest.raises(ErrInvalidGasLimitForInnerTransaction):
            builder.build()

    def test_compute_relayed_v2_transaction(self):
        network_config = NetworkConfig()
        transaction_computer = TransactionComputer()

        inner_tx = Transaction(
            chain_id=network_config.chain_id,
            sender=self.bob.label,
            receiver="erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u",
            gas_limit=0,
            nonce=15,
            data=b"getContractConfig"
        )
        inner_tx.signature = self.bob.secret_key.sign(transaction_computer.compute_bytes_for_signing(inner_tx))

        builder = RelayedTransactionV2Builder()
        builder.set_inner_transaction(inner_tx)
        builder.set_inner_transaction_gas_limit(60_000_000)
        builder.set_relayer_nonce(37)
        builder.set_network_config(network_config)
        builder.set_relayer_address(Address.new_from_bech32(self.alice.label))

        relayed_tx = builder.build()

        relayed_tx.sender = self.alice.label
        relayed_tx.signature = self.alice.secret_key.sign(transaction_computer.compute_bytes_for_signing(relayed_tx))

        assert relayed_tx.version == 2
        assert relayed_tx.options == 0
        assert relayed_tx.nonce == 37
        assert relayed_tx.data.decode() == "relayedTxV2@000000000000000000010000000000000000000000000000000000000002ffff@0f@676574436f6e7472616374436f6e666967@fc3ed87a51ee659f937c1a1ed11c1ae677e99629fae9cc289461f033e6514d1a8cfad1144ae9c1b70f28554d196bd6ba1604240c1c1dc19c959e96c1c3b62d0c"
