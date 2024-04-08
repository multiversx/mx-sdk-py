import base64
from typing import List

EGLD_NUM_DECIMALS = 18


def create_account_egld_balance(egld: int) -> int:
    value_as_str = str(egld) + ("0" * EGLD_NUM_DECIMALS)
    return int(value_as_str)


def base64_topics_to_bytes(topics: List[str]) -> List[bytes]:
    return [base64.b64decode(topic) for topic in topics]
