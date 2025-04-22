from dataclasses import dataclass, field
from http.client import (
    BAD_GATEWAY,
    GATEWAY_TIMEOUT,
    INTERNAL_SERVER_ERROR,
    SERVICE_UNAVAILABLE,
)
from typing import Any, Optional


@dataclass
class RequestsRetryOptions:
    retries: int = 3
    backoff_factor: float = 1
    status_forcelist: list[int] = field(
        default_factory=lambda: [
            INTERNAL_SERVER_ERROR,
            BAD_GATEWAY,
            SERVICE_UNAVAILABLE,
            GATEWAY_TIMEOUT,
        ]
    )


class NetworkProviderConfig:
    def __init__(
        self,
        client_name: Optional[str] = None,
        requests_options: Optional[dict[str, Any]] = None,
        requests_retry_options: Optional[RequestsRetryOptions] = None,
    ) -> None:
        self.client_name = client_name
        self.requests_options = requests_options or {}
        self.requests_options.setdefault("timeout", 5)
        self.requests_options.setdefault("auth", tuple())
        self.requests_retry_options = requests_retry_options if requests_retry_options else RequestsRetryOptions()
