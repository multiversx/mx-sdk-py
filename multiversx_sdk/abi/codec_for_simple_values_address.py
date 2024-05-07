

import io

from multiversx_sdk.abi.interface import ICodec
from multiversx_sdk.abi.shared import read_bytes_exactly
from multiversx_sdk.abi.values_single import AddressValue


def encode_nested_address(codec: ICodec, writer: io.BytesIO, value: AddressValue):
    check_pub_key_length(codec, value.value)
    writer.write(value.value)


def encode_top_level_address(codec: ICodec, writer: io.BytesIO, value: AddressValue):
    encode_nested_address(codec, writer, value)


def decode_nested_address(codec: ICodec, reader: io.BytesIO, value: AddressValue):
    data = read_bytes_exactly(reader, codec.pubkey_length)
    value.value = data


def decode_top_level_address(codec: ICodec, data: bytes, value: AddressValue):
    check_pub_key_length(codec, data)
    value.value = data


def check_pub_key_length(codec: ICodec, pubkey: bytes) -> None:
    if len(pubkey) != codec.pubkey_length:
        raise ValueError(f"public key (address) has invalid length: {len(pubkey)}")
