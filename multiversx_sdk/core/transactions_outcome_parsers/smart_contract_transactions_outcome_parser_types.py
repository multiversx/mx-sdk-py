from dataclasses import dataclass
from typing import Any


@dataclass
class DeployedSmartContract:
    address: str
    owner_address: str
    code_hash: bytes

    def __repr__(self) -> str:
        return f"DeployedSmartContract(address={self.address}, owner_address={self.owner_address}, code_hash={self.code_hash.hex()})"


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
