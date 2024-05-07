import io

from multiversx_sdk.abi.interface import ICodec
from multiversx_sdk.abi.values_single import InputListValue, OutputListValue


def encode_nested_list(codec: ICodec, writer: io.BytesIO, value: InputListValue):
    pass


def encode_top_level_list(codec: ICodec, writer: io.BytesIO, value: InputListValue):
    pass


def decode_nested_list(codec: ICodec, reader: io.BytesIO, value: OutputListValue):
    pass


def decode_top_level_list(codec: ICodec, data: bytes, value: OutputListValue):
    pass


