
import io
from typing import Any

from multiversx_sdk.abi.codec_for_address import CodecForAddress
from multiversx_sdk.abi.codec_for_big_int import CodecForBigInt
from multiversx_sdk.abi.codec_for_bool import CodecForBool
from multiversx_sdk.abi.codec_for_bytes import CodecForBytes
from multiversx_sdk.abi.codec_for_enum import CodecForEnum
from multiversx_sdk.abi.codec_for_list import CodecForList
from multiversx_sdk.abi.codec_for_option import CodecForOption
from multiversx_sdk.abi.codec_for_small_int import CodecForSmallInt
from multiversx_sdk.abi.codec_for_string import CodecForString
from multiversx_sdk.abi.codec_for_struct import CodecForStruct
from multiversx_sdk.abi.values_single import *


class Codec:
    def __init__(self, pubkey_length: int) -> None:
        if pubkey_length == 0:
            raise ValueError("cannot create codec: bad public key length")

        self.pubkey_length = pubkey_length
        self.codec_for_bool = CodecForBool()
        self.codec_for_small_int = CodecForSmallInt()
        self.codec_for_big_int = CodecForBigInt()
        self.codec_for_address = CodecForAddress(self)
        self.codec_for_string = CodecForString()
        self.codec_for_bytes = CodecForBytes()
        self.codec_for_struct = CodecForStruct(self)
        self.codec_for_enum = CodecForEnum(self)
        self.codec_for_option = CodecForOption(self)
        self.codec_for_list = CodecForList(self)

    def encode_nested(self, value: Any) -> bytes:
        buffer = io.BytesIO()
        self.do_encode_nested(buffer, value)
        return buffer.getvalue()

    def do_encode_nested(self, writer: io.BytesIO, value: Any) -> None:
        if isinstance(value, BoolValue):
            self.codec_for_bool.encode_nested(writer, value)
        elif isinstance(value, U8Value):
            self.codec_for_small_int.encode_nested_unsigned(writer, value.value, 1)
        elif isinstance(value, U16Value):
            self.codec_for_small_int.encode_nested_unsigned(writer, value.value, 2)
        elif isinstance(value, U32Value):
            self.codec_for_small_int.encode_nested_unsigned(writer, value.value, 4)
        elif isinstance(value, U64Value):
            self.codec_for_small_int.encode_nested_unsigned(writer, value.value, 8)
        elif isinstance(value, I8Value):
            self.codec_for_small_int.encode_nested_signed(writer, value.value, 1)
        elif isinstance(value, I16Value):
            self.codec_for_small_int.encode_nested_signed(writer, value.value, 2)
        elif isinstance(value, I32Value):
            self.codec_for_small_int.encode_nested_signed(writer, value.value, 4)
        elif isinstance(value, I64Value):
            self.codec_for_small_int.encode_nested_signed(writer, value.value, 8)
        elif isinstance(value, BigUIntValue):
            self.codec_for_big_int.encode_nested_unsigned(writer, value.value)
        elif isinstance(value, BigIntValue):
            self.codec_for_big_int.encode_nested_signed(writer, value.value)
        elif isinstance(value, AddressValue):
            self.codec_for_address.encode_nested(writer, value)
        elif isinstance(value, StringValue):
            self.codec_for_string.encode_nested(writer, value)
        elif isinstance(value, BytesValue):
            self.codec_for_bytes.encode_nested(writer, value)
        elif isinstance(value, StructValue):
            self.codec_for_struct.encode_nested(writer, value)
        elif isinstance(value, EnumValue):
            self.codec_for_enum.encode_nested(writer, value)
        elif isinstance(value, OptionValue):
            self.codec_for_option.encode_nested(writer, value)
        elif isinstance(value, InputListValue):
            self.codec_for_list.encode_nested(writer, value)
        else:
            raise ValueError(f"unsupported type for nested encoding: {type(value).__name__}")

    def encode_top_level(self, value: Any) -> bytes:
        buffer = io.BytesIO()
        self.do_encode_top_level(buffer, value)
        return buffer.getvalue()

    def do_encode_top_level(self, writer: io.BytesIO, value: Any) -> None:
        if isinstance(value, BoolValue):
            self.codec_for_bool.encode_top_level(writer, value)
        elif isinstance(value, U8Value):
            self.codec_for_small_int.encode_top_level_unsigned(writer, value.value)
        elif isinstance(value, U16Value):
            self.codec_for_small_int.encode_top_level_unsigned(writer, value.value)
        elif isinstance(value, U32Value):
            self.codec_for_small_int.encode_top_level_unsigned(writer, value.value)
        elif isinstance(value, U64Value):
            self.codec_for_small_int.encode_top_level_unsigned(writer, value.value)
        elif isinstance(value, I8Value):
            self.codec_for_small_int.encode_top_level_signed(writer, value.value)
        elif isinstance(value, I16Value):
            self.codec_for_small_int.encode_top_level_signed(writer, value.value)
        elif isinstance(value, I32Value):
            self.codec_for_small_int.encode_top_level_signed(writer, value.value)
        elif isinstance(value, I64Value):
            self.codec_for_small_int.encode_top_level_signed(writer, value.value)
        elif isinstance(value, BigUIntValue):
            self.codec_for_big_int.encode_top_level_unsigned(writer, value.value)
        elif isinstance(value, BigIntValue):
            self.codec_for_big_int.encode_top_level_signed(writer, value.value)
        elif isinstance(value, AddressValue):
            self.codec_for_address.encode_top_level(writer, value)
        elif isinstance(value, StringValue):
            self.codec_for_string.encode_top_level(writer, value)
        elif isinstance(value, BytesValue):
            self.codec_for_bytes.encode_top_level(writer, value)
        elif isinstance(value, StructValue):
            self.codec_for_struct.encode_top_level(writer, value)
        elif isinstance(value, EnumValue):
            self.codec_for_enum.encode_top_level(writer, value)
        elif isinstance(value, OptionValue):
            self.codec_for_option.encode_top_level(writer, value)
        elif isinstance(value, InputListValue):
            self.codec_for_list.encode_top_level(writer, value)
        else:
            raise ValueError(f"unsupported type for top-level encoding: {type(value).__name__}")

    def decode_nested(self, data: bytes, value: Any) -> None:
        reader = io.BytesIO(data)

        try:
            self.do_decode_nested(reader, value)
        except ValueError as e:
            raise ValueError(f"cannot decode (nested) {type(value)}, because of: {e}")

    def do_decode_nested(self, reader: io.BytesIO, value: Any) -> None:
        if isinstance(value, BoolValue):
            self.codec_for_bool.decode_nested(reader, value)
        elif isinstance(value, U8Value):
            self.codec_for_small_int.decode_nested_unsigned(reader, value, 1)
        elif isinstance(value, U16Value):
            self.codec_for_small_int.decode_nested_unsigned(reader, value, 2)
        elif isinstance(value, U32Value):
            self.codec_for_small_int.decode_nested_unsigned(reader, value, 4)
        elif isinstance(value, U64Value):
            self.codec_for_small_int.decode_nested_unsigned(reader, value, 8)
        elif isinstance(value, I8Value):
            self.codec_for_small_int.decode_nested_signed(reader, value, 1)
        elif isinstance(value, I16Value):
            self.codec_for_small_int.decode_nested_signed(reader, value, 2)
        elif isinstance(value, I32Value):
            self.codec_for_small_int.decode_nested_signed(reader, value, 4)
        elif isinstance(value, I64Value):
            self.codec_for_small_int.decode_nested_signed(reader, value, 8)
        elif isinstance(value, BigUIntValue):
            self.codec_for_big_int.decode_nested_unsigned(reader, value)
        elif isinstance(value, BigIntValue):
            self.codec_for_big_int.decode_nested_signed(reader, value)
        elif isinstance(value, AddressValue):
            self.codec_for_address.decode_nested(reader, value)
        elif isinstance(value, StringValue):
            self.codec_for_string.decode_nested(reader, value)
        elif isinstance(value, BytesValue):
            self.codec_for_bytes.decode_nested(reader, value)
        elif isinstance(value, StructValue):
            self.codec_for_struct.decode_nested(reader, value)
        elif isinstance(value, EnumValue):
            self.codec_for_enum.decode_nested(reader, value)
        elif isinstance(value, OptionValue):
            self.codec_for_option.decode_nested(reader, value)
        elif isinstance(value, OutputListValue):
            self.codec_for_list.decode_nested(reader, value)
        else:
            raise ValueError(f"unsupported type for nested decoding: {type(value).__name__}")

    def decode_top_level(self, data: bytes, value: Any) -> None:
        try:
            self.do_decode_top_level(data, value)
        except ValueError as e:
            raise ValueError(f"cannot decode (top-level) {type(value).__name__}, because of: {e}")

    def do_decode_top_level(self, data: bytes, value: Any) -> None:
        if isinstance(value, BoolValue):
            self.codec_for_bool.decode_top_level(data, value)
        elif isinstance(value, U8Value):
            self.codec_for_small_int.decode_top_level_unsigned(data, value, 1)
        elif isinstance(value, U16Value):
            self.codec_for_small_int.decode_top_level_unsigned(data, value, 2)
        elif isinstance(value, U32Value):
            self.codec_for_small_int.decode_top_level_unsigned(data, value, 4)
        elif isinstance(value, U64Value):
            self.codec_for_small_int.decode_top_level_unsigned(data, value, 8)
        elif isinstance(value, I8Value):
            self.codec_for_small_int.decode_top_level_signed(data, value, 1)
        elif isinstance(value, I16Value):
            self.codec_for_small_int.decode_top_level_signed(data, value, 2)
        elif isinstance(value, I32Value):
            self.codec_for_small_int.decode_top_level_signed(data, value, 4)
        elif isinstance(value, I64Value):
            self.codec_for_small_int.decode_top_level_signed(data, value, 8)
        elif isinstance(value, BigUIntValue):
            self.codec_for_big_int.decode_top_level_unsigned(data, value)
        elif isinstance(value, BigIntValue):
            self.codec_for_big_int.decode_top_level_signed(data, value)
        elif isinstance(value, AddressValue):
            self.codec_for_address.decode_top_level(data, value)
        elif isinstance(value, StringValue):
            self.codec_for_string.decode_top_level(data, value)
        elif isinstance(value, BytesValue):
            self.codec_for_bytes.decode_top_level(data, value)
        elif isinstance(value, StructValue):
            self.codec_for_struct.decode_top_level(data, value)
        elif isinstance(value, EnumValue):
            self.codec_for_enum.decode_top_level(data, value)
        elif isinstance(value, OptionValue):
            self.codec_for_option.decode_top_level(data, value)
        elif isinstance(value, OutputListValue):
            self.codec_for_list.decode_top_level(data, value)
        else:
            raise ValueError(f"unsupported type for top-level decoding: {type(value).__name__}")
