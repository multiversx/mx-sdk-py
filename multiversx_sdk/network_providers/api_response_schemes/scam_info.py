from typing import Any, Dict


class ScamInfo:
    def __init__(self) -> None:
        self.type = ""
        self.info = ""

    @classmethod
    def from_response(cls, response: Dict[str, Any]) -> "ScamInfo":
        scam_info = ScamInfo()
        scam_info.type = response.get("type", "")
        scam_info.info = response.get("info", "")
        return scam_info
