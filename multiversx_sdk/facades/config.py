from dataclasses import dataclass


@dataclass
class TestnetConfig:
    api = "https://testnet-api.multiversx.com"
    kind = "api"
    chain_id = "T"


@dataclass
class DevnetConfig:
    api = "https://devnet-api.multiversx.com"
    kind = "api"
    chain_id = "D"


@dataclass
class MainnetConfig:
    api = "https://api.multiversx.com"
    kind = "api"
    chain_id = "1"
