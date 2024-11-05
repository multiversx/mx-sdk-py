import threading
import time
from typing import Any, Callable, Dict, List, Union

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.smart_contract_query import (
    SmartContractQuery, SmartContractQueryResponse)
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transaction_computer import TransactionComputer
from multiversx_sdk.core.transaction_on_network import (SmartContractResult,
                                                        TransactionOnNetwork)
from multiversx_sdk.core.transaction_status import TransactionStatus
from multiversx_sdk.network_providers.resources import AccountOnNetwork
from multiversx_sdk.testutils.utils import create_account_egld_balance


class MockNetworkProvider:
    alice = Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
    bob = Address.new_from_bech32("erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx")
    carol = Address.new_from_bech32("erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8")

    def __init__(self) -> None:
        self.transactions: Dict[str, TransactionOnNetwork] = {}

        alice_account = AccountOnNetwork(
            raw={},
            address=MockNetworkProvider.alice.to_bech32(),
            nonce=0,
            balance=create_account_egld_balance(1000),
            is_guarded=False
        )

        bob_account = AccountOnNetwork(
            raw={},
            address=MockNetworkProvider.bob.to_bech32(),
            nonce=5,
            balance=create_account_egld_balance(500),
            is_guarded=False
        )

        carol_account = AccountOnNetwork(
            raw={},
            address=MockNetworkProvider.carol.to_bech32(),
            nonce=42,
            balance=create_account_egld_balance(300),
            is_guarded=False
        )

        self.accounts: Dict[str, AccountOnNetwork] = {
            MockNetworkProvider.alice.to_bech32(): alice_account,
            MockNetworkProvider.bob.to_bech32(): bob_account,
            MockNetworkProvider.carol.to_bech32(): carol_account
        }
        self.query_contract_responders: List[QueryContractResponder] = []
        self.get_transaction_responders: List[GetTransactionResponder] = []

    def mock_update_account(self, address: Address, mutate: Callable[[AccountOnNetwork], None]) -> None:
        account = self.accounts.get(address.to_bech32(), None)

        if account:
            mutate(account)

    def mock_update_transaction(self, hash: str, mutate: Callable[[TransactionOnNetwork], None]) -> None:
        transaction = self.transactions.get(hash, None)

        if transaction:
            mutate(transaction)

    def mock_put_transaction(self, hash: str, transaction: TransactionOnNetwork) -> None:
        transaction.is_completed = False
        self.transactions[hash] = transaction

    def mock_query_contract_on_function(self, function: str, response: SmartContractQueryResponse) -> None:
        def predicate(query: SmartContractQuery) -> bool:
            return query.function == function

        self.query_contract_responders.append(QueryContractResponder(predicate, response))

    def mock_get_transaction_with_any_hash_as_completed_with_one_result(self, return_code_and_data: str) -> None:
        def predicate(hash: str) -> bool:
            return True

        response = TransactionOnNetwork()
        response.status = TransactionStatus("executed")
        response.contract_results = [SmartContractResult(data=return_code_and_data.encode())]
        response.is_completed = True

        self.get_transaction_responders.insert(0, GetTransactionResponder(predicate, response))

    def mock_transaction_timeline(self, transaction: Transaction, timeline_points: List[Any]) -> None:
        tx_computer = TransactionComputer()
        tx_hash = tx_computer.compute_transaction_hash(transaction).hex()
        self.mock_transaction_timeline_by_hash(tx_hash, timeline_points)

    def mock_transaction_timeline_by_hash(self, hash: str, timeline_points: List[Any]) -> None:
        def fn():
            for point in timeline_points:
                if isinstance(point, TransactionStatus):
                    def set_tx_status(transaction: TransactionOnNetwork):
                        transaction.status = point

                    self.mock_update_transaction(hash, set_tx_status)

                elif isinstance(point, TimelinePointMarkCompleted):
                    def mark_tx_as_completed(transaction: TransactionOnNetwork):
                        transaction.is_completed = True

                    self.mock_update_transaction(hash, mark_tx_as_completed)

                elif isinstance(point, TimelinePointWait):
                    time.sleep(point.milliseconds // 1000)

        thread = threading.Thread(target=fn)
        thread.start()

    def get_account(self, address: Address) -> AccountOnNetwork:
        account = self.accounts.get(address.to_bech32(), None)

        if account:
            return account

        raise Exception("Account not found")

    def get_transaction(self, transaction_hash: Union[str, bytes]) -> TransactionOnNetwork:
        if isinstance(transaction_hash, bytes):
            transaction_hash = transaction_hash.hex()

        for responder in self.get_transaction_responders:
            if responder.matches(transaction_hash):
                return responder.response

        transaction = self.transactions.get(transaction_hash, None)
        if transaction:
            return transaction

        raise Exception("Transaction not found")

    def get_transaction_status(self, tx_hash: str) -> TransactionStatus:
        transaction = self.get_transaction(tx_hash)
        return transaction.status

    def query_contract(self, query: SmartContractQuery) -> SmartContractQueryResponse:
        for responder in self.query_contract_responders:
            if responder.matches(query):
                return responder.response

        raise Exception("No query response to return")


class QueryContractResponder:
    def __init__(self, matches: Callable[[SmartContractQuery], bool], response: SmartContractQueryResponse) -> None:
        self.matches = matches
        self.response = response


class GetTransactionResponder:
    def __init__(self, matches: Callable[[str], bool], response: TransactionOnNetwork) -> None:
        self.matches = matches
        self.response = response


class TimelinePointWait:
    def __init__(self, time_in_milliseconds: int) -> None:
        self.milliseconds = time_in_milliseconds


class TimelinePointMarkCompleted:
    pass
