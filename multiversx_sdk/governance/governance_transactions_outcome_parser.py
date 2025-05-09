from typing import Optional

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
    ProposeProposalOutcome,
    VoteOutcome,
)
from multiversx_sdk.smart_contracts.smart_contract_transactions_outcome_parser import (
    SmartContractTransactionsOutcomeParser,
)


class GovernanceTransactionsOutcomeParser:
    def __init__(self, address_hrp: Optional[str] = None) -> None:
        self._parser = SmartContractTransactionsOutcomeParser()
        self._address_hrp = address_hrp if address_hrp else LibraryConfig.default_address_hrp

    def parse_propose_proposal(self, transaction_on_network: TransactionOnNetwork) -> list[ProposeProposalOutcome]:
        self._ensure_no_error(transaction_on_network.logs.events)
        events = find_events_by_identifier(transaction_on_network, "proposal")
        outcome: list[ProposeProposalOutcome] = []

        for event in events:
            proposal_nonce = int.from_bytes(event.topics[0])
            commit_hash = event.topics[1].decode()
            start_vote_epoch = int.from_bytes(event.topics[2])
            end_vote_epoch = int.from_bytes(event.topics[3])
            outcome.append(ProposeProposalOutcome(proposal_nonce, commit_hash, start_vote_epoch, end_vote_epoch))

        return outcome

    def parse_vote(self, transaction_on_network: TransactionOnNetwork) -> list[VoteOutcome]:
        self._ensure_no_error(transaction_on_network.logs.events)
        events = find_events_by_identifier(transaction_on_network, "vote")
        outcome: list[VoteOutcome] = []

        for event in events:
            proposal_to_vote = int.from_bytes(event.topics[0])
            vote = event.topics[1].decode()
            total_stake = int.from_bytes(event.topics[2])
            voting_power = int.from_bytes(event.topics[3])
            outcome.append(VoteOutcome(proposal_to_vote, vote, total_stake, voting_power))

        return outcome

    def parse_delegate_vote(self, transaction_on_network: TransactionOnNetwork) -> list[DelegateVoteOutcome]:
        self._ensure_no_error(transaction_on_network.logs.events)
        events = find_events_by_identifier(transaction_on_network, "delegateVote")
        outcome: list[DelegateVoteOutcome] = []

        for event in events:
            proposal_to_vote = int.from_bytes(event.topics[0])
            vote = event.topics[1].decode()
            voter = Address(event.topics[2], self._address_hrp)
            user_stake = int.from_bytes(event.topics[3])
            voting_power = int.from_bytes(event.topics[4])
            outcome.append(DelegateVoteOutcome(proposal_to_vote, vote, voter, user_stake, voting_power))

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
