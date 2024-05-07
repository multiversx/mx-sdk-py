import io

from multiversx_sdk.abi.interface import ICodec
from multiversx_sdk.abi.values_single import OptionValue


def encode_nested_option(codec: ICodec, writer: io.BytesIO, value: OptionValue):
    pass


def encode_top_level_option(codec: ICodec, writer: io.BytesIO, value: OptionValue):
    pass


def decode_nested_option(codec: ICodec, reader: io.BytesIO, value: OptionValue):
    pass


def decode_top_level_option(codec: ICodec, data: bytes, value: OptionValue):
    pass
