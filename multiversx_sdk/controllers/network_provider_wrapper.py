from typing import Any

from multiversx_sdk.network_providers.proxy_network_provider import \
    ProxyNetworkProvider
from multiversx_sdk.network_providers.transactions import TransactionOnNetwork


class ProviderWrapper:
    def __init__(self, provider: Any) -> None:
        self.provider = provider

    def get_transaction(self, tx_hash: str) -> TransactionOnNetwork:
        if isinstance(self.provider, ProxyNetworkProvider):
            return self.provider.get_transaction(tx_hash, True)
        return self.provider.get_transaction(tx_hash)
