from typing import Any, Dict


class NetworkGeneralStatistics:
    def __init__(self):
        self.shards: int = 0
        self.blocks: int = 0
        self.accounts: int = 0
        self.transactions: int = 0
        self.refresh_rate: int = 0
        self.epoch: int = 0
        self.rounds_passed: int = 0
        self.rounds_per_epoch: int = 0

    @staticmethod
    def from_http_response(payload: Dict[str, Any]) -> 'NetworkGeneralStatistics':
        stats = NetworkGeneralStatistics()

        stats.shards = int(payload.get('shards', 0))
        stats.blocks = int(payload.get('blocks', 0))
        stats.accounts = int(payload.get('accounts', 0))
        stats.transactions = int(payload.get('transactions', 0))
        stats.refresh_rate = int(payload.get('refreshRate', 0))
        stats.epoch = int(payload.get('epoch', 0))
        stats.rounds_passed = int(payload.get('roundsPassed', 0))
        stats.rounds_per_epoch = int(payload.get('roundsPerEpoch', 0))

        return stats
