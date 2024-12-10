from multiversx_sdk.core import (Address, TransactionEvent,
                                 TransactionOnNetwork,
                                 find_events_by_identifier)
from multiversx_sdk.core.config import LibraryConfig
from multiversx_sdk.core.errors import ParseTransactionOnNetworkError
from multiversx_sdk.delegation.delegation_transactions_outcome_parser_types import \
    CreateNewDelegationContractOutcome


class DelegationTransactionsOutcomeParser:
    def __init__(self) -> None:
        pass

    def parse_create_new_delegation_contract(self,
                                             transaction: TransactionOnNetwork) -> list[CreateNewDelegationContractOutcome]:
        self._ensure_no_error(transaction.logs.events)

        events = find_events_by_identifier(transaction, "SCDeploy")
        return [CreateNewDelegationContractOutcome(self._extract_contract_address(event)) for event in events]

    def _ensure_no_error(self, transaction_events: list[TransactionEvent]) -> None:
        for event in transaction_events:
            if event.identifier == "signalError":
                data = event.additional_data[0].decode()[1:] if len(event.additional_data[0]) else ""
                message = event.topics[1].decode()

                raise ParseTransactionOnNetworkError(f"encountered signalError: {message} ({bytes.fromhex(data).decode()})")

    def _extract_contract_address(self, event: TransactionEvent) -> Address:
        if not event.topics[0]:
            raise Exception("No topic found for contract address")
        return Address(event.topics[0], LibraryConfig.default_address_hrp)
