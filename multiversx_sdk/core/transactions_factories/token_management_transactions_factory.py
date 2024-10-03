import logging
from enum import Enum
from typing import List, Protocol

from multiversx_sdk.core.errors import BadUsageError
from multiversx_sdk.core.interfaces import IAddress
from multiversx_sdk.core.serializer import arg_to_string
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transactions_factories.transaction_builder import \
    TransactionBuilder

logger = logging.getLogger(__name__)


class IConfig(Protocol):
    chain_id: str
    min_gas_limit: int
    gas_limit_per_byte: int
    gas_limit_issue: int
    gas_limit_toggle_burn_role_globally: int
    gas_limit_esdt_local_mint: int
    gas_limit_esdt_local_burn: int
    gas_limit_set_special_role: int
    gas_limit_pausing: int
    gas_limit_freezing: int
    gas_limit_wiping: int
    gas_limit_esdt_nft_create: int
    gas_limit_esdt_nft_update_attributes: int
    gas_limit_esdt_nft_add_quantity: int
    gas_limit_esdt_nft_burn: int
    gas_limit_store_per_byte: int
    gas_limit_esdt_modify_royalties: int
    gas_limit_esdt_modify_creator: int
    gas_limit_esdt_metadata_update: int
    gas_limit_set_new_uris: int
    gas_limit_nft_metadata_recreate: int
    gas_limit_nft_change_to_dynamic: int
    gas_limit_update_token_id: int
    gas_limit_register_dynamic: int
    issue_cost: int
    esdt_contract_address: IAddress


class TokenType(Enum):
    NFT = "NFT"
    SFT = "SFT"
    META = "META"
    FNG = "FNG"


class TokenManagementTransactionsFactory:
    def __init__(self, config: IConfig):
        self._config = config
        self._true_as_hex = arg_to_string("true")
        self._false_as_hex = arg_to_string("false")

    def create_transaction_for_issuing_fungible(
        self,
        sender: IAddress,
        token_name: str,
        token_ticker: str,
        initial_supply: int,
        num_decimals: int,
        can_freeze: bool,
        can_wipe: bool,
        can_pause: bool,
        can_change_owner: bool,
        can_upgrade: bool,
        can_add_special_roles: bool
    ) -> Transaction:
        self._notify_about_unsetting_burn_role_globally()

        parts: List[str] = [
            "issue",
            arg_to_string(token_name),
            arg_to_string(token_ticker),
            arg_to_string(initial_supply),
            arg_to_string(num_decimals),
            *([arg_to_string("canFreeze"), self._true_as_hex if can_freeze else self._false_as_hex]),
            *([arg_to_string("canWipe"), self._true_as_hex if can_wipe else self._false_as_hex]),
            *([arg_to_string("canPause"), self._true_as_hex if can_pause else self._false_as_hex]),
            *([arg_to_string("canChangeOwner"), self._true_as_hex if can_change_owner else self._false_as_hex]),
            *([arg_to_string("canUpgrade"), self._true_as_hex if can_upgrade else self._false_as_hex]),
            *([arg_to_string("canAddSpecialRoles"), self._true_as_hex if can_add_special_roles else self._false_as_hex])
        ]

        return TransactionBuilder(
            config=self._config,
            sender=sender,
            receiver=self._config.esdt_contract_address,
            amount=self._config.issue_cost,
            gas_limit=self._config.gas_limit_issue,
            add_data_movement_gas=True,
            data_parts=parts
        ).build()

    def _notify_about_unsetting_burn_role_globally(self) -> None:
        logger.info("""
==========
IMPORTANT!
==========
You are about to issue (register) a new token. This will set the role "ESDTRoleBurnForAll" (globally).
Once the token is registered, you can unset this role by calling "unsetBurnRoleGlobally" (in a separate transaction).""")

    def create_transaction_for_issuing_semi_fungible(
        self,
        sender: IAddress,
        token_name: str,
        token_ticker: str,
        can_freeze: bool,
        can_wipe: bool,
        can_pause: bool,
        can_transfer_nft_create_role: bool,
        can_change_owner: bool,
        can_upgrade: bool,
        can_add_special_roles: bool
    ) -> Transaction:
        self._notify_about_unsetting_burn_role_globally()

        parts: List[str] = [
            "issueSemiFungible",
            arg_to_string(token_name),
            arg_to_string(token_ticker),
            *([arg_to_string("canFreeze"), self._true_as_hex if can_freeze else self._false_as_hex]),
            *([arg_to_string("canWipe"), self._true_as_hex if can_wipe else self._false_as_hex]),
            *([arg_to_string("canPause"), self._true_as_hex if can_pause else self._false_as_hex]),
            *([arg_to_string("canTransferNFTCreateRole"), self._true_as_hex if can_transfer_nft_create_role else self._false_as_hex]),
            *([arg_to_string("canChangeOwner"), self._true_as_hex if can_change_owner else self._false_as_hex]),
            *([arg_to_string("canUpgrade"), self._true_as_hex if can_upgrade else self._false_as_hex]),
            *([arg_to_string("canAddSpecialRoles"), self._true_as_hex if can_add_special_roles else self._false_as_hex])
        ]

        return TransactionBuilder(
            config=self._config,
            sender=sender,
            receiver=self._config.esdt_contract_address,
            amount=self._config.issue_cost,
            gas_limit=self._config.gas_limit_issue,
            add_data_movement_gas=True,
            data_parts=parts
        ).build()

    def create_transaction_for_issuing_non_fungible(
        self,
        sender: IAddress,
        token_name: str,
        token_ticker: str,
        can_freeze: bool,
        can_wipe: bool,
        can_pause: bool,
        can_transfer_nft_create_role: bool,
        can_change_owner: bool,
        can_upgrade: bool,
        can_add_special_roles: bool
    ) -> Transaction:
        self._notify_about_unsetting_burn_role_globally()

        parts: List[str] = [
            "issueNonFungible",
            arg_to_string(token_name),
            arg_to_string(token_ticker),
            *([arg_to_string("canFreeze"), self._true_as_hex if can_freeze else self._false_as_hex]),
            *([arg_to_string("canWipe"), self._true_as_hex if can_wipe else self._false_as_hex]),
            *([arg_to_string("canPause"), self._true_as_hex if can_pause else self._false_as_hex]),
            *([arg_to_string("canTransferNFTCreateRole"), self._true_as_hex if can_transfer_nft_create_role else self._false_as_hex]),
            *([arg_to_string("canChangeOwner"), self._true_as_hex if can_change_owner else self._false_as_hex]),
            *([arg_to_string("canUpgrade"), self._true_as_hex if can_upgrade else self._false_as_hex]),
            *([arg_to_string("canAddSpecialRoles"), self._true_as_hex if can_add_special_roles else self._false_as_hex])
        ]

        return TransactionBuilder(
            config=self._config,
            sender=sender,
            receiver=self._config.esdt_contract_address,
            amount=self._config.issue_cost,
            gas_limit=self._config.gas_limit_issue,
            add_data_movement_gas=True,
            data_parts=parts
        ).build()

    def create_transaction_for_registering_meta_esdt(
        self,
        sender: IAddress,
        token_name: str,
        token_ticker: str,
        num_decimals: int,
        can_freeze: bool,
        can_wipe: bool,
        can_pause: bool,
        can_transfer_nft_create_role: bool,
        can_change_owner: bool,
        can_upgrade: bool,
        can_add_special_roles: bool
    ) -> Transaction:
        self._notify_about_unsetting_burn_role_globally()

        parts: List[str] = [
            "registerMetaESDT",
            arg_to_string(token_name),
            arg_to_string(token_ticker),
            arg_to_string(num_decimals),
            *([arg_to_string("canFreeze"), self._true_as_hex if can_freeze else self._false_as_hex]),
            *([arg_to_string("canWipe"), self._true_as_hex if can_wipe else self._false_as_hex]),
            *([arg_to_string("canPause"), self._true_as_hex if can_pause else self._false_as_hex]),
            *([arg_to_string("canTransferNFTCreateRole"), self._true_as_hex if can_transfer_nft_create_role else self._false_as_hex]),
            *([arg_to_string("canChangeOwner"), self._true_as_hex if can_change_owner else self._false_as_hex]),
            *([arg_to_string("canUpgrade"), self._true_as_hex if can_upgrade else self._false_as_hex]),
            *([arg_to_string("canAddSpecialRoles"), self._true_as_hex if can_add_special_roles else self._false_as_hex])
        ]

        return TransactionBuilder(
            config=self._config,
            sender=sender,
            receiver=self._config.esdt_contract_address,
            amount=self._config.issue_cost,
            gas_limit=self._config.gas_limit_issue,
            add_data_movement_gas=True,
            data_parts=parts,
        ).build()

    def create_transaction_for_registering_and_setting_roles(
        self,
        sender: IAddress,
        token_name: str,
        token_ticker: str,
        token_type: TokenType,
        num_decimals: int
    ) -> Transaction:
        self._notify_about_unsetting_burn_role_globally()

        parts: List[str] = [
            "registerAndSetAllRoles",
            arg_to_string(token_name),
            arg_to_string(token_ticker),
            arg_to_string(token_type.value),
            arg_to_string(num_decimals)
        ]

        return TransactionBuilder(
            config=self._config,
            sender=sender,
            receiver=self._config.esdt_contract_address,
            amount=self._config.issue_cost,
            gas_limit=self._config.gas_limit_issue,
            add_data_movement_gas=True,
            data_parts=parts
        ).build()

    def create_transaction_for_setting_burn_role_globally(
        self,
        sender: IAddress,
        token_identifier: str
    ) -> Transaction:
        parts: List[str] = [
            "setBurnRoleGlobally",
            arg_to_string(token_identifier)
        ]

        return TransactionBuilder(
            config=self._config,
            sender=sender,
            receiver=self._config.esdt_contract_address,
            amount=None,
            gas_limit=self._config.gas_limit_toggle_burn_role_globally,
            add_data_movement_gas=True,
            data_parts=parts
        ).build()

    def create_transaction_for_unsetting_burn_role_globally(
        self,
        sender: IAddress,
        token_identifier: str
    ) -> Transaction:
        parts: List[str] = [
            "unsetBurnRoleGlobally",
            arg_to_string(token_identifier)
        ]

        return TransactionBuilder(
            config=self._config,
            sender=sender,
            receiver=self._config.esdt_contract_address,
            amount=None,
            gas_limit=self._config.gas_limit_toggle_burn_role_globally,
            add_data_movement_gas=True,
            data_parts=parts
        ).build()

    def create_transaction_for_setting_special_role_on_fungible_token(
        self,
        sender: IAddress,
        user: IAddress,
        token_identifier: str,
        add_role_local_mint: bool,
        add_role_local_burn: bool,
        add_role_esdt_transfer_role: bool
    ) -> Transaction:
        parts: List[str] = [
            "setSpecialRole",
            arg_to_string(token_identifier),
            user.to_hex(),
            *([arg_to_string("ESDTRoleLocalMint")] if add_role_local_mint else []),
            *([arg_to_string("ESDTRoleLocalBurn")] if add_role_local_burn else []),
            *([arg_to_string("ESDTTransferRole")] if add_role_esdt_transfer_role else [])
        ]

        return TransactionBuilder(
            config=self._config,
            sender=sender,
            receiver=self._config.esdt_contract_address,
            amount=None,
            gas_limit=self._config.gas_limit_set_special_role,
            add_data_movement_gas=True,
            data_parts=parts
        ).build()

    def create_transaction_for_unsetting_special_role_on_fungible_token(
        self,
        sender: IAddress,
        user: IAddress,
        token_identifier: str,
        remove_role_local_mint: bool,
        remove_role_local_burn: bool,
        remove_role_esdt_transfer_role: bool
    ) -> Transaction:
        parts: List[str] = [
            "unSetSpecialRole",
            arg_to_string(token_identifier),
            user.to_hex(),
            *([arg_to_string("ESDTRoleLocalMint")] if remove_role_local_mint else []),
            *([arg_to_string("ESDTRoleLocalBurn")] if remove_role_local_burn else []),
            *([arg_to_string("ESDTTransferRole")] if remove_role_esdt_transfer_role else [])
        ]

        return TransactionBuilder(
            config=self._config,
            sender=sender,
            receiver=self._config.esdt_contract_address,
            amount=None,
            gas_limit=self._config.gas_limit_set_special_role,
            add_data_movement_gas=True,
            data_parts=parts
        ).build()

    def create_transaction_for_setting_special_role_on_semi_fungible_token(
        self,
        sender: IAddress,
        user: IAddress,
        token_identifier: str,
        add_role_nft_create: bool = False,
        add_role_nft_burn: bool = False,
        add_role_nft_add_quantity: bool = False,
        add_role_esdt_transfer_role: bool = False,
        add_role_nft_update: bool = False,
        add_role_esdt_modify_royalties: bool = False,
        add_role_esdt_set_new_uri: bool = False,
        add_role_esdt_modify_creator: bool = False,
        add_role_nft_recreate: bool = False,
    ) -> Transaction:
        parts: List[str] = [
            "setSpecialRole",
            arg_to_string(token_identifier),
            user.to_hex(),
            *([arg_to_string("ESDTRoleNFTCreate")] if add_role_nft_create else []),
            *([arg_to_string("ESDTRoleNFTBurn")] if add_role_nft_burn else []),
            *([arg_to_string("ESDTRoleNFTAddQuantity")] if add_role_nft_add_quantity else []),
            *([arg_to_string("ESDTTransferRole")] if add_role_esdt_transfer_role else []),
            *([arg_to_string("ESDTRoleNFTUpdate")] if add_role_nft_update else []),
            *([arg_to_string("ESDTRoleModifyRoyalties")] if add_role_esdt_modify_royalties else []),
            *([arg_to_string("ESDTRoleSetNewURI")] if add_role_esdt_set_new_uri else []),
            *([arg_to_string("ESDTRoleModifyCreator")] if add_role_esdt_modify_creator else []),
            *([arg_to_string("ESDTRoleNFTRecreate")] if add_role_nft_recreate else []),
        ]

        return TransactionBuilder(
            config=self._config,
            sender=sender,
            receiver=self._config.esdt_contract_address,
            amount=None,
            gas_limit=self._config.gas_limit_set_special_role,
            add_data_movement_gas=True,
            data_parts=parts
        ).build()

    def create_transaction_for_unsetting_special_role_on_semi_fungible_token(
        self,
        sender: IAddress,
        user: IAddress,
        token_identifier: str,
        remove_role_nft_burn: bool = False,
        remove_role_nft_add_quantity: bool = False,
        remove_role_esdt_transfer_role: bool = False,
        remove_role_nft_update: bool = False,
        remove_role_esdt_modify_royalties: bool = False,
        remove_role_esdt_set_new_uri: bool = False,
        remove_role_esdt_modify_creator: bool = False,
        remove_role_nft_recreate: bool = False,
    ) -> Transaction:
        parts: List[str] = [
            "unSetSpecialRole",
            arg_to_string(token_identifier),
            user.to_hex(),
            *([arg_to_string("ESDTRoleNFTBurn")] if remove_role_nft_burn else []),
            *([arg_to_string("ESDTRoleNFTAddQuantity")] if remove_role_nft_add_quantity else []),
            *([arg_to_string("ESDTTransferRole")] if remove_role_esdt_transfer_role else []),
            *([arg_to_string("ESDTRoleNFTUpdate")] if remove_role_nft_update else []),
            *([arg_to_string("ESDTRoleModifyRoyalties")] if remove_role_esdt_modify_royalties else []),
            *([arg_to_string("ESDTRoleSetNewURI")] if remove_role_esdt_set_new_uri else []),
            *([arg_to_string("ESDTRoleModifyCreator")] if remove_role_esdt_modify_creator else []),
            *([arg_to_string("ESDTRoleNFTRecreate")] if remove_role_nft_recreate else []),
        ]

        return TransactionBuilder(
            config=self._config,
            sender=sender,
            receiver=self._config.esdt_contract_address,
            amount=None,
            gas_limit=self._config.gas_limit_set_special_role,
            add_data_movement_gas=True,
            data_parts=parts
        ).build()

    def create_transaction_for_setting_special_role_on_non_fungible_token(
        self,
        sender: IAddress,
        user: IAddress,
        token_identifier: str,
        add_role_nft_create: bool = False,
        add_role_nft_burn: bool = False,
        add_role_nft_update_attributes: bool = False,
        add_role_nft_add_uri: bool = False,
        add_role_esdt_transfer_role: bool = False,
        add_role_nft_update: bool = False,
        add_role_esdt_modify_royalties: bool = False,
        add_role_esdt_set_new_uri: bool = False,
        add_role_esdt_modify_creator: bool = False,
        add_role_nft_recreate: bool = False,
    ) -> Transaction:
        parts: List[str] = [
            "setSpecialRole",
            arg_to_string(token_identifier),
            user.to_hex(),
            *([arg_to_string("ESDTRoleNFTCreate")] if add_role_nft_create else []),
            *([arg_to_string("ESDTRoleNFTBurn")] if add_role_nft_burn else []),
            *([arg_to_string("ESDTRoleNFTUpdateAttributes")] if add_role_nft_update_attributes else []),
            *([arg_to_string("ESDTRoleNFTAddURI")] if add_role_nft_add_uri else []),
            *([arg_to_string("ESDTTransferRole")] if add_role_esdt_transfer_role else []),
            *([arg_to_string("ESDTRoleNFTUpdate")] if add_role_nft_update else []),
            *([arg_to_string("ESDTRoleModifyRoyalties")] if add_role_esdt_modify_royalties else []),
            *([arg_to_string("ESDTRoleSetNewURI")] if add_role_esdt_set_new_uri else []),
            *([arg_to_string("ESDTRoleModifyCreator")] if add_role_esdt_modify_creator else []),
            *([arg_to_string("ESDTRoleNFTRecreate")] if add_role_nft_recreate else []),
        ]

        return TransactionBuilder(
            config=self._config,
            sender=sender,
            receiver=self._config.esdt_contract_address,
            amount=None,
            gas_limit=self._config.gas_limit_set_special_role,
            add_data_movement_gas=True,
            data_parts=parts,
        ).build()

    def create_transaction_for_unsetting_special_role_on_non_fungible_token(
        self,
        sender: IAddress,
        user: IAddress,
        token_identifier: str,
        remove_role_nft_burn: bool = False,
        remove_role_nft_update_attributes: bool = False,
        remove_role_nft_remove_uri: bool = False,
        remove_role_esdt_transfer_role: bool = False,
        remove_role_nft_update: bool = False,
        remove_role_esdt_modify_royalties: bool = False,
        remove_role_esdt_set_new_uri: bool = False,
        remove_role_esdt_modify_creator: bool = False,
        remove_role_nft_recreate: bool = False,
    ) -> Transaction:
        parts: List[str] = [
            "unSetSpecialRole",
            arg_to_string(token_identifier),
            user.to_hex(),
            *([arg_to_string("ESDTRoleNFTBurn")] if remove_role_nft_burn else []),
            *([arg_to_string("ESDTRoleNFTUpdateAttributes")] if remove_role_nft_update_attributes else []),
            *([arg_to_string("ESDTRoleNFTAddURI")] if remove_role_nft_remove_uri else []),
            *([arg_to_string("ESDTTransferRole")] if remove_role_esdt_transfer_role else []),
            *([arg_to_string("ESDTRoleNFTUpdate")] if remove_role_nft_update else []),
            *([arg_to_string("ESDTRoleModifyRoyalties")] if remove_role_esdt_modify_royalties else []),
            *([arg_to_string("ESDTRoleSetNewURI")] if remove_role_esdt_set_new_uri else []),
            *([arg_to_string("ESDTRoleModifyCreator")] if remove_role_esdt_modify_creator else []),
            *([arg_to_string("ESDTRoleNFTRecreate")] if remove_role_nft_recreate else []),
        ]

        return TransactionBuilder(
            config=self._config,
            sender=sender,
            receiver=self._config.esdt_contract_address,
            amount=None,
            gas_limit=self._config.gas_limit_set_special_role,
            add_data_movement_gas=True,
            data_parts=parts,
        ).build()

    def create_transaction_for_creating_nft(
        self,
        sender: IAddress,
        token_identifier: str,
        initial_quantity: int,
        name: str,
        royalties: int,
        hash: str,
        attributes: bytes,
        uris: List[str]
    ) -> Transaction:
        if not uris:
            raise BadUsageError("No URIs provided")

        parts: List[str] = [
            "ESDTNFTCreate",
            arg_to_string(token_identifier),
            arg_to_string(initial_quantity),
            arg_to_string(name),
            arg_to_string(royalties),
            arg_to_string(hash),
            arg_to_string(attributes),
            *map(arg_to_string, uris)
        ]

        # Note that the following is an approximation (a reasonable one):
        nft_data = name + hash + attributes.hex() + "".join(uris)
        storage_gas_limit = len(nft_data) * self._config.gas_limit_store_per_byte

        return TransactionBuilder(
            config=self._config,
            sender=sender,
            receiver=sender,
            amount=None,
            gas_limit=self._config.gas_limit_esdt_nft_create + storage_gas_limit,
            add_data_movement_gas=True,
            data_parts=parts
        ).build()

    def create_transaction_for_pausing(
        self,
        sender: IAddress,
        token_identifier: str
    ) -> Transaction:
        parts: List[str] = [
            "pause",
            arg_to_string(token_identifier)
        ]

        return TransactionBuilder(
            config=self._config,
            sender=sender,
            receiver=self._config.esdt_contract_address,
            amount=None,
            gas_limit=self._config.gas_limit_pausing,
            add_data_movement_gas=True,
            data_parts=parts
        ).build()

    def create_transaction_for_unpausing(
        self,
        sender: IAddress,
        token_identifier: str
    ) -> Transaction:
        parts: List[str] = [
            "unPause",
            arg_to_string(token_identifier)
        ]

        return TransactionBuilder(
            config=self._config,
            sender=sender,
            receiver=self._config.esdt_contract_address,
            amount=None,
            gas_limit=self._config.gas_limit_pausing,
            add_data_movement_gas=True,
            data_parts=parts
        ).build()

    def create_transaction_for_freezing(
        self,
        sender: IAddress,
        user: IAddress,
        token_identifier: str
    ) -> Transaction:
        parts: List[str] = [
            "freeze",
            arg_to_string(token_identifier),
            user.to_hex()
        ]

        return TransactionBuilder(
            config=self._config,
            sender=sender,
            receiver=self._config.esdt_contract_address,
            amount=None,
            gas_limit=self._config.gas_limit_freezing,
            add_data_movement_gas=True,
            data_parts=parts,
        ).build()

    def create_transaction_for_unfreezing(
        self,
        sender: IAddress,
        user: IAddress,
        token_identifier: str
    ) -> Transaction:
        parts: List[str] = [
            "unFreeze",
            arg_to_string(token_identifier),
            user.to_hex()
        ]

        return TransactionBuilder(
            config=self._config,
            sender=sender,
            receiver=self._config.esdt_contract_address,
            amount=None,
            gas_limit=self._config.gas_limit_freezing,
            add_data_movement_gas=True,
            data_parts=parts
        ).build()

    def create_transaction_for_wiping(
        self,
        sender: IAddress,
        user: IAddress,
        token_identifier: str
    ) -> Transaction:
        parts: List[str] = [
            "wipe",
            arg_to_string(token_identifier),
            user.to_hex()
        ]

        return TransactionBuilder(
            config=self._config,
            sender=sender,
            receiver=self._config.esdt_contract_address,
            amount=None,
            gas_limit=self._config.gas_limit_wiping,
            add_data_movement_gas=True,
            data_parts=parts
        ).build()

    def create_transaction_for_local_minting(
        self,
        sender: IAddress,
        token_identifier: str,
        supply_to_mint: int
    ) -> Transaction:
        parts: List[str] = [
            "ESDTLocalMint",
            arg_to_string(token_identifier),
            arg_to_string(supply_to_mint)
        ]

        return TransactionBuilder(
            config=self._config,
            sender=sender,
            receiver=sender,
            amount=None,
            gas_limit=self._config.gas_limit_esdt_local_mint,
            add_data_movement_gas=True,
            data_parts=parts
        ).build()

    def create_transaction_for_local_burning(
        self,
        sender: IAddress,
        token_identifier: str,
        supply_to_burn: int
    ) -> Transaction:
        parts: List[str] = [
            "ESDTLocalBurn",
            arg_to_string(token_identifier),
            arg_to_string(supply_to_burn)
        ]

        return TransactionBuilder(
            config=self._config,
            sender=sender,
            receiver=sender,
            amount=None,
            gas_limit=self._config.gas_limit_esdt_local_burn,
            add_data_movement_gas=True,
            data_parts=parts
        ).build()

    def create_transaction_for_updating_attributes(
        self,
        sender: IAddress,
        token_identifier: str,
        token_nonce: int,
        attributes: bytes
    ) -> Transaction:
        parts: List[str] = [
            "ESDTNFTUpdateAttributes",
            arg_to_string(token_identifier),
            arg_to_string(token_nonce),
            arg_to_string(attributes)
        ]

        return TransactionBuilder(
            config=self._config,
            sender=sender,
            receiver=sender,
            amount=None,
            gas_limit=self._config.gas_limit_esdt_nft_update_attributes,
            add_data_movement_gas=True,
            data_parts=parts
        ).build()

    def create_transaction_for_adding_quantity(
        self,
        sender: IAddress,
        token_identifier: str,
        token_nonce: int,
        quantity_to_add: int
    ) -> Transaction:
        parts: List[str] = [
            "ESDTNFTAddQuantity",
            arg_to_string(token_identifier),
            arg_to_string(token_nonce),
            arg_to_string(quantity_to_add)
        ]

        return TransactionBuilder(
            config=self._config,
            sender=sender,
            receiver=sender,
            amount=None,
            gas_limit=self._config.gas_limit_esdt_nft_add_quantity,
            add_data_movement_gas=True,
            data_parts=parts
        ).build()

    def create_transaction_for_burning_quantity(
        self,
        sender: IAddress,
        token_identifier: str,
        token_nonce: int,
        quantity_to_burn: int
    ) -> Transaction:
        parts: List[str] = [
            "ESDTNFTBurn",
            arg_to_string(token_identifier),
            arg_to_string(token_nonce),
            arg_to_string(quantity_to_burn)
        ]

        return TransactionBuilder(
            config=self._config,
            sender=sender,
            receiver=sender,
            amount=None,
            gas_limit=self._config.gas_limit_esdt_nft_burn,
            add_data_movement_gas=True,
            data_parts=parts
        ).build()

    def create_transaction_for_modifying_royalties(self,
                                                   sender: IAddress,
                                                   token_identifier: str,
                                                   token_nonce: int,
                                                   new_royalties: int) -> Transaction:
        parts: List[str] = [
            "ESDTModifyRoyalties",
            arg_to_string(token_identifier),
            arg_to_string(token_nonce),
            arg_to_string(new_royalties)
        ]

        return TransactionBuilder(
            config=self._config,
            sender=sender,
            receiver=sender,
            amount=None,
            gas_limit=self._config.gas_limit_esdt_modify_royalties,
            add_data_movement_gas=True,
            data_parts=parts
        ).build()

    def create_transaction_for_setting_new_uris(self,
                                                sender: IAddress,
                                                token_identifier: str,
                                                token_nonce: int,
                                                new_uris: List[str]) -> Transaction:
        if not new_uris:
            raise BadUsageError("No URIs provided")

        parts: List[str] = [
            "ESDTSetNewURIs",
            arg_to_string(token_identifier),
            arg_to_string(token_nonce),
            *map(arg_to_string, new_uris)
        ]

        return TransactionBuilder(
            config=self._config,
            sender=sender,
            receiver=sender,
            amount=None,
            gas_limit=self._config.gas_limit_set_new_uris,
            add_data_movement_gas=True,
            data_parts=parts
        ).build()

    def create_transaction_for_modifying_creator(self,
                                                 sender: IAddress,
                                                 token_identifier: str,
                                                 token_nonce: int) -> Transaction:
        parts: List[str] = [
            "ESDTModifyCreator",
            arg_to_string(token_identifier),
            arg_to_string(token_nonce)
        ]

        return TransactionBuilder(
            config=self._config,
            sender=sender,
            receiver=sender,
            amount=None,
            gas_limit=self._config.gas_limit_esdt_modify_creator,
            add_data_movement_gas=True,
            data_parts=parts
        ).build()

    def create_transaction_for_updating_metadata(self,
                                                 sender: IAddress,
                                                 token_identifier: str,
                                                 token_nonce: int,
                                                 new_token_name: str,
                                                 new_royalties: int,
                                                 new_hash: str,
                                                 new_attributes: bytes,
                                                 new_uris: List[str]) -> Transaction:
        parts: List[str] = [
            "ESDTMetaDataUpdate",
            arg_to_string(token_identifier),
            arg_to_string(token_nonce),
            arg_to_string(new_token_name),
            arg_to_string(new_royalties),
            arg_to_string(new_hash),
            arg_to_string(new_attributes),
            *map(arg_to_string, new_uris)
        ]

        return TransactionBuilder(
            config=self._config,
            sender=sender,
            receiver=sender,
            amount=None,
            gas_limit=self._config.gas_limit_esdt_metadata_update,
            add_data_movement_gas=True,
            data_parts=parts
        ).build()

    def create_transaction_for_nft_metadata_recreate(self,
                                                     sender: IAddress,
                                                     token_identifier: str,
                                                     token_nonce: int,
                                                     new_token_name: str,
                                                     new_royalties: int,
                                                     new_hash: str,
                                                     new_attributes: bytes,
                                                     new_uris: List[str]) -> Transaction:
        parts: List[str] = [
            "ESDTMetaDataRecreate",
            arg_to_string(token_identifier),
            arg_to_string(token_nonce),
            arg_to_string(new_token_name),
            arg_to_string(new_royalties),
            arg_to_string(new_hash),
            arg_to_string(new_attributes),
            *map(arg_to_string, new_uris)
        ]

        return TransactionBuilder(
            config=self._config,
            sender=sender,
            receiver=sender,
            amount=None,
            gas_limit=self._config.gas_limit_nft_metadata_recreate,
            add_data_movement_gas=True,
            data_parts=parts
        ).build()

    def create_transaction_for_changing_token_to_dynamic(self,
                                                         sender: IAddress,
                                                         token_identifier: str) -> Transaction:
        parts: List[str] = [
            "changeToDynamic",
            arg_to_string(token_identifier)
        ]

        return TransactionBuilder(
            config=self._config,
            sender=sender,
            receiver=self._config.esdt_contract_address,
            amount=None,
            gas_limit=self._config.gas_limit_nft_change_to_dynamic,
            add_data_movement_gas=True,
            data_parts=parts
        ).build()

    def create_transaction_for_updating_token_id(self,
                                                 sender: IAddress,
                                                 token_identifier: str) -> Transaction:
        parts: List[str] = [
            "updateTokenID",
            arg_to_string(token_identifier)
        ]

        return TransactionBuilder(
            config=self._config,
            sender=sender,
            receiver=self._config.esdt_contract_address,
            amount=None,
            gas_limit=self._config.gas_limit_update_token_id,
            add_data_movement_gas=True,
            data_parts=parts
        ).build()

    def create_transaction_for_registering_dynamic_token(self,
                                                         sender: IAddress,
                                                         token_name: str,
                                                         token_ticker: str,
                                                         token_type: TokenType) -> Transaction:
        parts: List[str] = [
            "registerDynamic",
            arg_to_string(token_name),
            arg_to_string(token_ticker),
            arg_to_string(token_type.value)
        ]

        return TransactionBuilder(
            config=self._config,
            sender=sender,
            receiver=self._config.esdt_contract_address,
            amount=self._config.issue_cost,
            gas_limit=self._config.gas_limit_register_dynamic,
            add_data_movement_gas=True,
            data_parts=parts
        ).build()

    def create_transaction_for_registering_dynamic_and_setting_roles(self,
                                                                     sender: IAddress,
                                                                     token_name: str,
                                                                     token_ticker: str,
                                                                     token_type: TokenType) -> Transaction:
        parts: List[str] = [
            "registerAndSetAllRolesDynamic",
            arg_to_string(token_name),
            arg_to_string(token_ticker),
            arg_to_string(token_type.value)
        ]

        return TransactionBuilder(
            config=self._config,
            sender=sender,
            receiver=self._config.esdt_contract_address,
            amount=self._config.issue_cost,
            gas_limit=self._config.gas_limit_register_dynamic,
            add_data_movement_gas=True,
            data_parts=parts
        ).build()
