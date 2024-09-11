from typing import Any, Optional

from multiversx_sdk.network_providers.interface import IPagination


class DefaultPagination(IPagination):
    def __init__(self):
        self.start = 0
        self.size = 100

    def get_start(self) -> int:
        return self.start

    def get_size(self) -> int:
        return self.size


class NetworkProviderConfig:
    def __init__(self,
                 client_name: Optional[str] = None,
                 requests_options: Optional[dict[str, Any]] = None) -> None:
        self.client_name = client_name
        self.requests_options = requests_options or {}
        self.requests_options.setdefault("timeout", 5)
