from erdpy_core.interfaces import ISignature


class Message:
    def __init__(self, data: bytes) -> None:
        self.data: bytes = data
        self.signature: ISignature = bytes()

    @classmethod
    def from_string(cls, data: str) -> 'Message':
        return Message(data.encode())

    def serialize_for_signing(self) -> bytes:
        return self.data
