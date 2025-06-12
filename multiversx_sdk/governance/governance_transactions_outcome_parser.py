from typing import Optional

from multiversx_sdk.abi.address_value import AddressValue
from multiversx_sdk.abi.biguint_value import BigUIntValue
from multiversx_sdk.abi.serializer import Serializer
from multiversx_sdk.abi.string_value import StringValue
from multiversx_sdk.core.address import Address
from multiversx_sdk.core.config import LibraryConfig
from multiversx_sdk.core.transaction_on_network import (
    TransactionEvent,
    TransactionOnNetwork,
    find_events_by_identifier,
)
from multiversx_sdk.governance.resources import (
    CloseProposalOutcome,
    DelegateVoteOutcome,
    NewProposalOutcome,
    VoteOutcome,
)


class GovernanceTransactionsOutcomeParser:
    def __init__(self, address_hrp: Optional[str] = None) -> None:
        self._address_hrp = address_hrp if address_hrp else LibraryConfig.default_address_hrp
        self._serializer = Serializer()

    def parse_new_proposal(self, transaction_on_network: TransactionOnNetwork) -> list[NewProposalOutcome]:
        self._ensure_no_error(transaction_on_network.logs.events)
        events = find_events_by_identifier(transaction_on_network, "proposal")
        outcome: list[NewProposalOutcome] = []

        proposal_nonce = BigUIntValue()
        commit_hash = StringValue()
        start_vote_epoch = BigUIntValue()
        end_vote_epoch = BigUIntValue()

        for event in events:
            self._serializer.deserialize_parts(
                event.topics, [proposal_nonce, commit_hash, start_vote_epoch, end_vote_epoch]
            )
            outcome.append(
                NewProposalOutcome(
                    proposal_nonce.get_payload(),
                    commit_hash.get_payload(),
                    start_vote_epoch.get_payload(),
                    end_vote_epoch.get_payload(),
                )
            )

        return outcome

    def parse_vote(self, transaction_on_network: TransactionOnNetwork) -> list[VoteOutcome]:
        self._ensure_no_error(transaction_on_network.logs.events)
        events = find_events_by_identifier(transaction_on_network, "vote")
        outcome: list[VoteOutcome] = []

        proposal_to_vote = BigUIntValue()
        vote = StringValue()
        total_stake = BigUIntValue()
        voting_power = BigUIntValue()

        for event in events:
            self._serializer.deserialize_parts(event.topics, [proposal_to_vote, vote, total_stake, voting_power])
            outcome.append(
                VoteOutcome(
                    proposal_to_vote.get_payload(),
                    vote.get_payload(),
                    total_stake.get_payload(),
                    voting_power.get_payload(),
                )
            )

        return outcome

    def parse_delegate_vote(self, transaction_on_network: TransactionOnNetwork) -> list[DelegateVoteOutcome]:
        self._ensure_no_error(transaction_on_network.logs.events)
        events = find_events_by_identifier(transaction_on_network, "delegateVote")
        outcome: list[DelegateVoteOutcome] = []

        proposal_to_vote = BigUIntValue()
        vote = StringValue()
        voter = AddressValue()
        user_stake = BigUIntValue()
        voting_power = BigUIntValue()

        for event in events:
            self._serializer.deserialize_parts(event.topics, [proposal_to_vote, vote, voter, user_stake, voting_power])
            outcome.append(
                DelegateVoteOutcome(
                    proposal_to_vote.get_payload(),
                    vote.get_payload(),
                    Address(voter.get_payload(), self._address_hrp),
                    user_stake.get_payload(),
                    voting_power.get_payload(),
                )
            )

        return outcome

    def parse_close_proposal(self, transaction_on_network: TransactionOnNetwork) -> list[CloseProposalOutcome]:
        self._ensure_no_error(transaction_on_network.logs.events)
        events = find_events_by_identifier(transaction_on_network, "closeProposal")
        outcome: list[CloseProposalOutcome] = []

        for event in events:
            commit_hash = event.topics[0].decode()
            vote = True if event.topics[1].decode() == "true" else False
            outcome.append(CloseProposalOutcome(commit_hash, vote))

        return outcome

    def _ensure_no_error(self, transaction_events: list[TransactionEvent]) -> None:
        for event in transaction_events:
            if event.identifier == "signalError":
                data = event.additional_data[0].decode()[1:] if len(event.additional_data[0]) else ""
                message = event.topics[1].decode()

                raise Exception(f"encountered signalError: {message} ({bytes.fromhex(data).decode()})")
