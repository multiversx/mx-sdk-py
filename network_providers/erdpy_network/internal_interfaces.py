from typing import Protocol, Any, List, Tuple
from erdpy_network.interface import IContractQuery
from erdpy_network.contract_query_response import ContractQueryResponse
from erdpy_network.transactions import TransactionOnNetwork
from erdpy_network.interface import IAddress
from erdpy_network.accounts import AccountsOnNetwork


class INetworkProvider(Protocol):
    def get_account(self, address: IAddress) -> AccountsOnNetwork:
        return AccountsOnNetwork()

    def get_account_nonce(self, address: IAddress) -> int:
        return 0

    def get_transaction(self, tx_hash: str) -> TransactionOnNetwork:
        return TransactionOnNetwork()

    def send_transaction(self, payload: Any) -> str:
        return ""

    def send_transactions(self, payload: List[Any]) -> Tuple[int, List[str]]:
        return 0, []

    def send_transaction_and_wait_for_result(self, payload: Any, num_seconds_timeout: int) -> TransactionOnNetwork:
        return TransactionOnNetwork()

    def query_contract(self, payload: IContractQuery) -> ContractQueryResponse:
        return ContractQueryResponse()
