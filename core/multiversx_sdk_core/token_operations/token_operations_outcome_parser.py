
from dataclasses import dataclass
from typing import List

from multiversx_sdk_core.interfaces_of_network import (ITransactionEvent,
                                                       ITransactionOnNetwork)
from multiversx_sdk_core.transaction_outcome_parser import \
    TransactionOutcomeParser


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


class TokenOperationsOutcomeParser(TransactionOutcomeParser):
    def __init__(self):
        pass

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
        roles = event_set_role.topics[3:].map(lambda topic: str(topic))

        return RegisterAndSetAllRolesOutcome(token_identifier, roles)

    def parse_set_burn_role_globally(self, transaction: ITransactionOnNetwork) -> None:
        self._ensure_no_error(transaction)

    def parse_unset_burn_role_globally(self, transaction: ITransactionOnNetwork) -> None:
        self._ensure_no_error(transaction)

    def parse_set_special_role(self, transaction: ITransactionOnNetwork) -> SetSpecialRoleOutcome:
        self._ensure_no_error(transaction)

        event = self._find_single_event_by_identifier(transaction, "ESDTSetRole")
        user_address = event.address.toString()
        token_identifier = self._extract_token_identifier(event)
        roles = event.topics[3:].map(lambda topic: str(topic))

        return SetSpecialRoleOutcome(user_address, token_identifier, roles)

    def _extract_token_identifier(self, event: ITransactionEvent) -> str:
        return str(event.topics[0])
