from typing import Any, List, Optional, Protocol

from multiversx_sdk.core.smart_contract_query import (
    SmartContractQuery, SmartContractQueryResponse)


class IQueryRunner(Protocol):
    def run_query(self, query: SmartContractQuery) -> SmartContractQueryResponse:
        ...


class SmartContractQueriesController:
    def __init__(self, query_runner: IQueryRunner) -> None:
        self.query_runner = query_runner

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
