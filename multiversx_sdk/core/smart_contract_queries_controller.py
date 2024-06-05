from typing import Any, List, Optional, Protocol

from multiversx_sdk.core.errors import SmartContractQueryError
from multiversx_sdk.core.smart_contract_query import (
    SmartContractQuery, SmartContractQueryResponse)


class IQueryRunner(Protocol):
    def run_query(self, query: SmartContractQuery) -> SmartContractQueryResponse:
        ...


class SmartContractQueriesController:
    def __init__(self, query_runner: IQueryRunner) -> None:
        self.query_runner = query_runner

    def query(
        self,
        contract: str,
        function: str,
        arguments: List[bytes],
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
        query_response = self.query_runner.run_query(query)
        return query_response

    def parse_query_response(self, response: SmartContractQueryResponse) -> List[Any]:
        return response.return_data_parts
