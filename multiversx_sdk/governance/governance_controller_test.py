import base64
from pathlib import Path

from multiversx_sdk.accounts.account import Account
from multiversx_sdk.core.address import Address
from multiversx_sdk.governance.governance_controller import GovernanceController
from multiversx_sdk.governance.resources import VoteType
from multiversx_sdk.network_providers.proxy_network_provider import ProxyNetworkProvider
from multiversx_sdk.smart_contracts.smart_contract_query import (
    SmartContractQueryResponse,
)
from multiversx_sdk.testutils.mock_network_provider import MockNetworkProvider


class TestGovernanceController:
    proxy = ProxyNetworkProvider("https://devnet-gateway.multiversx.com")
    controller = GovernanceController(chain_id="D", network_provider=proxy)
    commit_hash = "1db734c0315f9ec422b88f679ccfe3e0197b9d67"
    governance_address = "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqrlllsrujgla"

    testdata = Path(__file__).parent.parent / "testutils" / "testdata"
    testwallets = Path(__file__).parent.parent / "testutils" / "testwallets"
    alice = Account.new_from_pem(testwallets / "alice.pem")

    def test_create_transaction_for_new_proposal(self):
        transaction = self.controller.create_transaction_for_new_proposal(
            sender=self.alice,
            nonce=self.alice.get_nonce_then_increment(),
            commit_hash=self.commit_hash,
            start_vote_epoch=10,
            end_vote_epoch=15,
            native_token_amount=1000_000000000000000000,
        )

        assert transaction.sender == self.alice.address
        assert transaction.receiver.to_bech32() == self.governance_address
        assert transaction.chain_id == "D"
        assert transaction.value == 1000_000000000000000000
        assert transaction.gas_limit == 50_192_500
        assert transaction.data.decode() == f"proposal@{self.commit_hash.encode().hex()}@0a@0f"

    def test_create_transaction_for_voting(self):
        transaction = self.controller.create_transaction_for_voting(
            sender=self.alice,
            nonce=self.alice.get_nonce_then_increment(),
            proposal_nonce=1,
            vote=VoteType.YES,
        )

        assert transaction.sender == self.alice.address
        assert transaction.receiver.to_bech32() == self.governance_address
        assert transaction.chain_id == "D"
        assert transaction.value == 0
        assert transaction.gas_limit == 5_171_000
        assert transaction.data.decode() == "vote@01@796573"

    def test_create_transaction_for_closing_proposal(self):
        transaction = self.controller.create_transaction_for_closing_proposal(
            sender=self.alice,
            nonce=self.alice.get_nonce_then_increment(),
            proposal_nonce=1,
        )

        assert transaction.sender == self.alice.address
        assert transaction.receiver.to_bech32() == self.governance_address
        assert transaction.chain_id == "D"
        assert transaction.value == 0
        assert transaction.gas_limit == 50_074_000
        assert transaction.data.decode() == "closeProposal@01"

    def test_create_transaction_for_clearing_ended_proposals(self):
        transaction = self.controller.create_transaction_for_clearing_ended_proposals(
            sender=self.alice,
            nonce=self.alice.get_nonce_then_increment(),
            proposers=[
                self.alice.address,
                Address.new_from_bech32("erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"),
            ],
        )

        assert transaction.sender == self.alice.address
        assert transaction.receiver.to_bech32() == self.governance_address
        assert transaction.chain_id == "D"
        assert transaction.value == 0
        assert transaction.gas_limit == 150_273_500
        assert (
            transaction.data.decode()
            == "clearEndedProposals@0139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1@8049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f8"
        )

    def test_create_transaction_for_claiming_accumulated_fees(self):
        transaction = self.controller.create_transaction_for_claiming_accumulated_fees(
            sender=self.alice,
            nonce=self.alice.get_nonce_then_increment(),
        )

        assert transaction.sender == self.alice.address
        assert transaction.receiver.to_bech32() == self.governance_address
        assert transaction.chain_id == "D"
        assert transaction.value == 0
        assert transaction.gas_limit == 1_080_000
        assert transaction.data.decode() == "claimAccumulatedFees"

    def test_create_transaction_for_changing_config(self):
        transaction = self.controller.create_transaction_for_changing_config(
            sender=self.alice,
            nonce=self.alice.get_nonce_then_increment(),
            proposal_fee=1000000000000000000000,
            lost_proposal_fee=10000000000000000000,
            min_quorum=5000,
            min_veto_threshold=3000,
            min_pass_threshold=6000,
        )

        assert transaction.sender == self.alice.address
        assert transaction.receiver.to_bech32() == self.governance_address
        assert transaction.chain_id == "D"
        assert transaction.value == 0
        assert transaction.gas_limit == 50_237_500
        assert (
            transaction.data.decode()
            == "changeConfig@31303030303030303030303030303030303030303030@3130303030303030303030303030303030303030@35303030@33303030@36303030"
        )

    def test_get_voting_power(self):
        network_provider = MockNetworkProvider()
        controller = GovernanceController(chain_id="D", network_provider=network_provider)

        contract_query_response = SmartContractQueryResponse(
            function="viewVotingPower",
            return_code="ok",
            return_message="",
            return_data_parts=[b"\x87\x86x2n\xac\x90\x00\x00"],
        )
        network_provider.mock_query_contract_on_function("viewVotingPower", contract_query_response)

        voting_power = controller.get_voting_power(self.alice.address)
        assert voting_power == 2500_000000000000000000

    def test_get_config(self):
        network_provider = MockNetworkProvider()
        controller = GovernanceController(chain_id="D", network_provider=network_provider)

        contract_query_response = SmartContractQueryResponse(
            function="viewConfig",
            return_code="ok",
            return_message="",
            return_data_parts=[b"1000000000000000000000", b"0.2000", b"0.5000", b"0.3300", b"1"],
        )
        network_provider.mock_query_contract_on_function("viewConfig", contract_query_response)

        config = controller.get_config()
        assert config.proposal_fee == 1000_000000000000000000
        assert config.min_quorum == 0.2
        assert config.min_pass_threshold == 0.5
        assert config.min_veto_threshold == 0.33
        assert config.last_proposal_nonce == 1

    def test_get_proposal(self):
        network_provider = MockNetworkProvider()
        controller = GovernanceController(chain_id="D", network_provider=network_provider)

        contract_query_response = SmartContractQueryResponse(
            function="viewProposal",
            return_code="ok",
            return_message="",
            return_data_parts=[
                base64.b64decode("NjXJrcXeoAAA"),
                base64.b64decode("MWRiNzM0YzAzMTVmOWVjNDIyYjg4ZjY3OWNjZmUzZTAxOTdiOWQ2Nw=="),
                base64.b64decode("AQ=="),
                base64.b64decode("ATlHLv9ohncamC8wg9pdQh8kwpGB5jiIIo3IHKYNaeE="),
                base64.b64decode("NQ=="),
                base64.b64decode("Nw=="),
                base64.b64decode(""),
                base64.b64decode(""),
                base64.b64decode(""),
                base64.b64decode(""),
                base64.b64decode(""),
                base64.b64decode("ZmFsc2U="),
                base64.b64decode("ZmFsc2U="),
            ],
        )
        network_provider.mock_query_contract_on_function("viewProposal", contract_query_response)

        proposal = controller.get_proposal(1)
        assert proposal.cost == 1000_000000000000000000
        assert proposal.commit_hash == "1db734c0315f9ec422b88f679ccfe3e0197b9d67"
        assert proposal.nonce == 1
        assert proposal.issuer == self.alice.address
        assert proposal.start_vote_epoch == 53
        assert proposal.end_vote_epoch == 55
        assert proposal.quorum_stake == 0
        assert proposal.num_yes_votes == 0
        assert proposal.num_no_votes == 0
        assert proposal.num_veto_votes == 0
        assert proposal.num_abstain_votes == 0
        assert not proposal.is_closed
        assert not proposal.is_passed
