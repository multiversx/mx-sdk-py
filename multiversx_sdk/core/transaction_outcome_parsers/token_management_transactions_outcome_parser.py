import base64
from typing import List

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.constants import DEFAULT_HRP
from multiversx_sdk.core.errors import ParseTransactionOutcomeError
from multiversx_sdk.core.transaction_outcome_parsers.resources import (
    TransactionEvent, TransactionOutcome)
from multiversx_sdk.core.transaction_outcome_parsers.token_management_transactions_outcome_parser_types import (
    AddQuantityOutcome, BurnOutcome, BurnQuantityOutcome, FreezeOutcome,
    IssueFungibleOutcome, IssueNonFungibleOutcome, IssueSemiFungibleOutcome,
    MintOutcome, NFTCreateOutcome, PauseOutcome, RegisterAndSetAllRolesOutcome,
    RegisterMetaEsdtOutcome, SetSpecialRoleOutcome, UnFreezeOutcome,
    UnPauseOutcome, UpdateAttributesOutcome, WipeOutcome)


class TokenManagementTransactionsOutcomeParser:
    def __init__(self) -> None:
        pass

    def parse_issue_fungible(self, transaction_outcome: TransactionOutcome) -> IssueFungibleOutcome:
        self.ensure_no_error(transaction_outcome.transaction_logs.events)

        event = self.find_single_event_by_identifier(transaction_outcome, "issue")
        identifier = self.extract_token_identifier(event)

        return IssueFungibleOutcome(identifier)

    def parse_issue_non_fungible(self, transaction_outcome: TransactionOutcome) -> IssueNonFungibleOutcome:
        self.ensure_no_error(transaction_outcome.transaction_logs.events)

        event = self.find_single_event_by_identifier(transaction_outcome, "issueNonFungible")
        identifier = self.extract_token_identifier(event)

        return IssueNonFungibleOutcome(identifier)

    def parse_issue_semi_fungible(self, transaction_outcome: TransactionOutcome) -> IssueSemiFungibleOutcome:
        self.ensure_no_error(transaction_outcome.transaction_logs.events)

        event = self.find_single_event_by_identifier(transaction_outcome, "issueSemiFungible")
        identifier = self.extract_token_identifier(event)

        return IssueSemiFungibleOutcome(identifier)

    def parse_register_meta_esdt(self, transaction_outcome: TransactionOutcome) -> RegisterMetaEsdtOutcome:
        self.ensure_no_error(transaction_outcome.transaction_logs.events)

        event = self.find_single_event_by_identifier(transaction_outcome, "registerMetaESDT")
        identifier = self.extract_token_identifier(event)

        return RegisterMetaEsdtOutcome(identifier)

    def parse_register_and_set_all_roles(self, transaction_outcome: TransactionOutcome) -> RegisterAndSetAllRolesOutcome:
        self.ensure_no_error(transaction_outcome.transaction_logs.events)

        register_event = self.find_single_event_by_identifier(transaction_outcome, "registerAndSetAllRoles")
        token_identifier = self.extract_token_identifier(register_event)

        set_role_event = self.find_single_event_by_identifier(transaction_outcome, "ESDTSetRole")
        encoded_roles = set_role_event.topics[3:]

        roles: List[str] = []
        for role in encoded_roles:
            hex_encoded_role = base64.b64decode(role).hex()
            roles.append(bytes.fromhex(hex_encoded_role).decode())

        return RegisterAndSetAllRolesOutcome(token_identifier, roles)

    def parse_set_burn_role_globally(self, transaction_outcome: TransactionOutcome) -> None:
        self.ensure_no_error(transaction_outcome.transaction_logs.events)

    def parse_unset_burn_role_globally(self, transaction_outcome: TransactionOutcome) -> None:
        self.ensure_no_error(transaction_outcome.transaction_logs.events)

    def parse_set_special_role(self, transaction_outcome: TransactionOutcome) -> SetSpecialRoleOutcome:
        self.ensure_no_error(transaction_outcome.transaction_logs.events)

        event = self.find_single_event_by_identifier(transaction_outcome, "ESDTSetRole")
        user_address = event.address
        token_identifier = self.extract_token_identifier(event)

        encoded_roles = event.topics[3:]
        roles: List[str] = []

        for role in encoded_roles:
            hex_encoded_role = base64.b64decode(role).hex()
            roles.append(bytes.fromhex(hex_encoded_role).decode())

        return SetSpecialRoleOutcome(user_address, token_identifier, roles)

    def parse_nft_create(self, transaction_outcome: TransactionOutcome) -> NFTCreateOutcome:
        self.ensure_no_error(transaction_outcome.transaction_logs.events)

        event = self.find_single_event_by_identifier(transaction_outcome, "ESDTNFTCreate")
        token_identifier = self.extract_token_identifier(event)
        nonce = self.extract_nonce(event)
        amount = self.extract_amount(event)

        return NFTCreateOutcome(token_identifier, nonce, amount)

    def parse_local_mint(self, transaction_outcome: TransactionOutcome) -> MintOutcome:
        self.ensure_no_error(transaction_outcome.transaction_logs.events)

        event = self.find_single_event_by_identifier(transaction_outcome, "ESDTLocalMint")
        user_address = event.address
        token_identifier = self.extract_token_identifier(event)
        nonce = self.extract_nonce(event)
        minted_supply = self.extract_amount(event)

        return MintOutcome(user_address, token_identifier, nonce, minted_supply)

    def parse_local_burn(self, transaction_outcome: TransactionOutcome) -> BurnOutcome:
        self.ensure_no_error(transaction_outcome.transaction_logs.events)

        event = self.find_single_event_by_identifier(transaction_outcome, "ESDTLocalBurn")
        user_address = event.address
        token_identifier = self.extract_token_identifier(event)
        nonce = self.extract_nonce(event)
        burnt_supply = self.extract_amount(event)

        return BurnOutcome(user_address, token_identifier, nonce, burnt_supply)

    def parse_pause(self, transaction_outcome: TransactionOutcome) -> PauseOutcome:
        self.ensure_no_error(transaction_outcome.transaction_logs.events)

        event = self.find_single_event_by_identifier(transaction_outcome, "ESDTPause")
        identifier = self.extract_token_identifier(event)

        return PauseOutcome(identifier)

    def parse_unpause(self, transaction_outcome: TransactionOutcome) -> UnPauseOutcome:
        self.ensure_no_error(transaction_outcome.transaction_logs.events)

        event = self.find_single_event_by_identifier(transaction_outcome, "ESDTUnPause")
        identifier = self.extract_token_identifier(event)

        return UnPauseOutcome(identifier)

    def parse_freeze(self, transaction_outcome: TransactionOutcome) -> FreezeOutcome:
        self.ensure_no_error(transaction_outcome.transaction_logs.events)

        event = self.find_single_event_by_identifier(transaction_outcome, "ESDTFreeze")
        user_address = self.extract_address(event)
        token_identifier = self.extract_token_identifier(event)
        nonce = self.extract_nonce(event)
        balance = self.extract_amount(event)

        return FreezeOutcome(user_address, token_identifier, nonce, balance)

    def parse_unfreeze(self, transaction_outcome: TransactionOutcome) -> UnFreezeOutcome:
        self.ensure_no_error(transaction_outcome.transaction_logs.events)

        event = self.find_single_event_by_identifier(transaction_outcome, "ESDTUnFreeze")
        user_address = self.extract_address(event)
        token_identifier = self.extract_token_identifier(event)
        nonce = self.extract_nonce(event)
        balance = self.extract_amount(event)

        return UnFreezeOutcome(user_address, token_identifier, nonce, balance)

    def parse_wipe(self, transaction_outcome: TransactionOutcome) -> WipeOutcome:
        self.ensure_no_error(transaction_outcome.transaction_logs.events)

        event = self.find_single_event_by_identifier(transaction_outcome, "ESDTWipe")
        user_address = self.extract_address(event)
        token_identifier = self.extract_token_identifier(event)
        nonce = self.extract_nonce(event)
        balance = self.extract_amount(event)

        return WipeOutcome(user_address, token_identifier, nonce, balance)

    def parse_update_attributes(self, transaction_outcome: TransactionOutcome) -> UpdateAttributesOutcome:
        self.ensure_no_error(transaction_outcome.transaction_logs.events)

        event = self.find_single_event_by_identifier(transaction_outcome, "ESDTNFTUpdateAttributes")
        token_identifier = self.extract_token_identifier(event)
        nonce = self.extract_nonce(event)
        attributes = base64.b64decode(event.topics[3]) if event.topics[3] else b""

        return UpdateAttributesOutcome(token_identifier, nonce, attributes)

    def parse_add_quantity(self, transaction_outcome: TransactionOutcome) -> AddQuantityOutcome:
        self.ensure_no_error(transaction_outcome.transaction_logs.events)

        event = self.find_single_event_by_identifier(transaction_outcome, "ESDTNFTAddQuantity")
        token_identifier = self.extract_token_identifier(event)
        nonce = self.extract_nonce(event)
        added_quantity = self.extract_amount(event)

        return AddQuantityOutcome(token_identifier, nonce, added_quantity)

    def parse_burn_quantity(self, transaction_outcome: TransactionOutcome) -> BurnQuantityOutcome:
        self.ensure_no_error(transaction_outcome.transaction_logs.events)

        event = self.find_single_event_by_identifier(transaction_outcome, "ESDTNFTBurn")
        token_identifier = self.extract_token_identifier(event)
        nonce = self.extract_nonce(event)
        added_quantity = self.extract_amount(event)

        return BurnQuantityOutcome(token_identifier, nonce, added_quantity)

    def ensure_no_error(self, transaction_events: List[TransactionEvent]) -> None:
        for event in transaction_events:
            if event.identifier == "signalError":
                hex_data = base64.b64decode(event.data or "").hex()
                data = bytes.fromhex(hex_data).decode()

                hex_message = base64.b64decode(event.topics[1] or "").hex()
                message = bytes.fromhex(hex_message).decode()

                raise ParseTransactionOutcomeError(f"encountered signalError: {message} ({bytes.fromhex(data[1:]).decode()})")

    def find_single_event_by_identifier(self, transaction_outcome: TransactionOutcome, identifier: str) -> TransactionEvent:
        events = self.gather_all_events(transaction_outcome)
        events_with_matching_id = [event for event in events if event.identifier == identifier]

        if len(events_with_matching_id) == 0:
            raise ParseTransactionOutcomeError(f"cannot find event of type {identifier}")

        if len(events_with_matching_id) > 1:
            raise ParseTransactionOutcomeError(f"found more than one event of type {identifier}")

        return events_with_matching_id[0]

    def gather_all_events(self, transaction_outcome: TransactionOutcome) -> List[TransactionEvent]:
        all_events = [*transaction_outcome.transaction_logs.events]

        for result in transaction_outcome.transaction_results:
            all_events.extend([*result.logs.events])

        return all_events

    def extract_token_identifier(self, event: TransactionEvent) -> str:
        if event.topics[0]:
            hex_ticker = base64.b64decode(event.topics[0]).hex()
            return bytes.fromhex(hex_ticker).decode()
        return ""

    def extract_nonce(self, event: TransactionEvent) -> str:
        if event.topics[1]:
            hex_nonce = base64.b64decode(event.topics[1]).hex()
            return str(int(hex_nonce, 16))
        return ""

    def extract_amount(self, event: TransactionEvent) -> str:
        if event.topics[2]:
            hex_amount = base64.b64decode(event.topics[2]).hex()
            return str(int(hex_amount, 16))
        return ""

    def extract_address(self, event: TransactionEvent) -> str:
        if event.topics[3]:
            hex_address = base64.b64decode(event.topics[3]).hex()
            return Address.new_from_hex(hex_address, DEFAULT_HRP).to_bech32()
        return ""
