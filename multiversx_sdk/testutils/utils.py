import base64
from typing import List

from multiversx_sdk.network_providers.config import NetworkProviderConfig

EGLD_NUM_DECIMALS = 18


def create_account_egld_balance(egld: int) -> int:
    value_as_str = str(egld) + ("0" * EGLD_NUM_DECIMALS)
    return int(value_as_str)


def base64_topics_to_bytes(topics: List[str]) -> List[bytes]:
    return [base64.b64decode(topic) for topic in topics]


def create_network_providers_config(client: str = "sdk-py-tests") -> NetworkProviderConfig:
    return NetworkProviderConfig(client_name=client)
