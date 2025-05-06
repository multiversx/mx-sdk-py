from enum import Enum


class VoteType(Enum):
    YES = "796573"  # "yes" hex-encoded
    NO = "6e6f"  # "no" hex-encoded
    ABSTAIN = "6162737461696e"  # "abstain" hex-encoded
    VETO = "7665746f"  # "veto" hex-encoded
