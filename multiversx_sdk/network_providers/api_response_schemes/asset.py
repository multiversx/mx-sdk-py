from typing import Any, Dict, List


class Asset:
    def __init__(self) -> None:
        self.name = ""
        self.description = ""
        self.social: Dict[str, str] = {}
        self.tags: List[str] = []
        self.icon_png = ""
        self.icon_svg = ""
        self.raw_response: Dict[str, Any] = {}

    @classmethod
    def from_response(cls, response: Dict[str, Any]) -> "Asset":
        asset = Asset()

        asset.name = response.get("name", "")
        asset.description = response.get("description", "")
        asset.social = response.get("social", {})
        asset.tags = response.get("tags", [])
        asset.icon_png = response.get("iconPng", "")
        asset.icon_svg = response.get("iconSvg", "")
        asset.raw_response = response

        return asset
