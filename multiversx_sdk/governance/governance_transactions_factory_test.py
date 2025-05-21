from pathlib import Path

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.transactions_factory_config import TransactionsFactoryConfig
from multiversx_sdk.governance.governance_transactions_factory import (
    GovernanceTransactionsFactory,
)
from multiversx_sdk.governance.resources import VoteType


class TestGovernanceTransactionsFactory:
    factory = GovernanceTransactionsFactory(TransactionsFactoryConfig("D"))
    commit_hash = "1db734c0315f9ec422b88f679ccfe3e0197b9d67"
    alice = Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
    governance_address = "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqrlllsrujgla"

    testdata = Path(__file__).parent.parent / "testutils" / "testdata"
    testwallets = Path(__file__).parent.parent / "testutils" / "testwallets"

    def test_create_transaction_for_new_proposal(self):
        transaction = self.factory.create_transaction_for_new_proposal(
            sender=self.alice,
            commit_hash=self.commit_hash,
            start_vote_epoch=10,
            end_vote_epoch=15,
            native_token_amount=1000_000000000000000000,
        )

        assert transaction.sender == self.alice
        assert transaction.receiver.to_bech32() == self.governance_address
        assert transaction.chain_id == "D"
        assert transaction.value == 1000_000000000000000000
        assert transaction.gas_limit == 50_192_500
        assert transaction.data.decode() == f"proposal@{self.commit_hash.encode().hex()}@0a@0f"

    def test_create_transaction_for_voting(self):
        transaction = self.factory.create_transaction_for_voting(
            sender=self.alice,
            proposal_nonce=1,
            vote=VoteType.YES,
        )

        assert transaction.sender == self.alice
        assert transaction.receiver.to_bech32() == self.governance_address
        assert transaction.chain_id == "D"
        assert transaction.value == 0
        assert transaction.gas_limit == 5_171_000
        assert transaction.data.decode() == "vote@01@796573"

    def test_create_transaction_for_closing_proposal(self):
        transaction = self.factory.create_transaction_for_closing_proposal(sender=self.alice, proposal_nonce=1)

        assert transaction.sender == self.alice
        assert transaction.receiver.to_bech32() == self.governance_address
        assert transaction.chain_id == "D"
        assert transaction.value == 0
        assert transaction.gas_limit == 50_074_000
        assert transaction.data.decode() == "closeProposal@01"

    def test_create_transaction_for_clearing_ended_proposals(self):
        transaction = self.factory.create_transaction_for_clearing_ended_proposals(
            sender=self.alice,
            proposers=[
                self.alice,
                Address.new_from_bech32("erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"),
            ],
        )

        assert transaction.sender == self.alice
        assert transaction.receiver.to_bech32() == self.governance_address
        assert transaction.chain_id == "D"
        assert transaction.value == 0
        assert transaction.gas_limit == 150_273_500
        assert (
            transaction.data.decode()
            == "clearEndedProposals@0139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1@8049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f8"
        )

    def test_create_transaction_for_claiming_accumulated_fees(self):
        transaction = self.factory.create_transaction_for_claiming_accumulated_fees(
            sender=self.alice,
        )

        assert transaction.sender == self.alice
        assert transaction.receiver.to_bech32() == self.governance_address
        assert transaction.chain_id == "D"
        assert transaction.value == 0
        assert transaction.gas_limit == 1_080_000
        assert transaction.data.decode() == "claimAccumulatedFees"

    def test_create_transaction_for_changing_config(self):
        transaction = self.factory.create_transaction_for_changing_config(
            sender=self.alice,
            proposal_fee=1000000000000000000000,
            lost_proposal_fee=10000000000000000000,
            min_quorum=5000,
            min_veto_threshold=3000,
            min_pass_threshold=6000,
        )

        assert transaction.sender == self.alice
        assert transaction.receiver.to_bech32() == self.governance_address
        assert transaction.chain_id == "D"
        assert transaction.value == 0
        assert transaction.gas_limit == 50_237_500
        assert (
            transaction.data.decode()
            == "changeConfig@31303030303030303030303030303030303030303030@3130303030303030303030303030303030303030@35303030@33303030@36303030"
        )
