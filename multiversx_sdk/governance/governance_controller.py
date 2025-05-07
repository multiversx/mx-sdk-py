from typing import Optional, Protocol, Union

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.base_controller import BaseController
from multiversx_sdk.core.constants import GOVERNANCE_SMART_CONTRACT_ADDRESS_HEX
from multiversx_sdk.core.interfaces import IAccount
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transaction_on_network import TransactionOnNetwork
from multiversx_sdk.core.transactions_factory_config import TransactionsFactoryConfig
from multiversx_sdk.governance.governance_transactions_factory import (
    GovernanceTransactionsFactory,
)
from multiversx_sdk.network_providers.resources import AwaitingOptions
from multiversx_sdk.smart_contracts.smart_contract_query import (
    SmartContractQuery,
    SmartContractQueryResponse,
)


# fmt: off
class INetworkProvider(Protocol):
    def query_contract(self, query: SmartContractQuery) -> SmartContractQueryResponse:
        ...

    def await_transaction_completed(
        self, transaction_hash: Union[str, bytes], options: Optional[AwaitingOptions] = None
    ) -> TransactionOnNetwork:
        ...
# fmt: on


class GovernanceController(BaseController):
    def __init__(self, chain_id: str, network_provider: INetworkProvider, address_hrp: Optional[str] = None) -> None:
        self._factory = GovernanceTransactionsFactory(TransactionsFactoryConfig(chain_id))
        self._network_provider = network_provider
        self._governance_contract = Address.new_from_hex(GOVERNANCE_SMART_CONTRACT_ADDRESS_HEX)

    def create_transaction_for_new_proposal(
        self,
        sender: IAccount,
        nonce: int,
        github_commit_hash: str,
        start_vote_epoch: int,
        end_vote_epoch: int,
        value: int,
        native_token_amount: int,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
    ) -> Transaction:
        pass
