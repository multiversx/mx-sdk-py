from typing import Protocol

from erdpy_network.transaction_logs import TransactionLogs
from erdpy_network.transaction_status import TransactionStatus
from erdpy_network.utils import is_padded_hex

KNOWN_COMPLETION_EVENTS = ["completedTxEvent", "SCDeploy", "signalError"]


class ITransactionStatus(Protocol):
    def is_pending(self) -> bool: ...


class ITransactionOnNetwork(Protocol):
    logs: TransactionLogs
    status: TransactionStatus
    hyperblock_nonce: int
    data: str

    def get_status(self) -> ITransactionStatus: ...


class TransactionCompletionStrategyOnApi:
    def is_completed(self, transaction: ITransactionOnNetwork) -> bool:
        return not transaction.get_status().is_pending()


# this class is similar to the one in erdjs-network-providers
# https://github.com/ElrondNetwork/elrond-sdk-erdjs-network-providers/blob/main/src/transactionCompletionStrategy.ts
class TransactionCompletionStrategyOnProxy:
    def is_completed(self, transaction: ITransactionOnNetwork) -> bool:
        if transaction.get_status().is_pending():
            return False

        for event in KNOWN_COMPLETION_EVENTS:
            if transaction.logs.find_first_or_none_event(event):
                return True

        if self.__is_certainly_move_balance(transaction.data):
            return transaction.status.is_executed()

        #  Imprecise condition, uncertain completion (usually sufficient, though).
        #  This is WRONG when (at least): timeOf(block with execution at destination is notarized) < timeOf(the "completedTxEvent" occurs).
        if transaction.hyperblock_nonce > 0:
            return True

        return False

    # erdjs implementation:
    # https://github.com/ElrondNetwork/elrond-sdk-erdjs-network-providers/blob/main/src/transactionCompletionStrategy.ts#L50
    def __is_certainly_move_balance(self, transaction_data: str) -> bool:
        parts = transaction_data.split("@")
        prefix = parts[0]
        other_parts = parts[1:]
        empty_prefix = not prefix
        some_parts_are_not_valid_args = not all(
            map(self.__is_valid_argument, other_parts)
        )

        return empty_prefix or some_parts_are_not_valid_args

    def __is_valid_argument(self, arg: str) -> bool:
        return is_padded_hex(arg)
