from typing import Any, Dict


class NetworkConfig:
    def __init__(self) -> None:
        self.chain_id: str = 'T'
        self.gas_per_data_byte: int = 1500
        self.top_up_factor: float = 0
        self.start_time: int = 0
        self.round_duration: int = 0
        self.rounds_per_epoch: int = 0
        self.top_up_rewards_gradient_point: int = 0
        self.min_gas_limit: int = 50000
        self.min_gas_price: int = 1000000000
        self.gas_price_modifier: float = 1
        self.min_transaction_version: int = 1

    @staticmethod
    def from_http_response(payload: Dict[str, Any]) -> 'NetworkConfig':
        network_config = NetworkConfig()

        network_config.chain_id = str(payload.get('erd_chain_id', ''))
        network_config.gas_per_data_byte = int(payload.get('erd_gas_per_data_byte', 0))
        network_config.top_up_factor = float(payload.get('erd_top_up_factor', 0))
        network_config.start_time = int(payload.get('erd_start_time', 0))
        network_config.round_duration = int(payload.get('erd_round_duration', 0))
        network_config.rounds_per_epoch = int(payload.get('erd_rounds_per_epoch', 0))
        network_config.top_up_rewards_gradient_point = int(payload.get('erd_rewards_top_up_gradient_point', 0))
        network_config.min_gas_limit = int(payload.get('erd_min_gas_limit', 0))
        network_config.min_gas_price = int(payload.get('erd_min_gas_price', 0))
        network_config.min_transaction_version = int(payload.get('erd_min_transaction_version', 0))
        network_config.gas_price_modifier = float(payload.get('erd_gas_price_modifier', 0))

        return network_config
