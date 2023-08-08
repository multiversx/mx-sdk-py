
import logging
from typing import List, Optional, Protocol

from multiversx_sdk_core import TransactionPayload
from multiversx_sdk_core.constants import ARGS_SEPARATOR
from multiversx_sdk_core.interfaces import IAddress
from multiversx_sdk_core.serializer import arg_to_string
from multiversx_sdk_core.transaction_intent import TransactionIntent

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
    issue_cost: int
    esdt_contract_address: IAddress


class TokenOperationsFactory:
    def __init__(self, config: IConfig):
        self._config = config
        self._true_as_hex = arg_to_string("true")

    def create_transaction_intent_for_issuing_fungible(
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
    ) -> TransactionIntent:
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

        return self._create_transaction_intent(
            sender=sender,
            receiver=self._config.esdt_contract_address,
            value=self._config.issue_cost,
            execution_gas_limit=self._config.gas_limit_issue,
            data_parts=parts,
        )

    def _notify_about_unsetting_burn_role_globally(self) -> None:
        logger.info("""
==========
IMPORTANT!
==========
You are about to issue (register) a new token. This will set the role "ESDTRoleBurnForAll" (globally).
Once the token is registered, you can unset this role by calling "unsetBurnRoleGlobally" (in a separate transaction).""")

    def create_transaction_intent_for_issuing_semi_fungible(
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
    ) -> TransactionIntent:
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

        return self._create_transaction_intent(
            sender=sender,
            receiver=self._config.esdt_contract_address,
            value=self._config.issue_cost,
            execution_gas_limit=self._config.gas_limit_issue,
            data_parts=parts
        )

    def create_transaction_intent_for_issuing_non_fungible(
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
    ) -> TransactionIntent:
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

        return self._create_transaction_intent(
            sender=sender,
            receiver=self._config.esdt_contract_address,
            value=self._config.issue_cost,
            execution_gas_limit=self._config.gas_limit_issue,
            data_parts=parts
        )

    def create_transaction_intent_for_registering_meta_esdt(
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
    ) -> TransactionIntent:
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

        return self._create_transaction_intent(
            sender=sender,
            receiver=self._config.esdt_contract_address,
            value=self._config.issue_cost,
            execution_gas_limit=self._config.gas_limit_issue,
            data_parts=parts,
        )

    def create_transaction_intent_for_registering_and_setting_roles(
        self,
        sender: IAddress,
        token_name: str,
        token_ticker: str,
        token_type: str,
        num_decimals: int
    ) -> TransactionIntent:
        self._notify_about_unsetting_burn_role_globally()

        parts: List[str] = [
            "registerAndSetAllRoles",
            arg_to_string(token_name),
            arg_to_string(token_ticker),
            arg_to_string(token_type),
            arg_to_string(num_decimals)
        ]

        return self._create_transaction_intent(
            sender=sender,
            receiver=self._config.esdt_contract_address,
            value=self._config.issue_cost,
            execution_gas_limit=self._config.gas_limit_issue,
            data_parts=parts
        )

    def create_transaction_intent_for_setting_burn_role_globally(
        self,
        sender: IAddress,
        token_identifier: str
    ) -> TransactionIntent:
        parts: List[str] = [
            "setBurnRoleGlobally",
            arg_to_string(token_identifier)
        ]

        return self._create_transaction_intent(
            sender=sender,
            receiver=self._config.esdt_contract_address,
            value=None,
            execution_gas_limit=self._config.gas_limit_toggle_burn_role_globally,
            data_parts=parts
        )

    def create_transaction_intent_for_unsetting_burn_role_globally(
        self,
        sender: IAddress,
        token_identifier: str
    ) -> TransactionIntent:
        parts: List[str] = [
            "unsetBurnRoleGlobally",
            arg_to_string(token_identifier)
        ]

        return self._create_transaction_intent(
            sender=sender,
            receiver=self._config.esdt_contract_address,
            value=None,
            execution_gas_limit=self._config.gas_limit_toggle_burn_role_globally,
            data_parts=parts
        )

    def create_transaction_intent_for_setting_special_role_on_fungible_token(
        self,
        sender: IAddress,
        user: IAddress,
        token_identifier: str,
        add_role_local_mint: bool,
        add_role_local_burn: bool
    ) -> TransactionIntent:
        parts: List[str] = [
            "setSpecialRole",
            arg_to_string(token_identifier),
            arg_to_string(user),
            *([arg_to_string("ESDTRoleLocalMint")] if add_role_local_mint else []),
            *([arg_to_string("ESDTRoleLocalBurn")] if add_role_local_burn else [])
        ]

        return self._create_transaction_intent(
            sender=sender,
            receiver=self._config.esdt_contract_address,
            value=None,
            execution_gas_limit=self._config.gas_limit_set_special_role,
            data_parts=parts
        )

    def create_transaction_intent_for_setting_special_role_on_semi_fungible_token(
        self,
        sender: IAddress,
        user: IAddress,
        token_identifier: str,
        add_role_nft_create: bool,
        add_role_nft_burn: bool,
        add_role_nft_add_quantity: bool,
        add_role_esdt_transfer_role: bool
    ) -> TransactionIntent:
        parts: List[str] = [
            "setSpecialRole",
            arg_to_string(token_identifier),
            arg_to_string(user),
            *([arg_to_string("ESDTRoleNFTCreate")] if add_role_nft_create else []),
            *([arg_to_string("ESDTRoleNFTBurn")] if add_role_nft_burn else []),
            *([arg_to_string("ESDTRoleNFTAddQuantity")] if add_role_nft_add_quantity else []),
            *([arg_to_string("ESDTTransferRole")] if add_role_esdt_transfer_role else [])
        ]

        return self._create_transaction_intent(
            sender=sender,
            receiver=self._config.esdt_contract_address,
            value=None,
            execution_gas_limit=self._config.gas_limit_set_special_role,
            data_parts=parts
        )

    def create_transaction_intent_for_setting_special_role_on_non_fungible_token(
        self,
        sender: IAddress,
        user: IAddress,
        token_identifier: str,
        add_role_nft_create: bool,
        add_role_nft_burn: bool,
        add_role_nft_update_attributes: bool,
        add_role_nft_add_uri: bool,
        add_role_esdt_transfer_role: bool
    ) -> TransactionIntent:
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

        return self._create_transaction_intent(
            sender=sender,
            receiver=self._config.esdt_contract_address,
            value=None,
            execution_gas_limit=self._config.gas_limit_set_special_role,
            data_parts=parts,
        )

    def create_transaction_intent_for_creating_nft(
        self,
        sender: IAddress,
        token_identifier: str,
        initial_quantity: int,
        name: str,
        royalties: int,
        hash: str,
        attributes: bytes,
        uris: List[str]
    ) -> TransactionIntent:
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

        return self._create_transaction_intent(
            sender=sender,
            receiver=sender,
            value=None,
            execution_gas_limit=self._config.gas_limit_esdt_nft_create + storage_gas_limit,
            data_parts=parts
        )

    def create_transaction_intent_for_pausing(
        self,
        sender: IAddress,
        token_identifier: str
    ) -> TransactionIntent:
        parts: List[str] = [
            "pause",
            arg_to_string(token_identifier)
        ]

        return self._create_transaction_intent(
            sender=sender,
            receiver=self._config.esdt_contract_address,
            value=None,
            execution_gas_limit=self._config.gas_limit_pausing,
            data_parts=parts
        )

    def create_transaction_intent_for_unpausing(
        self,
        sender: IAddress,
        token_identifier: str
    ) -> TransactionIntent:
        parts: List[str] = [
            "unPause",
            arg_to_string(token_identifier)
        ]

        return self._create_transaction_intent(
            sender=sender,
            receiver=self._config.esdt_contract_address,
            value=None,
            execution_gas_limit=self._config.gas_limit_pausing,
            data_parts=parts
        )

    def create_transaction_intent_for_freezing(
        self,
        sender: IAddress,
        user: IAddress,
        token_identifier: str
    ) -> TransactionIntent:
        parts: List[str] = [
            "freeze",
            arg_to_string(token_identifier),
            arg_to_string(user)
        ]

        return self._create_transaction_intent(
            sender=sender,
            receiver=self._config.esdt_contract_address,
            value=None,
            execution_gas_limit=self._config.gas_limit_freezing,
            data_parts=parts,
        )

    def create_transaction_intent_for_unfreezing(
        self,
        sender: IAddress,
        user: IAddress,
        token_identifier: str
    ) -> TransactionIntent:
        parts: List[str] = [
            "unFreeze",
            arg_to_string(token_identifier),
            arg_to_string(user)
        ]

        return self._create_transaction_intent(
            sender=sender,
            receiver=self._config.esdt_contract_address,
            value=None,
            execution_gas_limit=self._config.gas_limit_freezing,
            data_parts=parts
        )

    def create_transaction_intent_for_wiping(
        self,
        sender: IAddress,
        user: IAddress,
        token_identifier: str
    ) -> TransactionIntent:
        parts: List[str] = [
            "wipe",
            arg_to_string(token_identifier),
            arg_to_string(user)
        ]

        return self._create_transaction_intent(
            sender=sender,
            receiver=self._config.esdt_contract_address,
            value=None,
            execution_gas_limit=self._config.gas_limit_wiping,
            data_parts=parts
        )

    def create_transaction_intent_for_local_minting(
        self,
        sender: IAddress,
        token_identifier: str,
        supply_to_mint: int
    ) -> TransactionIntent:
        parts: List[str] = [
            "ESDTLocalMint",
            arg_to_string(token_identifier),
            arg_to_string(supply_to_mint)
        ]

        return self._create_transaction_intent(
            sender=sender,
            receiver=sender,
            value=None,
            execution_gas_limit=self._config.gas_limit_esdt_local_mint,
            data_parts=parts
        )

    def create_transaction_intent_for_local_burning(
        self,
        sender: IAddress,
        token_identifier: str,
        supply_to_burn: int
    ) -> TransactionIntent:
        parts: List[str] = [
            "ESDTLocalBurn",
            arg_to_string(token_identifier),
            arg_to_string(supply_to_burn)
        ]

        return self._create_transaction_intent(
            sender=sender,
            receiver=sender,
            value=None,
            execution_gas_limit=self._config.gas_limit_esdt_local_burn,
            data_parts=parts
        )

    def create_transaction_intent_for_updating_attributes(
        self,
        sender: IAddress,
        token_identifier: str,
        token_nonce: int,
        attributes: bytes
    ) -> TransactionIntent:
        parts: List[str] = [
            "ESDTNFTUpdateAttributes",
            arg_to_string(token_identifier),
            arg_to_string(token_nonce),
            arg_to_string(attributes)
        ]

        return self._create_transaction_intent(
            sender=sender,
            receiver=sender,
            value=None,
            execution_gas_limit=self._config.gas_limit_esdt_nft_update_attributes,
            data_parts=parts
        )

    def create_transaction_intent_for_adding_quantity(
        self,
        sender: IAddress,
        token_identifier: str,
        token_nonce: int,
        quantity_to_add: int
    ) -> TransactionIntent:
        parts: List[str] = [
            "ESDTNFTAddQuantity",
            arg_to_string(token_identifier),
            arg_to_string(token_nonce),
            arg_to_string(quantity_to_add)
        ]

        return self._create_transaction_intent(
            sender=sender,
            receiver=sender,
            value=None,
            execution_gas_limit=self._config.gas_limit_esdt_nft_add_quantity,
            data_parts=parts
        )

    def create_transaction_intent_for_burning_quantity(
        self,
        sender: IAddress,
        token_identifier: str,
        token_nonce: int,
        quantity_to_burn: int
    ) -> TransactionIntent:
        parts: List[str] = [
            "ESDTNFTBurn",
            arg_to_string(token_identifier),
            arg_to_string(token_nonce),
            arg_to_string(quantity_to_burn)
        ]

        return self._create_transaction_intent(
            sender=sender,
            receiver=sender,
            value=None,
            execution_gas_limit=self._config.gas_limit_esdt_nft_burn,
            data_parts=parts
        )

    def _create_transaction_intent(
        self,
        sender: IAddress,
        receiver: IAddress,
        value: Optional[int],
        execution_gas_limit: int,
        data_parts: List[str]
    ) -> TransactionIntent:
        payload = self._build_transaction_payload(data_parts)

        gas_limit = self._compute_gas_limit(payload, execution_gas_limit)

        transaction_intent = TransactionIntent()

        transaction_intent.sender = sender.bech32()
        transaction_intent.receiver = receiver.bech32()
        transaction_intent.gas_limit = gas_limit
        transaction_intent.data = str(payload).encode()
        transaction_intent.value = value if value else 0

        return transaction_intent

    def _build_transaction_payload(self, parts: List[str]) -> TransactionPayload:
        data = ARGS_SEPARATOR.join(parts)
        return TransactionPayload.from_str(data)

    def _compute_gas_limit(self, payload: TransactionPayload, execution_gas: int) -> int:
        data_movement_gas = self._config.min_gas_limit + self._config.gas_limit_per_byte * payload.length()
        gas = data_movement_gas + execution_gas

        return gas
