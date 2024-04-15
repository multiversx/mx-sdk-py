import base64
import re

import pytest

from multiversx_sdk.core.errors import ParseTransactionOutcomeError
from multiversx_sdk.core.transactions_outcome_parsers.resources import (
    SmartContractResult, TransactionEvent, TransactionLogs, TransactionOutcome)
from multiversx_sdk.core.transactions_outcome_parsers.token_management_transactions_outcome_parser import \
    TokenManagementTransactionsOutcomeParser
from multiversx_sdk.testutils.utils import base64_topics_to_bytes


class TestTokenManagementTransactionsOutcomeParser:
    parser = TokenManagementTransactionsOutcomeParser()

    def test_ensure_error(self):
        encoded_topics = ["Avk0jZ1kR+l9c76wQQoYcu4hvXPz+jxxTdqQeaCrbX8=", "dGlja2VyIG5hbWUgaXMgbm90IHZhbGlk"]
        event = TransactionEvent(
            address="erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u",
            identifier="signalError",
            topics=base64_topics_to_bytes(encoded_topics),
            data_items=[base64.b64decode("QDc1NzM2NTcyMjA2NTcyNzI2Zjcy")]
        )

        sc_result = SmartContractResult()
        logs = TransactionLogs("", [event])

        tx_outcome = TransactionOutcome(transaction_results=[sc_result], transaction_logs=logs)

        with pytest.raises(ParseTransactionOutcomeError, match=re.escape("encountered signalError: ticker name is not valid (user error)")):
            self.parser.parse_issue_fungible(tx_outcome)

    def test_parse_issue_fungible(self):
        identifier = "ZZZ-9ee87d"
        identifier_base64 = base64.b64encode(identifier.encode()).decode()
        encoded_topics = [
            identifier_base64,
            "U0VDT05E",
            "Wlpa",
            "RnVuZ2libGVFU0RU",
            "Ag=="
        ]

        event = TransactionEvent(
            address="erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2",
            identifier="issue",
            topics=base64_topics_to_bytes(encoded_topics)
        )
        empty_result = SmartContractResult()
        tx_log = TransactionLogs("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2", [event])
        tx_results_and_logs = TransactionOutcome(transaction_results=[empty_result], transaction_logs=tx_log)

        outcome = self.parser.parse_issue_fungible(tx_results_and_logs)
        assert len(outcome) == 1
        assert outcome[0].token_identifier == identifier

    def test_parse_issue_non_fungible(self):
        identifier = "NFT-f01d1e"
        identifier_base64 = base64.b64encode(identifier.encode()).decode()

        encoded_topics = [
            "TkZULWYwMWQxZQ==",
            "",
            "Y2FuVXBncmFkZQ==",
            "dHJ1ZQ==",
            "Y2FuQWRkU3BlY2lhbFJvbGVz",
            "dHJ1ZQ=="
        ]
        first_event = TransactionEvent(
            address="erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2",
            identifier="upgradeProperties",
            topics=base64_topics_to_bytes(encoded_topics)
        )

        encoded_topics = [
            "TkZULWYwMWQxZQ==",
            "",
            "",
            "RVNEVFJvbGVCdXJuRm9yQWxs"
        ]
        second_event = TransactionEvent(
            address="erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2",
            identifier="ESDTSetBurnRoleForAll",
            topics=base64_topics_to_bytes(encoded_topics)
        )

        encoded_topics = [
            identifier_base64,
            "TkZURVNU",
            "TkZU",
            "Tm9uRnVuZ2libGVFU0RU"
        ]
        third_event = TransactionEvent(
            address="erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2",
            identifier="issueNonFungible",
            topics=base64_topics_to_bytes(encoded_topics)
        )
        empty_result = SmartContractResult()
        tx_log = TransactionLogs("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2", [first_event, second_event, third_event])
        tx_results_and_logs = TransactionOutcome(transaction_results=[empty_result], transaction_logs=tx_log)

        outcome = self.parser.parse_issue_non_fungible(tx_results_and_logs)
        assert len(outcome) == 1
        assert outcome[0].token_identifier == identifier

    def test_parse_issue_semi_fungible(self):
        identifier = "SEMIFNG-2c6d9f"
        identifier_base64 = base64.b64encode(identifier.encode()).decode()

        encoded_topics = [
            identifier_base64,
            "U0VNSQ==",
            "U0VNSUZORw==",
            "U2VtaUZ1bmdpYmxlRVNEVA=="
        ]
        event = TransactionEvent(
            address="erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2",
            identifier="issueSemiFungible",
            topics=base64_topics_to_bytes(encoded_topics)
        )
        empty_result = SmartContractResult()
        tx_log = TransactionLogs("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2", [event])
        tx_results_and_logs = TransactionOutcome(transaction_results=[empty_result], transaction_logs=tx_log)

        outcome = self.parser.parse_issue_semi_fungible(tx_results_and_logs)
        assert len(outcome) == 1
        assert outcome[0].token_identifier == identifier

    def test_parse_register_meta_esdt(self):
        identifier = "METATEST-e05d11"
        identifier_base64 = base64.b64encode(identifier.encode()).decode()

        encoded_topics = [
            identifier_base64,
            "TUVURVNU",
            "TUVUQVRFU1Q=",
            "TWV0YUVTRFQ="
        ]
        event = TransactionEvent(
            address="erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2",
            identifier="registerMetaESDT",
            topics=base64_topics_to_bytes(encoded_topics)
        )
        empty_result = SmartContractResult()
        tx_log = TransactionLogs("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2", [event])
        tx_results_and_logs = TransactionOutcome(transaction_results=[empty_result], transaction_logs=tx_log)

        outcome = self.parser.parse_register_meta_esdt(tx_results_and_logs)
        assert len(outcome) == 1
        assert outcome[0].token_identifier == identifier

    def test_parse_register_and_set_all_roles(self):
        first_identifier = "LMAO-d9f892"
        first_identifier_base64 = base64.b64encode(first_identifier.encode()).decode()

        second_identifier = "TST-123456"
        second_identifier_base64 = base64.b64encode(second_identifier.encode()).decode()
        roles = ["ESDTRoleLocalMint", "ESDTRoleLocalBurn"]

        encoded_topics = [
            first_identifier_base64,
            "TE1BTw==",
            "TE1BTw==",
            "RnVuZ2libGVFU0RU",
            "Ag=="
        ]
        first_event = TransactionEvent(
            address="erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2",
            identifier="registerAndSetAllRoles",
            topics=base64_topics_to_bytes(encoded_topics)
        )

        encoded_topics = [second_identifier_base64, "TE1BTw==", "TE1BTw==", "RnVuZ2libGVFU0RU", "Ag=="]
        second_event = TransactionEvent(
            address="erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2",
            identifier="registerAndSetAllRoles",
            topics=base64_topics_to_bytes(encoded_topics)
        )

        tx_log = TransactionLogs("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2", [first_event, second_event])

        encoded_topics = [
            "TE1BTy1kOWY4OTI=",
            "",
            "",
            "RVNEVFJvbGVMb2NhbE1pbnQ=",
            "RVNEVFJvbGVMb2NhbEJ1cm4="
        ]
        first_result_event = TransactionEvent(
            address="erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2",
            identifier="ESDTSetRole",
            topics=base64_topics_to_bytes(encoded_topics)
        )

        encoded_topics = [
            "VFNULTEyMzQ1Ng==",
            "",
            "",
            "RVNEVFJvbGVMb2NhbE1pbnQ=",
            "RVNEVFJvbGVMb2NhbEJ1cm4="
        ]
        second_result_event = TransactionEvent(
            address="erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2",
            identifier="ESDTSetRole",
            topics=base64_topics_to_bytes(encoded_topics)
        )

        result_logs = TransactionLogs("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2", [first_result_event, second_result_event])
        sc_result = SmartContractResult(
            sender="erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u",
            receiver="erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2",
            data="RVNEVFNldFJvbGVANGM0ZDQxNGYyZDY0Mzk2NjM4MzkzMkA0NTUzNDQ1NDUyNmY2YzY1NGM2ZjYzNjE2YzRkNjk2ZTc0QDQ1NTM0NDU0NTI2ZjZjNjU0YzZmNjM2MTZjNDI3NTcyNmU=".encode(),
            logs=result_logs
        )

        tx_results_and_logs = TransactionOutcome(transaction_results=[sc_result], transaction_logs=tx_log)
        outcome = self.parser.parse_register_and_set_all_roles(tx_results_and_logs)

        assert len(outcome) == 2
        assert outcome[0].token_identifier == first_identifier
        assert outcome[0].roles == roles
        assert outcome[1].token_identifier == second_identifier
        assert outcome[1].roles == roles

    def test_parse_set_special_role(self):
        identifier = "METATEST-e05d11"
        identifier_base64 = base64.b64encode(identifier.encode()).decode()
        roles = ["ESDTRoleNFTCreate", "ESDTRoleNFTAddQuantity", "ESDTRoleNFTBurn"]

        encoded_roles = [
            identifier_base64,
            "",
            "",
            "RVNEVFJvbGVORlRDcmVhdGU=",
            "RVNEVFJvbGVORlRBZGRRdWFudGl0eQ==",
            "RVNEVFJvbGVORlRCdXJu"
        ]
        event = TransactionEvent(
            address="erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2",
            identifier="ESDTSetRole",
            topics=base64_topics_to_bytes(encoded_roles)
        )
        empty_result = SmartContractResult()
        tx_log = TransactionLogs("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2", [event])
        tx_results_and_logs = TransactionOutcome(transaction_results=[empty_result], transaction_logs=tx_log)

        outcome = self.parser.parse_set_special_role(tx_results_and_logs)
        assert len(outcome) == 1
        assert outcome[0].user_address == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert outcome[0].token_identifier == identifier
        assert outcome[0].roles == roles

    def test_parse_nft_create(self):
        identifier = "NFT-f01d1e"
        identifier_base64 = base64.b64encode(identifier.encode()).decode()
        nonce = 1
        initial_quantity = 1

        encoded_topics = [
            identifier_base64,
            "AQ==",
            "AQ==",
            "CAESAgABIuUBCAESCE5GVEZJUlNUGiA8NdfqyxqZpKDMqlN+8MwK4Qn0H2wrQCID5jO/uwcfXCDEEyouUW1ZM3ZKQ3NVcWpNM3hxeGR3VWczemJoVFNMUWZoN0szbW5aWXhyaGNRRFl4RzJDaHR0cHM6Ly9pcGZzLmlvL2lwZnMvUW1ZM3ZKQ3NVcWpNM3hxeGR3VWczemJoVFNMUWZoN0szbW5aWXhyaGNRRFl4Rzo9dGFnczo7bWV0YWRhdGE6UW1SY1A5NGtYcjV6WmpSR3ZpN21KNnVuN0xweFVoWVZSNFI0UnBpY3h6Z1lrdA=="
        ]
        event = TransactionEvent(
            address="erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2",
            identifier="ESDTNFTCreate",
            topics=base64_topics_to_bytes(encoded_topics)
        )
        empty_result = SmartContractResult()
        tx_log = TransactionLogs("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2", [event])
        tx_results_and_logs = TransactionOutcome(transaction_results=[empty_result], transaction_logs=tx_log)

        outcome = self.parser.parse_nft_create(tx_results_and_logs)
        assert len(outcome) == 1
        assert outcome[0].token_identifier == identifier
        assert outcome[0].nonce == nonce
        assert outcome[0].initial_quantity == initial_quantity

    def test_parse_local_mint(self):
        identifier = "AAA-29c4c9"
        identifier_base64 = base64.b64encode(identifier.encode()).decode()
        nonce = 0
        minted_supply = 100000

        encoded_topics = [
            identifier_base64,
            "",
            "AYag"
        ]
        event = TransactionEvent(
            address="erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2",
            identifier="ESDTLocalMint",
            topics=base64_topics_to_bytes(encoded_topics)
        )
        empty_result = SmartContractResult()
        tx_log = TransactionLogs("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2", [event])
        tx_results_and_logs = TransactionOutcome(transaction_results=[empty_result], transaction_logs=tx_log)

        outcome = self.parser.parse_local_mint(tx_results_and_logs)
        assert len(outcome) == 1
        assert outcome[0].user_address == event.address
        assert outcome[0].token_identifier == identifier
        assert outcome[0].nonce == nonce
        assert outcome[0].minted_supply == minted_supply

    def test_parse_local_burn(self):
        identifier = "AAA-29c4c9"
        identifier_base64 = base64.b64encode(identifier.encode()).decode()
        nonce = 0
        burnt_supply = 100000

        encoded_topics = [
            identifier_base64,
            "",
            "AYag"
        ]
        event = TransactionEvent(
            address="erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2",
            identifier="ESDTLocalBurn",
            topics=base64_topics_to_bytes(encoded_topics)
        )
        empty_result = SmartContractResult()
        tx_log = TransactionLogs("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2", [event])
        tx_results_and_logs = TransactionOutcome(transaction_results=[empty_result], transaction_logs=tx_log)

        outcome = self.parser.parse_local_burn(tx_results_and_logs)
        assert len(outcome) == 1
        assert outcome[0].user_address == event.address
        assert outcome[0].token_identifier == identifier
        assert outcome[0].nonce == nonce
        assert outcome[0].burnt_supply == burnt_supply

    def test_parse_pause(self):
        identifier = "AAA-29c4c9"
        identifier_base64 = base64.b64encode(identifier.encode()).decode()

        event = TransactionEvent(
            address="erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2",
            identifier="ESDTPause",
            topics=base64_topics_to_bytes([identifier_base64])
        )
        empty_result = SmartContractResult()
        tx_log = TransactionLogs("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2", [event])
        tx_results_and_logs = TransactionOutcome(transaction_results=[empty_result], transaction_logs=tx_log)

        outcome = self.parser.parse_pause(tx_results_and_logs)
        assert len(outcome) == 1
        assert outcome[0].token_identifier == identifier

    def test_parse_unpause(self):
        identifier = "AAA-29c4c9"
        identifier_base64 = base64.b64encode(identifier.encode()).decode()

        event = TransactionEvent(
            address="erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2",
            identifier="ESDTUnPause",
            topics=base64_topics_to_bytes([identifier_base64])
        )
        empty_result = SmartContractResult()
        tx_log = TransactionLogs("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2", [event])
        tx_results_and_logs = TransactionOutcome(transaction_results=[empty_result], transaction_logs=tx_log)

        outcome = self.parser.parse_unpause(tx_results_and_logs)
        assert len(outcome) == 1
        assert outcome[0].token_identifier == identifier

    def test_parse_freeze(self):
        identifier = "AAA-29c4c9"
        identifier_base64 = base64.b64encode(identifier.encode()).decode()
        nonce = 0
        balance = 10000000
        address = "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"

        encoded_topics = [
            identifier_base64,
            "",
            "mJaA",
            "ATlHLv9ohncamC8wg9pdQh8kwpGB5jiIIo3IHKYNaeE="
        ]
        event = TransactionEvent(
            address="erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u",
            identifier="ESDTFreeze",
            topics=base64_topics_to_bytes(encoded_topics)
        )
        tx_log = TransactionLogs("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th", [event])
        sc_result = SmartContractResult(
            sender="erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u",
            receiver="erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
            data="RVNEVEZyZWV6ZUA0MTQxNDEyZDMyMzk2MzM0NjMzOQ==".encode(),
            logs=tx_log
        )
        tx_results_and_logs = TransactionOutcome(transaction_results=[sc_result])

        outcome = self.parser.parse_freeze(tx_results_and_logs)
        assert len(outcome) == 1
        assert outcome[0].user_address == address
        assert outcome[0].token_identifier == identifier
        assert outcome[0].nonce == nonce
        assert outcome[0].balance == balance

    def test_parse_unfreeze(self):
        identifier = "AAA-29c4c9"
        identifier_base64 = base64.b64encode(identifier.encode()).decode()
        nonce = 0
        balance = 10000000
        address = "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"

        encoded_topics = [
            identifier_base64,
            "",
            "mJaA",
            "ATlHLv9ohncamC8wg9pdQh8kwpGB5jiIIo3IHKYNaeE="
        ]
        event = TransactionEvent(
            address="erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u",
            identifier="ESDTUnFreeze",
            topics=base64_topics_to_bytes(encoded_topics)
        )
        tx_log = TransactionLogs("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th", [event])
        sc_result = SmartContractResult(
            sender="erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u",
            receiver="erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
            data="RVNEVEZyZWV6ZUA0MTQxNDEyZDMyMzk2MzM0NjMzOQ==".encode(),
            logs=tx_log
        )
        tx_results_and_logs = TransactionOutcome(transaction_results=[sc_result])

        outcome = self.parser.parse_unfreeze(tx_results_and_logs)
        assert len(outcome) == 1
        assert outcome[0].user_address == address
        assert outcome[0].token_identifier == identifier
        assert outcome[0].nonce == nonce
        assert outcome[0].balance == balance

    def test_parse_wipe(self):
        identifier = "AAA-29c4c9"
        identifier_base64 = base64.b64encode(identifier.encode()).decode()
        nonce = 0
        balance = 10000000
        address = "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"

        encoded_topics = [
            identifier_base64,
            "",
            "mJaA",
            "ATlHLv9ohncamC8wg9pdQh8kwpGB5jiIIo3IHKYNaeE="
        ]
        event = TransactionEvent(
            address="erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u",
            identifier="ESDTWipe",
            topics=base64_topics_to_bytes(encoded_topics)
        )
        tx_log = TransactionLogs("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th", [event])
        sc_result = SmartContractResult(
            sender="erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u",
            receiver="erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
            data="RVNEVEZyZWV6ZUA0MTQxNDEyZDMyMzk2MzM0NjMzOQ==".encode(),
            logs=tx_log
        )
        tx_results_and_logs = TransactionOutcome(transaction_results=[sc_result])

        outcome = self.parser.parse_wipe(tx_results_and_logs)
        assert len(outcome) == 1
        assert outcome[0].user_address == address
        assert outcome[0].token_identifier == identifier
        assert outcome[0].nonce == nonce
        assert outcome[0].balance == balance

    def test_parse_update_attributes(self):
        identifier = "NFT-f01d1e"
        identifier_base64 = base64.b64encode(identifier.encode()).decode()
        nonce = 1
        attributes = "metadata:ipfsCID/test.json;tags:tag1,tag2"
        attributes_base64 = base64.b64encode(attributes.encode()).decode()

        encoded_topics = [
            identifier_base64,
            "AQ==",
            "",
            attributes_base64
        ]
        event = TransactionEvent(
            address="erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2",
            identifier="ESDTNFTUpdateAttributes",
            topics=base64_topics_to_bytes(encoded_topics)
        )
        tx_log = TransactionLogs("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th", [event])
        tx_result = SmartContractResult()
        tx_results_and_logs = TransactionOutcome(transaction_results=[tx_result], transaction_logs=tx_log)

        outcome = self.parser.parse_update_attributes(tx_results_and_logs)
        assert len(outcome) == 1
        assert outcome[0].token_identifier == identifier
        assert outcome[0].nonce == nonce
        assert outcome[0].attributes.decode() == attributes

    def test_parse_add_quantity(self):
        identifier = "NFT-f01d1e"
        identifier_base64 = base64.b64encode(identifier.encode()).decode()
        nonce = 1
        added_quantity = 10

        encoded_topics = [
            identifier_base64,
            "AQ==",
            "Cg=="
        ]
        event = TransactionEvent(
            address="erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2",
            identifier="ESDTNFTAddQuantity",
            topics=base64_topics_to_bytes(encoded_topics)
        )
        tx_log = TransactionLogs("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th", [event])
        tx_result = SmartContractResult()
        tx_results_and_logs = TransactionOutcome(transaction_results=[tx_result], transaction_logs=tx_log)

        outcome = self.parser.parse_add_quantity(tx_results_and_logs)
        assert len(outcome) == 1
        assert outcome[0].token_identifier == identifier
        assert outcome[0].nonce == nonce
        assert outcome[0].added_quantity == added_quantity

    def test_parse_burn_quantity(self):
        identifier = "NFT-f01d1e"
        identifier_base64 = base64.b64encode(identifier.encode()).decode()
        nonce = 1
        burnt_quantity = 16

        encoded_topics = [
            identifier_base64,
            "AQ==",
            "EA=="
        ]
        event = TransactionEvent(
            address="erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2",
            identifier="ESDTNFTBurn",
            topics=base64_topics_to_bytes(encoded_topics)
        )
        tx_log = TransactionLogs("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th", [event])
        tx_result = SmartContractResult()
        tx_results_and_logs = TransactionOutcome(transaction_results=[tx_result], transaction_logs=tx_log)

        outcome = self.parser.parse_burn_quantity(tx_results_and_logs)
        assert len(outcome) == 1
        assert outcome[0].token_identifier == identifier
        assert outcome[0].nonce == nonce
        assert outcome[0].burnt_quantity == burnt_quantity
