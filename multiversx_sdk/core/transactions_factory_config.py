from dataclasses import dataclass, field

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.config import LibraryConfig
from multiversx_sdk.core.constants import ESDT_CONTRACT_ADDRESS_HEX


@dataclass
class TransactionsFactoryConfig:
    # General-purpose configuration
    chain_id: str
    address_hrp: str = LibraryConfig.default_address_hrp
    min_gas_limit: int = 50_000
    gas_limit_per_byte: int = 1_500

    # Configuration for token operations
    gas_limit_issue: int = 60_000_000
    gas_limit_toggle_burn_role_globally: int = 60_000_000
    gas_limit_esdt_local_mint: int = 300_000
    gas_limit_esdt_local_burn: int = 300_000
    gas_limit_set_special_role: int = 60_000_000
    gas_limit_pausing: int = 60_000_000
    gas_limit_freezing: int = 60_000_000
    gas_limit_wiping: int = 60_000_000
    gas_limit_esdt_nft_create: int = 3_000_000
    gas_limit_esdt_nft_update_attributes: int = 50_000
    gas_limit_esdt_nft_add_quantity: int = 50_000
    gas_limit_esdt_nft_burn: int = 50_000
    gas_limit_store_per_byte: int = 10_000
    gas_limit_esdt_modify_royalties: int = 60_000_000
    gas_limit_set_new_uris: int = 60_000_000
    gas_limit_esdt_modify_creator: int = 60_000_000
    gas_limit_esdt_metadata_update: int = 60_000_000
    gas_limit_nft_metadata_recreate: int = 60_000_000
    gas_limit_nft_change_to_dynamic: int = 60_000_000
    gas_limit_update_token_id: int = 60_000_000
    gas_limit_register_dynamic: int = 60_000_000
    issue_cost: int = 50_000_000_000_000_000
    gas_limit_transfer_ownership: int = 60_000_000
    gas_limit_freeze_single_nft: int = 60_000_000
    gas_limit_unfreeze_single_nft: int = 60_000_000
    gas_limit_change_sft_to_meta_esdt: int = 60_000_000
    gas_limit_transfer_nft_create_role: int = 60_000_000
    gas_limit_stop_nft_create: int = 60_000_000
    gas_limit_wipe_single_nft: int = 60_000_000
    gas_limit_esdt_nft_add_uri: int = 10_000_000
    esdt_contract_address: Address = field(
        default_factory=lambda: Address.new_from_hex(value=ESDT_CONTRACT_ADDRESS_HEX)
    )

    # Configuration for delegation operations
    gas_limit_stake: int = 5_000_000
    gas_limit_unstake: int = 5_000_000
    gas_limit_unbond: int = 5_000_000
    gas_limit_create_delegation_contract: int = 50_000_000
    gas_limit_delegation_operations: int = 1_000_000
    additional_gas_limit_per_validator_node: int = 6_000_000
    additional_gas_for_delegation_operations: int = 10_000_000

    # Configuration for token transfers
    gas_limit_esdt_transfer: int = 200_000
    gas_limit_esdt_nft_transfer: int = 200_000
    gas_limit_multi_esdt_nft_transfer: int = 200_000

    # Configuration for account operations
    gas_limit_save_key_value: int = 100_000
    gas_limit_persist_per_byte: int = 1_000
    gas_limit_set_guardian: int = 250_000
    gas_limit_guard_account: int = 250_000
    gas_limit_unguard_account: int = 250_000

    # Configuration for smart contract operations
    gas_limit_claim_developer_rewards: int = 6_000_000
    gas_limit_change_owner_address: int = 6_000_000

    # Configuration for staking
    gas_limit_for_staking: int = 5_000_000
    gas_limit_for_topping_up: int = 5_000_000
    gas_limit_for_unstaking: int = 5_000_000
    gas_limit_for_unjailing: int = 5_000_000
    gas_limit_for_unbonding: int = 5_000_000
    gas_limit_for_changing_rewards_address: int = 5_000_000
    gas_limit_for_claiming: int = 5_000_000
    gas_limit_for_unstaking_nodes: int = 5_000_000
    gas_limit_for_unstaking_tokens: int = 5_000_000
    gas_limit_for_unbonding_nodes: int = 5_000_000
    gas_limit_for_unbonding_tokens: int = 5_000_000
    gas_limit_for_cleaning_registered_data: int = 5_000_000
    gas_limit_for_restaking_unstaked_tokens: int = 5_000_000
