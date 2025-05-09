from multiversx_sdk.abi.address_value import AddressValue
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
        self._config = config
        self._governance_contract = Address.new_from_hex(GOVERNANCE_SMART_CONTRACT_ADDRESS_HEX)
        self._serializer = Serializer()

    def create_transaction_for_new_proposal(
        self,
        sender: Address,
        commit_hash: str,
        start_vote_epoch: int,
        end_vote_epoch: int,
        native_token_amount: int,
    ) -> Transaction:
        data_parts = ["proposal"]
        serialized_args = self._serializer.serialize_to_parts(
            [StringValue(commit_hash), BigUIntValue(start_vote_epoch), BigUIntValue(end_vote_epoch)]
        )
        serialized_args = [arg.hex() for arg in serialized_args]
        data_parts.extend(serialized_args)

        return TransactionBuilder(
            config=self._config,
            sender=sender,
            receiver=self._governance_contract,
            data_parts=data_parts,
            gas_limit=self._config.gas_limit_for_proposal,
            add_data_movement_gas=True,
            amount=native_token_amount,
        ).build()

    def create_transaction_for_voting(
        self,
        sender: Address,
        proposal_nonce: int,
        vote: VoteType,
    ) -> Transaction:
        serialized_args = self._serializer.serialize_to_parts([BigUIntValue(proposal_nonce), StringValue(vote.value)])
        data_parts = ["vote"] + [arg.hex() for arg in serialized_args]

        return TransactionBuilder(
            config=self._config,
            sender=sender,
            receiver=self._governance_contract,
            data_parts=data_parts,
            gas_limit=self._config.gas_limit_for_vote + EXTRA_GAS_LIMIT_FOR_VOTING_PROPOSAL,
            add_data_movement_gas=True,
        ).build()

    def create_transaction_for_closing_proposal(self, sender: Address, proposal_nonce: int) -> Transaction:
        data_parts = ["closeProposal", self._serializer.serialize([BigUIntValue(proposal_nonce)])]
        return TransactionBuilder(
            config=self._config,
            sender=sender,
            receiver=self._governance_contract,
            data_parts=data_parts,
            gas_limit=self._config.gas_limit_for_closing_proposal,
            add_data_movement_gas=True,
        ).build()

    def create_transaction_for_clearing_ended_proposals(
        self,
        sender: Address,
        proposers: list[Address],
    ) -> Transaction:
        serialized_proposers = self._serializer.serialize_to_parts(
            [AddressValue.new_from_address(user) for user in proposers]
        )

        data_parts = ["clearEndedProposals"] + [address.hex() for address in serialized_proposers]
        return TransactionBuilder(
            config=self._config,
            sender=sender,
            receiver=self._governance_contract,
            data_parts=data_parts,
            gas_limit=self._config.gas_limit_for_clear_proposals
            + len(proposers) * self._config.gas_limit_for_clear_proposals,
            add_data_movement_gas=True,
        ).build()

    def create_transaction_for_claiming_accumulated_fees(
        self,
        sender: Address,
    ) -> Transaction:
        data_parts = ["claimAccumulatedFees"]
        return TransactionBuilder(
            config=self._config,
            sender=sender,
            receiver=self._governance_contract,
            data_parts=data_parts,
            gas_limit=self._config.gas_limit_for_claim_accumulated_fees,
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
        args = self._serializer.serialize_to_parts(
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
            config=self._config,
            sender=sender,
            receiver=self._governance_contract,
            data_parts=data_parts,
            gas_limit=self._config.gas_limit_for_change_config,
            add_data_movement_gas=True,
        ).build()
