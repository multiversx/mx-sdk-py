import base64

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.transaction_on_network import (SmartContractResult,
                                                        TransactionEvent,
                                                        TransactionLogs)
from multiversx_sdk.delegation import DelegationTransactionsOutcomeParser
from multiversx_sdk.testutils.mock_transaction_on_network import \
    get_empty_transaction_on_network
from multiversx_sdk.testutils.utils import base64_topics_to_bytes


class TestDelegationTransactionsOutcomeParser:
    parser = DelegationTransactionsOutcomeParser()

    def test_parse_create_new_delegation_contract(self):
        contract_address = Address.new_from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqy8lllls62y8s5")

        encodedTopics = [
            "Q8M8GTdWSAAA",
            "Q8M8GTdWSAAA",
            "AQ==",
            "Q8M8GTdWSAAA",
            "AAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAABD///8=",
        ]

        delegate_event = TransactionEvent(
            raw={},
            address=Address.new_from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"),
            identifier="delegate",
            topics=base64_topics_to_bytes(encodedTopics),
            data=b"",
            additional_data=[]
        )

        encodedTopics = [
            "AAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAABD///8=",
            "PDXX6ssamaSgzKpTfvDMCuEJ9B9sK0AiA+Yzv7sHH1w=",
        ]

        sc_deploy_event = TransactionEvent(
            raw={},
            address=Address.new_from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqy8lllls62y8s5"),
            identifier="SCDeploy",
            topics=base64_topics_to_bytes(encodedTopics),
            data=b"",
            additional_data=[]
        )

        logs = TransactionLogs(address=Address.empty(), events=[delegate_event, sc_deploy_event])

        encoded_topics = ["b2g6sUl6beG17FCUIkFwCOTGJjoJJi5SjkP2077e6xA="]
        sc_result_event = TransactionEvent(
            raw={},
            address=Address.new_from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"),
            identifier="completedTxEvent",
            topics=base64_topics_to_bytes(encoded_topics),
            data=b"",
            additional_data=[]
        )

        sc_result_log = TransactionLogs(
            address=Address.new_from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"),
            events=[sc_result_event]
        )

        sc_result = SmartContractResult(
            raw={},
            sender=Address.new_from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqylllslmq6y6"),
            receiver=Address.new_from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"),
            data=base64.b64decode(
                "QDZmNmJAMDAwMDAwMDAwMDAwMDAwMDAwMDEwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAxMGZmZmZmZg=="),
            logs=sc_result_log
        )

        tx = get_empty_transaction_on_network()
        tx.smart_contract_results = [sc_result]
        tx.logs = logs

        outcome = self.parser.parse_create_new_delegation_contract(tx)

        assert len(outcome) == 1
        assert outcome[0].contract_address == contract_address
