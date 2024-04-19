from typing import Any


class GenericError(Exception):
    def __init__(self, url: str, data: Any):
        super().__init__(f"Url = [{url}], error = {data}")
        self.url = url
        self.data = data


class ExpectedTransactionStatusNotReached(Exception):
    def __init__(self) -> None:
        super().__init__("The expected transaction status was not reached")


class IsCompletedFieldMissingOnTransaction(Exception):
    def __init__(self) -> None:
        super().__init__("The transaction awaiter requires the `is_completed` property to be defined on the transaction object. Perhaps you've used `ProxyNetworkProvider.get_transaction()` and in that case you should also pass `with_process_status=True`")
