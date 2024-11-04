from typing import Any, Dict, Optional


class NetworkProviderConfig:
    def __init__(self,
                 client_name: Optional[str] = None,
                 requests_options: Optional[Dict[str, Any]] = None) -> None:
        self.client_name = client_name
        self.requests_options = requests_options or {}
        self.requests_options.setdefault("timeout", 5)
        self.requests_options.setdefault("auth", tuple())
