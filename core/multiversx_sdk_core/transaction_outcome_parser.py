from multiversx_sdk_core.interfaces_of_network import (ITransactionEvent,
                                                       ITransactionOnNetwork)


class TransactionOutcomeParser:
    def __init__(self):
        pass

    def _ensure_no_error(self, transaction: ITransactionOnNetwork):
        for event in transaction.logs.events:
            if event.identifier == "signalError":
                data = event.data[1:].hex()
                message = event.topics[1].valueOf().toString()

                raise Exception(f"encountered signalError: {message} ({data})")

    def _find_single_event_by_identifier(self, transaction: ITransactionOnNetwork, identifier: str) -> ITransactionEvent:
        events = self._gather_all_events(transaction).filter(lambda event: event.identifier == identifier)

        if len(events) == 0:
            raise Exception(f"cannot find event of type {identifier}")
        if len(events) > 1:
            raise Exception(f"more than one event of type {identifier}")

        return events[0]

    def _gather_all_events(self, transaction: ITransactionOnNetwork) -> ITransactionEvent:
        all_events = []

        all_events.append(transaction.logs.events)

        for item in transaction.contract_results.items:
            all_events.append(item.logs.events)

        return all_events
