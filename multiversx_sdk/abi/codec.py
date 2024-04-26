
import io
from typing import Any

from multiversx_sdk.abi.codec_for_custom_type_enum import (
    decode_nested_enum, decode_top_level_enum, encode_nested_enum,
    encode_top_level_enum)
from multiversx_sdk.abi.codec_for_custom_type_struct import (
    decode_nested_struct, decode_top_level_struct, encode_nested_struct,
    encode_top_level_struct)
from multiversx_sdk.abi.codec_for_simple_values_address import (
    decode_nested_address, decode_top_level_address, encode_nested_address,
    encode_top_level_address)
from multiversx_sdk.abi.codec_for_simple_values_boolean import (
    decode_nested_bool, decode_top_level_bool, encode_nested_bool,
    encode_top_level_bool)
from multiversx_sdk.abi.codec_for_simple_values_bytes import (
    decode_nested_bytes, decode_top_level_bytes, encode_nested_bytes,
    encode_top_level_bytes)
from multiversx_sdk.abi.codec_for_simple_values_numerical import (
    decode_nested_number, decode_top_level_number, encode_nested_number,
    encode_top_level_number)
from multiversx_sdk.abi.codec_for_simple_values_numerical_big import (
    decode_nested_big_number, decode_top_level_big_number,
    encode_nested_big_number, encode_top_level_big_number)
from multiversx_sdk.abi.codec_for_simple_values_string import (
    decode_nested_string, decode_top_level_string, encode_nested_string,
    encode_top_level_string)
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
        elif isinstance(value, BigUIntValue):
            encode_nested_big_number(writer, value.value, False)
        elif isinstance(value, BigIntValue):
            encode_nested_big_number(writer, value.value, True)
        elif isinstance(value, AddressValue):
            encode_nested_address(self, writer, value)
        elif isinstance(value, StringValue):
            encode_nested_string(writer, value)
        elif isinstance(value, BytesValue):
            encode_nested_bytes(writer, value)
        elif isinstance(value, StructValue):
            encode_nested_struct(self, writer, value)
        elif isinstance(value, EnumValue):
            encode_nested_enum(self, writer, value)
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
        elif isinstance(value, BigUIntValue):
            encode_top_level_big_number(writer, value.value, False)
        elif isinstance(value, BigIntValue):
            encode_top_level_big_number(writer, value.value, True)
        elif isinstance(value, AddressValue):
            encode_top_level_address(self, writer, value)
        elif isinstance(value, StringValue):
            encode_top_level_string(writer, value)
        elif isinstance(value, BytesValue):
            encode_top_level_bytes(writer, value)
        elif isinstance(value, StructValue):
            encode_top_level_struct(self, writer, value)
        elif isinstance(value, EnumValue):
            encode_top_level_enum(self, writer, value)
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
        elif isinstance(value, U8Value):
            decode_nested_number(reader, value, False, 1)
        elif isinstance(value, U16Value):
            decode_nested_number(reader, value, False, 2)
        elif isinstance(value, U32Value):
            decode_nested_number(reader, value, False, 4)
        elif isinstance(value, U64Value):
            decode_nested_number(reader, value, False, 8)
        elif isinstance(value, I8Value):
            decode_nested_number(reader, value, True, 1)
        elif isinstance(value, I16Value):
            decode_nested_number(reader, value, True, 2)
        elif isinstance(value, I32Value):
            decode_nested_number(reader, value, True, 4)
        elif isinstance(value, I64Value):
            decode_nested_number(reader, value, True, 8)
        elif isinstance(value, BigUIntValue):
            decode_nested_big_number(reader, value, False)
        elif isinstance(value, BigIntValue):
            decode_nested_big_number(reader, value, True)
        elif isinstance(value, AddressValue):
            decode_nested_address(self, reader, value)
        elif isinstance(value, StringValue):
            decode_nested_string(reader, value)
        elif isinstance(value, BytesValue):
            decode_nested_bytes(reader, value)
        elif isinstance(value, StructValue):
            decode_nested_struct(self, reader, value)
        elif isinstance(value, EnumValue):
            decode_nested_enum(self, reader, value)
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
        elif isinstance(value, U8Value):
            decode_top_level_number(data, value, False, 1)
        elif isinstance(value, U16Value):
            decode_top_level_number(data, value, False, 2)
        elif isinstance(value, U32Value):
            decode_top_level_number(data, value, False, 4)
        elif isinstance(value, U64Value):
            decode_top_level_number(data, value, False, 8)
        elif isinstance(value, I8Value):
            decode_top_level_number(data, value, True, 1)
        elif isinstance(value, I16Value):
            decode_top_level_number(data, value, True, 2)
        elif isinstance(value, I32Value):
            decode_top_level_number(data, value, True, 4)
        elif isinstance(value, I64Value):
            decode_top_level_number(data, value, True, 8)
        elif isinstance(value, BigUIntValue):
            decode_top_level_big_number(data, value, False)
        elif isinstance(value, BigIntValue):
            decode_top_level_big_number(data, value, True)
        elif isinstance(value, AddressValue):
            decode_top_level_address(self, data, value)
        elif isinstance(value, StringValue):
            decode_top_level_string(data, value)
        elif isinstance(value, BytesValue):
            decode_top_level_bytes(data, value)
        elif isinstance(value, StructValue):
            decode_top_level_struct(self, data, value)
        elif isinstance(value, EnumValue):
            decode_top_level_enum(self, data, value)
        else:
            raise ValueError(f"unsupported type for top-level decoding: {type(value)}")

