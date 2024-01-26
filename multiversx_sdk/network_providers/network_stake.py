from typing import Any, Dict


class NetworkStake:
    def __init__(self):
        self.total_validators: int = 0
        self.active_validators: int = 0
        self.queue_size: int = 0
        self.total_staked: int = 0

    @staticmethod
    def from_http_response(payload: Dict[str, Any]) -> 'NetworkStake':
        network_stake = NetworkStake()

        network_stake.total_validators = int(payload.get("totalValidators", 0))
        network_stake.active_validators = int(payload.get("activeValidators", 0))
        network_stake.queue_size = int(payload.get("queueSize", 0))
        network_stake.total_staked = int(payload.get("totalStaked", 0))

        return network_stake
