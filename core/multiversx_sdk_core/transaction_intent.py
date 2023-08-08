from typing import Optional


class TransactionIntent:
    def __init__(self) -> None:
        self.sender: str = ""
        self.receiver: str = ""
        self.gas_limit: int = 0
        self.value: Optional[int] = 0
        self.data: Optional[bytes] = b""
