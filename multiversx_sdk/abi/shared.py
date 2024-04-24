import io
import struct

from multiversx_sdk.abi.constants import STRUCT_PACKING_FORMAT_FOR_UINT32


def encode_length(writer: io.BufferedWriter, length: int):
    bytes = struct.pack(STRUCT_PACKING_FORMAT_FOR_UINT32, length)
    writer.write(bytes)


def decode_length(reader: io.BufferedReader) -> int:
    bytes = read_bytes_exactly(reader, 4)
    (length,) = struct.unpack(STRUCT_PACKING_FORMAT_FOR_UINT32, bytes)
    return length


def read_bytes_exactly(reader: io.BufferedReader, num_bytes: int):
    if num_bytes == 0:
        return b''

    data = reader.read(num_bytes)
    if len(data) != num_bytes:
        raise ValueError(f"cannot read exactly {num_bytes} bytes")

    return data
