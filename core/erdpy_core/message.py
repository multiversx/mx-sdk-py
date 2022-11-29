from erdpy_core.interfaces import ISignature


class Message:
    def __init__(self, data: bytes) -> None:
        self.data = data

    @classmethod
    def from_string(cls, data: str) -> 'Message':
        return Message(data.encode())

    def serialize_for_signing(self) -> bytes:
        return self.data

    def set_signature(self, signature: ISignature) -> None:
        self.signature = signature

    def get_signature(self) -> ISignature:
        return self.signature
