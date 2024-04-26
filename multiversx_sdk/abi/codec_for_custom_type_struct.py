import io

from multiversx_sdk.abi.interface import ICodec
from multiversx_sdk.abi.values_single import StructValue


def encode_nested_struct(codec: ICodec, writer: io.BytesIO, value: StructValue):
    for field in value.fields:
        try:
            codec.do_encode_nested(writer, field.value)
        except Exception as e:
            raise Exception(f"cannot encode field '{field.name}' of struct, because of: {e}")


def encode_top_level_struct(codec: ICodec, writer: io.BytesIO, value: StructValue):
    encode_nested_struct(codec, writer, value)


def decode_nested_struct(codec: ICodec, reader: io.BytesIO, value: StructValue):
    for field in value.fields:
        try:
            codec.do_decode_nested(reader, field.value)
        except Exception as e:
            raise Exception(f"cannot decode field '{field.name}' of struct, because of: {e}")


def decode_top_level_struct(codec: ICodec, data: bytes, value: StructValue):
    reader = io.BytesIO(data)
    decode_nested_struct(codec, reader, value)
