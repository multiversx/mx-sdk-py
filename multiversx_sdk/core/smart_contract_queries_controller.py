from typing import Any, List, Optional, Protocol, Sequence

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.interfaces import IAddress
from multiversx_sdk.core.smart_contract_query import (
    SmartContractQuery, SmartContractQueryResponse)
from multiversx_sdk.network_providers.proxy_network_provider import \
    ContractQuery


class ILegacyQuery(Protocol):
    def get_contract(self) -> IAddress:
        ...

    def get_function(self) -> str:
        ...

    def get_encoded_arguments(self) -> Sequence[str]:
        ...

    def get_caller(self) -> Optional[IAddress]:
        ...

    def get_value(self) -> int:
        ...


class ILegacyQueryResponse(Protocol):
    return_data: List[str]
    return_code: str
    return_message: str
    gas_used: int

    def get_return_data_parts(self) -> List[bytes]:
        ...


class INetworkProvider(Protocol):
    def query_contract(self, query: ILegacyQuery) -> ILegacyQueryResponse:
        ...


class SmartContractQueriesController:
    def __init__(self, network_provider: INetworkProvider) -> None:
        self.network_provider = network_provider

    def create_query(
            self,
            contract: str,
            function: str,
            arguments: List[bytes],
            caller: Optional[str] = None,
            value: Optional[int] = None
    ) -> SmartContractQuery:
        return SmartContractQuery(
            contract=contract,
            function=function,
            arguments=arguments,
            caller=caller,
            value=value
        )

    def run_query(self, query: SmartContractQuery) -> SmartContractQueryResponse:
        value = query.value if query.value else 0
        caller = Address.new_from_bech32(query.caller) if query.caller else None

        legacy_query = ContractQuery(
            address=Address.new_from_bech32(query.contract),
            function=query.function,
            value=value,
            arguments=query.arguments,
            caller=caller
        )

        legacy_query_response = self.network_provider.query_contract(legacy_query)

        return SmartContractQueryResponse(
            function=query.function,
            return_code=legacy_query_response.return_code,
            return_message=legacy_query_response.return_message,
            return_data_parts=legacy_query_response.get_return_data_parts()
        )

    def parse_query_response(self, response: SmartContractQueryResponse) -> List[Any]:
        return response.return_data_parts
