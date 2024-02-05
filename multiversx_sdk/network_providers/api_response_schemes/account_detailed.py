from typing import Any, Dict, List, Protocol

from multiversx_sdk.network_providers.api_response_schemes.asset import Asset
from multiversx_sdk.network_providers.api_response_schemes.scam_info import \
    ScamInfo


class IAsset(Protocol):
    name: str
    description: str
    social: Dict[str, str]
    tags: List[str]
    icon_png: str
    icon_svg: str
    raw_response: Dict[str, Any]


class IScamInfo(Protocol):
    type: str
    info: str


class AccountDetailed:
    def __init__(self) -> None:
        self.address = ""
        self.balance = 0
        self.nonce = 0
        self.timestamp = 0
        self.shard = 0
        self.owner_address = ""
        self.assets: IAsset = Asset()
        self.deployed_at = 0
        self.deploy_tx_hash = ""
        self.owner_assets = {}
        self.is_verified = False
        self.tx_count = 0
        self.scr_count = 0
        self.code = ""
        self.code_hash = ""
        self.root_hash = ""
        self.username = ""
        self.developer_reward = 0
        self.is_upgradeable = False
        self.is_readable = False
        self.is_payable = False
        self.is_payable_by_sc = False
        self.scam_info: IScamInfo = ScamInfo()
        self.active_guardian_activation_epoch = 0
        self.active_guardian_address = ""
        self.active_guardian_service_uid = ""
        self.pending_guardian_activation_epoch = 0
        self.pending_guardian_address = ""
        self.pending_guardian_service_uid = ""
        self.is_guarded = False

    @classmethod
    def from_response(cls, response: Dict[str, Any]) -> "AccountDetailed":
        account = AccountDetailed()

        account.address = response.get("address", "")
        account.balance = int(response.get("balance", 0))
        account.nonce = int(response.get("nonce", 0))
        account.timestamp = int(response.get("timestamp", ""))
        account.shard = int(response.get("shard", ""))
        account.owner_address = response.get("ownerAddress", "")
        account.assets = Asset.from_response(response.get("assets", {}))
        account.deployed_at = int(response.get("deployedAt", 0))
        account.deploy_tx_hash = response.get("deployTxHash", "")
        account.owner_assets = response.get("ownerAssets", {})
        account.is_verified = True if response.get("isVerified", "false") == "true" else False
        account.tx_count = int(response.get("txCount", 0))
        account.scr_count = int(response.get("scrCount", 0))
        account.code = response.get("code", "")
        account.code_hash = response.get("codeHash", "")
        account.root_hash = response.get("rootHash", "")
        account.username = response.get("username", "")
        account.developer_reward = int(response.get("developerReward", 0))
        account.is_upgradeable = True if response.get("isUpgradeable", "false") == "true" else False
        account.is_readable = True if response.get("isReadable", "false") == "true" else False
        account.is_payable = True if response.get("isPayable", "false") == "true" else False
        account.is_payable_by_sc = True if response.get("isPayableBySmartContract", "false") == "true" else False
        account.scam_info = ScamInfo.from_response(response.get("scamInfo", {}))
        account.active_guardian_activation_epoch = int(response.get("activeGuardianActivationEpoch", 0))
        account.active_guardian_address = response.get("activeGuardianAddress", "")
        account.active_guardian_service_uid = response.get("activeGuardianServiceUid", "")
        account.pending_guardian_activation_epoch = int(response.get("pendingGuardianActivationEpoch", 0))
        account.pending_guardian_address = response.get("pendingGuardianAddress", "")
        account.pending_guardian_service_uid = response.get("pendingGuardianServiceUid", "")
        account.is_guarded = True if response.get("isGuarded", "false") == "true" else False

        return account
