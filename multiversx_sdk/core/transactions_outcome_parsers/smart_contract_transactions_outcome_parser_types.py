from dataclasses import dataclass
from typing import List


@dataclass
class DeployedSmartContract:
    address: str
    owner_address: str
    code_hash: bytes


@dataclass
class SmartContractDeployOutcome:
    return_code: str
    return_message: str
    contracts: List[DeployedSmartContract]
