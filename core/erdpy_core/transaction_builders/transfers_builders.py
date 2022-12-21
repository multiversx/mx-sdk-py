from typing import List, Optional, Protocol, Sequence

from erdpy_core.interfaces import (IAddress, IGasLimit, IGasPrice, INonce,
                                   ITokenPayment, ITransactionValue)
from erdpy_core.serializer import arg_to_string
from erdpy_core.transaction_builders.transaction_builder import (
    ITransactionBuilderConfiguration, TransactionBuilder)


class IESDTTransferConfiguration(ITransactionBuilderConfiguration, Protocol):
    gas_limit_esdt_transfer: IGasLimit
    additional_gas_for_esdt_transfer: IGasLimit


class IESDTNFTTransferConfiguration(ITransactionBuilderConfiguration, Protocol):
    gas_limit_esdt_nft_transfer: IGasLimit
    additional_gas_for_esdt_nft_transfer: IGasLimit


class EGLDTransferBuilder(TransactionBuilder):
    def __init__(self,
                 config: ITransactionBuilderConfiguration,
                 sender: IAddress,
                 receiver: IAddress,
                 payment: ITokenPayment,
                 nonce: Optional[INonce] = None,
                 data: Optional[str] = None,
                 gas_limit: Optional[IGasLimit] = None,
                 gas_price: Optional[IGasPrice] = None
                 ) -> None:
        assert payment.is_egld()
        super().__init__(config, nonce, payment.amount_as_integer, gas_limit, gas_price)
        self.sender = sender
        self.receiver = receiver
        self.data = data

    def _estimate_execution_gas(self) -> IGasLimit:
        return 0

    def _build_payload_parts(self) -> List[str]:
        return [self.data] if self.data else []


class ESDTTransferBuilder(TransactionBuilder):
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


class ESDTNFTTransferBuilder(TransactionBuilder):
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


class MultiESDTNFTTransferBuilder(TransactionBuilder):
    def __init__(self,
                 config: IESDTNFTTransferConfiguration,
                 sender: IAddress,
                 destination: IAddress,
                 payments: Sequence[ITokenPayment],
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
