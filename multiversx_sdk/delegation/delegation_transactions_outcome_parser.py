from multiversx_sdk.core import (
    Address,
    TransactionEvent,
    TransactionOnNetwork,
    find_events_by_identifier,
)
from multiversx_sdk.core.config import LibraryConfig
from multiversx_sdk.core.errors import ParseTransactionOnNetworkError
from multiversx_sdk.delegation.delegation_transactions_outcome_parser_types import (
    ClaimRewardsOutcome,
    CreateNewDelegationContractOutcome,
    DelegateOutcome,
    RedelegateRewardsOutcome,
    UndelegateOutcome,
)


class DelegationTransactionsOutcomeParser:
    def __init__(self) -> None:
        pass

    def parse_create_new_delegation_contract(
        self, transaction: TransactionOnNetwork
    ) -> list[CreateNewDelegationContractOutcome]:
        self._ensure_no_error(transaction.logs.events)

        events = find_events_by_identifier(transaction, "SCDeploy")
        return [CreateNewDelegationContractOutcome(self._extract_contract_address(event)) for event in events]

    def parse_claim_rewards(self, transaction: TransactionOnNetwork) -> list[ClaimRewardsOutcome]:
        self._ensure_no_error(transaction.logs.events)

        events = find_events_by_identifier(transaction, "claimRewards")
        return [ClaimRewardsOutcome(self._extract_amount(event)) for event in events]

    def parse_delegate(self, transaction: TransactionOnNetwork) -> list[DelegateOutcome]:
        self._ensure_no_error(transaction.logs.events)

        events = find_events_by_identifier(transaction, "delegate")
        return [DelegateOutcome(self._extract_amount(event)) for event in events]

    def parse_undelegate(self, transaction: TransactionOnNetwork) -> list[UndelegateOutcome]:
        self._ensure_no_error(transaction.logs.events)

        events = find_events_by_identifier(transaction, "unDelegate")
        return [UndelegateOutcome(self._extract_amount(event)) for event in events]

    def parse_redelegate_rewards(self, transaction: TransactionOnNetwork) -> list[RedelegateRewardsOutcome]:
        outcome = self.parse_delegate(transaction)
        return [RedelegateRewardsOutcome(item.amount) for item in outcome]

    def _ensure_no_error(self, transaction_events: list[TransactionEvent]) -> None:
        for event in transaction_events:
            if event.identifier == "signalError":
                data = event.additional_data[0].decode()[1:] if len(event.additional_data[0]) else ""
                message = event.topics[1].decode()

                raise ParseTransactionOnNetworkError(
                    f"encountered signalError: {message} ({bytes.fromhex(data).decode()})"
                )

    def _extract_amount(self, event: TransactionEvent) -> int:
        if not event.topics[0]:
            raise Exception("No topic found for amount")
        return int.from_bytes(event.topics[0], byteorder="big", signed=False)

    def _extract_contract_address(self, event: TransactionEvent) -> Address:
        if not event.topics[0]:
            raise Exception("No topic found for contract address")
        return Address(event.topics[0], LibraryConfig.default_address_hrp)
