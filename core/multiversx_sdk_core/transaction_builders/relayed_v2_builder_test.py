import pytest

from multiversx_sdk_core.address import Address
from multiversx_sdk_core.errors import (ErrInvalidGasLimitForInnerTransaction,
                                        ErrInvalidRelayerV2BuilderArguments)
from multiversx_sdk_core.testutils.wallets import load_wallets
from multiversx_sdk_core.transaction import Transaction, TransactionComputer
from multiversx_sdk_core.transaction_builders.relayed_v2_builder import \
    RelayedTransactionV2Builder


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
        # version is set to 1 to match the test in sdk-js-core
        inner_tx.version = 1
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
        # version is set to 1 to match the test in sdk-js-core
        inner_tx.version = 1
        inner_tx.signature = self.bob.secret_key.sign(transaction_computer.compute_bytes_for_signing(inner_tx))

        builder = RelayedTransactionV2Builder()
        builder.set_inner_transaction(inner_tx)
        builder.set_inner_transaction_gas_limit(60_000_000)
        builder.set_relayer_nonce(37)
        builder.set_network_config(network_config)
        builder.set_relayer_address(Address.new_from_bech32(self.alice.label))

        relayed_tx = builder.build()
        # version is set to 1 to match the test in sdk-js-core
        relayed_tx.version = 1

        relayed_tx.sender = self.alice.label
        relayed_tx.signature = self.alice.secret_key.sign(transaction_computer.compute_bytes_for_signing(relayed_tx))

        assert relayed_tx.nonce == 37
        assert relayed_tx.data.decode() == "relayedTxV2@000000000000000000010000000000000000000000000000000000000002ffff@0f@676574436f6e7472616374436f6e666967@b6c5262d9837853e2201de357c1cc4c9803988a42d7049d26b7785dd0ac2bd4c6a8804b6fd9cf845fe2c2a622774b1a2dbd0a417c9a0bc3f0563a85bd15e710a"
