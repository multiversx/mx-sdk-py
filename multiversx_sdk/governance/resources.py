from enum import Enum


class VoteType(Enum):
    YES = "yes"
    NO = "no"
    ABSTAIN = "abstain"
    VETO = "veto"
