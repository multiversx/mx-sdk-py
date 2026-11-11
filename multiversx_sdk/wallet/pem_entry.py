import base64
import binascii
import textwrap

from multiversx_sdk.wallet.errors import InvalidPemError

HEADER_PREFIX = "-----BEGIN PRIVATE KEY for"
FOOTER_PREFIX = "-----END PRIVATE KEY for"
DELIMITER = "-----"


class PemEntry:
    def __init__(self, label: str, message: bytes) -> None:
        self.label: str = label
        self.message: bytes = message

    @classmethod
    def from_text_all(cls, pem_text: str) -> list["PemEntry"]:
        lines = pem_text.splitlines()
        lines = _clean_lines(lines)

        result: list[PemEntry] = []

        # Each entry is parsed on its own (header, message lines, footer), so that labels can't be paired with the wrong messages.
        for header, message_lines, footer in _group_blocks(lines):
            label = _parse_label(header, HEADER_PREFIX)
            if _parse_label(footer, FOOTER_PREFIX) != label:
                raise InvalidPemError("the END line does not match the BEGIN line")

            if not message_lines:
                raise InvalidPemError("an entry has no content")

            message_base64 = "".join(message_lines)
            message_bytes = _decode_message(message_base64)
            result.append(cls(label, message_bytes))

        return result

    def to_text(self) -> str:
        # Such labels would break the structure of the file.
        if DELIMITER in self.label or "".join(self.label.splitlines()) != self.label:
            raise InvalidPemError(f"the label must not contain line breaks or '{DELIMITER}'")

        # Such labels would not survive a save / load cycle: when parsing, the trailing dashes and the surrounding whitespace are dropped.
        if self.label != self.label.strip() or self.label.endswith("-"):
            raise InvalidPemError("the label must not start or end with whitespace, nor end with '-'")

        header = f"-----BEGIN PRIVATE KEY for {self.label}-----"
        footer = f"-----END PRIVATE KEY for {self.label}-----"

        message_hex = self.message.hex().encode()
        message_base64 = base64.b64encode(message_hex).decode()

        payload_lines = textwrap.wrap(message_base64, 64)
        payload = "\n".join(payload_lines)
        text = "\n".join([header, payload, footer])
        return text


def assert_index_is_valid(index: int, number_of_entries: int) -> None:
    # Negative indices are rejected, as well, since they would silently select entries from the end (hiding off-by-one errors).
    if not 0 <= index < number_of_entries:
        raise IndexError(f"PEM entry index {index} is out of range (number of entries: {number_of_entries})")


def _clean_lines(lines: list[str]) -> list[str]:
    lines = [line.strip() for line in lines]
    lines = list(filter(None, lines))
    return lines


def _group_blocks(lines: list[str]) -> list[tuple[str, list[str], str]]:
    blocks: list[tuple[str, list[str], str]] = []
    header = None
    message_lines: list[str] = []

    for line in lines:
        if line.startswith(HEADER_PREFIX):
            if header is not None:
                raise InvalidPemError("missing END line")

            header = line
            message_lines = []
        elif line.startswith(FOOTER_PREFIX):
            if header is None:
                raise InvalidPemError("missing BEGIN line")

            blocks.append((header, message_lines, line))
            header = None
        elif header is None:
            # The content of the line is not included in the error message, since it could be secret.
            raise InvalidPemError("unexpected line outside of an entry")
        else:
            message_lines.append(line)

    if header is not None:
        raise InvalidPemError("missing END line")

    return blocks


def _parse_label(line: str, prefix: str) -> str:
    # Only the delimiters are removed, so that dashes within the label are kept.
    # The trailing delimiter is handled leniently (e.g. "---" instead of "-----"), as before: such files exist in the wild.
    return line[len(prefix) :].rstrip("-").strip()


def _decode_message(message_base64: str) -> bytes:
    try:
        message_hex = base64.b64decode(message_base64, validate=True).decode()
        return bytes.fromhex(message_hex)
    except (binascii.Error, ValueError):
        # The underlying error is not chained, since its message could reveal bits of the (secret) content.
        raise InvalidPemError("the content of an entry is not properly encoded") from None
