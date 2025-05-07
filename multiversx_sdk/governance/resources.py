from dataclasses import dataclass
from enum import Enum

from multiversx_sdk.core.address import Address


class VoteType(Enum):
    YES = "796573"  # "yes" hex-encoded
    NO = "6e6f"  # "no" hex-encoded
    ABSTAIN = "6162737461696e"  # "abstain" hex-encoded
    VETO = "7665746f"  # "veto" hex-encoded


@dataclass
class GovernaceConfig:
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
    proposal_cost: int
    commit_hash: str
    proposal_nonce: int
    issuer_address: Address
    start_vote_epoch: int
    end_vote_epoch: int
    quorum_stake: int
    yes_votes: int
    no_votes: int
    veto_votes: int
    abstain_votes: int
    is_proposal_closed: bool
    is_proposal_passed: bool
