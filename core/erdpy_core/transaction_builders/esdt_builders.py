from typing import List, Optional, Protocol

from erdpy_core.interfaces import (IAddress, IGasLimit, IGasPrice, INonce,
                                   ITokenPayment, ITransactionValue)
from erdpy_core.serializer import arg_to_string, args_to_strings
from erdpy_core.transaction_builders.base_builder import (BaseBuilder,
                                                          IBaseConfiguration)


class IESDTIssueConfiguration(IBaseConfiguration, Protocol):
    gas_limit_esdt_issue: IGasLimit
    issue_cost: ITransactionValue
    esdt_contract_address: IAddress


class IESDTTransferConfiguration(IBaseConfiguration, Protocol):
    gas_limit_esdt_transfer: IGasLimit
    additional_gas_for_esdt_transfer: IGasLimit


class IESDTNFTTransferConfiguration(IBaseConfiguration, Protocol):
    gas_limit_esdt_nft_transfer: IGasLimit
    additional_gas_for_esdt_nft_transfer: IGasLimit


class ESDTIssueBuilder(BaseBuilder):
    def __init__(self,
                 config: IESDTIssueConfiguration,
                 issuer: IAddress,
                 token_name: str,
                 token_ticker: str,
                 initial_supply: int,
                 num_decimals: int,
                 can_freeze: bool = False,
                 can_wipe: bool = False,
                 can_pause: bool = False,
                 can_mint: bool = False,
                 can_burn: bool = False,
                 can_change_owner: bool = False,
                 can_upgrade: bool = False,
                 can_add_special_roles: bool = False,
                 nonce: Optional[INonce] = None,
                 value: Optional[ITransactionValue] = None,
                 gas_limit: Optional[IGasLimit] = None,
                 gas_price: Optional[IGasPrice] = None
                 ) -> None:
        super().__init__(config, nonce, value, gas_limit, gas_price)
        self.gas_limit_esdt_issue = config.gas_limit_esdt_issue

        self.sender = issuer
        self.receiver = config.esdt_contract_address
        self.value = config.issue_cost

        self.token_name = token_name
        self.token_ticker = token_ticker
        self.initial_supply = initial_supply
        self.num_decimals = num_decimals
        self.can_freeze = can_freeze
        self.can_wipe = can_wipe
        self.can_pause = can_pause
        self.can_mint = can_mint
        self.can_burn = can_burn
        self.can_change_owner = can_change_owner
        self.can_upgrade = can_upgrade
        self.can_add_special_roles = can_add_special_roles

    def _estimate_execution_gas(self) -> IGasLimit:
        return self.gas_limit_esdt_issue

    def _build_payload_parts(self) -> List[str]:
        return [
            "issue",
            arg_to_string(self.token_name),
            arg_to_string(self.token_ticker),
            arg_to_string(self.initial_supply),
            arg_to_string(self.num_decimals),
            *(args_to_strings(["canFreeze", "true"]) if self.can_freeze else []),
            *(args_to_strings(["canWipe", "true"]) if self.can_wipe else []),
            *(args_to_strings(["canPause", "true"]) if self.can_pause else []),
            *(args_to_strings(["canMint", "true"]) if self.can_mint else []),
            *(args_to_strings(["canBurn", "true"]) if self.can_burn else []),
            *(args_to_strings(["canChangeOwner", "true"]) if self.can_change_owner else []),
            *(args_to_strings(["canUpgrade", "true"]) if self.can_upgrade else []),
            *(args_to_strings(["canAddSpecialRoles", "true"]) if self.can_add_special_roles else [])
        ]


class ESDTTransferBuilder(BaseBuilder):
    def __init__(self,
                 config: IESDTTransferConfiguration,
                 sender: IAddress,
                 receiver: IAddress,
                 payment: ITokenPayment,
                 nonce: Optional[INonce] = None,
                 value: Optional[ITransactionValue] = None,
                 gas_limit: Optional[IGasLimit] = None,
                 gas_price: Optional[IGasPrice] = None
                 ) -> None:
        super().__init__(config, nonce, value, gas_limit, gas_price)
        self.gas_limit_esdt_transfer = config.gas_limit_esdt_transfer
        self.additional_gas_for_esdt_transfer = config.additional_gas_for_esdt_transfer

        self.sender = sender
        self.receiver = receiver
        self.payment = payment

    def _estimate_execution_gas(self) -> IGasLimit:
        return self.gas_limit_esdt_transfer + self.additional_gas_for_esdt_transfer

    def _build_payload_parts(self) -> List[str]:
        return [
            "ESDTTransfer",
            arg_to_string(self.payment.token_identifier),
            arg_to_string(self.payment.amount_as_integer)
        ]


class ESDTNFTTransferBuilder(BaseBuilder):
    def __init__(self,
                 config: IESDTNFTTransferConfiguration,
                 sender: IAddress,
                 destination: IAddress,
                 payment: ITokenPayment,
                 nonce: Optional[INonce] = None,
                 value: Optional[ITransactionValue] = None,
                 gas_limit: Optional[IGasLimit] = None,
                 gas_price: Optional[IGasPrice] = None
                 ) -> None:
        super().__init__(config, nonce, value, gas_limit, gas_price)
        self.gas_limit_esdt_nft_transfer = config.gas_limit_esdt_nft_transfer
        self.additional_gas_for_esdt_nft_transfer = config.additional_gas_for_esdt_nft_transfer

        self.sender = sender
        self.receiver = sender
        self.destination = destination
        self.payment = payment

    def _estimate_execution_gas(self) -> IGasLimit:
        return self.gas_limit_esdt_nft_transfer + self.additional_gas_for_esdt_nft_transfer

    def _build_payload_parts(self) -> List[str]:
        return [
            "ESDTNFTTransfer",
            arg_to_string(self.payment.token_identifier),
            arg_to_string(self.payment.token_nonce),
            arg_to_string(self.payment.amount_as_integer),
            arg_to_string(self.destination)
        ]


class MultiESDTNFTTransferBuilder(BaseBuilder):
    def __init__(self,
                 config: IESDTNFTTransferConfiguration,
                 sender: IAddress,
                 destination: IAddress,
                 payments: List[ITokenPayment],
                 nonce: Optional[INonce] = None,
                 value: Optional[ITransactionValue] = None,
                 gas_limit: Optional[IGasLimit] = None,
                 gas_price: Optional[IGasPrice] = None
                 ) -> None:
        super().__init__(config, nonce, value, gas_limit, gas_price)
        self.gas_limit_esdt_nft_transfer = config.gas_limit_esdt_nft_transfer
        self.additional_gas_for_esdt_nft_transfer = config.additional_gas_for_esdt_nft_transfer

        self.sender = sender
        self.receiver = sender
        self.destination = destination
        self.payments = payments

    def _estimate_execution_gas(self) -> IGasLimit:
        return (self.gas_limit_esdt_nft_transfer + self.additional_gas_for_esdt_nft_transfer) * len(self.payments)

    def _build_payload_parts(self) -> List[str]:
        parts = [
            "MultiESDTNFTTransfer",
            arg_to_string(self.destination),
            arg_to_string(len(self.payments))
        ]

        for payment in self.payments:
            parts.extend([
                arg_to_string(payment.token_identifier),
                arg_to_string(payment.token_nonce),
                arg_to_string(payment.amount_as_integer)
            ])

        return parts
