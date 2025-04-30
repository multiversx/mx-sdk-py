from enum import Enum


class VoteType(Enum):
    YES = "00"
    NO = "01"
    VETO = "02"
    ABSTAIN = "03"
