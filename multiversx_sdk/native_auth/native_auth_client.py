import base64
import json
from typing import Any, Optional

import requests

from multiversx_sdk.core.address import Address
from multiversx_sdk.native_auth.config import NativeAuthClientConfig
from multiversx_sdk.native_auth.errors import NativeAuthClientError


class NativeAuthClient:
    def __init__(self, config: Optional[NativeAuthClientConfig] = None) -> None:
        self.config = config or NativeAuthClientConfig()

    def initialize(self, extra_info: Optional[dict[Any, Any]] = None) -> str:
        extra_info = extra_info if extra_info else {}

        block_hash = self.get_current_block_hash()
        encoded_extra_info = self._encode_value(json.dumps(extra_info))
        encoded_origin = self._encode_value(self.config.origin)

        return f"{encoded_origin}.{block_hash}.{self.config.expiry_seconds}.{encoded_extra_info}"

    def get_token_for_signing(self, address: Address, init_token: str) -> bytes:
        return f"{address.to_bech32()}{init_token}".encode()

    def get_token(self, address: Address, token: str, signature: str) -> str:
        encoded_address = self._encode_value(address.to_bech32())
        encoded_token = self._encode_value(token)

        return f"{encoded_address}.{encoded_token}.{signature}"

    def get_current_block_hash(self) -> str:
        if self.config.gateway_url:
            return self._get_current_block_hash_using_gateway()
        return self._get_current_block_hash_using_api()

    def _get_current_block_hash_using_gateway(self) -> str:
        round = self._get_current_round()
        url = f"{self.config.gateway_url}/blocks/by-round/{round}"
        response = self._execute_request(url)
        blocks: list[dict[str, Any]] = response["data"]["blocks"]
        block: dict[str, str] = [b for b in blocks if b["shard"] == self.config.block_hash_shard][0]
        return block["hash"]

    def _get_current_round(self) -> int:
        if self.config.gateway_url is None:
            raise NativeAuthClientError("Gateway URL not set")

        if self.config.block_hash_shard is None:
            raise NativeAuthClientError("Blockhash shard not set")

        url = f"{self.config.gateway_url}/network/status/{self.config.block_hash_shard}"
        response = self._execute_request(url)
        status: dict[str, int] = response["data"]["status"]

        return status["erd_current_round"]

    def _get_current_block_hash_using_api(self) -> str:
        try:
            url = f"{self.config.api_url}/blocks/latest?ttl={self.config.expiry_seconds}&fields=hash"
            response: dict[str, str] = self._execute_request(url)
            if response["hash"]:
                return response["hash"]
        except Exception:
            pass

        return self._get_current_block_hash_using_api_fallback()

    def _get_current_block_hash_using_api_fallback(self) -> str:
        url = f"{self.config.api_url}/blocks?size=1&fields=hash"

        if self.config.block_hash_shard:
            url += f"&shard={self.config.block_hash_shard}"

        response: list[dict[str, str]] = self._execute_request(url)
        return response[0]["hash"]

    def _encode_value(self, string: str) -> str:
        encoded = base64.b64encode(string.encode("utf-8")).decode("utf-8")
        return self._escape(encoded)

    def _escape(self, string: str) -> str:
        return string.replace("+", "-").replace("/", "_").replace("=", "")

    def _execute_request(self, url: str) -> Any:
        response = requests.get(url=url, headers=self.config.extra_request_headers)
        response.raise_for_status()
        return response.json()
