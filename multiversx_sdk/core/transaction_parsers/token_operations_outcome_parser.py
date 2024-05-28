import logging
from typing import Protocol

from multiversx_sdk.core import Address
from multiversx_sdk.core.codec import decode_unsigned_number
from multiversx_sdk.core.transaction_parsers.token_operations_outcome_parser_types import (
    AddQuantityOutcome, BurnOutcome, BurnQuantityOutcome, ESDTIssueOutcome,
    FreezingOutcome, MintOutcome, NFTCreateOutcome, PausingOutcome,
    RegisterAndSetAllRolesOutcome, SetSpecialRoleOutcome,
    UpdateAttributesOutcome, WipingOutcome)
from multiversx_sdk.core.transaction_parsers.transaction_on_network_wrapper import (
    ITransactionEvent, ITransactionOnNetwork, TransactionOnNetworkWrapper)

logger = logging.getLogger("TokenOperationsOutcomeParser")


class IConfig(Protocol):
    address_hrp: str


class TokenOperationsOutcomeParser:
    def __init__(self, config: IConfig) -> None:
        logger.warning("The 'TokenOperationsOutcomeParser' is deprecated and will soon be removed. Please use 'TokenManagementTransactionsOutcomeParser' instead.")
        self._config = config

    def parse_issue_fungible(self, transaction: ITransactionOnNetwork) -> ESDTIssueOutcome:
        wrapper = TransactionOnNetworkWrapper.from_transaction(transaction)
        wrapper.ensure_no_error()

        event = wrapper.find_single_event_by_identifier("issue")
        token_identifier = self._extract_token_identifier(event)
        return ESDTIssueOutcome(token_identifier)

    def parse_issue_non_fungible(self, transaction: ITransactionOnNetwork) -> ESDTIssueOutcome:
        wrapper = TransactionOnNetworkWrapper.from_transaction(transaction)
        wrapper.ensure_no_error()

        event = wrapper.find_single_event_by_identifier("issueNonFungible")
        token_identifier = self._extract_token_identifier(event)
        return ESDTIssueOutcome(token_identifier)

    def parse_issue_semi_fungible(self, transaction: ITransactionOnNetwork) -> ESDTIssueOutcome:
        wrapper = TransactionOnNetworkWrapper.from_transaction(transaction)
        wrapper.ensure_no_error()

        event = wrapper.find_single_event_by_identifier("issueSemiFungible")
        token_identifier = self._extract_token_identifier(event)
        return ESDTIssueOutcome(token_identifier)

    def parse_register_meta_esdt(self, transaction: ITransactionOnNetwork) -> ESDTIssueOutcome:
        wrapper = TransactionOnNetworkWrapper.from_transaction(transaction)
        wrapper.ensure_no_error()

        event = wrapper.find_single_event_by_identifier("registerMetaESDT")
        token_identifier = self._extract_token_identifier(event)
        return ESDTIssueOutcome(token_identifier)

    def parse_register_and_set_all_roles(self, transaction: ITransactionOnNetwork) -> RegisterAndSetAllRolesOutcome:
        wrapper = TransactionOnNetworkWrapper.from_transaction(transaction)
        wrapper.ensure_no_error()

        event_register = wrapper.find_single_event_by_identifier("registerAndSetAllRoles")
        token_identifier = self._extract_token_identifier(event_register)

        event_set_role = wrapper.find_single_event_by_identifier("ESDTSetRole")
        roles = [str(topic) for topic in event_set_role.topics[3:]]

        return RegisterAndSetAllRolesOutcome(token_identifier, roles)

    def parse_set_burn_role_globally(self, transaction: ITransactionOnNetwork) -> None:
        wrapper = TransactionOnNetworkWrapper.from_transaction(transaction)
        wrapper.ensure_no_error()

    def parse_unset_burn_role_globally(self, transaction: ITransactionOnNetwork) -> None:
        wrapper = TransactionOnNetworkWrapper.from_transaction(transaction)
        wrapper.ensure_no_error()

    def parse_set_special_role(self, transaction: ITransactionOnNetwork) -> SetSpecialRoleOutcome:
        wrapper = TransactionOnNetworkWrapper.from_transaction(transaction)
        wrapper.ensure_no_error()

        event = wrapper.find_single_event_by_identifier("ESDTSetRole")
        user_address = event.address.to_bech32()
        token_identifier = self._extract_token_identifier(event)
        roles = [str(topic) for topic in event.topics[3:]]

        return SetSpecialRoleOutcome(user_address, token_identifier, roles)

    def parse_nft_create(self, transaction: ITransactionOnNetwork) -> NFTCreateOutcome:
        wrapper = TransactionOnNetworkWrapper.from_transaction(transaction)
        wrapper.ensure_no_error()

        event = wrapper.find_single_event_by_identifier("ESDTNFTCreate")
        token_identifier = self._extract_token_identifier(event)
        nonce = self._extract_nonce(event)
        initial_quantity = self._extract_amount(event)

        return NFTCreateOutcome(token_identifier, nonce, initial_quantity)

    def parse_local_mint(self, transaction: ITransactionOnNetwork) -> MintOutcome:
        wrapper = TransactionOnNetworkWrapper.from_transaction(transaction)
        wrapper.ensure_no_error()

        event = wrapper.find_single_event_by_identifier("ESDTLocalMint")
        user_address = event.address.to_bech32()
        token_identifier = self._extract_token_identifier(event)
        nonce = self._extract_nonce(event)
        minted_supply = self._extract_amount(event)

        return MintOutcome(user_address, token_identifier, nonce, minted_supply)

    def parse_local_burn(self, transaction: ITransactionOnNetwork) -> BurnOutcome:
        wrapper = TransactionOnNetworkWrapper.from_transaction(transaction)
        wrapper.ensure_no_error()

        event = wrapper.find_single_event_by_identifier("ESDTLocalBurn")
        user_address = event.address.to_bech32()
        token_identifier = self._extract_token_identifier(event)
        nonce = self._extract_nonce(event)
        burnt_supply = self._extract_amount(event)

        return BurnOutcome(user_address, token_identifier, nonce, burnt_supply)

    def parse_pause(self, transaction: ITransactionOnNetwork) -> PausingOutcome:
        wrapper = TransactionOnNetworkWrapper.from_transaction(transaction)
        wrapper.ensure_no_error()

        _ = wrapper.find_single_event_by_identifier("ESDTPause")
        return PausingOutcome()

    def parse_unpause(self, transaction: ITransactionOnNetwork) -> PausingOutcome:
        wrapper = TransactionOnNetworkWrapper.from_transaction(transaction)
        wrapper.ensure_no_error()

        _ = wrapper.find_single_event_by_identifier("ESDTUnPause")
        return PausingOutcome()

    def parse_freeze(self, transaction: ITransactionOnNetwork) -> FreezingOutcome:
        wrapper = TransactionOnNetworkWrapper.from_transaction(transaction)
        wrapper.ensure_no_error()

        event = wrapper.find_single_event_by_identifier("ESDTFreeze")
        token_identifier = self._extract_token_identifier(event)
        nonce = self._extract_nonce(event)
        balance = self._extract_amount(event)
        user_address = self._extract_address(event)

        return FreezingOutcome(user_address, token_identifier, nonce, balance)

    def parse_unfreeze(self, transaction: ITransactionOnNetwork) -> FreezingOutcome:
        wrapper = TransactionOnNetworkWrapper.from_transaction(transaction)
        wrapper.ensure_no_error()

        event = wrapper.find_single_event_by_identifier("ESDTUnFreeze")
        token_identifier = self._extract_token_identifier(event)
        nonce = self._extract_nonce(event)
        balance = self._extract_amount(event)
        user_address = self._extract_address(event)

        return FreezingOutcome(user_address, token_identifier, nonce, balance)

    def parse_wipe(self, transaction: ITransactionOnNetwork) -> WipingOutcome:
        wrapper = TransactionOnNetworkWrapper.from_transaction(transaction)
        wrapper.ensure_no_error()

        event = wrapper.find_single_event_by_identifier("ESDTWipe")
        token_identifier = self._extract_token_identifier(event)
        nonce = self._extract_nonce(event)
        balance = self._extract_amount(event)
        user_address = self._extract_address(event)

        return WipingOutcome(user_address, token_identifier, nonce, balance)

    def parse_update_attributes(self, transaction: ITransactionOnNetwork) -> UpdateAttributesOutcome:
        wrapper = TransactionOnNetworkWrapper.from_transaction(transaction)
        wrapper.ensure_no_error()

        event = wrapper.find_single_event_by_identifier("ESDTNFTUpdateAttributes")
        token_identifier = self._extract_token_identifier(event)
        nonce = self._extract_nonce(event)
        attributes = event.topics[3].raw

        return UpdateAttributesOutcome(token_identifier, nonce, attributes)

    def parse_add_quantity(self, transaction: ITransactionOnNetwork) -> AddQuantityOutcome:
        wrapper = TransactionOnNetworkWrapper.from_transaction(transaction)
        wrapper.ensure_no_error()

        event = wrapper.find_single_event_by_identifier("ESDTNFTAddQuantity")
        token_identifier = self._extract_token_identifier(event)
        nonce = self._extract_nonce(event)
        added_quantity = self._extract_amount(event)

        return AddQuantityOutcome(token_identifier, nonce, added_quantity)

    def parse_burn_quantity(self, transaction: ITransactionOnNetwork) -> BurnQuantityOutcome:
        wrapper = TransactionOnNetworkWrapper.from_transaction(transaction)
        wrapper.ensure_no_error()

        event = wrapper.find_single_event_by_identifier("ESDTNFTBurn")
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
        return Address(event.topics[3].raw, self._config.address_hrp).to_bech32()
