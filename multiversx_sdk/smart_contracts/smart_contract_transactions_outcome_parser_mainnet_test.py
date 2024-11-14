import json
from pathlib import Path

import pytest

from multiversx_sdk.network_providers.config import NetworkProviderConfig
from multiversx_sdk.network_providers.proxy_network_provider import \
    ProxyNetworkProvider
from multiversx_sdk.smart_contracts.smart_contract_transactions_outcome_parser import \
    SmartContractTransactionsOutcomeParser


@pytest.mark.mainnet
class TestSmartContractDeployMainnet:
    parser = SmartContractTransactionsOutcomeParser()
    network_config = NetworkProviderConfig(client_name="mx-sdk-py/tests")
    provider = ProxyNetworkProvider(url="https://gateway.multiversx.com", config=network_config)

    def test_should_parse_execute(self):
        records = self._load_records("execute_success")

        for tx in records:
            hash = tx["hash"]
            transaction = self.provider.get_transaction(hash)
            parsed = self.parser.parse_deploy(transaction)

            assert parsed.return_code == "ok"
            assert parsed.return_message == "ok"

    def test_should_parse_execute_error(self):
        records = self._load_records("execute_error")

        for tx in records:
            hash = tx["hash"]
            transaction = self.provider.get_transaction(hash)
            parsed = self.parser.parse_execute(transaction)
            assert len(parsed.return_code)
            assert len(parsed.return_message)
            assert len(parsed.values) == 0

    def test_should_parse_transfer_execute_success(self):
        records = self._load_records("transfer_execute_success")

        for tx in records:
            hash = tx["hash"]
            transaction = self.provider.get_transaction(hash)
            parsed = self.parser.parse_execute(transaction)

            assert parsed.return_code == "ok"
            assert parsed.return_message == "ok"

    def test_should_parse_transfer_execute_error(self):
        records = self._load_records("transfer_execute_error")

        for tx in records:
            hash = tx["hash"]
            transaction = self.provider.get_transaction(hash)
            parsed = self.parser.parse_execute(transaction)

            assert len(parsed.return_code)
            assert len(parsed.return_message)
            assert len(parsed.values) == 0

    def test_should_parse_relayed_success(self):
        records = self._load_records("relayed_success")

        for tx in records:
            hash = tx["hash"]
            transaction = self.provider.get_transaction(hash)
            parsed = self.parser.parse_execute(transaction)

            assert parsed.return_code == "ok"
            assert parsed.return_message == "ok"

    def test_should_parse_relayed_error(self):
        records = self._load_records("relayed_error")

        for tx in records:
            hash = tx["hash"]
            transaction = self.provider.get_transaction(hash)
            parsed = self.parser.parse_execute(transaction)

            assert len(parsed.return_code)
            assert len(parsed.return_message)
            assert len(parsed.values) == 0

    def _load_records(self, kind: str) -> list[dict[str, str]]:
        path = Path(__file__).parent.parent / "testutils" / "testdata" / "transactions.mainnet.json"
        with open(path, "r") as f:
            content = json.load(f)

        records_filtered = filter(lambda record: record["kind"] == kind, content)
        return list(records_filtered)
