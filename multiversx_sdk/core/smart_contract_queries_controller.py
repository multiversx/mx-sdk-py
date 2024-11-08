from typing import Any, List, Optional, Protocol

from multiversx_sdk.abi import Serializer
from multiversx_sdk.abi.typesystem import (is_list_of_bytes,
                                           is_list_of_typed_values)
from multiversx_sdk.core.errors import SmartContractQueryError
from multiversx_sdk.core.smart_contract_query import (
    SmartContractQuery, SmartContractQueryResponse)


class INetworkProvider(Protocol):
    def query_contract(self, query: SmartContractQuery) -> SmartContractQueryResponse:
        ...


class IAbi(Protocol):
    def encode_endpoint_input_parameters(self, endpoint_name: str, values: List[Any]) -> List[bytes]:
        ...

    def decode_endpoint_output_parameters(self, endpoint_name: str, encoded_values: List[bytes]) -> List[Any]:
        ...


class SmartContractQueriesController:
    def __init__(self, network_provider: INetworkProvider, abi: Optional[IAbi] = None) -> None:
        self.network_provider = network_provider
        self.abi = abi
        self.serializer = Serializer()

    def query(
        self,
        contract: str,
        function: str,
        arguments: List[Any],
        caller: Optional[str] = None,
        value: Optional[int] = None
    ):
        query = self.create_query(
            contract=contract,
            function=function,
            arguments=arguments,
            caller=caller,
            value=value
        )

        query_response = self.run_query(query)
        self._raise_for_status(query_response)
        return self.parse_query_response(query_response)

    def _raise_for_status(self, query_response: SmartContractQueryResponse):
        is_ok = query_response.return_code == "ok"
        if not is_ok:
            raise SmartContractQueryError(query_response.return_code, query_response.return_message)

    def create_query(
            self,
            contract: str,
            function: str,
            arguments: List[Any],
            caller: Optional[str] = None,
            value: Optional[int] = None
    ) -> SmartContractQuery:
        prepared_arguments = self._encode_arguments(function, arguments)

        return SmartContractQuery(
            contract=contract,
            function=function,
            arguments=prepared_arguments,
            caller=caller,
            value=value
        )

    def _encode_arguments(self, function_name: str, args: List[Any]) -> List[bytes]:
        if self.abi:
            return self.abi.encode_endpoint_input_parameters(function_name, args)

        if is_list_of_typed_values(args):
            return self.serializer.serialize_to_parts(args)

        if is_list_of_bytes(args):
            return args

        raise Exception("Can't serialize arguments")

    def run_query(self, query: SmartContractQuery) -> SmartContractQueryResponse:
        return self.network_provider.query_contract(query)

    def parse_query_response(self, response: SmartContractQueryResponse) -> List[Any]:
        encoded_values = response.return_data_parts

        if self.abi:
            return self.abi.decode_endpoint_output_parameters(response.function, encoded_values)

        return encoded_values
