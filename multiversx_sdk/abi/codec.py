import io

from multiversx_sdk.abi.interface import ISingleValue


class Codec:
    def __init__(self) -> None:
        pass

    def encode_nested(self, value: ISingleValue) -> bytes:
        buffer = io.BytesIO()
        value.encode_nested(buffer)
        return buffer.getvalue()

    def encode_top_level(self, value: ISingleValue) -> bytes:
        buffer = io.BytesIO()
        value.encode_top_level(buffer)
        return buffer.getvalue()

    def decode_nested(self, data: bytes, value: ISingleValue) -> None:
        reader = io.BytesIO(data)

        try:
            value.decode_nested(reader)
        except ValueError as e:
            raise ValueError(f"cannot decode (nested) {type(value)}, because of: {e}")

    def decode_top_level(self, data: bytes, value: ISingleValue) -> None:
        try:
            value.decode_top_level(data)
        except ValueError as e:
            raise ValueError(f"cannot decode (top-level) {type(value).__name__}, because of: {e}")
