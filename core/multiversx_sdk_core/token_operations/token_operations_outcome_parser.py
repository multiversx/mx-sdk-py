
from dataclasses import dataclass
from typing import List, Protocol

from multiversx_sdk_core import Address
from multiversx_sdk_core.codec import decode_unsigned_number
from multiversx_sdk_core.transaction_outcome_parser import (
    ITransactionEvent, ITransactionOnNetwork, TransactionOutcomeParser)


class IConfig(Protocol):
    address_hrp: str


@dataclass
class ESDTIssueOutcome:
    token_identifier: str


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
    nonce: int
    initial_quantity: int


@dataclass
class MintOutcome:
    user_address: str
    token_identifier: str
    nonce: int
    minted_supply: int


@dataclass
class BurnOutcome:
    user_address: str
    token_identifier: str
    nonce: int
    burnt_supply: int


@dataclass
class PausingOutcome:
    pass


@dataclass
class FreezingOutcome:
    user_address: str
    token_identifier: str
    nonce: int
    balance: int


@dataclass
class WipingOutcome:
    user_address: str
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


class TokenOperationsOutcomeParser(TransactionOutcomeParser):
    def __init__(self, config: IConfig) -> None:
        self._config = config

    def parse_issue_fungible(self, transaction: ITransactionOnNetwork) -> ESDTIssueOutcome:
        self._ensure_no_error(transaction)

        event = self._find_single_event_by_identifier(transaction, "issue")
        token_identifier = self._extract_token_identifier(event)
        return ESDTIssueOutcome(token_identifier)

    def parse_issue_non_fungible(self, transaction: ITransactionOnNetwork) -> ESDTIssueOutcome:
        self._ensure_no_error(transaction)

        event = self._find_single_event_by_identifier(transaction, "issueNonFungible")
        token_identifier = self._extract_token_identifier(event)
        return ESDTIssueOutcome(token_identifier)

    def parse_issue_semi_fungible(self, transaction: ITransactionOnNetwork) -> ESDTIssueOutcome:
        self._ensure_no_error(transaction)

        event = self._find_single_event_by_identifier(transaction, "issueSemiFungible")
        token_identifier = self._extract_token_identifier(event)
        return ESDTIssueOutcome(token_identifier)

    def parse_register_meta_esdt(self, transaction: ITransactionOnNetwork) -> ESDTIssueOutcome:
        self._ensure_no_error(transaction)

        event = self._find_single_event_by_identifier(transaction, "registerMetaESDT")
        token_identifier = self._extract_token_identifier(event)
        return ESDTIssueOutcome(token_identifier)

    def parse_register_and_set_all_roles(self, transaction: ITransactionOnNetwork) -> RegisterAndSetAllRolesOutcome:
        self._ensure_no_error(transaction)

        event_register = self._find_single_event_by_identifier(transaction, "registerAndSetAllRoles")
        token_identifier = self._extract_token_identifier(event_register)

        event_set_role = self._find_single_event_by_identifier(transaction, "ESDTSetRole")
        roles = [str(topic) for topic in event_set_role.topics[3:]]

        return RegisterAndSetAllRolesOutcome(token_identifier, roles)

    def parse_set_burn_role_globally(self, transaction: ITransactionOnNetwork) -> None:
        self._ensure_no_error(transaction)

    def parse_unset_burn_role_globally(self, transaction: ITransactionOnNetwork) -> None:
        self._ensure_no_error(transaction)

    def parse_set_special_role(self, transaction: ITransactionOnNetwork) -> SetSpecialRoleOutcome:
        self._ensure_no_error(transaction)

        event = self._find_single_event_by_identifier(transaction, "ESDTSetRole")
        user_address = event.address.bech32()
        token_identifier = self._extract_token_identifier(event)
        roles = [str(topic) for topic in event.topics[3:]]

        return SetSpecialRoleOutcome(user_address, token_identifier, roles)

    def parse_nft_create(self, transaction: ITransactionOnNetwork) -> NFTCreateOutcome:
        self._ensure_no_error(transaction)

        event = self._find_single_event_by_identifier(transaction, "ESDTNFTCreate")
        token_identifier = self._extract_token_identifier(event)
        nonce = self._extract_nonce(event)
        initial_quantity = self._extract_amount(event)

        return NFTCreateOutcome(token_identifier, nonce, initial_quantity)

    def parse_local_mint(self, transaction: ITransactionOnNetwork) -> MintOutcome:
        self._ensure_no_error(transaction)

        event = self._find_single_event_by_identifier(transaction, "ESDTLocalMint")
        user_address = event.address.bech32()
        token_identifier = self._extract_token_identifier(event)
        nonce = self._extract_nonce(event)
        minted_supply = self._extract_amount(event)

        return MintOutcome(user_address, token_identifier, nonce, minted_supply)

    def parse_local_burn(self, transaction: ITransactionOnNetwork) -> BurnOutcome:
        self._ensure_no_error(transaction)

        event = self._find_single_event_by_identifier(transaction, "ESDTLocalBurn")
        user_address = event.address.bech32()
        token_identifier = self._extract_token_identifier(event)
        nonce = self._extract_nonce(event)
        burnt_supply = self._extract_amount(event)

        return BurnOutcome(user_address, token_identifier, nonce, burnt_supply)

    def parse_pause(self, transaction: ITransactionOnNetwork) -> PausingOutcome:
        self._ensure_no_error(transaction)

        _ = self._find_single_event_by_identifier(transaction, "ESDTPause")
        return PausingOutcome()

    def parse_unpause(self, transaction: ITransactionOnNetwork) -> PausingOutcome:
        self._ensure_no_error(transaction)

        _ = self._find_single_event_by_identifier(transaction, "ESDTUnPause")
        return PausingOutcome()

    def parse_freeze(self, transaction: ITransactionOnNetwork) -> FreezingOutcome:
        self._ensure_no_error(transaction)

        event = self._find_single_event_by_identifier(transaction, "ESDTFreeze")
        token_identifier = self._extract_token_identifier(event)
        nonce = self._extract_nonce(event)
        balance = self._extract_amount(event)
        user_address = self._extract_address(event)

        return FreezingOutcome(user_address, token_identifier, nonce, balance)

    def parse_unfreeze(self, transaction: ITransactionOnNetwork) -> FreezingOutcome:
        self._ensure_no_error(transaction)

        event = self._find_single_event_by_identifier(transaction, "ESDTUnFreeze")
        token_identifier = self._extract_token_identifier(event)
        nonce = self._extract_nonce(event)
        balance = self._extract_amount(event)
        user_address = self._extract_address(event)

        return FreezingOutcome(user_address, token_identifier, nonce, balance)

    def parse_wipe(self, transaction: ITransactionOnNetwork) -> WipingOutcome:
        self._ensure_no_error(transaction)

        event = self._find_single_event_by_identifier(transaction, "ESDTWipe")
        token_identifier = self._extract_token_identifier(event)
        nonce = self._extract_nonce(event)
        balance = self._extract_amount(event)
        user_address = self._extract_address(event)

        return WipingOutcome(user_address, token_identifier, nonce, balance)

    def parse_update_attributes(self, transaction: ITransactionOnNetwork) -> UpdateAttributesOutcome:
        self._ensure_no_error(transaction)

        event = self._find_single_event_by_identifier(transaction, "ESDTNFTUpdateAttributes")
        token_identifier = self._extract_token_identifier(event)
        nonce = self._extract_nonce(event)
        attributes = event.topics[3].raw

        return UpdateAttributesOutcome(token_identifier, nonce, attributes)

    def parse_add_quantity(self, transaction: ITransactionOnNetwork) -> AddQuantityOutcome:
        self._ensure_no_error(transaction)

        event = self._find_single_event_by_identifier(transaction, "ESDTNFTAddQuantity")
        token_identifier = self._extract_token_identifier(event)
        nonce = self._extract_nonce(event)
        added_quantity = self._extract_amount(event)

        return AddQuantityOutcome(token_identifier, nonce, added_quantity)

    def parse_burn_quantity(self, transaction: ITransactionOnNetwork) -> BurnQuantityOutcome:
        self._ensure_no_error(transaction)

        event = self._find_single_event_by_identifier(transaction, "ESDTNFTBurn")
        token_identifier = self._extract_token_identifier(event)
        nonce = self._extract_nonce(event)
        burnt_quantity = self._extract_amount(event)

        return BurnQuantityOutcome(token_identifier, nonce, burnt_quantity)

    def _extract_token_identifier(self, event: ITransactionEvent) -> str:
        return str(event.topics[0])

    def _extract_nonce(self, event: ITransactionEvent) -> int:
        return decode_unsigned_number(event.topics[1].raw)

    def _extract_amount(self, event: ITransactionEvent) -> int:
        return decode_unsigned_number(event.topics[2].raw)

    def _extract_address(self, event: ITransactionEvent) -> str:
        return Address(event.topics[3].raw, self._config.address_hrp).bech32()
