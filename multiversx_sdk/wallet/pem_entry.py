import base64
import itertools
import textwrap


class PemEntry:
    def __init__(self, label: str, message: bytes) -> None:
        self.label: str = label
        self.message: bytes = message

    @classmethod
    def from_text_all(cls, pem_text: str) -> list["PemEntry"]:
        lines = pem_text.splitlines()
        lines = _clean_lines(lines)

        messages_lines = [
            list(message_lines)
            for is_next_entry, message_lines in itertools.groupby(lines, lambda line: "-----" in line)
            if not is_next_entry
        ]
        messages_base64 = ["".join(message_lines) for message_lines in messages_lines]
        labels = _parse_labels(lines)

        result: list[PemEntry] = []

        for index, message_base64 in enumerate(messages_base64):
            message_hex = base64.b64decode(message_base64).decode()
            message_bytes = bytes.fromhex(message_hex)
            label = labels[index]

            result.append(cls(label, message_bytes))

        return result

    def to_text(self) -> str:
        header = f"-----BEGIN PRIVATE KEY for {self.label}-----"
        footer = f"-----END PRIVATE KEY for {self.label}-----"

        message_hex = self.message.hex().encode()
        message_base64 = base64.b64encode(message_hex).decode()

        payload_lines = textwrap.wrap(message_base64, 64)
        payload = "\n".join(payload_lines)
        text = "\n".join([header, payload, footer])
        return text


def _clean_lines(lines: list[str]) -> list[str]:
    lines = [line.strip() for line in lines]
    lines = list(filter(None, lines))
    return lines


def _parse_labels(headers: list[str]) -> list[str]:
    marker = "-----BEGIN PRIVATE KEY for"
    headers = [line for line in headers if line.startswith(marker)]
    labels = [line.replace(marker, "").replace("-", "").strip() for line in headers]
    return labels
