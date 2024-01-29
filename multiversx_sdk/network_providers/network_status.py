from typing import Dict, Any


class NetworkStatus:
    def __init__(self):
        self.current_round: int = 0
        self.epoch_number: int = 0
        self.highest_final_nonce: int = 0
        self.nonce: int = 0
        self.nonce_at_epoch_start: int = 0
        self.nonces_passed_in_current_epoch: int = 0
        self.round_at_epoch_start: int = 0
        self.rounds_passed_in_current_epcoch: int = 0
        self.rounds_per_epoch: int = 0

    @staticmethod
    def from_http_response(payload: Dict[str, Any]) -> 'NetworkStatus':
        network_status = NetworkStatus()

        network_status.current_round = payload.get('erd_current_round', 0)
        network_status.epoch_number = payload.get('erd_epoch_number', 0)
        network_status.highest_final_nonce = payload.get('erd_highest_final_nonce', 0)
        network_status.nonce = payload.get('erd_nonce', 0)
        network_status.nonce_at_epoch_start = payload.get('erd_nonce_at_epoch_start', 0)
        network_status.nonces_passed_in_current_epoch = payload.get('erd_nonces_passed_in_current_epoch', 0)
        network_status.round_at_epoch_start = payload.get('erd_round_at_epoch_start', 0)
        network_status.rounds_passed_in_current_epcoch = payload.get('erd_rounds_passed_in_current_epoch', 0)
        network_status.rounds_per_epoch = payload.get('erd_rounds_per_epoch', 0)

        return network_status
