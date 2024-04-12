import pytest

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transaction_computer import TransactionComputer
from multiversx_sdk.core.transaction_watcher import TransactionWatcher
from multiversx_sdk.network_providers.proxy_network_provider import \
    ProxyNetworkProvider
from multiversx_sdk.network_providers.transaction_status import \
    TransactionStatus
from multiversx_sdk.network_providers.transactions import TransactionOnNetwork
from multiversx_sdk.testutils.mock_network_provider import (
    MockNetworkProvider, TimelinePointMarkCompleted, TimelinePointWait)
from multiversx_sdk.testutils.wallets import load_wallets


class ProxyWrapper:
    def __init__(self, proxy: ProxyNetworkProvider) -> None:
        self.proxy = proxy

    def get_nonce(self, address: Address) -> int:
        return self.proxy.get_account(address).nonce

    def get_transaction(self, tx_hash: str) -> TransactionOnNetwork:
        return self.proxy.get_transaction(tx_hash, True)

    def send_transaction(self, transaction: Transaction) -> str:
        return self.proxy.send_transaction(transaction)


class TestTransactionWatcher:
    provider = MockNetworkProvider()
    watcher = TransactionWatcher(
        fetcher=provider,
        polling_interval_in_milliseconds=42,
        timeout_interval_in_milliseconds=42 * 42
    )

    def test_await_status_executed(self):
        tx_hash = "abbaabbaabbaabbaabbaabbaabbaabbaabbaabbaabbaabbaabbaabbaabbaabba"
        tx_on_network = TransactionOnNetwork()
        tx_on_network.status = TransactionStatus("unknown")
        self.provider.mock_put_transaction(tx_hash, tx_on_network)

        self.provider.mock_transaction_timeline_by_hash(
            tx_hash,
            [TimelinePointWait(40), TransactionStatus("pending"), TimelinePointWait(40), TransactionStatus("executed"), TimelinePointMarkCompleted()]
        )
        tx_from_network = self.watcher.await_completed(tx_hash)

        assert tx_from_network.status.is_executed()

    @pytest.mark.networkInteraction
    @pytest.mark.skip
    def test_on_network(self):
        transaction = Transaction(
            sender="erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
            receiver="erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
            gas_limit=50000,
            chain_id="D",
        )

        alice = load_wallets()["alice"]
        tx_computer = TransactionComputer()

        proxy = ProxyWrapper(ProxyNetworkProvider("https://devnet-api.multiversx.com"))
        watcher = TransactionWatcher(proxy)

        transaction.nonce = proxy.get_nonce(Address.new_from_bech32(alice.label))

        transaction.signature = alice.secret_key.sign(tx_computer.compute_bytes_for_signing(transaction))

        hash = proxy.send_transaction(transaction)
        tx_on_network = watcher.await_completed(hash)
        assert tx_on_network.status.is_executed()
