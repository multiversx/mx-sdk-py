from dataclasses import dataclass

from erdpy_core.address import Address
from erdpy_core.interfaces import (IAddress, IChainID, IGasPrice,
                                   ITransactionValue)


@dataclass
class DefaultTransactionBuildersConfiguration:
    chain_id: IChainID
    min_gas_price: IGasPrice = 1000000000
    min_gas_limit = 50000
    gas_limit_per_byte = 1500

    issue_cost: ITransactionValue = 50000000000000000
    gas_limit_esdt_issue = 60000000
    gas_limit_esdt_transfer = 200000
    gas_limit_esdt_nft_transfer = 200000
    additional_gas_for_esdt_transfer = 100000
    additional_gas_for_esdt_nft_transfer = 800000

    esdt_contract_address: IAddress = Address.from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u")
    deployment_address: IAddress = Address.from_bech32("erd1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq6gq4hu")
