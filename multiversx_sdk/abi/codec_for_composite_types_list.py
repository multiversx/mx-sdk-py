import io

from multiversx_sdk.abi.interface import ICodec
from multiversx_sdk.abi.shared import decode_length, encode_length
from multiversx_sdk.abi.values_single import InputListValue, OutputListValue


def encode_nested_list(codec: ICodec, writer: io.BytesIO, value: InputListValue):
    encode_length(writer, len(value.items))
    _encode_list_items(codec, writer, value)


def encode_top_level_list(codec: ICodec, writer: io.BytesIO, value: InputListValue):
    _encode_list_items(codec, writer, value)


def decode_nested_list(codec: ICodec, reader: io.BytesIO, value: OutputListValue):
    length = decode_length(reader)

    value.items = []
    for _ in range(length):
        _decode_list_item(codec, reader, value)


def decode_top_level_list(codec: ICodec, data: bytes, value: OutputListValue):
    reader = io.BytesIO(data)
    value.items = []

    while reader.tell() < len(data):
        _decode_list_item(codec, reader, value)


def _encode_list_items(codec: ICodec, writer: io.BytesIO, value: InputListValue):
    for item in value.items:
        codec.do_encode_nested(writer, item)


def _decode_list_item(codec: ICodec, reader: io.BytesIO, value: OutputListValue):
    new_item = value.item_creator()
    codec.do_decode_nested(reader, new_item)
    value.items.append(new_item)
