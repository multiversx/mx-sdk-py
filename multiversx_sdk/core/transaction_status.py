from dataclasses import dataclass


@dataclass
class TransactionStatus:
    status: str
    is_completed: bool
    is_successful: bool
    is_failed: bool
    is_not_executable_in_block: bool

    def __init__(self, status: str):
        self.status = status.lower()
        self.is_completed = self._is_status_completed()
        self.is_successful = self._is_status_successful()
        self.is_failed = self._is_status_failed()
        self.is_not_executable_in_block = self._is_status_not_executable_in_block()

    def _is_status_completed(self) -> bool:
        return self._is_status_successful() or self._is_status_failed()

    def _is_status_successful(self) -> bool:
        return self.status == "executed" or self.status == "success" or self.status == "successful"

    def _is_status_failed(self) -> bool:
        return (
            self.status == "fail"
            or self.status == "failed"
            or self.status == "unsuccessful"
            or self.status == "invalid"
        )

    def _is_status_not_executable_in_block(self) -> bool:
        return self.status == "not-executable-in-block"
