from typing import Any, Dict, List, Protocol

from multiversx_sdk.network_providers.api_response_schemes.asset import Asset


class IAsset(Protocol):
    name: str
    description: str
    social: Dict[str, str]
    tags: List[str]
    icon_png: str
    icon_svg: str
    raw_response: Dict[str, Any]


class Account:
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
        self.owner_assets = {}  # not described by swagger
        self.is_verified = False
        self.tx_count = 0
        self.scr_count = 0
        self.raw_response: Dict[str, Any] = {}

    @classmethod
    def from_response(cls, response: Dict[str, Any]) -> "Account":
        account = Account()

        account.address = response.get("address", "")
        account.balance = int(response.get("balance", 0))
        account.nonce = int(response.get("nonce", "0"))
        account.timestamp = int(response.get("timestamp", 0))
        account.shard = int(response.get("shard", 0))
        account.owner_address = response.get("ownerAddress", "")
        account.assets = Asset.from_response(response.get("assets", {}))
        account.deployed_at = int(response.get("deplyedAt", 0))
        account.deploy_tx_hash = response.get("deployedTxHash", "")
        account.owner_assets = response.get("ownerAssets", {})
        account.is_verified = True if response.get("isVerified", "false") == "true" else False
        account.tx_count = response.get("txCount", 0)
        account.scr_count = response.get("scrCount", 0)
        account.raw_response = response

        return account
