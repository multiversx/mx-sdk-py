import pytest

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transaction_computer import TransactionComputer
from multiversx_sdk.network_providers.account_awaiter import AccountAwaiter
from multiversx_sdk.network_providers.api_network_provider import \
    ApiNetworkProvider
from multiversx_sdk.network_providers.resources import AccountOnNetwork
from multiversx_sdk.testutils.mock_network_provider import (
    MockNetworkProvider, TimelinePointMarkCompleted, TimelinePointWait)
from multiversx_sdk.testutils.utils import create_account_egld_balance
from multiversx_sdk.testutils.wallets import load_wallets


class TestAccountAwaiter:
    provider = MockNetworkProvider()
    watcher = AccountAwaiter(
        fetcher=provider,
        polling_interval_in_milliseconds=42,
        timeout_interval_in_milliseconds=42 * 42,
        patience_time_in_milliseconds=0
    )

    def test_await_on_balance_increase(self):
        alice = Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
        # alice account is created with 1000 EGLD
        initial_balance = self.provider.get_account(alice).balance

        # adds 7 EGLD to the account balance
        self.provider.mock_account_balance_timeline_by_address(
            alice,
            [TimelinePointWait(40), TimelinePointWait(40), TimelinePointWait(45), TimelinePointMarkCompleted()]
        )

        def condition(account: AccountOnNetwork):
            return account.balance == initial_balance + create_account_egld_balance(7)

        account = self.watcher.await_on_condition(alice, condition)
        assert account.balance == create_account_egld_balance(1007)

    @pytest.mark.networkInteraction
    def test_await_for_account_balance_increase_on_network(self):
        alice = load_wallets()["alice"]
        alice_address = Address.new_from_bech32(alice.label)
        frank = Address.new_from_bech32("erd1kdl46yctawygtwg2k462307dmz2v55c605737dp3zkxh04sct7asqylhyv")

        api = ApiNetworkProvider("https://devnet-api.multiversx.com")
        watcher = AccountAwaiter(fetcher=api)
        tx_computer = TransactionComputer()
        value = 100_000

        transaction = Transaction(
            sender=alice_address,
            receiver=frank,
            gas_limit=50000,
            chain_id="D",
            value=value
        )
        transaction.nonce = api.get_account(alice_address).nonce
        transaction.signature = alice.secret_key.sign(tx_computer.compute_bytes_for_signing(transaction))

        initial_balance = api.get_account(frank).balance

        def condition(account: AccountOnNetwork):
            return account.balance == initial_balance + value

        api.send_transaction(transaction)

        account_on_network = watcher.await_on_condition(frank, condition)
        assert account_on_network.balance == initial_balance + value
