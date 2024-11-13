from pathlib import Path

import pytest

from multiversx_sdk.abi.abi import Abi
from multiversx_sdk.abi.small_int_values import U64Value
from multiversx_sdk.abi.string_value import StringValue
from multiversx_sdk.network_providers.api_network_provider import \
    ApiNetworkProvider
from multiversx_sdk.smart_contracts.smart_contract_queries_controller import \
    SmartContractQueriesController
from multiversx_sdk.smart_contracts.smart_contract_query import (
    SmartContractQuery, SmartContractQueryResponse)
from multiversx_sdk.testutils.mock_network_provider import MockNetworkProvider


class TestSmartContractQueriesController:
    testdata = Path(__file__).parent.parent / "testutils" / "testdata"

    def test_create_query_without_arguments(self):
        controller = SmartContractQueriesController(MockNetworkProvider())
        contract = "erd1qqqqqqqqqqqqqpgqsnwuj85zv7t0wnxfetyqqyjvvg444lpk7uasxv8ktx"
        function = "getSum"

        query = controller.create_query(
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
        controller = SmartContractQueriesController(MockNetworkProvider())
        contract = "erd1qqqqqqqqqqqqqpgqsnwuj85zv7t0wnxfetyqqyjvvg444lpk7uasxv8ktx"
        function = "getSum"

        query = controller.create_query(
            contract=contract,
            function=function,
            arguments=[U64Value(7), StringValue("abba")]
        )

        assert query.contract == contract
        assert query.function == function
        assert query.arguments == [b'\x07', b"abba"]
        assert query.caller is None
        assert query.value is None

    def test_create_query_with_arguments_with_abi(self):
        abi = Abi.load(self.testdata / "lottery-esdt.abi.json")
        controller = SmartContractQueriesController(MockNetworkProvider(), abi)
        contract = "erd1qqqqqqqqqqqqqpgqsnwuj85zv7t0wnxfetyqqyjvvg444lpk7uasxv8ktx"
        function = "getLotteryInfo"

        query = controller.create_query(
            contract=contract,
            function=function,
            arguments=["myLottery"]
        )

        query_with_typed = controller.create_query(
            contract=contract,
            function=function,
            arguments=[StringValue("myLottery")]
        )

        assert query.contract == contract
        assert query.function == function
        assert query.arguments == [b"myLottery"]
        assert query.caller is None
        assert query.value is None

        assert query_with_typed == query

    def test_run_query_with_mock_provider(self):
        network_provider = MockNetworkProvider()
        controller = SmartContractQueriesController(network_provider)

        contract_query_response = SmartContractQueryResponse(
            function="bar",
            return_code="ok",
            return_message="",
            return_data_parts=["abba".encode()]
        )

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
        controller = SmartContractQueriesController(MockNetworkProvider())

        response = SmartContractQueryResponse(
            function="bar",
            return_code="ok",
            return_message="ok",
            return_data_parts=["abba".encode()]
        )

        parsed = controller.parse_query_response(response)
        assert parsed == ["abba".encode()]

    def test_parse_query_response_with_abi(self):
        abi = Abi.load(self.testdata / "lottery-esdt.abi.json")
        controller = SmartContractQueriesController(MockNetworkProvider(), abi)

        response = SmartContractQueryResponse(
            function="getLotteryInfo",
            return_code="ok",
            return_message="ok",
            return_data_parts=[bytes.fromhex(
                "0000000b6c75636b792d746f6b656e000000010100000000000000005fc2b9dbffffffff00000001640000000a140ec80fa7ee88000000")]
        )

        [lottery_info] = controller.parse_query_response(response)
        assert lottery_info.token_identifier == "lucky-token"
        assert lottery_info.ticket_price == 1
        assert lottery_info.tickets_left == 0
        assert lottery_info.deadline == 0x000000005fc2b9db
        assert lottery_info.max_entries_per_user == 0xffffffff
        assert lottery_info.prize_distribution == bytes([0x64])
        assert lottery_info.prize_pool == 94720000000000000000000

    @pytest.mark.networkInteraction
    def test_run_query_on_network(self):
        provider = ApiNetworkProvider("https://devnet-api.multiversx.com")
        controller = SmartContractQueriesController(provider)
        contract = "erd1qqqqqqqqqqqqqpgqsnwuj85zv7t0wnxfetyqqyjvvg444lpk7uasxv8ktx"
        function = "getSum"

        query = controller.create_query(
            contract=contract,
            function=function,
            arguments=[]
        )

        query_response = controller.run_query(query)
        assert query_response.return_code == "ok"
        assert query_response.return_message == ""
        assert query_response.return_data_parts == [b'\x05']

    @pytest.mark.networkInteraction
    def test_query_on_network(self):
        provider = ApiNetworkProvider("https://devnet-api.multiversx.com")
        controller = SmartContractQueriesController(provider)
        contract = "erd1qqqqqqqqqqqqqpgqsnwuj85zv7t0wnxfetyqqyjvvg444lpk7uasxv8ktx"
        function = "getSum"

        return_data_parts = controller.query(
            contract=contract,
            function=function,
            arguments=[]
        )

        assert return_data_parts == [b'\x05']
