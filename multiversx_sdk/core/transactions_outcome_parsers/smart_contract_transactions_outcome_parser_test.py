import re
from pathlib import Path

import pytest

from multiversx_sdk.abi.abi import Abi
from multiversx_sdk.core.address import Address
from multiversx_sdk.core.transaction_on_network import (SmartContractResult,
                                                        TransactionEvent,
                                                        TransactionLogs,
                                                        TransactionOnNetwork)
from multiversx_sdk.core.transactions_outcome_parsers.smart_contract_transactions_outcome_parser import \
    SmartContractTransactionsOutcomeParser
from multiversx_sdk.network_providers.proxy_network_provider import \
    ProxyNetworkProvider


class TestSmartContractTransactionsOutcomeParser:
    parser = SmartContractTransactionsOutcomeParser()

    def test_parse_minimalistic_deploy_outcome(self):
        contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqpgqqacl85rd0gl2q8wggl8pwcyzcr4fflc5d8ssve45cj")
        deployer = Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
        code_hash = b"abba"

        event = TransactionEvent(
            identifier="SCDeploy",
            topics=[contract.get_public_key(), deployer.get_public_key(), code_hash]
        )

        transaction = TransactionOnNetwork()
        transaction.logs = TransactionLogs(events=[event])

        parsed = self.parser.parse_deploy(transaction)
        assert len(parsed.contracts) == 1
        assert parsed.contracts[0].address == contract.to_bech32()
        assert parsed.contracts[0].owner_address == deployer.to_bech32()
        assert parsed.contracts[0].code_hash == code_hash

    def test_parse_deploy_outcome(self):
        contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqpgqqacl85rd0gl2q8wggl8pwcyzcr4fflc5d8ssve45cj")
        deployer = Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
        code_hash = bytes.fromhex("abba")

        event = TransactionEvent()
        event.identifier = "SCDeploy"
        event.topics = [
            contract.get_public_key(),
            deployer.get_public_key(),
            code_hash
        ]

        logs = TransactionLogs(events=[event])
        contract_result = SmartContractResult(data="@6f6b".encode())

        tx_on_network = TransactionOnNetwork()
        tx_on_network.nonce = 7
        tx_on_network.logs = logs
        tx_on_network.contract_results = [contract_result]

        parsed = self.parser.parse_deploy(tx_on_network)

        assert parsed.return_code == "ok"
        assert parsed.return_message == "ok"
        assert len(parsed.contracts) == 1
        assert parsed.contracts[0].address == contract.to_bech32()
        assert parsed.contracts[0].owner_address == deployer.to_bech32()
        assert parsed.contracts[0].code_hash == code_hash

    def test_parse_deploy_outcome_with_error(self):
        deployer = Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")

        event = TransactionEvent()
        event.identifier = "signalError"
        event.topics = [
            deployer.get_public_key(),
            b"wrong number of arguments",
        ]
        event.data = "@75736572206572726f72".encode()

        logs = TransactionLogs(events=[event])

        tx_on_network = TransactionOnNetwork()
        tx_on_network.nonce = 7
        tx_on_network.logs = logs

        parsed = self.parser.parse_deploy(tx_on_network)

        assert parsed.return_code == "user error"
        assert parsed.return_message == "wrong number of arguments"
        assert len(parsed.contracts) == 0
        assert parsed.contracts == []

    def test_parse_execute_outcome_with_abi(self):
        abi_path = Path(__file__).parent.parent.parent / "testutils" / "testdata" / "answer.abi.json"
        abi = Abi.load(abi_path)
        parser = SmartContractTransactionsOutcomeParser(abi)

        transaction = TransactionOnNetwork()
        transaction.function = "getUltimateAnswer"
        transaction.contract_results = [
            SmartContractResult(data="@6f6b@2a".encode())
        ]

        parsed_tx = parser.parse_execute(transaction)
        assert parsed_tx.return_code == "ok"
        assert parsed_tx.return_message == "ok"
        assert parsed_tx.values == [42]

    def test_parse_execute_without_function_name(self):
        abi_path = Path(__file__).parent.parent.parent / "testutils" / "testdata" / "answer.abi.json"
        abi = Abi.load(abi_path)
        parser = SmartContractTransactionsOutcomeParser(abi)

        transaction = TransactionOnNetwork()
        transaction.contract_results = [
            SmartContractResult(data="@6f6b@2a".encode())
        ]

        with pytest.raises(Exception, match=re.escape('Function name is not available in the transaction, thus endpoint definition (ABI) cannot be picked (for parsing). Please provide the "function" parameter explicitly.')):
            parser.parse_execute(transaction)

    @pytest.mark.networkInteraction
    def test_parse_successful_deploy(self):
        successful_tx_hash = "30bc4f262543e235b73ae6db7bcbf3a54513fe3c1ed7a86af688a8f0e7fe8655"
        proxy = ProxyNetworkProvider("https://devnet-gateway.multiversx.com")

        tx_on_network = proxy.get_transaction(successful_tx_hash)

        parsed = self.parser.parse_deploy(tx_on_network)
        assert parsed.contracts[0].address == "erd1qqqqqqqqqqqqqpgq29deu3uhcvuk7jhxd5cxrvh23xulkcewd8ssyf38ec"
        assert parsed.contracts[0].owner_address == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"

    @pytest.mark.networkInteraction
    def test_parse_failed_deploy(self):
        faied_tx_hash = "832780459c6c9589035dbbe5b8d1d86ca9674f4aab8379cbca9a94978e604ffd"
        proxy = ProxyNetworkProvider("https://devnet-gateway.multiversx.com")

        tx_on_network = proxy.get_transaction(faied_tx_hash)

        parsed = self.parser.parse_deploy(tx_on_network)
        assert len(parsed.contracts) == 0
        assert parsed.contracts == []

    @pytest.mark.networkInteraction
    def test_parse_sc_call(self):
        tx_hash = "8b599aa57d456aab573fcc1d5f409d4d00b897edbe1b7522a00604c0d64ea6cd"
        proxy = ProxyNetworkProvider("https://devnet-gateway.multiversx.com")

        tx_on_network = proxy.get_transaction(tx_hash)

        parsed = self.parser.parse_execute(tx_on_network, "getActionSigners")
        assert parsed.return_code == "ok"
        assert parsed.return_message == "ok"
        assert len(parsed.values) == 1

        expected_value = 2
        assert parsed.values == [expected_value.to_bytes(length=1, byteorder="big")]
