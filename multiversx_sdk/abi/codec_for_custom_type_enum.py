import io

from values_single import EnumValue, U8Value

from multiversx_sdk.abi.interface import ICodec


def encode_nested_enum(codec: ICodec, writer: io.BytesIO, value: EnumValue):
    codec.do_decode_nested(writer, U8Value(value.discriminant))

    for field in value.fields:
        try:
            codec.do_encode_nested(writer, field.value)
        except Exception as e:
            raise Exception(f"cannot encode field '{field.name}' of enum, because of: {e}")


def encode_top_level_enum(codec: ICodec, writer: io.BytesIO, value: EnumValue):
    if value.discriminant == 0 and len(value.fields) == 0:
        # Write nothing
        return

    encode_nested_enum(codec, writer, value)


def decode_nested_enum(codec: ICodec, reader: io.BytesIO, value: EnumValue):
    discriminant = U8Value()
    codec.do_decode_nested(reader, discriminant)
    value.discriminant = discriminant.value

    for field in value.fields:
        try:
            codec.do_decode_nested(reader, field.value)
        except Exception as e:
            raise Exception(f"cannot decode field '{field.name}' of enum, because of: {e}")


def decode_top_level_enum(codec: ICodec, data: bytes, value: EnumValue):
    if len(data) == 0:
        value.discriminant = 0
        return

    reader = io.BytesIO(data)
    decode_nested_enum(codec, reader, value)
