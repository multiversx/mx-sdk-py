from multiversx_sdk_core.address import DEFAULT_HRP, Address
from multiversx_sdk_core.interfaces import (IAddress, IChainID, IGasLimit,
                                            ITransactionValue)


class TransactionFactoryConfig:
    def __init__(self, chain_id: IChainID) -> None:
        # General-purpose configuration
        self.chain_id: IChainID = chain_id
        self.address_hrp: str = DEFAULT_HRP
        self.min_gas_limit: IGasLimit = 50_000
        self.gas_limit_per_byte: IGasLimit = 1_500

        # Configuration for token operations
        self.gas_limit_issue: IGasLimit = 60_000_000
        self.gas_limit_toggle_burn_role_globally: IGasLimit = 60_000_000
        self.gas_limit_esdt_local_mint: IGasLimit = 300_000
        self.gas_limit_esdt_local_burn: IGasLimit = 300_000
        self.gas_limit_set_special_role: IGasLimit = 60_000_000
        self.gas_limit_pausing: IGasLimit = 60_000_000
        self.gas_limit_freezing: IGasLimit = 60_000_000
        self.gas_limit_wiping: IGasLimit = 60_000_000
        self.gas_limit_esdt_nft_create: IGasLimit = 3_000_000
        self.gas_limit_esdt_nft_update_attributes: IGasLimit = 1_000_000
        self.gas_limit_esdt_nft_add_quantity: IGasLimit = 1_000_000
        self.gas_limit_esdt_nft_burn: IGasLimit = 1_000_000
        self.gas_limit_store_per_byte: IGasLimit = 50_000
        self.issue_cost: ITransactionValue = 50_000_000_000_000_000
        self.esdt_contract_address: IAddress = Address.from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u")

        # Configuration for delegation operations
        self.gas_limit_stake = 5_000_000
        self.gas_limit_unstake = 5_000_000
        self.gas_limit_unbond = 5_000_000
        self.gas_limit_create_delegation_contract = 50_000_000
        self.gas_limit_delegation_operations = 1_000_000
        self.additional_gas_limit_per_validator_node = 6_000_000
        self.additional_gas_for_delegation_operations = 10_000_000
