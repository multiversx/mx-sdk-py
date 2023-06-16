from typing import List

from multiversx_sdk_core.interfaces_of_network import (ITransactionEvent,
                                                       ITransactionOnNetwork)


class TransactionOutcomeParser:
    def __init__(self):
        pass

    def _ensure_no_error(self, transaction: ITransactionOnNetwork):
        for event in transaction.logs.events:
            if event.identifier == "signalError":
                data = event.data[1:]
                message = str(event.topics[1])

                raise Exception(f"encountered signalError: {message} ({data})")

    def _find_single_event_by_identifier(self, transaction: ITransactionOnNetwork, identifier: str) -> ITransactionEvent:
        all_events = self._gather_all_events(transaction)
        filtered_events = [event for event in all_events if event.identifier == identifier]

        if len(filtered_events) == 0:
            raise Exception(f"cannot find event of type {identifier}")
        if len(filtered_events) > 1:
            raise Exception(f"more than one event of type {identifier}")

        return filtered_events[0]

    def _gather_all_events(self, transaction: ITransactionOnNetwork) -> List[ITransactionEvent]:
        all_events: List[ITransactionEvent] = []
        all_events.extend(transaction.logs.events)

        for item in transaction.contract_results.items:
            all_events.extend(item.logs.events)

        return all_events
