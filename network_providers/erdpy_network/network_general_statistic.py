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

        stats.shards = int(payload['shards'])
        stats.blocks = int(payload['blocks'])
        stats.accounts = int(payload['accounts'])
        stats.transactions = int(payload['transactions'])
        stats.refresh_rate = int(payload['refreshRate'])
        stats.epoch = int(payload['epoch'])
        stats.rounds_passed = int(payload['roundsPassed'])
        stats.rounds_per_epoch = int(payload['roundsPerEpoch'])

        return stats
