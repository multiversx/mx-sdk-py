import pytest

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transaction_computer import TransactionComputer
from multiversx_sdk.network_providers.proxy_network_provider import \
    ProxyNetworkProvider
from multiversx_sdk.network_providers.transaction_awaiter import \
    TransactionAwaiter
from multiversx_sdk.network_providers.transaction_status import \
    TransactionStatus
from multiversx_sdk.network_providers.transactions import TransactionOnNetwork
from multiversx_sdk.testutils.mock_network_provider import (
    MockNetworkProvider, TimelinePointMarkCompleted, TimelinePointWait)
from multiversx_sdk.testutils.wallets import load_wallets


class ProxyWrapper:
    def __init__(self, proxy: ProxyNetworkProvider) -> None:
        self.proxy = proxy

    def get_transaction(self, tx_hash: str) -> TransactionOnNetwork:
        return self.proxy.get_transaction(tx_hash, True)


class TestTransactionAwaiter:
    provider = MockNetworkProvider()
    watcher = TransactionAwaiter(
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
        alice = load_wallets()["alice"]
        proxy = ProxyNetworkProvider("https://devnet-api.multiversx.com")
        proxy_wrapper = ProxyWrapper(proxy)
        watcher = TransactionAwaiter(proxy_wrapper)
        tx_computer = TransactionComputer()

        transaction = Transaction(
            sender=alice.label,
            receiver=alice.label,
            gas_limit=50000,
            chain_id="D",
        )
        transaction.nonce = proxy.get_account(Address.new_from_bech32(alice.label)).nonce
        transaction.signature = alice.secret_key.sign(tx_computer.compute_bytes_for_signing(transaction))

        hash = proxy.send_transaction(transaction)
        tx_on_network = watcher.await_completed(hash)
        assert tx_on_network.status.is_executed()

    def test_await_on_condition(self):
        tx_hash = "abbaabbaabbaabbaabbaabbaabbaabbaabbaabbaabbaabbaabbaabbaabbaabba"
        tx_on_network = TransactionOnNetwork()
        tx_on_network.status = TransactionStatus("unknown")
        self.provider.mock_put_transaction(tx_hash, tx_on_network)

        self.provider.mock_transaction_timeline_by_hash(
            tx_hash,
            [TimelinePointWait(40), TransactionStatus("pending"), TimelinePointWait(40), TransactionStatus("pending"), TimelinePointWait(40), TransactionStatus("failed")]
        )

        def condition(tx: TransactionOnNetwork) -> bool:
            return tx.status.is_failed()

        tx_from_network = self.watcher.await_on_condition(tx_hash, condition)
        assert tx_from_network.status.is_failed()
