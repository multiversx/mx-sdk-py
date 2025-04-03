import io
from typing import Any, cast

from multiversx_sdk.abi.shared import read_bytes_exactly
from multiversx_sdk.core.code_metadata import CODE_METADATA_LENGTH, CodeMetadata


class CodeMetadataValue:
    def __init__(self, value: bytes = b"") -> None:
        self.value = value

    @classmethod
    def new_from_code_metadata(cls, code_metadata: CodeMetadata) -> "CodeMetadataValue":
        return cls(code_metadata.serialize())

    def encode_nested(self, writer: io.BytesIO):
        writer.write(self.value)

    def encode_top_level(self, writer: io.BytesIO):
        writer.write(self.value)

    def decode_nested(self, reader: io.BytesIO):
        length = CODE_METADATA_LENGTH
        data = read_bytes_exactly(reader, length)
        self.value = data

    def decode_top_level(self, data: bytes):
        self.value = data

    def set_payload(self, value: Any):
        if isinstance(value, bytes):
            self.value = CodeMetadata.new_from_bytes(value).serialize()
        elif isinstance(value, CodeMetadata):
            self.value = value.serialize()
        elif isinstance(value, dict):
            value = cast(dict[str, str], value)
            self.value = self._extract_value_from_dict(value)
        else:
            raise ValueError(
                f"cannot set payload for code metadata (should be either a CodeMetadata, bytes or dict, but got: {type(value)})"
            )

    def _extract_value_from_dict(self, value: dict[str, str]) -> bytes:
        hex_value = value.get("hex", None)

        if not hex_value:
            raise ValueError("cannot get value from dictionary: missing 'hex' key")

        return bytes.fromhex(hex_value)

    def get_payload(self) -> Any:
        return self.value

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, CodeMetadataValue) and self.value == other.value

    def __bytes__(self) -> bytes:
        return self.value
