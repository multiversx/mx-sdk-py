from typing import List

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.errors import ParseTransactionOutcomeError
from multiversx_sdk.core.transactions_outcome_parsers.delegation_transactions_outcome_parser_types import \
    CreateNewDelegationContractOutcome
from multiversx_sdk.core.transactions_outcome_parsers.resources import (
    TransactionEvent, TransactionOutcome, find_events_by_identifier)
from multiversx_sdk.network_providers.constants import DEFAULT_ADDRESS_HRP


class DelegationTransactionsOutcomeParser:
    def __init__(self) -> None:
        pass

    def parse_create_new_delegation_contract(
            self,
            transaction_outcome: TransactionOutcome
    ) -> List[CreateNewDelegationContractOutcome]:
        self._ensure_no_error(transaction_outcome.logs.events)

        events = find_events_by_identifier(transaction_outcome, "SCDeploy")
        return [CreateNewDelegationContractOutcome(self._extract_contract_address(event)) for event in events]

    def _ensure_no_error(self, transaction_events: List[TransactionEvent]) -> None:
        for event in transaction_events:
            if event.identifier == "signalError":
                data = event.data_items[0].decode()[1:] if len(event.data_items[0]) else ""
                message = event.topics[1].decode()

                raise ParseTransactionOutcomeError(f"encountered signalError: {message} ({bytes.fromhex(data).decode()})")

    def _extract_contract_address(self, event: TransactionEvent) -> str:
        if not event.topics[0]:
            return ""

        return Address(event.topics[0], DEFAULT_ADDRESS_HRP).to_bech32()
