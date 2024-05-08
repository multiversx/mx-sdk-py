import io

from values_single import EnumValue, U8Value

from multiversx_sdk.abi.interface import ICodec


class CodecForEnum:
    def __init__(self, general_codec: ICodec) -> None:
        self.general_codec = general_codec

    def encode_nested(self, writer: io.BytesIO, value: EnumValue):
        self.general_codec.do_decode_nested(writer, U8Value(value.discriminant))

        for field in value.fields:
            try:
                self.general_codec.do_encode_nested(writer, field.value)
            except Exception as e:
                raise Exception(f"cannot encode field '{field.name}' of enum, because of: {e}")

    def encode_top_level(self, writer: io.BytesIO, value: EnumValue):
        if value.discriminant == 0 and len(value.fields) == 0:
            # Write nothing
            return

        self.encode_nested(writer, value)

    def decode_nested(self, reader: io.BytesIO, value: EnumValue):
        discriminant = U8Value()
        self.general_codec.do_decode_nested(reader, discriminant)
        value.discriminant = discriminant.value

        for field in value.fields:
            try:
                self.general_codec.do_decode_nested(reader, field.value)
            except Exception as e:
                raise Exception(f"cannot decode field '{field.name}' of enum, because of: {e}")

    def decode_top_level(self, data: bytes, value: EnumValue):
        if len(data) == 0:
            value.discriminant = 0
            return

        reader = io.BytesIO(data)
        self.decode_nested(reader, value)
