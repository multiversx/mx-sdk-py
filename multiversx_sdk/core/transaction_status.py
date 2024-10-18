from dataclasses import dataclass


@dataclass
class TransactionStatus:
    status: str
    is_completed: bool
    is_successful: bool

    def __init__(self, status: str):
        self.status = status.lower()
        self.is_completed = self.__is_status_completed()
        self.is_successful = self.__is_status_successful()

    def __is_status_completed(self) -> bool:
        return self.__is_status_successful() or self.__is_failed()

    def __is_status_successful(self) -> bool:
        return self.status == 'executed' or self.status == 'success' or self.status == 'successful'

    def __is_failed(self) -> bool:
        return self.status == 'fail' or self.status == 'failed' or self.status == 'unsuccessful' or self.status == "invalid"
