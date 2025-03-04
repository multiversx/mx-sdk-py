from dataclasses import dataclass, field
from typing import Callable, Optional, Protocol

from multiversx_sdk.native_auth.constants import (
    DEFAULT_API_URL,
    DEFAULT_EXPIRY_TIME_IN_SECONDS,
)


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


# fmt: off
class NativeAuthCacheInterface(Protocol):
    def get(self, key: str) -> Optional[str]:
        ...

    def set(self, key: str, value: int, ttl: int) -> None:
        ...
# fmt: on


@dataclass
class NativeAuthServerConfig:
    """
    Configuration for Native Authentication.

    Attributes:
        api_url: Optional API URL (default: https://api.multiversx.com).
        accepted_origins: Mandatory list of accepted origins (must have at least one value).
        validate_impersonate_url: Optional endpoint for validating impersonation.
        validate_impersonate_callback: Optional callback function to validate impersonation.
        is_origin_accepted: Optional callback to validate an origin dynamically.
        max_expiry_seconds: Maximum allowed TTL (default: 86400 seconds, one day).
        skip_legacy_validation: Determines whether legacy signature validation should be skipped.
        extra_request_headers: Optional extra request headers.
        verify_signature: Optional function to verify signatures.
    """

    api_url: str = DEFAULT_API_URL
    accepted_origins: list[str] = field(default_factory=list)
    validate_impersonate_url: Optional[str] = None
    validate_impersonate_callback: Optional[Callable[[str, str], bool]] = None
    is_origin_accepted: Optional[Callable[[str], bool]] = None
    max_expiry_seconds: int = 86400
    skip_legacy_validation: bool = False
    extra_request_headers: Optional[dict[str, str]] = None
    verify_signature: Optional[Callable[[str, str, bytes], bool]] = None
