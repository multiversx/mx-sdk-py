from dataclasses import dataclass

from multiversx_sdk.core import Address


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
    roles: list[str]


@dataclass
class SetSpecialRoleOutcome:
    user_address: Address
    token_identifier: str
    roles: list[str]


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


@dataclass
class ModifyRoyaltiesOutcome:
    token_identifier: str
    nonce: int
    royalties: int


@dataclass
class SetNewUrisOutcome:
    token_identifier: str
    nonce: int
    uris: list[str]


@dataclass
class ModifyCreatorOutcome:
    token_identifier: str
    nonce: int


@dataclass
class UpdateMetadataOutcome:
    token_identifier: str
    nonce: int
    metadata: bytes


@dataclass
class MetadataRecreateOutcome:
    token_identifier: str
    nonce: int
    metadata: bytes


@dataclass
class ChangeTokenToDynamicOutcome:
    token_identifier: str
    token_name: str
    ticker: str
    token_type: str


@dataclass
class RegisterDynamicOutcome:
    token_identifier: str
    token_name: str
    ticker: str
    token_type: str
    num_of_decimals: int
