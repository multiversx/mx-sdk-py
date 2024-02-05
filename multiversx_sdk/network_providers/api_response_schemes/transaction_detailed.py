

from typing import Any, Dict, Protocol

from multiversx_sdk.network_providers.api_response_schemes.scam_info import \
    ScamInfo


class IAction(Protocol):
    category: str
    name: str
    description: str
    arguments: Dict[str, Any]


class IScamInfo(Protocol):
    type: str
    info: str


class Action:
    def __init__(self) -> None:
        self.category = ""
        self.name = ""
        self.description = ""
        self.arguments = {}

    @classmethod
    def from_response(cls, response: Dict[str, Any]) -> "Action":
        action = Action()

        action.category = response.get("category", "")
        action.name = response.get("name", "")
        action.description = response.get("description", "")
        action.arguments = response.get("arguments", {})

        return action


class TransactionDetailed:
    def __init__(self) -> None:
        self.tx_hash = ""
        self.gas_limit = 0
        self.gas_price = 0
        self.gas_used = 0
        self.miniblock_hash = ""
        self.nonce = 0
        self.receiver = ""
        self.receiver_username = ""
        self.receiver_assets = {}
        self.receiver_shard = 0
        self.round = 0
        self.sender = ""
        self.sender_username = ""
        self.sender_assets = {}
        self.sender_shard = 0
        self.signature = ""
        self.status = ""
        self.value = 0
        self.fee = 0
        self.timestamp = 0
        self.data = ""
        self.function = ""
        self.action: IAction = Action()
        self.scam_info: IScamInfo = ScamInfo()
        self.type = ""
        self.original_tx_hash = ""
        self.pending_results = False
        self.guardian_address = ""
        self.guardian_signature = ""
        self.is_relayed = ""
