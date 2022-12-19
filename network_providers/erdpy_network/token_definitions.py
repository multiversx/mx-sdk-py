from typing import Any, Dict, List

from erdpy_core import Address

from erdpy_network.interface import IAddress
from erdpy_network.resources import EmptyAddress


class DefinitionOfFungibleTokenOnNetwork:
    def __init__(self):
        self.identifier: str = ''
        self.name: str = ''
        self.ticker: str = ''
        self.owner: IAddress = EmptyAddress()
        self.decimals: int = 0
        self.supply: int = 0
        self.burnt_value = 0
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

        owner = payload.get('owner', '')
        result.owner = Address.from_bech32(owner) if owner else EmptyAddress()

        result.decimals = payload.get('decimals', 0)
        result.supply = int(payload.get('supply', 0))
        result.burnt_value = payload.get('burntValue', 0)
        result.is_paused = payload.get('isPaused', False)
        result.can_upgrade = payload.get('canUpgrade', False)
        result.can_mint = payload.get('canMint', False)
        result.can_burn = payload.get('canBurn', False)
        result.can_change_owner = payload.get('canChangeOwner', False)
        result.can_pause = payload.get('canPause', False)
        result.can_freeze = payload.get('canFreeze', False)
        result.can_wipe = payload.get('canWipe', False)

        return result

    @staticmethod
    def from_response_of_get_token_properties(identifier: str, data: List[bytes], address_hrp: str):
        result = DefinitionOfFungibleTokenOnNetwork()

        token_name, _, owner, supply, burnt_value, *properties_buffers = data
        properties = parse_token_properties(properties_buffers)

        result.identifier = identifier
        result.name = token_name.decode()
        result.ticker = identifier
        result.owner = Address(owner, address_hrp)
        result.decimals = properties.get('NumDecimals', 0)
        result.supply = int(supply.decode()[:-result.decimals])
        result.burnt_value = int(burnt_value.decode())
        result.is_paused = properties.get('IsPaused', False)
        result.can_upgrade = properties.get('CanUpgrade', False)
        result.can_mint = properties.get('CanMint', False)
        result.can_burn = properties.get('CanBurn', False)
        result.can_change_owner = properties.get('CanChangeOwner', False)
        result.can_pause = properties.get('CanPause', False)
        result.can_freeze = properties.get('CanFreeze', False)
        result.can_wipe = properties.get('CanWipe', False)

        return result


class DefinitionOfTokenCollectionOnNetwork:
    def __init__(self):
        self.collection: str = ''
        self.type: str = ''
        self.name: str = ''
        self.ticker: str = ''
        self.owner: IAddress = EmptyAddress()
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

        owner = payload.get('owner', '')
        result.owner = Address.from_bech32(owner) if owner else EmptyAddress()

        result.decimals = payload.get('decimals', 0)
        result.can_pause = payload.get('canPause', False)
        result.can_freeze = payload.get('canFreeze', False)
        result.can_freeze = payload.get('canWipe', False)
        result.can_transfer_nft_create_role = payload.get('canTransferNftCreateRole', False)

        return result

    @staticmethod
    def from_response_of_get_token_properties(collection: str, data: List[bytes], address_hrp: str) -> 'DefinitionOfTokenCollectionOnNetwork':
        result = DefinitionOfTokenCollectionOnNetwork()

        token_name, token_type, owner, _, _, *properties_buffers = data
        properties = parse_token_properties(properties_buffers)

        result.collection = collection
        result.type = token_type.decode()
        result.name = token_name.decode()
        result.ticker = collection
        result.owner = Address(owner, address_hrp)
        result.decimals = properties.get('NumDecimals', 0)
        result.can_pause = properties.get('CanPause', False)
        result.can_freeze = properties.get('CanFreeze', False)
        result.can_wipe = properties.get('CanWipe', False)
        result.can_transfer_nft_create_role = properties.get('CanTransferNFTCreateRole', False)

        return result


def parse_token_properties(properties_buffer: List[bytes]) -> Dict[str, Any]:
    properties: Dict[str, Any] = {}

    for buffer in properties_buffer:
        name, value = buffer.decode().split('-')
        properties[name] = parse_value_of_token_property(value)

    return properties


def parse_value_of_token_property(value: str) -> Any:
    if value == 'true':
        return True
    elif value == 'false':
        return False
    else:
        return int(value)
