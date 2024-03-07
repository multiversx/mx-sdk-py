from typing import List, Optional, Protocol, Sequence

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.interfaces import IAddress
from multiversx_sdk.core.smart_contract_query import (
    SmartContractQuery, SmartContractQueryResponse)


class IQuery(Protocol):
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


class IQueryResponse(Protocol):
    return_data: List[str]
    return_code: str
    return_message: str
    gas_used: int

    def get_return_data_parts(self) -> List[bytes]:
        ...


class INetworkProvider(Protocol):
    def query_contract(self, query: IQuery) -> IQueryResponse:
        ...


class ContractQuery(IQuery):
    def __init__(self, address: IAddress, function: str, value: int, arguments: List[bytes], caller: Optional[IAddress] = None):
        self.contract = address
        self.function = function
        self.caller = caller
        self.value = value
        self.encoded_arguments = [item.hex() for item in arguments]

    def get_contract(self) -> IAddress:
        return self.contract

    def get_function(self) -> str:
        return self.function

    def get_encoded_arguments(self) -> Sequence[str]:
        return self.encoded_arguments

    def get_caller(self) -> Optional[IAddress]:
        return self.caller

    def get_value(self) -> int:
        return self.value


class QueryRunnerAdapter:
    def __init__(self, network_provider: INetworkProvider) -> None:
        self.network_provider = network_provider

    def run_query(self, query: SmartContractQuery) -> SmartContractQueryResponse:
        legacy_query = ContractQuery(
            address=Address.new_from_bech32(query.contract),
            function=query.function,
            value=query.value if query.value else 0,
            arguments=query.arguments,
            caller=Address.new_from_bech32(query.caller) if query.caller else None
        )

        legacy_query_response = self.network_provider.query_contract(legacy_query)

        return SmartContractQueryResponse(
            function=query.function,
            return_code=legacy_query_response.return_code,
            return_message=legacy_query_response.return_message,
            return_data_parts=legacy_query_response.get_return_data_parts()
        )
