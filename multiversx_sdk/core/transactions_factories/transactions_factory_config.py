from multiversx_sdk.core.address import Address
from multiversx_sdk.core.constants import DEFAULT_HRP
from multiversx_sdk.core.interfaces import IAddress


class TransactionsFactoryConfig:
    def __init__(self, chain_id: str) -> None:
        # General-purpose configuration
        self.chain_id = chain_id
        self.address_hrp = DEFAULT_HRP
        self.min_gas_limit = 50_000
        self.gas_limit_per_byte = 1_500

        # Configuration for token operations
        self.gas_limit_issue = 60_000_000
        self.gas_limit_toggle_burn_role_globally = 60_000_000
        self.gas_limit_esdt_local_mint = 300_000
        self.gas_limit_esdt_local_burn = 300_000
        self.gas_limit_set_special_role = 60_000_000
        self.gas_limit_pausing = 60_000_000
        self.gas_limit_freezing = 60_000_000
        self.gas_limit_wiping = 60_000_000
        self.gas_limit_esdt_nft_create = 3_000_000
        self.gas_limit_esdt_nft_update_attributes = 1_000_000
        self.gas_limit_esdt_nft_add_quantity = 1_000_000
        self.gas_limit_esdt_nft_burn = 1_000_000
        self.gas_limit_store_per_byte = 10_000
        self.gas_limit_esdt_modify_royalties = 60_000_000
        self.gas_limit_set_new_uris = 60_000_000
        self.gas_limit_esdt_modify_creator = 60_000_000
        self.gas_limit_esdt_metadata_update = 60_000_000
        self.gas_limit_nft_metadata_recreate = 60_000_000
        self.gas_limit_nft_change_to_dynamic = 60_000_000
        self.gas_limit_update_token_id = 60_000_000
        self.gas_limit_register_dynamic = 60_000_000
        self.issue_cost = 50_000_000_000_000_000
        self.esdt_contract_address: IAddress = Address.new_from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u")

        # Configuration for delegation operations
        self.gas_limit_stake = 5_000_000
        self.gas_limit_unstake = 5_000_000
        self.gas_limit_unbond = 5_000_000
        self.gas_limit_create_delegation_contract = 50_000_000
        self.gas_limit_delegation_operations = 1_000_000
        self.additional_gas_limit_per_validator_node = 6_000_000
        self.additional_gas_for_delegation_operations = 10_000_000

        # Configuration for token transfers
        self.gas_limit_esdt_transfer = 200_000
        self.gas_limit_esdt_nft_transfer = 200_000
        self.gas_limit_multi_esdt_nft_transfer = 200_000

        # Configuration for account operations
        self.gas_limit_save_key_value = 100_000
        self.gas_limit_persist_per_byte = 1_000
        self.gas_limit_set_guardian = 250_000
        self.gas_limit_guard_account = 250_000
        self.gas_limit_unguard_account = 250_000

        # Configuration for smart contract operations
        self.gas_limit_claim_developer_rewards = 6_000_000
        self.gas_limit_change_owner_address = 6_000_000
