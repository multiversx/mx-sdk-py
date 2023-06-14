
import logging
from typing import List, Optional, Protocol, TypedDict

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
    min_gas_price: IGasPrice
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
            gas_price=gas_price,
            gas_limit_hint=gas_limit,
            execution_gas_limit=self._config.gas_limit_toggle_burn_role_globally,
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
