import logging
from typing import Any, Union
from requests.auth import AuthBase
from erdpy_network.network_config import NetworkConfig
from erdpy_network.http_facade import do_get, do_post
from erdpy_network.internal_interfaces import INetworkProvider

AWAIT_TRANSACTION_PERIOD = 5

logger = logging.getLogger('NetworkProvider')
METACHAIN_ID = 4294967295


class NetworkProvider(INetworkProvider):
    def __init__(self, url: str, auth: Union[AuthBase, None] = None):
        self.url = url
        self.auth = auth

    def get_network_config(self) -> NetworkConfig:
        url = f"network/config"
        response = self.do_get_generic(url)
        payload = response.get("config")
        result = NetworkConfig(payload)
        return result

    def _get_network_status(self, shard_id: Union[str, int]):
        url = f"network/status/{shard_id}"
        response = self.do_get_generic(url)
        payload = response.get("status")
        return payload

    def get_epoch(self):
        status = self._get_network_status(METACHAIN_ID)
        nonce = status.get("erd_epoch_number", 0)
        return nonce

    def get_last_block_nonce(self, shard_id: Union[str, int]):
        if shard_id == "metachain":
            metrics = self._get_network_status(METACHAIN_ID)
        else:
            metrics = self._get_network_status(shard_id)

        nonce = metrics.get("erd_highest_final_nonce", 0)
        return nonce

    def get_num_shards(self):
        network_config = self.get_network_config()
        return network_config.num_shards

    def get_gas_price(self):
        network_config = self.get_network_config()
        return network_config.min_gas_price

    def get_chain_id(self):
        network_config = self.get_network_config()
        return network_config.chain_id

    def do_get_generic(self, resource_url: str):
        response = do_get(f'{self.url}/{resource_url}')
        return response

    def do_post_generic(self, resource_url: str, payload: Any):
        url = f'{self.url}/{resource_url}'
        response = do_post(url, payload)
        return response
