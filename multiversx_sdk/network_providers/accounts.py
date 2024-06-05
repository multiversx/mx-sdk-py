from typing import Any, Dict

from multiversx_sdk.core.address import Address
from multiversx_sdk.network_providers.interface import IAddress
from multiversx_sdk.network_providers.resources import EmptyAddress


class AccountOnNetwork:
    def __init__(self):
        self.address: IAddress = EmptyAddress()
        self.owner_address = EmptyAddress()
        self.nonce: int = 0
        self.balance: int = 0
        self.developer_reward = 0
        self.code: bytes = b""
        self.username: str = ""
        self.code_hash: str = ""
        self.root_hash: str = ""

    @staticmethod
    def from_http_response(payload: Dict[str, Any]) -> "AccountOnNetwork":
        result = AccountOnNetwork()

        address = payload.get("address", "")
        owner_address = payload.get("ownerAddress", "")

        result.address = Address.new_from_bech32(address) if address else EmptyAddress()
        result.owner_address = Address.new_from_bech32(owner_address) if owner_address else EmptyAddress()

        result.nonce = payload.get("nonce", 0)
        result.balance = int(payload.get("balance", 0))
        result.developer_reward = int(payload.get("developerReward", 0))

        result.code = bytes.fromhex(payload.get("code", ""))
        result.username = payload.get("username", "")
        result.code_hash = payload.get("codeHash", "")
        result.root_hash = payload.get("rootHash", "")

        return result

    def to_dictionary(self) -> Dict[str, Any]:
        return {
            "address": self.address.to_bech32(),
            "ownerAddress": self.owner_address.to_bech32(),
            "nonce": self.nonce,
            "balance": self.balance,
            "developerReward": self.developer_reward,
            "code": self.code.hex(),
            "username": self.username,
            "codeHash": self.code_hash,
            "rootHash": self.root_hash
        }


class GuardianData:
    def __init__(self):
        self.guarded: bool = False
        self.active_guardian: Guardian = Guardian()
        self.pending_guardian: Guardian = Guardian()

    @staticmethod
    def from_http_response(response: Dict[str, Any]) -> "GuardianData":
        result = GuardianData()

        result.guarded = response.get("guarded", False)

        if response.get("activeGuardian", None):
            result.active_guardian = Guardian.from_http_response(response["activeGuardian"])

        if response.get("pendingGuardian", None):
            result.pending_guardian = Guardian.from_http_response(response["pendingGuardian"])

        return result

    def get_current_guardian_address(self):
        if not self.guarded:
            return None
        return self.active_guardian.address


class Guardian:
    def __init__(self) -> None:
        self.activation_epoch: int = 0
        self.address: IAddress = EmptyAddress()
        self.service_uid: str = ""

    @staticmethod
    def from_http_response(response: Dict[str, Any]) -> "Guardian":
        result = Guardian()

        result.activation_epoch = int(response.get("activationEpoch", 0))
        result.address = Address.new_from_bech32(response.get("address", ""))
        result.service_uid = response.get("serviceUID", "")

        return result
