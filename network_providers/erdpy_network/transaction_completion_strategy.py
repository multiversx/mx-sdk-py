from typing import Protocol


class ITransactionStatus(Protocol):
    def is_pending(self):
        return False


class ITransactionOnNetwork(Protocol):
    def get_status(self) -> ITransactionStatus:
        return ITransactionStatus()


class TransactionCompletionStrategyOnApi:
    def is_completed(self, transaction: ITransactionOnNetwork) -> bool:
        return not transaction.get_status().is_pending()
