
import logging
from typing import List, Optional, Protocol

from multiversx_sdk_core import Transaction, TransactionPayload
from multiversx_sdk_core.constants import (ARGS_SEPARATOR,
                                           TRANSACTION_OPTIONS_DEFAULT,
                                           TRANSACTION_VERSION_DEFAULT)
from multiversx_sdk_core.interfaces import (IAddress, IChainID, IGasLimit,
                                            IGasPrice, INonce,
                                            ITransactionValue)
from multiversx_sdk_core.serializer import arg_to_string

logger = logging.getLogger(__name__)


class IConfig(Protocol):
    chain_id: IChainID
    min_gas_limit: IGasLimit
    gas_limit_per_byte: IGasLimit
    gas_limit_issue: IGasLimit
    gas_limit_toggle_burn_role_globally: IGasLimit
    gas_limit_esdt_local_mint: IGasLimit
    gas_limit_esdt_local_burn: IGasLimit
    gas_limit_set_special_role: IGasLimit
    gas_limit_pausing: IGasLimit
    gas_limit_freezing: IGasLimit
    gas_limit_wiping: IGasLimit
    gas_limit_esdt_nft_create: IGasLimit
    gas_limit_esdt_nft_update_attributes: IGasLimit
    gas_limit_esdt_nft_add_quantity: IGasLimit
    gas_limit_esdt_nft_burn: IGasLimit
    gas_limit_store_per_byte: IGasLimit
    issue_cost: ITransactionValue
    esdt_contract_address: IAddress


class TokenOperationsFactory:
    def __init__(self, config: IConfig):
        self._config = config
        self._true_as_hex = arg_to_string("true")

    def issue_fungible(
        self,
        issuer: IAddress,
        token_name: str,
        token_ticker: str,
        initial_supply: int,
        num_decimals: int,
        can_freeze: bool,
        can_wipe: bool,
        can_pause: bool,
        can_change_owner: bool,
        can_upgrade: bool,
        can_add_special_roles: bool,
        transaction_nonce: Optional[INonce] = None,
        gas_price: Optional[IGasPrice] = None,
        gas_limit: Optional[IGasLimit] = None
    ) -> Transaction:
        self._notify_about_unsetting_burn_role_globally()

        parts: List[str] = [
            "issue",
            arg_to_string(token_name),
            arg_to_string(token_ticker),
            arg_to_string(initial_supply),
            arg_to_string(num_decimals),
            *([arg_to_string("canFreeze"), self._true_as_hex] if can_freeze else []),
            *([arg_to_string("canWipe"), self._true_as_hex] if can_wipe else []),
            *([arg_to_string("canPause"), self._true_as_hex] if can_pause else []),
            *([arg_to_string("canChangeOwner"), self._true_as_hex] if can_change_owner else []),
            *([arg_to_string("canUpgrade"), self._true_as_hex] if can_upgrade else []),
            *([arg_to_string("canAddSpecialRoles"), self._true_as_hex] if can_add_special_roles else []),
        ]

        return self._create_transaction(
            sender=issuer,
            receiver=self._config.esdt_contract_address,
            nonce=transaction_nonce,
            value=self._config.issue_cost,
            gas_price=gas_price,
            gas_limit_hint=gas_limit,
            execution_gas_limit=self._config.gas_limit_issue,
            data_parts=parts
        )

    def _notify_about_unsetting_burn_role_globally(self) -> None:
        logger.info("""
==========
IMPORTANT!
==========
You are about to issue (register) a new token. This will set the role "ESDTRoleBurnForAll" (globally).
Once the token is registered, you can unset this role by calling "unsetBurnRoleGlobally" (in a separate transaction).""")

    def issue_semi_fungible(
        self,
        issuer: IAddress,
        token_name: str,
        token_ticker: str,
        can_freeze: bool,
        can_wipe: bool,
        can_pause: bool,
        can_transfer_nft_create_role: bool,
        can_change_owner: bool,
        can_upgrade: bool,
        can_add_special_roles: bool,
        transaction_nonce: Optional[INonce] = None,
        gas_price: Optional[IGasPrice] = None,
        gas_limit: Optional[IGasLimit] = None
    ) -> Transaction:
        self._notify_about_unsetting_burn_role_globally()

        parts: List[str] = [
            "issueSemiFungible",
            arg_to_string(token_name),
            arg_to_string(token_ticker),
            *([arg_to_string("canFreeze"), self._true_as_hex] if can_freeze else []),
            *([arg_to_string("canWipe"), self._true_as_hex] if can_wipe else []),
            *([arg_to_string("canPause"), self._true_as_hex] if can_pause else []),
            *([arg_to_string("canTransferNFTCreateRole"), self._true_as_hex] if can_transfer_nft_create_role else []),
            *([arg_to_string("canChangeOwner"), self._true_as_hex] if can_change_owner else []),
            *([arg_to_string("canUpgrade"), self._true_as_hex] if can_upgrade else []),
            *([arg_to_string("canAddSpecialRoles"), self._true_as_hex] if can_add_special_roles else []),
        ]

        return self._create_transaction(
            sender=issuer,
            receiver=self._config.esdt_contract_address,
            nonce=transaction_nonce,
            value=self._config.issue_cost,
            gas_price=gas_price,
            gas_limit_hint=gas_limit,
            execution_gas_limit=self._config.gas_limit_issue,
            data_parts=parts
        )

    def issue_non_fungible(
        self,
        issuer: IAddress,
        token_name: str,
        token_ticker: str,
        can_freeze: bool,
        can_wipe: bool,
        can_pause: bool,
        can_transfer_nft_create_role: bool,
        can_change_owner: bool,
        can_upgrade: bool,
        can_add_special_roles: bool,
        transaction_nonce: Optional[INonce] = None,
        gas_price: Optional[IGasPrice] = None,
        gas_limit: Optional[IGasLimit] = None
    ) -> Transaction:
        self._notify_about_unsetting_burn_role_globally()

        parts: List[str] = [
            "issueNonFungible",
            arg_to_string(token_name),
            arg_to_string(token_ticker),
            *([arg_to_string("canFreeze"), self._true_as_hex] if can_freeze else []),
            *([arg_to_string("canWipe"), self._true_as_hex] if can_wipe else []),
            *([arg_to_string("canPause"), self._true_as_hex] if can_pause else []),
            *([arg_to_string("canTransferNFTCreateRole"), self._true_as_hex] if can_transfer_nft_create_role else []),
            *([arg_to_string("canChangeOwner"), self._true_as_hex] if can_change_owner else []),
            *([arg_to_string("canUpgrade"), self._true_as_hex] if can_upgrade else []),
            *([arg_to_string("canAddSpecialRoles"), self._true_as_hex] if can_add_special_roles else []),
        ]

        return self._create_transaction(
            sender=issuer,
            receiver=self._config.esdt_contract_address,
            nonce=transaction_nonce,
            value=self._config.issue_cost,
            gas_price=gas_price,
            gas_limit_hint=gas_limit,
            execution_gas_limit=self._config.gas_limit_issue,
            data_parts=parts
        )

    def register_meta_esdt(
        self,
        issuer: IAddress,
        token_name: str,
        token_ticker: str,
        num_decimals: int,
        can_freeze: bool,
        can_wipe: bool,
        can_pause: bool,
        can_transfer_nft_create_role: bool,
        can_change_owner: bool,
        can_upgrade: bool,
        can_add_special_roles: bool,
        transaction_nonce: Optional[INonce] = None,
        gas_price: Optional[IGasPrice] = None,
        gas_limit: Optional[IGasLimit] = None
    ) -> Transaction:
        self._notify_about_unsetting_burn_role_globally()

        parts: List[str] = [
            "registerMetaESDT",
            arg_to_string(token_name),
            arg_to_string(token_ticker),
            arg_to_string(num_decimals),
            *([arg_to_string("canFreeze"), self._true_as_hex] if can_freeze else []),
            *([arg_to_string("canWipe"), self._true_as_hex] if can_wipe else []),
            *([arg_to_string("canPause"), self._true_as_hex] if can_pause else []),
            *([arg_to_string("canTransferNFTCreateRole"), self._true_as_hex] if can_transfer_nft_create_role else []),
            *([arg_to_string("canChangeOwner"), self._true_as_hex] if can_change_owner else []),
            *([arg_to_string("canUpgrade"), self._true_as_hex] if can_upgrade else []),
            *([arg_to_string("canAddSpecialRoles"), self._true_as_hex] if can_add_special_roles else []),
        ]

        return self._create_transaction(
            sender=issuer,
            receiver=self._config.esdt_contract_address,
            nonce=transaction_nonce,
            value=self._config.issue_cost,
            gas_price=gas_price,
            gas_limit_hint=gas_limit,
            execution_gas_limit=self._config.gas_limit_issue,
            data_parts=parts
        )

    def register_and_set_all_roles(
        self,
        issuer: IAddress,
        token_name: str,
        token_ticker: str,
        token_type: str,
        num_decimals: int,
        transaction_nonce: Optional[INonce] = None,
        gas_price: Optional[IGasPrice] = None,
        gas_limit: Optional[IGasLimit] = None
    ) -> Transaction:
        self._notify_about_unsetting_burn_role_globally()

        parts: List[str] = [
            "registerAndSetAllRoles",
            arg_to_string(token_name),
            arg_to_string(token_ticker),
            arg_to_string(token_type),
            arg_to_string(num_decimals)
        ]

        return self._create_transaction(
            sender=issuer,
            receiver=self._config.esdt_contract_address,
            nonce=transaction_nonce,
            value=self._config.issue_cost,
            gas_price=gas_price,
            gas_limit_hint=gas_limit,
            execution_gas_limit=self._config.gas_limit_issue,
            data_parts=parts
        )

    def set_burn_role_globally(
        self,
        manager: IAddress,
        token_identifier: str,
        transaction_nonce: Optional[INonce] = None,
        gas_price: Optional[IGasPrice] = None,
        gas_limit: Optional[IGasLimit] = None
    ) -> Transaction:
        parts: List[str] = [
            "setBurnRoleGlobally",
            arg_to_string(token_identifier)
        ]

        return self._create_transaction(
            sender=manager,
            receiver=self._config.esdt_contract_address,
            nonce=transaction_nonce,
            value=None,
            gas_price=gas_price,
            gas_limit_hint=gas_limit,
            execution_gas_limit=self._config.gas_limit_toggle_burn_role_globally,
            data_parts=parts
        )

    def unset_burn_role_globally(
        self,
        manager: IAddress,
        token_identifier: str,
        transaction_nonce: Optional[INonce] = None,
        gas_price: Optional[IGasPrice] = None,
        gas_limit: Optional[IGasLimit] = None
    ) -> Transaction:
        parts: List[str] = [
            "unsetBurnRoleGlobally",
            arg_to_string(token_identifier)
        ]

        return self._create_transaction(
            sender=manager,
            receiver=self._config.esdt_contract_address,
            nonce=transaction_nonce,
            value=None,
            gas_price=gas_price,
            gas_limit_hint=gas_limit,
            execution_gas_limit=self._config.gas_limit_toggle_burn_role_globally,
            data_parts=parts
        )

    def set_special_role_on_fungible(
        self,
        manager: IAddress,
        user: IAddress,
        token_identifier: str,
        add_role_local_mint: bool,
        add_role_local_burn: bool,
        transaction_nonce: Optional[INonce] = None,
        gas_price: Optional[IGasPrice] = None,
        gas_limit: Optional[IGasLimit] = None
    ) -> Transaction:
        parts: List[str] = [
            "setSpecialRole",
            arg_to_string(token_identifier),
            arg_to_string(user),
            *([arg_to_string("ESDTRoleLocalMint")] if add_role_local_mint else []),
            *([arg_to_string("ESDTRoleLocalBurn")] if add_role_local_burn else [])
        ]

        return self._create_transaction(
            sender=manager,
            receiver=self._config.esdt_contract_address,
            nonce=transaction_nonce,
            value=None,
            gas_price=gas_price,
            gas_limit_hint=gas_limit,
            execution_gas_limit=self._config.gas_limit_set_special_role,
            data_parts=parts
        )

    def set_special_role_on_semi_fungible(
        self,
        manager: IAddress,
        user: IAddress,
        token_identifier: str,
        add_role_nft_create: bool,
        add_role_nft_burn: bool,
        add_role_nft_add_quantity: bool,
        add_role_esdt_transfer_role: bool,
        transaction_nonce: Optional[INonce] = None,
        gas_price: Optional[IGasPrice] = None,
        gas_limit: Optional[IGasLimit] = None
    ) -> Transaction:
        parts: List[str] = [
            "setSpecialRole",
            arg_to_string(token_identifier),
            arg_to_string(user),
            *([arg_to_string("ESDTRoleNFTCreate")] if add_role_nft_create else []),
            *([arg_to_string("ESDTRoleNFTBurn")] if add_role_nft_burn else []),
            *([arg_to_string("ESDTRoleNFTAddQuantity")] if add_role_nft_add_quantity else []),
            *([arg_to_string("ESDTTransferRole")] if add_role_esdt_transfer_role else [])
        ]

        return self._create_transaction(
            sender=manager,
            receiver=self._config.esdt_contract_address,
            nonce=transaction_nonce,
            value=None,
            gas_price=gas_price,
            gas_limit_hint=gas_limit,
            execution_gas_limit=self._config.gas_limit_set_special_role,
            data_parts=parts
        )

    def set_special_role_on_non_fungible(
        self,
        manager: IAddress,
        user: IAddress,
        token_identifier: str,
        add_role_nft_create: bool,
        add_role_nft_burn: bool,
        add_role_nft_update_attributes: bool,
        add_role_nft_add_uri: bool,
        add_role_esdt_transfer_role: bool,
        transaction_nonce: Optional[INonce] = None,
        gas_price: Optional[IGasPrice] = None,
        gas_limit: Optional[IGasLimit] = None
    ) -> Transaction:
        parts: List[str] = [
            "setSpecialRole",
            arg_to_string(token_identifier),
            arg_to_string(user),
            *([arg_to_string("ESDTRoleNFTCreate")] if add_role_nft_create else []),
            *([arg_to_string("ESDTRoleNFTBurn")] if add_role_nft_burn else []),
            *([arg_to_string("ESDTRoleNFTUpdateAttributes")] if add_role_nft_update_attributes else []),
            *([arg_to_string("ESDTRoleNFTAddURI")] if add_role_nft_add_uri else []),
            *([arg_to_string("ESDTTransferRole")] if add_role_esdt_transfer_role else [])
        ]

        return self._create_transaction(
            sender=manager,
            receiver=self._config.esdt_contract_address,
            nonce=transaction_nonce,
            value=None,
            gas_price=gas_price,
            gas_limit_hint=gas_limit,
            execution_gas_limit=self._config.gas_limit_set_special_role,
            data_parts=parts
        )

    def nft_create(
        self,
        creator: IAddress,
        token_identifier: str,
        initial_quantity: int,
        name: str,
        royalties: int,
        hash: str,
        attributes: bytes,
        uris: List[str],
        transaction_nonce: Optional[INonce] = None,
        gas_price: Optional[IGasPrice] = None,
        gas_limit: Optional[IGasLimit] = None
    ) -> Transaction:
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

        return self._create_transaction(
            sender=creator,
            receiver=creator,
            nonce=transaction_nonce,
            value=None,
            gas_price=gas_price,
            gas_limit_hint=gas_limit,
            execution_gas_limit=self._config.gas_limit_esdt_nft_create + storage_gas_limit,
            data_parts=parts
        )

    def pause(
        self,
        manager: IAddress,
        token_identifier: str,
        transaction_nonce: Optional[INonce] = None,
        gas_price: Optional[IGasPrice] = None,
        gas_limit: Optional[IGasLimit] = None,
    ) -> Transaction:
        parts: List[str] = [
            "pause",
            arg_to_string(token_identifier)
        ]

        return self._create_transaction(
            sender=manager,
            receiver=self._config.esdt_contract_address,
            nonce=transaction_nonce,
            value=None,
            gas_price=gas_price,
            gas_limit_hint=gas_limit,
            execution_gas_limit=self._config.gas_limit_pausing,
            data_parts=parts
        )

    def unpause(
        self,
        manager: IAddress,
        token_identifier: str,
        transaction_nonce: Optional[INonce] = None,
        gas_price: Optional[IGasPrice] = None,
        gas_limit: Optional[IGasLimit] = None,
    ) -> Transaction:
        parts: List[str] = [
            "unPause",
            arg_to_string(token_identifier)
        ]

        return self._create_transaction(
            sender=manager,
            receiver=self._config.esdt_contract_address,
            nonce=transaction_nonce,
            value=None,
            gas_price=gas_price,
            gas_limit_hint=gas_limit,
            execution_gas_limit=self._config.gas_limit_pausing,
            data_parts=parts
        )

    def freeze(
        self,
        manager: IAddress,
        user: IAddress,
        token_identifier: str,
        transaction_nonce: Optional[INonce] = None,
        gas_price: Optional[IGasPrice] = None,
        gas_limit: Optional[IGasLimit] = None,
    ) -> Transaction:
        parts: List[str] = [
            "freeze",
            arg_to_string(token_identifier),
            arg_to_string(user)
        ]

        return self._create_transaction(
            sender=manager,
            receiver=self._config.esdt_contract_address,
            nonce=transaction_nonce,
            value=None,
            gas_price=gas_price,
            gas_limit_hint=gas_limit,
            execution_gas_limit=self._config.gas_limit_freezing,
            data_parts=parts
        )

    def unfreeze(
        self,
        manager: IAddress,
        user: IAddress,
        token_identifier: str,
        transaction_nonce: Optional[INonce] = None,
        gas_price: Optional[IGasPrice] = None,
        gas_limit: Optional[IGasLimit] = None,
    ) -> Transaction:
        parts: List[str] = [
            "unFreeze",
            arg_to_string(token_identifier),
            arg_to_string(user)
        ]

        return self._create_transaction(
            sender=manager,
            receiver=self._config.esdt_contract_address,
            nonce=transaction_nonce,
            value=None,
            gas_price=gas_price,
            gas_limit_hint=gas_limit,
            execution_gas_limit=self._config.gas_limit_freezing,
            data_parts=parts
        )

    def wipe(
        self,
        manager: IAddress,
        user: IAddress,
        token_identifier: str,
        transaction_nonce: Optional[INonce] = None,
        gas_price: Optional[IGasPrice] = None,
        gas_limit: Optional[IGasLimit] = None,
    ) -> Transaction:
        parts: List[str] = [
            "wipe",
            arg_to_string(token_identifier),
            arg_to_string(user)
        ]

        return self._create_transaction(
            sender=manager,
            receiver=self._config.esdt_contract_address,
            nonce=transaction_nonce,
            value=None,
            gas_price=gas_price,
            gas_limit_hint=gas_limit,
            execution_gas_limit=self._config.gas_limit_wiping,
            data_parts=parts
        )

    def local_mint(
        self,
        manager: IAddress,
        token_identifier: str,
        supply_to_mint: int,
        transaction_nonce: Optional[INonce] = None,
        gas_price: Optional[IGasPrice] = None,
        gas_limit: Optional[IGasLimit] = None,
    ) -> Transaction:
        parts: List[str] = [
            "ESDTLocalMint",
            arg_to_string(token_identifier),
            arg_to_string(supply_to_mint)
        ]

        return self._create_transaction(
            sender=manager,
            receiver=manager,
            nonce=transaction_nonce,
            value=None,
            gas_price=gas_price,
            gas_limit_hint=gas_limit,
            execution_gas_limit=self._config.gas_limit_esdt_local_mint,
            data_parts=parts
        )

    def local_burn(
        self,
        manager: IAddress,
        token_identifier: str,
        supply_to_burn: int,
        transaction_nonce: Optional[INonce] = None,
        gas_price: Optional[IGasPrice] = None,
        gas_limit: Optional[IGasLimit] = None,
    ) -> Transaction:
        parts: List[str] = [
            "ESDTLocalBurn",
            arg_to_string(token_identifier),
            arg_to_string(supply_to_burn)
        ]

        return self._create_transaction(
            sender=manager,
            receiver=manager,
            nonce=transaction_nonce,
            value=None,
            gas_price=gas_price,
            gas_limit_hint=gas_limit,
            execution_gas_limit=self._config.gas_limit_esdt_local_burn,
            data_parts=parts
        )

    def update_attributes(
        self,
        manager: IAddress,
        token_identifier: str,
        token_nonce: int,
        attributes: bytes,
        transaction_nonce: Optional[INonce] = None,
        gas_price: Optional[IGasPrice] = None,
        gas_limit: Optional[IGasLimit] = None,
    ) -> Transaction:
        parts: List[str] = [
            "ESDTNFTUpdateAttributes",
            arg_to_string(token_identifier),
            arg_to_string(token_nonce),
            arg_to_string(attributes)
        ]

        return self._create_transaction(
            sender=manager,
            receiver=manager,
            nonce=transaction_nonce,
            value=None,
            gas_price=gas_price,
            gas_limit_hint=gas_limit,
            execution_gas_limit=self._config.gas_limit_esdt_nft_update_attributes,
            data_parts=parts
        )

    def add_quantity(
        self,
        manager: IAddress,
        token_identifier: str,
        token_nonce: int,
        quantity_to_add: int,
        transaction_nonce: Optional[INonce] = None,
        gas_price: Optional[IGasPrice] = None,
        gas_limit: Optional[IGasLimit] = None,
    ) -> Transaction:
        parts: List[str] = [
            "ESDTNFTAddQuantity",
            arg_to_string(token_identifier),
            arg_to_string(token_nonce),
            arg_to_string(quantity_to_add)
        ]

        return self._create_transaction(
            sender=manager,
            receiver=manager,
            nonce=transaction_nonce,
            value=None,
            gas_price=gas_price,
            gas_limit_hint=gas_limit,
            execution_gas_limit=self._config.gas_limit_esdt_nft_add_quantity,
            data_parts=parts
        )

    def burn_quantity(
        self,
        manager: IAddress,
        token_identifier: str,
        token_nonce: int,
        quantity_to_burn: int,
        transaction_nonce: Optional[INonce] = None,
        gas_price: Optional[IGasPrice] = None,
        gas_limit: Optional[IGasLimit] = None,
    ) -> Transaction:
        parts: List[str] = [
            "ESDTNFTBurn",
            arg_to_string(token_identifier),
            arg_to_string(token_nonce),
            arg_to_string(quantity_to_burn)
        ]

        return self._create_transaction(
            sender=manager,
            receiver=manager,
            nonce=transaction_nonce,
            value=None,
            gas_price=gas_price,
            gas_limit_hint=gas_limit,
            execution_gas_limit=self._config.gas_limit_esdt_nft_burn,
            data_parts=parts
        )

    def _create_transaction(
        self,
        sender: IAddress,
        receiver: IAddress,
        nonce: Optional[INonce],
        value: Optional[ITransactionValue],
        gas_price: Optional[IGasPrice],
        gas_limit_hint: Optional[IGasLimit],
        execution_gas_limit: IGasLimit,
        data_parts: List[str]
    ) -> Transaction:
        payload = self._build_transaction_payload(data_parts)
        gas_limit = gas_limit_hint or self._compute_gas_limit(payload, execution_gas_limit)
        version = TRANSACTION_VERSION_DEFAULT
        options = TRANSACTION_OPTIONS_DEFAULT

        return Transaction(
            chain_id=self._config.chain_id,
            sender=sender,
            receiver=receiver,
            gas_limit=gas_limit,
            gas_price=gas_price,
            nonce=nonce or 0,
            value=value or 0,
            data=payload,
            version=version,
            options=options
        )

    def _build_transaction_payload(self, parts: List[str]) -> TransactionPayload:
        data = ARGS_SEPARATOR.join(parts)
        return TransactionPayload.from_str(data)

    def _compute_gas_limit(self, payload: TransactionPayload, execution_gas: IGasLimit) -> IGasLimit:
        data_movement_gas = self._config.min_gas_limit + self._config.gas_limit_per_byte * payload.length()
        return data_movement_gas + execution_gas
