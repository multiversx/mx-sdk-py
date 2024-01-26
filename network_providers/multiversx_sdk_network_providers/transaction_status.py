from typing import Union


class TransactionStatus:
    def __init__(self, status: Union[str, None] = None):
        if not status:
            self.status: str = 'unknown'
        else:
            self.status = status.lower()

    def is_pending(self) -> bool:
        return self.status == 'received' or self.status == 'pending'

    def is_successful(self) -> bool:
        return self.status == 'executed' or self.status == 'success' or self.status == 'successful'

    def is_invalid(self) -> bool:
        return self.status == 'invalid'

    def is_failed(self) -> bool:
        return self.status == 'fail' or self.status == 'failed' or self.status == 'unsuccessful' or self.is_invalid()

    def is_executed(self) -> bool:
        return self.is_successful() or self.is_failed() or self.is_invalid()

    def equals(self, other: 'TransactionStatus') -> bool:
        return self.status == other.status

    def __str__(self) -> str:
        return self.status
