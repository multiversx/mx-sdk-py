import logging
from typing import Any, Dict

from multiversx_sdk.network_providers.config import NetworkProviderConfig
from multiversx_sdk.network_providers.constants import UNKNOWN_CLIENT_NAME

logger = logging.getLogger("user_agent")


def extend_user_agent(user_agent_prefix: str, config: NetworkProviderConfig):
    if config.client_name is None:
        logger.debug("Please provide the client name of the application that uses the SDK. It will be used for metrics.")

    headers: Dict[str, Any] = config.requests_options.setdefault("headers", {})
    resolved_client_name = config.client_name or UNKNOWN_CLIENT_NAME

    current_user_agent = headers.get("User-Agent", "")
    new_user_agent = f"{current_user_agent} {user_agent_prefix}/{resolved_client_name}" if current_user_agent else f"{user_agent_prefix}/{resolved_client_name}"

    headers["User-Agent"] = new_user_agent
