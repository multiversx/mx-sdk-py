from dataclasses import dataclass
from typing import Any

from multiversx_sdk.core import Address


@dataclass
class DeployedSmartContract:
    address: Address
    owner_address: Address
    code_hash: bytes

    def __repr__(self) -> str:
        return f"DeployedSmartContract(address={self.address.to_bech32()}, owner_address={self.owner_address.to_bech32()}, code_hash={self.code_hash.hex()})"


@dataclass
class SmartContractDeployOutcome:
    return_code: str
    return_message: str
    contracts: list[DeployedSmartContract]


@dataclass
class ParsedSmartContractCallOutcome:
    values: list[Any]
    return_code: str
    return_message: str
