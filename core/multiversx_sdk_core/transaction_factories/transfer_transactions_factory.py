from typing import List, Optional, Protocol, Sequence

from multiversx_sdk_core.errors import BadUsageError
from multiversx_sdk_core.interfaces import IAddress, IToken, ITokenTransfer
from multiversx_sdk_core.transaction import Transaction
from multiversx_sdk_core.transaction_factories.token_transfers_data_builder import \
    TokenTransfersDataBuilder
from multiversx_sdk_core.transaction_factories.transaction_builder import \
    TransactionBuilder

ADDITIONAL_GAS_FOR_ESDT_TRANSFER = 100000
ADDITIONAL_GAS_FOR_ESDT_NFT_TRANSFER = 800000


class IConfig(Protocol):
    chain_id: str
    min_gas_limit: int
    gas_limit_per_byte: int
    gas_limit_esdt_transfer: int
    gas_limit_esdt_nft_transfer: int
    gas_limit_multi_esdt_nft_transfer: int


class ITokenComputer(Protocol):
    def is_fungible(self, token: IToken) -> bool:
        ...

    def extract_identifier_from_extended_identifier(self, identifier: str) -> str:
        ...


class TransferTransactionsFactory:
    def __init__(self, config: IConfig, token_computer: ITokenComputer) -> None:
        self.config = config
        self.token_computer = token_computer
        self._data_args_builder = TokenTransfersDataBuilder(token_computer)

    def create_transaction_for_native_token_transfer(self,
                                                     sender: IAddress,
                                                     receiver: IAddress,
                                                     native_amount: int,
                                                     data: Optional[str] = None) -> Transaction:
        transaction_data = data if data else ""
        return TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=receiver,
            data_parts=[transaction_data],
            gas_limit=0,
            add_data_movement_gas=True,
            amount=native_amount
        ).build()

    def create_transaction_for_esdt_token_transfer(self,
                                                   sender: IAddress,
                                                   receiver: IAddress,
                                                   token_transfers: Sequence[ITokenTransfer]) -> Transaction:
        data_parts: List[str] = []
        extra_gas_for_transfer = 0

        if len(token_transfers) == 0:
            raise BadUsageError("No token transfer has been provided")
        elif len(token_transfers) == 1:
            transfer = token_transfers[0]

            if self.token_computer.is_fungible(transfer.token):
                data_parts = self._data_args_builder.build_args_for_esdt_transfer(transfer)
                extra_gas_for_transfer = self.config.gas_limit_esdt_transfer + ADDITIONAL_GAS_FOR_ESDT_TRANSFER
            else:
                data_parts = self._data_args_builder.build_args_for_single_esdt_nft_transfer(transfer, receiver)
                extra_gas_for_transfer = self.config.gas_limit_esdt_nft_transfer + ADDITIONAL_GAS_FOR_ESDT_NFT_TRANSFER
                receiver = sender
        else:
            data_parts = self._data_args_builder.build_args_for_multi_esdt_nft_transfer(receiver, token_transfers)
            extra_gas_for_transfer = self.config.gas_limit_multi_esdt_nft_transfer * len(token_transfers) + ADDITIONAL_GAS_FOR_ESDT_NFT_TRANSFER
            receiver = sender

        return TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=receiver,
            data_parts=data_parts,
            gas_limit=extra_gas_for_transfer,
            add_data_movement_gas=True
        ).build()
