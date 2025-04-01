from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class RequestsRetryOptions:
    retries: int = 3
    backoff_factor: float = 0.05
    status_forecelist: list[int] = field(default_factory=lambda: [500, 502, 503, 504])


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
