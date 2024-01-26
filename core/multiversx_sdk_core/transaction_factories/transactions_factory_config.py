from multiversx_sdk_core.address import DEFAULT_HRP, Address
from multiversx_sdk_core.interfaces import IAddress


class TransactionsFactoryConfig:
    def __init__(self, chain_id: str) -> None:
        # General-purpose configuration
        self.chain_id: str = chain_id
        self.address_hrp: str = DEFAULT_HRP
        self.min_gas_limit: int = 50_000
        self.gas_limit_per_byte: int = 1_500

        # Configuration for token operations
        self.gas_limit_issue: int = 60_000_000
        self.gas_limit_toggle_burn_role_globally: int = 60_000_000
        self.gas_limit_esdt_local_mint: int = 300_000
        self.gas_limit_esdt_local_burn: int = 300_000
        self.gas_limit_set_special_role: int = 60_000_000
        self.gas_limit_pausing: int = 60_000_000
        self.gas_limit_freezing: int = 60_000_000
        self.gas_limit_wiping: int = 60_000_000
        self.gas_limit_esdt_nft_create: int = 3_000_000
        self.gas_limit_esdt_nft_update_attributes: int = 1_000_000
        self.gas_limit_esdt_nft_add_quantity: int = 1_000_000
        self.gas_limit_esdt_nft_burn: int = 1_000_000
        self.gas_limit_store_per_byte: int = 50_000
        self.issue_cost: int = 50_000_000_000_000_000
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
