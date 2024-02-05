from dataclasses import dataclass
from typing import List


@dataclass
class IssueFungibleOutcome:
    identifier: str


@dataclass
class IssueNonFungibleOutcome:
    identifier: str


@dataclass
class IssueSemiFungibleOutcome:
    identifier: str


@dataclass
class RegisterMetaEsdtOutcome:
    identifier: str


@dataclass
class RegisterAndSetAllRolesOutcome:
    token_identifier: str
    roles: List[str]


@dataclass
class SetSpecialRoleOutcome:
    user_address: str
    token_identifier: str
    roles: List[str]


@dataclass
class NFTCreateOutcome:
    token_identifier: str
    nonce: str
    initial_quantity: str


@dataclass
class MintOutcome:
    user_address: str
    token_identifier: str
    nonce: str
    minted_supply: str


@dataclass
class BurnOutcome:
    user_address: str
    token_identifier: str
    nonce: str
    burnt_supply: str


@dataclass
class PauseOutcome:
    identifier: str


@dataclass
class UnPauseOutcome:
    identifier: str


@dataclass
class FreezeOutcome:
    user_address: str
    token_identifier: str
    nonce: str
    balance: str


@dataclass
class UnFreezeOutcome(FreezeOutcome):
    pass


@dataclass
class WipeOutcome:
    user_address: str
    token_identifier: str
    nonce: str
    balance: str


@dataclass
class UpdateAttributesOutcome:
    token_identifier: str
    nonce: str
    attributes: bytes


@dataclass
class AddQuantityOutcome:
    token_identifier: str
    nonce: str
    added_quantity: str


@dataclass
class BurnQuantityOutcome:
    token_identifier: str
    nonce: str
    burnt_quantity: str
