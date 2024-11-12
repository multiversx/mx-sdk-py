from dataclasses import dataclass
from typing import List

from multiversx_sdk.core.address import Address


@dataclass
class IssueFungibleOutcome:
    token_identifier: str


@dataclass
class IssueNonFungibleOutcome:
    token_identifier: str


@dataclass
class IssueSemiFungibleOutcome:
    token_identifier: str


@dataclass
class RegisterMetaEsdtOutcome:
    token_identifier: str


@dataclass
class RegisterAndSetAllRolesOutcome:
    token_identifier: str
    roles: List[str]


@dataclass
class SetSpecialRoleOutcome:
    user_address: Address
    token_identifier: str
    roles: List[str]


@dataclass
class NFTCreateOutcome:
    token_identifier: str
    nonce: int
    initial_quantity: int


@dataclass
class MintOutcome:
    user_address: Address
    token_identifier: str
    nonce: int
    minted_supply: int


@dataclass
class BurnOutcome:
    user_address: Address
    token_identifier: str
    nonce: int
    burnt_supply: int


@dataclass
class PauseOutcome:
    token_identifier: str


@dataclass
class UnPauseOutcome:
    token_identifier: str


@dataclass
class FreezeOutcome:
    user_address: Address
    token_identifier: str
    nonce: int
    balance: int


@dataclass
class UnFreezeOutcome:
    user_address: Address
    token_identifier: str
    nonce: int
    balance: int


@dataclass
class WipeOutcome:
    user_address: Address
    token_identifier: str
    nonce: int
    balance: int


@dataclass
class UpdateAttributesOutcome:
    token_identifier: str
    nonce: int
    attributes: bytes


@dataclass
class AddQuantityOutcome:
    token_identifier: str
    nonce: int
    added_quantity: int


@dataclass
class BurnQuantityOutcome:
    token_identifier: str
    nonce: int
    burnt_quantity: int
