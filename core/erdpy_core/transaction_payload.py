import base64

from erdpy_core.interfaces import ITransactionPayload


class TransactionPayload(ITransactionPayload):
    def __init__(self, data: bytes) -> None:
        self.data = data

    @classmethod
    def empty(cls):
        return TransactionPayload(bytes())

    @classmethod
    def from_str(cls, data: str):
        """
        Creates a TransactionPayload from a utf-8 string.
        """
        return TransactionPayload(data.encode("utf-8"))

    @classmethod
    def from_encoded_str(cls, encoded: str):
        """
        Creates a TransactionPayload from a base-64 encoded string.
        """
        data = base64.b64decode(encoded)
        return TransactionPayload(data)

    def is_empty(self):
        return len(self.data) == 0

    def length(self):
        return len(self.data)

    def encoded(self) -> str:
        return base64.b64encode(self.data).decode()

    def __str__(self) -> str:
        return self.data.decode("utf-8")
