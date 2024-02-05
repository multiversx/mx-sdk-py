import re

import pytest

from multiversx_sdk.core.errors import ParseTransactionOutcomeError
from multiversx_sdk.core.transaction_outcome_parsers.resources import (
    SmartContractResult, TransactionEvent, TransactionLogs, TransactionOutcome)
from multiversx_sdk.core.transaction_outcome_parsers.token_management_transactions_outcome_parser import \
    TokenManagementTransactionsOutcomeParser


class TestTokenManagementTransactionsOutcomeParser:
    parser = TokenManagementTransactionsOutcomeParser()

    def test_ensure_error(self):
        event = TransactionEvent(
            address="erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u",
            identifier="signalError",
            topics=["Avk0jZ1kR+l9c76wQQoYcu4hvXPz+jxxTdqQeaCrbX8=", "dGlja2VyIG5hbWUgaXMgbm90IHZhbGlk"],
            data="QDc1NzM2NTcyMjA2NTcyNzI2Zjcy"
        )

        with pytest.raises(ParseTransactionOutcomeError, match=re.escape("encountered signalError: ticker name is not valid (user error)")):
            self.parser.ensure_no_error([event])

        event = TransactionEvent(
            address="erd1qqqqqqqqqqqqqpgq50wpucem6hvn0g8mwa670fznqz4n38h9d8ss564tlz",
            identifier="writeLog",
            topics=["ATlHLv9ohncamC8wg9pdQh8kwpGB5jiIIo3IHKYNaeE=",
                    "QHRvbyBtdWNoIGdhcyBwcm92aWRlZCBmb3IgcHJvY2Vzc2luZzogZ2FzIHByb3ZpZGVkID0gOTc4MzIwMDAsIGdhcyB1c2VkID0gNTg5MTc1"],
            data="QDc1NzM2NTcyMjA2NTcyNzI2Zjcy"
        )
        self.parser.ensure_no_error([event])

    def test_parse_issue_fungible(self):
        event = TransactionEvent(
            address="erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2",
            identifier="issue",
            topics=[
                "WlpaLTllZTg3ZA==",
                "U0VDT05E",
                "Wlpa",
                "RnVuZ2libGVFU0RU",
                "Ag=="
            ]
        )
        empty_result = SmartContractResult()
        tx_log = TransactionLogs("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2", [event])
        tx_results_and_logs = TransactionOutcome([empty_result], tx_log)

        outcome = self.parser.parse_issue_fungible(tx_results_and_logs)
        assert outcome.identifier == "ZZZ-9ee87d"

    def test_parse_issue_non_fungible(self):
        first_event = TransactionEvent(
            address="erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2",
            identifier="upgradeProperties",
            topics=["TkZULWYwMWQxZQ==",
                    "",
                    "Y2FuVXBncmFkZQ==",
                    "dHJ1ZQ==",
                    "Y2FuQWRkU3BlY2lhbFJvbGVz",
                    "dHJ1ZQ=="
                    ]
        )

        second_event = TransactionEvent(
            address="erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2",
            identifier="ESDTSetBurnRoleForAll",
            topics=["TkZULWYwMWQxZQ==",
                    "",
                    "",
                    "RVNEVFJvbGVCdXJuRm9yQWxs"
                    ]
        )

        third_event = TransactionEvent(
            address="erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2",
            identifier="issueNonFungible",
            topics=["TkZULWYwMWQxZQ==",
                    "TkZURVNU",
                    "TkZU",
                    "Tm9uRnVuZ2libGVFU0RU"
                    ]
        )
        empty_result = SmartContractResult()
        tx_log = TransactionLogs("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2", [first_event, second_event, third_event])
        tx_results_and_logs = TransactionOutcome([empty_result], tx_log)

        outcome = self.parser.parse_issue_non_fungible(tx_results_and_logs)
        assert outcome.identifier == "NFT-f01d1e"

    def test_parse_issue_semi_fungible(self):
        event = TransactionEvent(
            address="erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2",
            identifier="issueSemiFungible",
            topics=[
                "U0VNSUZORy0yYzZkOWY=",
                "U0VNSQ==",
                "U0VNSUZORw==",
                "U2VtaUZ1bmdpYmxlRVNEVA=="
            ]
        )
        empty_result = SmartContractResult()
        tx_log = TransactionLogs("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2", [event])
        tx_results_and_logs = TransactionOutcome([empty_result], tx_log)

        outcome = self.parser.parse_issue_semi_fungible(tx_results_and_logs)
        assert outcome.identifier == "SEMIFNG-2c6d9f"

    def test_parse_register_meta_esdt(self):
        event = TransactionEvent(
            address="erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2",
            identifier="registerMetaESDT",
            topics=[
                "TUVUQVRFU1QtZTA1ZDEx",
                "TUVURVNU",
                "TUVUQVRFU1Q=",
                "TWV0YUVTRFQ="
            ]
        )
        empty_result = SmartContractResult()
        tx_log = TransactionLogs("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2", [event])
        tx_results_and_logs = TransactionOutcome([empty_result], tx_log)

        outcome = self.parser.parse_register_meta_esdt(tx_results_and_logs)
        assert outcome.identifier == "METATEST-e05d11"

    def test_parse_register_and_set_all_roles(self):
        event = TransactionEvent(
            address="erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2",
            identifier="registerAndSetAllRoles",
            topics=[
                "TE1BTy1kOWY4OTI=",
                "TE1BTw==",
                "TE1BTw==",
                "RnVuZ2libGVFU0RU",
                "Ag=="
            ]
        )
        tx_log = TransactionLogs("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2", [event])

        result_event = TransactionEvent(
            address="erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2",
            identifier="ESDTSetRole",
            topics=[
                "TE1BTy1kOWY4OTI=",
                "",
                "",
                "RVNEVFJvbGVMb2NhbE1pbnQ=",
                "RVNEVFJvbGVMb2NhbEJ1cm4="
            ]
        )
        result_log = TransactionLogs("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2", [result_event])
        sc_result = SmartContractResult(
            hash="777a55e938a76ae57c832e235ee6360c03f4d80e7fee10ed5e71a9ba293d1ea2",
            timestamp=1706171168,
            sender="erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u",
            receiver="erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2",
            data="RVNEVFNldFJvbGVANGM0ZDQxNGYyZDY0Mzk2NjM4MzkzMkA0NTUzNDQ1NDUyNmY2YzY1NGM2ZjYzNjE2YzRkNjk2ZTc0QDQ1NTM0NDU0NTI2ZjZjNjU0YzZmNjM2MTZjNDI3NTcyNmU=",
            original_tx_hash="24b8bb9782c07092e8ce75b819690de58839f650a1287e27bbcc652c6d310664",
            miniblock_hash="042835c44b06cf0cbf0d26e903873a71f1418598dbbf8dde5f5e1616498ffa03",
            logs=result_log
        )

        tx_results_and_logs = TransactionOutcome([sc_result], tx_log)
        outcome = self.parser.parse_register_and_set_all_roles(tx_results_and_logs)

        assert outcome.token_identifier == "LMAO-d9f892"
        assert outcome.roles == ["ESDTRoleLocalMint", "ESDTRoleLocalBurn"]

    def test_parse_set_special_role(self):
        event = TransactionEvent(
            address="erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2",
            identifier="ESDTSetRole",
            topics=[
                "TUVUQVRFU1QtZTA1ZDEx",
                "",
                "",
                "RVNEVFJvbGVORlRDcmVhdGU=",
                "RVNEVFJvbGVORlRBZGRRdWFudGl0eQ==",
                "RVNEVFJvbGVORlRCdXJu"
            ]
        )
        empty_result = SmartContractResult()
        tx_log = TransactionLogs("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2", [event])
        tx_results_and_logs = TransactionOutcome([empty_result], tx_log)

        outcome = self.parser.parse_set_special_role(tx_results_and_logs)
        assert outcome.user_address == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert outcome.token_identifier == "METATEST-e05d11"
        assert outcome.roles == ["ESDTRoleNFTCreate", "ESDTRoleNFTAddQuantity", "ESDTRoleNFTBurn"]

    def test_parse_nft_create(self):
        event = TransactionEvent(
            address="erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2",
            identifier="ESDTNFTCreate",
            topics=[
                "TkZULWYwMWQxZQ==",
                "AQ==",
                "AQ==",
                "CAESAgABIuUBCAESCE5GVEZJUlNUGiA8NdfqyxqZpKDMqlN+8MwK4Qn0H2wrQCID5jO/uwcfXCDEEyouUW1ZM3ZKQ3NVcWpNM3hxeGR3VWczemJoVFNMUWZoN0szbW5aWXhyaGNRRFl4RzJDaHR0cHM6Ly9pcGZzLmlvL2lwZnMvUW1ZM3ZKQ3NVcWpNM3hxeGR3VWczemJoVFNMUWZoN0szbW5aWXhyaGNRRFl4Rzo9dGFnczo7bWV0YWRhdGE6UW1SY1A5NGtYcjV6WmpSR3ZpN21KNnVuN0xweFVoWVZSNFI0UnBpY3h6Z1lrdA=="
            ]
        )
        empty_result = SmartContractResult()
        tx_log = TransactionLogs("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2", [event])
        tx_results_and_logs = TransactionOutcome([empty_result], tx_log)

        outcome = self.parser.parse_nft_create(tx_results_and_logs)
        assert outcome.token_identifier == "NFT-f01d1e"
        assert outcome.nonce == 1
        assert outcome.initial_quantity == 1

    def test_parse_local_mint(self):
        event = TransactionEvent(
            address="erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2",
            identifier="ESDTLocalMint",
            topics=[
                "QUFBLTI5YzRjOQ==",
                "",
                "AYag"
            ]
        )
        empty_result = SmartContractResult()
        tx_log = TransactionLogs("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2", [event])
        tx_results_and_logs = TransactionOutcome([empty_result], tx_log)

        outcome = self.parser.parse_local_mint(tx_results_and_logs)
        assert outcome.user_address == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert outcome.token_identifier == "AAA-29c4c9"
        assert outcome.nonce == 0
        assert outcome.minted_supply == 100000

    def test_parse_local_burn(self):
        event = TransactionEvent(
            address="erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2",
            identifier="ESDTLocalBurn",
            topics=[
                "QUFBLTI5YzRjOQ==",
                "",
                "AYag"
            ]
        )
        empty_result = SmartContractResult()
        tx_log = TransactionLogs("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2", [event])
        tx_results_and_logs = TransactionOutcome([empty_result], tx_log)

        outcome = self.parser.parse_local_burn(tx_results_and_logs)
        assert outcome.user_address == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert outcome.token_identifier == "AAA-29c4c9"
        assert outcome.nonce == 0
        assert outcome.burnt_supply == 100000

    def test_parse_pause(self):
        event = TransactionEvent(
            address="erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2",
            identifier="ESDTPause",
            topics=[
                "QUFBLTI5YzRjOQ=="
            ]
        )
        empty_result = SmartContractResult()
        tx_log = TransactionLogs("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2", [event])
        tx_results_and_logs = TransactionOutcome([empty_result], tx_log)

        outcome = self.parser.parse_pause(tx_results_and_logs)
        assert outcome.identifier == "AAA-29c4c9"

    def test_parse_unpause(self):
        event = TransactionEvent(
            address="erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2",
            identifier="ESDTUnPause",
            topics=[
                "QUFBLTI5YzRjOQ=="
            ]
        )
        empty_result = SmartContractResult()
        tx_log = TransactionLogs("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2", [event])
        tx_results_and_logs = TransactionOutcome([empty_result], tx_log)

        outcome = self.parser.parse_unpause(tx_results_and_logs)
        assert outcome.identifier == "AAA-29c4c9"

    def test_parse_freeze(self):
        event = TransactionEvent(
            address="erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u",
            identifier="ESDTFreeze",
            topics=[
                "QUFBLTI5YzRjOQ==",
                "",
                "mJaA",
                "ATlHLv9ohncamC8wg9pdQh8kwpGB5jiIIo3IHKYNaeE="
            ]
        )
        tx_log = TransactionLogs("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th", [event])
        sc_result = SmartContractResult(
            hash="db39f9a792f56641aff6196d542d6aff437a6cb8b39c78c6b8b48b5a7830d714",
            timestamp=1706177672,
            sender="erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u",
            receiver="erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
            data="RVNEVEZyZWV6ZUA0MTQxNDEyZDMyMzk2MzM0NjMzOQ==",
            original_tx_hash="1594205eff82126a8c34da4db46fcf6a7838b953317f6c1186b6a514be91895d",
            miniblock_hash="a6a783d73d61d93041aa04382107f92a704fcfcf42567bdd7a045c7cd5c97c4a",
            logs=tx_log
        )
        tx_results_and_logs = TransactionOutcome([sc_result], TransactionLogs())

        outcome = self.parser.parse_freeze(tx_results_and_logs)
        assert outcome.user_address == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert outcome.token_identifier == "AAA-29c4c9"
        assert outcome.nonce == 0
        assert outcome.balance == 10000000

    def test_parse_unfreeze(self):
        event = TransactionEvent(
            address="erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u",
            identifier="ESDTUnFreeze",
            topics=[
                "QUFBLTI5YzRjOQ==",
                "",
                "mJaA",
                "ATlHLv9ohncamC8wg9pdQh8kwpGB5jiIIo3IHKYNaeE="
            ]
        )
        tx_log = TransactionLogs("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th", [event])
        sc_result = SmartContractResult(
            hash="db39f9a792f56641aff6196d542d6aff437a6cb8b39c78c6b8b48b5a7830d714",
            timestamp=1706177672,
            sender="erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u",
            receiver="erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
            data="RVNEVEZyZWV6ZUA0MTQxNDEyZDMyMzk2MzM0NjMzOQ==",
            original_tx_hash="1594205eff82126a8c34da4db46fcf6a7838b953317f6c1186b6a514be91895d",
            miniblock_hash="a6a783d73d61d93041aa04382107f92a704fcfcf42567bdd7a045c7cd5c97c4a",
            logs=tx_log
        )
        tx_results_and_logs = TransactionOutcome([sc_result], TransactionLogs())

        outcome = self.parser.parse_unfreeze(tx_results_and_logs)
        assert outcome.user_address == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert outcome.token_identifier == "AAA-29c4c9"
        assert outcome.nonce == 0
        assert outcome.balance == 10000000

    def test_parse_wipe(self):
        event = TransactionEvent(
            address="erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u",
            identifier="ESDTWipe",
            topics=[
                "QUFBLTI5YzRjOQ==",
                "",
                "mJaA",
                "ATlHLv9ohncamC8wg9pdQh8kwpGB5jiIIo3IHKYNaeE="
            ]
        )
        tx_log = TransactionLogs("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th", [event])
        sc_result = SmartContractResult(
            hash="6e5baf006ee871d856360ae7ac4e4e3b3ad756db532b218601f236461583c511",
            timestamp=1706177672,
            sender="erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u",
            receiver="erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
            data="RVNEVEZyZWV6ZUA0MTQxNDEyZDMyMzk2MzM0NjMzOQ==",
            original_tx_hash="1594205eff82126a8c34da4db46fcf6a7838b953317f6c1186b6a514be91895d",
            miniblock_hash="a6a783d73d61d93041aa04382107f92a704fcfcf42567bdd7a045c7cd5c97c4a",
            logs=tx_log
        )
        tx_results_and_logs = TransactionOutcome([sc_result], TransactionLogs())

        outcome = self.parser.parse_wipe(tx_results_and_logs)
        assert outcome.user_address == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert outcome.token_identifier == "AAA-29c4c9"
        assert outcome.nonce == 0
        assert outcome.balance == 10000000

    def test_parse_update_attributes(self):
        event = TransactionEvent(
            address="erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2",
            identifier="ESDTNFTUpdateAttributes",
            topics=[
                "TkZULWYwMWQxZQ==",
                "AQ==",
                "",
                "bWV0YWRhdGE6aXBmc0NJRC90ZXN0Lmpzb247dGFnczp0YWcxLHRhZzI="
            ]
        )
        tx_log = TransactionLogs("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th", [event])
        tx_result = SmartContractResult()
        tx_results_and_logs = TransactionOutcome([tx_result], tx_log)

        outcome = self.parser.parse_update_attributes(tx_results_and_logs)
        assert outcome.token_identifier == "NFT-f01d1e"
        assert outcome.nonce == 1
        assert outcome.attributes.decode() == "metadata:ipfsCID/test.json;tags:tag1,tag2"

    def test_parse_add_quantity(self):
        event = TransactionEvent(
            address="erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2",
            identifier="ESDTNFTAddQuantity",
            topics=[
                "U0VNSUZORy0yYzZkOWY=",
                "AQ==",
                "Cg=="
            ]
        )
        tx_log = TransactionLogs("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th", [event])
        tx_result = SmartContractResult()
        tx_results_and_logs = TransactionOutcome([tx_result], tx_log)

        outcome = self.parser.parse_add_quantity(tx_results_and_logs)
        assert outcome.token_identifier == "SEMIFNG-2c6d9f"
        assert outcome.nonce == 1
        assert outcome.added_quantity == 10

    def test_parse_burn_quantity(self):
        event = TransactionEvent(
            address="erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2",
            identifier="ESDTNFTBurn",
            topics=[
                "U0VNSUZORy0yYzZkOWY=",
                "AQ==",
                "EA=="
            ]
        )
        tx_log = TransactionLogs("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th", [event])
        tx_result = SmartContractResult()
        tx_results_and_logs = TransactionOutcome([tx_result], tx_log)

        outcome = self.parser.parse_burn_quantity(tx_results_and_logs)
        assert outcome.token_identifier == "SEMIFNG-2c6d9f"
        assert outcome.nonce == 1
        assert outcome.burnt_quantity == 16
