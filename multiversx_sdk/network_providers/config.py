from typing import Any, Optional


class NetworkProviderConfig:
    def __init__(
        self,
        client_name: Optional[str] = None,
        requests_options: Optional[dict[str, Any]] = None,
    ) -> None:
        self.client_name = client_name
        self.requests_options = requests_options or {}
        self.requests_options.setdefault("timeout", 5)
        self.requests_options.setdefault("auth", tuple())
        self.requests_options.setdefault("retries", 3)
        self.requests_options.setdefault("backoff_factor", 0.05)
        self.requests_options.setdefault("status_forcelist", [500, 502, 503, 504])
