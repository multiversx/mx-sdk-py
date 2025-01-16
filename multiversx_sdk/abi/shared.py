import io
import struct
from typing import Any, Tuple

from multiversx_sdk.abi.constants import STRUCT_PACKING_FORMAT_FOR_UINT32


def encode_length(writer: io.BytesIO, length: int):
    bytes = struct.pack(STRUCT_PACKING_FORMAT_FOR_UINT32, length)
    writer.write(bytes)


def decode_length(reader: io.BytesIO) -> int:
    bytes = read_bytes_exactly(reader, 4)
    (length,) = struct.unpack(STRUCT_PACKING_FORMAT_FOR_UINT32, bytes)
    return length


def read_bytes_exactly(reader: io.BytesIO, num_bytes: int):
    if num_bytes == 0:
        return b""

    data = reader.read(num_bytes)
    if len(data) != num_bytes:
        raise ValueError(f"cannot read exactly {num_bytes} bytes")

    return data


def convert_native_value_to_dictionary(obj: Any, raise_on_failure: bool = True) -> Tuple[dict[str, Any], bool]:
    try:
        return dict(obj), True
    except Exception as error:
        error_on_dict_constructor = error

    try:
        return obj.__dict__, True
    except Exception as error:
        error_on_dict_attribute = error

    if raise_on_failure:
        raise ValueError(
            f"cannot convert native value to dictionary, because of: {error_on_dict_constructor} and {error_on_dict_attribute}"
        )

    return {}, False


def convert_native_value_to_list(obj: Any, raise_on_failure: bool = True) -> Tuple[list[Any], bool]:
    if isinstance(obj, dict):
        raise ValueError("cannot properly convert dictionary to list")

    try:
        return list(obj), True
    except Exception as error:
        if raise_on_failure:
            raise ValueError(f"cannot convert native value to list, because of: {error}")

        return [], False
