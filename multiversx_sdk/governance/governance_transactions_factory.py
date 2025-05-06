from multiversx_sdk.abi.biguint_value import BigUIntValue
from multiversx_sdk.abi.serializer import Serializer
from multiversx_sdk.abi.string_value import StringValue
from multiversx_sdk.builders.transaction_builder import TransactionBuilder
from multiversx_sdk.core.address import Address
from multiversx_sdk.core.constants import GOVERNANCE_SMART_CONTRACT_ADDRESS_HEX
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transactions_factory_config import TransactionsFactoryConfig
from multiversx_sdk.governance.resources import VoteType

# will be changed in the future when a formula on how gas is computed will be available
EXTRA_GAS_LIMIT_FOR_VOTING_PROPOSAL = 100_000


class GovernanceTransactionsFactory:
    def __init__(self, config: TransactionsFactoryConfig) -> None:
        self.config = config
        self.governance_contract = Address.new_from_hex(GOVERNANCE_SMART_CONTRACT_ADDRESS_HEX)
        self.serializer = Serializer()

    def create_transaction_for_new_proposal(
        self,
        sender: Address,
        github_commit_hash: str,
        start_vote_epoch: int,
        end_vote_epoch: int,
        value: int,
    ) -> Transaction:
        data_parts = ["proposal"]
        serialized_args = self.serializer.serialize_to_parts(
            [StringValue(github_commit_hash), BigUIntValue(start_vote_epoch), BigUIntValue(end_vote_epoch)]
        )
        serialized_args = [arg.hex() for arg in serialized_args]
        data_parts.extend(serialized_args)

        return TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=self.governance_contract,
            data_parts=data_parts,
            gas_limit=self.config.gas_limit_for_proposal,
            add_data_movement_gas=True,
            amount=value,
        ).build()

    def create_transaction_for_voting(
        self,
        sender: Address,
        proposal_nonce: int,
        vote: VoteType,
    ) -> Transaction:
        data_parts = ["vote", self.serializer.serialize([BigUIntValue(proposal_nonce)]), vote.value]
        return TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=self.governance_contract,
            data_parts=data_parts,
            gas_limit=self.config.gas_limit_for_vote + EXTRA_GAS_LIMIT_FOR_VOTING_PROPOSAL,
            add_data_movement_gas=True,
        ).build()

    def create_transaction_for_delegating_vote(
        self,
        sender: Address,
        proposal_nonce: int,
        vote: VoteType,
        delegate_to: Address,
        balance_to_vote: int,
    ) -> Transaction:
        data_parts = [
            "delegateVote",
            self.serializer.serialize([BigUIntValue(proposal_nonce)]),
            vote.value,
            delegate_to.to_hex(),
            self.serializer.serialize([BigUIntValue(balance_to_vote)]),
        ]
        return TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=self.governance_contract,
            data_parts=data_parts,
            gas_limit=self.config.gas_limit_for_delegate_vote,
            add_data_movement_gas=True,
        ).build()

    def create_transaction_for_closing_proposal(self, sender: Address, proposal_nonce: int) -> Transaction:
        data_parts = ["closeProposal", self.serializer.serialize([BigUIntValue(proposal_nonce)])]
        return TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=self.governance_contract,
            data_parts=data_parts,
            gas_limit=self.config.gas_limit_for_closing_proposal,
            add_data_movement_gas=True,
        ).build()

    def create_transaction_for_clearing_ended_proposals(
        self,
        sender: Address,
    ) -> Transaction:
        data_parts = ["clearEndedProposals"]
        return TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=self.governance_contract,
            data_parts=data_parts,
            gas_limit=self.config.gas_limit_for_clear_proposals,
            add_data_movement_gas=True,
        ).build()

    def create_transaction_for_claiming_accumulated_fees(
        self,
        sender: Address,
    ) -> Transaction:
        data_parts = ["claimAccumulatedFees"]
        return TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=self.governance_contract,
            data_parts=data_parts,
            gas_limit=self.config.gas_limit_for_claim_accumulated_fees,
            add_data_movement_gas=True,
        ).build()

    def create_transaction_for_changing_config(
        self,
        sender: Address,
        proposal_fee: str,
        lost_proposal_fee: str,
        min_quorum: int,
        min_veto_threshold: int,
        min_pass_threshold: int,
    ) -> Transaction:
        data_parts = ["changeConfig"]
        args = self.serializer.serialize_to_parts(
            [
                StringValue(proposal_fee),
                StringValue(lost_proposal_fee),
                BigUIntValue(min_quorum),
                BigUIntValue(min_veto_threshold),
                BigUIntValue(min_pass_threshold),
            ]
        )

        data_parts = data_parts + [arg.hex() for arg in args]
        return TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=self.governance_contract,
            data_parts=data_parts,
            gas_limit=self.config.gas_limit_for_change_config,
            add_data_movement_gas=True,
        ).build()
