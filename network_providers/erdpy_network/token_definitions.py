from typing import Any, Dict
from erdpy_network.interface import IAddress
from erdpy_network.primitives import Address


class DefinitionOfFungibleTokenOnNetwork:
    def __init__(self):
        self.identifier: str = ''
        self.name: str = ''
        self.ticker: str = ''
        self.owner: IAddress = Address('')
        self.decimals: int = 0
        self.supply: int = 0
        self.is_paused: bool = False
        self.can_upgrade: bool = False
        self.can_mint: bool = False
        self.can_burn: bool = False
        self.can_change_owner: bool = False
        self.can_pause: bool = False
        self.can_freeze: bool = False
        self.can_wipe: bool = False
        self.can_add_special_roles: bool = False

    @staticmethod
    def from_api_http_response(payload: Dict[str, Any]) -> 'DefinitionOfFungibleTokenOnNetwork':
        result = DefinitionOfFungibleTokenOnNetwork()

        result.identifier = payload.get('identifier', '')
        result.name = payload.get('name', '')
        result.ticker = payload.get('ticker', '')
        result.owner = Address(payload.get('owner', ''))
        result.decimals = payload.get('decimals', 0)
        result.supply = payload.get('supply', 0)
        result.is_paused = payload.get('isPaused', False)
        result.can_upgrade = payload.get('canUpgrade', False)
        result.can_mint = payload.get('canMint', False)
        result.can_burn = payload.get('canBurn', False)
        result.can_change_owner = payload.get('canChangeOwner', False)
        result.can_pause = payload.get('canPause', False)
        result.can_freeze = payload.get('canFreeze', False)
        result.can_wipe = payload.get('canWipe', False)

        return result


class DefinitionOfTokenCollectionOnNetwork:
    def __init__(self):
        self.collection: str = ''
        self.type: str = ''
        self.name: str = ''
        self.ticker: str = ''
        self.owner: IAddress = Address('')
        self.decimals: int = 0
        self.can_pause: bool = False
        self.can_freeze: bool = False
        self.can_wipe: bool = False
        self.can_transfer_nft_create_role: bool = False

    @staticmethod
    def from_api_http_response(payload: Dict[str, Any]) -> 'DefinitionOfTokenCollectionOnNetwork':
        result = DefinitionOfTokenCollectionOnNetwork()

        result.collection = payload.get('collection', '')
        result.type = payload.get('type', '')
        result.name = payload.get('name', '')
        result.ticker = payload.get('ticker', '')
        result.owner = Address(payload.get('owner', ''))
        result.decimals = payload.get('decimals', 0)
        result.can_pause = payload.get('canPause', False)
        result.can_freeze = payload.get('canFreeze', False)
        result.can_freeze = payload.get('canWipe', False)
        result.can_transfer_nft_create_role = payload.get('canTransferNftCreateRole', False)

        return result
