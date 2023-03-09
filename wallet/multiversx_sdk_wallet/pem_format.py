import base64
import itertools
import textwrap
from pathlib import Path
from typing import List


class PemEntry:
    def __init__(self, label: str, message: bytes) -> None:
        self.label: str = label
        self.message: bytes = message


def parse_text(pem_text: str) -> List[PemEntry]:
    lines = pem_text.splitlines()
    lines = _clean_lines(lines)

    messages_lines = [list(message_lines) for is_next_entry, message_lines in itertools.groupby(lines, lambda line: "-----" in line)
                      if not is_next_entry]
    messages_base64 = ["".join(message_lines) for message_lines in messages_lines]
    labels = _parse_labels(lines)

    result: List[PemEntry] = []

    for index, message_base64 in enumerate(messages_base64):
        message_hex = base64.b64decode(message_base64).decode()
        message_bytes = bytes.fromhex(message_hex)
        label = labels[index]

        result.append(PemEntry(label, message_bytes))

    return result


def _clean_lines(lines: List[str]) -> List[str]:
    lines = [line.strip() for line in lines]
    lines = list(filter(None, lines))
    return lines


def _parse_labels(headers: List[str]) -> List[str]:
    marker = "-----BEGIN PRIVATE KEY for"
    headers = [line for line in headers if line.startswith(marker)]
    labels = [line.replace(marker, "").replace("-", "").strip() for line in headers]
    return labels


def write(path: Path, label: str, message: bytes):
    path = path.expanduser()
    header = f"-----BEGIN PRIVATE KEY for {label}-----"
    footer = f"-----END PRIVATE KEY for {label}-----"

    message_hex = message.hex().encode()
    message_base64 = base64.b64encode(message_hex).decode()

    payload_lines = textwrap.wrap(message_base64, 64)
    payload = "\n".join(payload_lines)
    content = "\n".join([header, payload, footer])
    _write_file(path, content)


def _write_file(file_path: Path, text: str):
    with open(file_path, "w") as file:
        return file.write(text)
