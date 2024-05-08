import io

from multiversx_sdk.abi.interface import ICodec
from multiversx_sdk.abi.shared import decode_length, encode_length
from multiversx_sdk.abi.values_single import InputListValue, OutputListValue


class CodecForList:
    def __init__(self, general_codec: ICodec) -> None:
        self.general_codec = general_codec

    def encode_nested(self, writer: io.BytesIO, value: InputListValue):
        encode_length(writer, len(value.items))
        self._encode_list_items(writer, value)

    def encode_top_level(self, writer: io.BytesIO, value: InputListValue):
        self._encode_list_items(writer, value)

    def decode_nested(self, reader: io.BytesIO, value: OutputListValue):
        length = decode_length(reader)

        value.items = []
        for _ in range(length):
            self._decode_list_item(reader, value)

    def decode_top_level(self, data: bytes, value: OutputListValue):
        reader = io.BytesIO(data)
        value.items = []

        while reader.tell() < len(data):
            self._decode_list_item(reader, value)

    def _encode_list_items(self, writer: io.BytesIO, value: InputListValue):
        for item in value.items:
            self.general_codec.do_encode_nested(writer, item)

    def _decode_list_item(self, reader: io.BytesIO, value: OutputListValue):
        new_item = value.item_creator()
        self.general_codec.do_decode_nested(reader, new_item)
        value.items.append(new_item)
