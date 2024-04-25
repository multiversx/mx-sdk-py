
import io
from typing import Any

from multiversx_sdk.abi.codec_for_simple_values_address import \
    encode_nested_address
from multiversx_sdk.abi.codec_for_simple_values_boolean import \
    encode_nested_bool
from multiversx_sdk.abi.values_single import AddressValue, BoolValue


class Codec:
    def __init__(self, pubkey_length: int) -> None:
        if pubkey_length == 0:
            raise ValueError("cannot create codec: bad public key length")

        self.pubkey_length = pubkey_length

    def encode_nested(self, value: Any) -> bytes:
        buffer = io.BytesIO()
        self.do_encode_nested(buffer, value)
        return buffer.getvalue()

    def do_encode_nested(self, writer: io.BytesIO, value: Any) -> None:
        if isinstance(value, AddressValue):
            encode_nested_address(self, writer, value)
        if isinstance(value, BoolValue):
            encode_nested_bool(writer, value)
        else:
            raise ValueError(f"unsupported type for nested encoding: {type(value)}")
