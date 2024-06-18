from dataclasses import dataclass
from typing import List


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
    contracts: List[DeployedSmartContract]
