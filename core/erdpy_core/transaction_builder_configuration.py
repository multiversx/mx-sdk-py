from erdpy_core.address import Address
from erdpy_core.interfaces import (IAddress, IGasLimit, IGasPrice,
                                   ITransactionBuildersConfiguration,
                                   ITransactionOptions, ITransactionValue,
                                   ITransactionVersion)


class DefaultTransactionBuildersConfiguration(ITransactionBuildersConfiguration):
    def __init__(self) -> None:
        self.gas_price: IGasPrice = 1000000000
        self.gas_limit_esdt_issue: IGasLimit = 60000000
        self.gas_limit_esdt_local_mint: IGasLimit = 300000
        self.gas_limit_esdt_local_burn: IGasLimit = 300000
        self.gas_limit_set_special_role: IGasLimit = 60000000
        self.gas_limit_pausing: IGasLimit = 60000000
        self.gas_limit_freezing: IGasLimit = 60000000
        self.issue_cost: ITransactionValue = 50000000000000000
        self.transaction_version: ITransactionVersion = 1
        self.transaction_options: ITransactionOptions = 0

        self.deployment_address: IAddress = Address.from_bech32("erd1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq6gq4hu")
        self.esdt_contract_address: IAddress = Address.from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u")
