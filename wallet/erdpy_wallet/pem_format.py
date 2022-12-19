import base64
import itertools
import textwrap
from pathlib import Path
from typing import List


class PemEntry:
    def __init__(self, label: str, message: bytes) -> None:
        self.label: str = label
        self.message: bytes = message


def parse(pem_file: Path, index: int = 0) -> PemEntry:
    pairs = parse_all(pem_file)
    pair = pairs[index]
    return pair


def parse_all(pem_file: Path) -> List[PemEntry]:
    pem_file = pem_file.expanduser()
    _guard_is_file(pem_file)

    lines = _read_lines(pem_file)
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


def _guard_is_file(input: Path):
    if not input.is_file():
        raise Exception(str(input), "is not a valid file")


def _read_lines(file: Path) -> List[str]:
    with open(file) as f:
        lines = f.readlines()
    lines = [line.strip() for line in lines]
    lines = [line for line in lines if line]
    return lines


def _write_file(file_path: Path, text: str):
    with open(file_path, "w") as file:
        return file.write(text)
