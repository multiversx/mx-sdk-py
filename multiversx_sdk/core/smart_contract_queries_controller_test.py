import base64

import pytest

from multiversx_sdk.adapters.query_runner_adapter import QueryRunnerAdapter
from multiversx_sdk.core.codec import encode_unsigned_number
from multiversx_sdk.core.smart_contract_queries_controller import \
    SmartContractQueriesController
from multiversx_sdk.core.smart_contract_query import (
    SmartContractQuery, SmartContractQueryResponse)
from multiversx_sdk.network_providers.contract_query_response import \
    ContractQueryResponse
from multiversx_sdk.network_providers.proxy_network_provider import \
    ProxyNetworkProvider
from multiversx_sdk.testutils.mock_network_provider import MockNetworkProvider


class TestSmartContractQueriesController:
    provider = ProxyNetworkProvider("https://devnet-api.multiversx.com")
    query_runner = QueryRunnerAdapter(network_provider=provider)
    controller = SmartContractQueriesController(query_runner=query_runner)

    def test_create_query_without_arguments(self):
        contract = "erd1qqqqqqqqqqqqqpgqsnwuj85zv7t0wnxfetyqqyjvvg444lpk7uasxv8ktx"
        function = "getSum"

        query = self.controller.create_query(
            contract=contract,
            function=function,
            arguments=[]
        )
        assert query.contract == contract
        assert query.function == function
        assert query.arguments == []
        assert query.caller is None
        assert query.value is None

    def test_create_query_with_arguments(self):
        contract = "erd1qqqqqqqqqqqqqpgqsnwuj85zv7t0wnxfetyqqyjvvg444lpk7uasxv8ktx"
        function = "getSum"

        query = self.controller.create_query(
            contract=contract,
            function=function,
            arguments=[encode_unsigned_number(7), "abba".encode()]
        )
        assert query.contract == contract
        assert query.function == function
        assert query.arguments == [encode_unsigned_number(7), "abba".encode()]
        assert query.caller is None
        assert query.value is None

    def test_run_query_with_mock_provider(self):
        network_provider = MockNetworkProvider()
        query_runner = QueryRunnerAdapter(network_provider=network_provider)
        controller = SmartContractQueriesController(query_runner)

        contract_query_response = ContractQueryResponse()
        contract_query_response.return_code = "ok"
        contract_query_response.return_data = [base64.b64encode("abba".encode()).decode()]

        network_provider.mock_query_contract_on_function("bar", contract_query_response)

        query = SmartContractQuery(
            contract="erd1qqqqqqqqqqqqqpgqvc7gdl0p4s97guh498wgz75k8sav6sjfjlwqh679jy",
            function="bar",
            arguments=[]
        )

        response = controller.run_query(query)
        assert response.return_code == "ok"
        assert response.return_data_parts == ["abba".encode()]

    def test_parse_query_response(self):
        network_provider = MockNetworkProvider()
        query_runner = QueryRunnerAdapter(network_provider=network_provider)
        controller = SmartContractQueriesController(query_runner)

        response = SmartContractQueryResponse(
            function="bar",
            return_code="ok",
            return_message="ok",
            return_data_parts=["abba".encode()]
        )

        parsed = controller.parse_query_response(response)
        assert parsed == ["abba".encode()]

    @pytest.mark.networkInteraction
    def test_run_query_on_network(self):
        contract = "erd1qqqqqqqqqqqqqpgqsnwuj85zv7t0wnxfetyqqyjvvg444lpk7uasxv8ktx"
        function = "getSum"

        query = self.controller.create_query(
            contract=contract,
            function=function,
            arguments=[]
        )

        query_response = self.controller.run_query(query)
        assert query_response.return_code == "ok"
        assert query_response.return_message == ""
        assert query_response.return_data_parts == [b'\x05']

    @pytest.mark.networkInteraction
    def test_query_on_network(self):
        contract = "erd1qqqqqqqqqqqqqpgqsnwuj85zv7t0wnxfetyqqyjvvg444lpk7uasxv8ktx"
        function = "getSum"

        return_data_parts = self.controller.query(
            contract=contract,
            function=function,
            arguments=[]
        )

        assert return_data_parts == [b'\x05']
