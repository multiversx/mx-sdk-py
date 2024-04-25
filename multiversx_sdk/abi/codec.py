
import io
from typing import Any

from multiversx_sdk.abi.codec_for_simple_values_address import (
    decode_nested_address, decode_top_level_address, encode_nested_address,
    encode_top_level_address)
from multiversx_sdk.abi.codec_for_simple_values_boolean import (
    decode_nested_bool, decode_top_level_bool, encode_nested_bool,
    encode_top_level_bool)
from multiversx_sdk.abi.codec_for_simple_values_numerical import (
    encode_nested_number, encode_top_level_number)
from multiversx_sdk.abi.values_single import *


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
        if isinstance(value, BoolValue):
            encode_nested_bool(writer, value)
        elif isinstance(value, U8Value):
            encode_nested_number(writer, value.value, False, 1)
        elif isinstance(value, U16Value):
            encode_nested_number(writer, value.value, False, 2)
        elif isinstance(value, U32Value):
            encode_nested_number(writer, value.value, False, 4)
        elif isinstance(value, U64Value):
            encode_nested_number(writer, value.value, False, 8)
        elif isinstance(value, I8Value):
            encode_nested_number(writer, value.value, True, 1)
        elif isinstance(value, I16Value):
            encode_nested_number(writer, value.value, True, 2)
        elif isinstance(value, I32Value):
            encode_nested_number(writer, value.value, True, 4)
        elif isinstance(value, I64Value):
            encode_nested_number(writer, value.value, True, 8)
        elif isinstance(value, AddressValue):
            encode_nested_address(self, writer, value)
        else:
            raise ValueError(f"unsupported type for nested encoding: {type(value)}")

    def encode_top_level(self, value: Any) -> bytes:
        buffer = io.BytesIO()
        self.do_encode_top_level(buffer, value)
        return buffer.getvalue()

    def do_encode_top_level(self, writer: io.BytesIO, value: Any) -> None:
        if isinstance(value, BoolValue):
            encode_top_level_bool(writer, value)
        elif isinstance(value, U8Value):
            encode_top_level_number(writer, value.value, False)
        elif isinstance(value, U16Value):
            encode_top_level_number(writer, value.value, False)
        elif isinstance(value, U32Value):
            encode_top_level_number(writer, value.value, False)
        elif isinstance(value, U64Value):
            encode_top_level_number(writer, value.value, False)
        elif isinstance(value, I8Value):
            encode_top_level_number(writer, value.value, True)
        elif isinstance(value, I16Value):
            encode_top_level_number(writer, value.value, True)
        elif isinstance(value, I32Value):
            encode_top_level_number(writer, value.value, True)
        elif isinstance(value, I64Value):
            encode_top_level_number(writer, value.value, True)
        elif isinstance(value, AddressValue):
            encode_top_level_address(self, writer, value)
        else:
            raise ValueError(f"unsupported type for top-level encoding: {type(value)}")

    def decode_nested(self, data: bytes, value: Any) -> None:
        reader = io.BytesIO(data)

        try:
            self.do_decode_nested(reader, value)
        except ValueError as e:
            raise ValueError(f"cannot decode (nested) {type(value)}, because of: {e}")

    def do_decode_nested(self, reader: io.BytesIO, value: Any) -> None:
        if isinstance(value, BoolValue):
            decode_nested_bool(reader, value)
        elif isinstance(value, AddressValue):
            decode_nested_address(self, reader, value)
        else:
            raise ValueError(f"unsupported type for nested decoding: {type(value)}")

    def decode_top_level(self, data: bytes, value: Any) -> None:
        try:
            self.do_decode_top_level(data, value)
        except ValueError as e:
            raise ValueError(f"cannot decode (top-level) {type(value)}, because of: {e}")

    def do_decode_top_level(self, data: bytes, value: Any) -> None:
        if isinstance(value, BoolValue):
            decode_top_level_bool(data, value)
        elif isinstance(value, AddressValue):
            decode_top_level_address(self, data, value)
        else:
            raise ValueError(f"unsupported type for top-level decoding: {type(value)}")


