from typing import Optional

DEFAULT_EXPIRY_TIME_IN_SECONDS = 60 * 60 * 2
DEFAULT_API_URL = "https://api.multiversx.com"


class NativeAuthClientConfig:
    def __init__(
        self,
        origin: str = "",
        api_url: str = DEFAULT_API_URL,
        expiry_seconds: int = DEFAULT_EXPIRY_TIME_IN_SECONDS,
        block_hash_shard: Optional[int] = None,
        gateway_url: Optional[str] = None,
        extra_request_headers: Optional[dict[str, str]] = None,
    ) -> None:
        self.origin = origin
        self.api_url = api_url
        self.expiry_seconds = expiry_seconds
        self.block_hash_shard = block_hash_shard
        self.gateway_url = gateway_url
        self.extra_request_headers = extra_request_headers
