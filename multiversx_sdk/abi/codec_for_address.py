

import io

from multiversx_sdk.abi.interface import ICodec
from multiversx_sdk.abi.shared import read_bytes_exactly
from multiversx_sdk.abi.values_single import AddressValue


class CodecForAddress:
    def __init__(self, general_codec: ICodec) -> None:
        self.general_codec = general_codec

    def encode_nested(self, writer: io.BytesIO, value: AddressValue):
        self._check_pub_key_length(value.value)
        writer.write(value.value)

    def encode_top_level(self, writer: io.BytesIO, value: AddressValue):
        self.encode_nested(writer, value)

    def decode_nested(self, reader: io.BytesIO, value: AddressValue):
        data = read_bytes_exactly(reader, self.general_codec.pubkey_length)
        value.value = data

    def decode_top_level(self, data: bytes, value: AddressValue):
        self._check_pub_key_length(data)
        value.value = data

    def _check_pub_key_length(self, pubkey: bytes) -> None:
        if len(pubkey) != self.general_codec.pubkey_length:
            raise ValueError(f"public key (address) has invalid length: {len(pubkey)}")
