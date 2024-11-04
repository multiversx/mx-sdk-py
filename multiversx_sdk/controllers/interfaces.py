from typing import Any, List, Optional, Protocol, Union

from multiversx_sdk.core.interfaces import IAddress
from multiversx_sdk.core.smart_contract_query import (
    SmartContractQuery, SmartContractQueryResponse)
from multiversx_sdk.core.transaction_on_network import TransactionOnNetwork
from multiversx_sdk.network_providers.resources import AwaitingOptions


class IAccount(Protocol):
    @property
    def address(self) -> IAddress:
        ...

    def sign(self, data: bytes) -> bytes:
        ...


class INetworkProvider(Protocol):
    def query_contract(self, query: SmartContractQuery) -> SmartContractQueryResponse:
        ...

    def await_transaction_completed(self, transaction_hash: Union[str, bytes], options: Optional[AwaitingOptions] = None) -> TransactionOnNetwork:
        ...


class IAbi(Protocol):
    def encode_endpoint_input_parameters(self, endpoint_name: str, values: List[Any]) -> List[bytes]:
        ...

    def encode_constructor_input_parameters(self, values: List[Any]) -> List[bytes]:
        ...

    def encode_upgrade_constructor_input_parameters(self, values: List[Any]) -> List[bytes]:
        ...

    def decode_endpoint_output_parameters(self, endpoint_name: str, encoded_values: List[bytes]) -> List[Any]:
        ...
