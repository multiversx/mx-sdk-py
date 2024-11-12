from dataclasses import dataclass

from multiversx_sdk.core.address import Address


@dataclass
class CreateNewDelegationContractOutcome:
    contract_address: Address
