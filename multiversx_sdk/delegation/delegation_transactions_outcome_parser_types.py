from dataclasses import dataclass

from multiversx_sdk.core.address import Address


@dataclass
class CreateNewDelegationContractOutcome:
    contract_address: Address


@dataclass
class ClaimRewardsOutcome:
    amount: int


@dataclass
class DelegateOutcome:
    amount: int


@dataclass
class RedelegateRewardsOutcome:
    amount: int


@dataclass
class UndelegateOutcome:
    amount: int
