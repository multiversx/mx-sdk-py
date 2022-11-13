
ISignature = bytes


class ISignable:
    def serialize_for_signing(self) -> ISignature:
        return bytes()

    def apply_signature(self, signature: ISignature):
        pass
