from dataclasses import dataclass


@dataclass
class TestnetEntrypointConfig:
    network_provider_url = "https://testnet-api.multiversx.com"
    network_provider_kind = "api"
    chain_id = "T"


@dataclass
class DevnetEntrypointConfig:
    network_provider_url = "https://devnet-api.multiversx.com"
    network_provider_kind = "api"
    chain_id = "D"


@dataclass
class MainnetEntrypointConfig:
    network_provider_url = "https://api.multiversx.com"
    network_provider_kind = "api"
    chain_id = "1"


@dataclass
class LocalnetEntrypointConfig:
    network_provider_url = "http://localhost:7950"
    network_provider_kind = "proxy"
    chain_id = "localnet"
