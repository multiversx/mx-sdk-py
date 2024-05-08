import io

from multiversx_sdk.abi.interface import ICodec
from multiversx_sdk.abi.values_single import StructValue


class CodecForStruct:
    def __init__(self, general_codec: ICodec) -> None:
        self.general_codec = general_codec

    def encode_nested(self, writer: io.BytesIO, value: StructValue):
        for field in value.fields:
            try:
                self.general_codec.do_encode_nested(writer, field.value)
            except Exception as e:
                raise Exception(f"cannot encode field '{field.name}' of struct, because of: {e}")

    def encode_top_level(self, writer: io.BytesIO, value: StructValue):
        self.encode_nested(writer, value)

    def decode_nested(self, reader: io.BytesIO, value: StructValue):
        for field in value.fields:
            try:
                self.general_codec.do_decode_nested(reader, field.value)
            except Exception as e:
                raise Exception(f"cannot decode field '{field.name}' of struct, because of: {e}")

    def decode_top_level(self, data: bytes, value: StructValue):
        reader = io.BytesIO(data)
        self.decode_nested(reader, value)
