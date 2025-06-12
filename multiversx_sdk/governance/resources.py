from dataclasses import dataclass
from enum import Enum

from multiversx_sdk.core.address import Address


class VoteType(Enum):
    YES = "yes"
    NO = "no"
    ABSTAIN = "abstain"
    VETO = "veto"


@dataclass
class GovernanceConfig:
    proposal_fee: int
    min_quorum: float
    min_pass_threshold: float
    min_veto_threshold: float
    last_proposal_nonce: int


@dataclass
class DelegatedVoteInfo:
    used_stake: int
    used_power: int
    total_stake: int
    total_power: int


@dataclass
class ProposalInfo:
    cost: int
    commit_hash: str
    nonce: int
    issuer: Address
    start_vote_epoch: int
    end_vote_epoch: int
    quorum_stake: int
    num_yes_votes: int
    num_no_votes: int
    num_veto_votes: int
    num_abstain_votes: int
    is_closed: bool
    is_passed: bool


@dataclass
class NewProposalOutcome:
    proposal_nonce: int
    commit_hash: str
    start_vote_epoch: int
    end_vote_epoch: int


@dataclass
class VoteOutcome:
    proposal_nonce: int
    vote: str
    total_stake: int
    total_voting_power: int


@dataclass
class DelegateVoteOutcome:
    proposal_nonce: int
    vote: str
    voter: Address
    user_stake: int
    voting_power: int


@dataclass
class CloseProposalOutcome:
    commit_hash: str
    passed: bool
