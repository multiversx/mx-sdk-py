from typing import Any


class NetworkProviderError(Exception):
    def __init__(self, url: str, data: Any):
        super().__init__(f"Url = [{url}], error = {data}")
        self.url = url
        self.data = data


class ExpectedTransactionStatusNotReachedError(Exception):
    def __init__(self) -> None:
        super().__init__("The expected transaction status was not reached")


class ExpectedAccountConditionNotReachedError(Exception):
    def __init__(self) -> None:
        super().__init__("The expected account condition was not reached")


class TransactionFetchingError(NetworkProviderError):
    def __init__(self, url: str, error: Any):
        super().__init__(url, error)
