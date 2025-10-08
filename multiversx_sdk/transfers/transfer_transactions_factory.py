from typing import Optional

from multiversx_sdk.abi.serializer import Serializer
from multiversx_sdk.abi.string_value import StringValue
from multiversx_sdk.builders.token_transfers_data_builder import (
    TokenTransfersDataBuilder,
)
from multiversx_sdk.core import Address, TokenComputer, TokenTransfer, Transaction
from multiversx_sdk.core.base_factory import BaseFactory
from multiversx_sdk.core.constants import EGLD_IDENTIFIER_FOR_MULTI_ESDTNFT_TRANSFER
from multiversx_sdk.core.errors import BadUsageError
from multiversx_sdk.core.interfaces import IGasLimitEstimator
from multiversx_sdk.core.transactions_factory_config import TransactionsFactoryConfig

ADDITIONAL_GAS_FOR_ESDT_TRANSFER = 100000
ADDITIONAL_GAS_FOR_ESDT_NFT_TRANSFER = 800000


class TransferTransactionsFactory(BaseFactory):
    def __init__(
        self,
        config: TransactionsFactoryConfig,
        gas_limit_estimator: Optional[IGasLimitEstimator] = None,
    ) -> None:
        super().__init__(config, gas_limit_estimator)
        self.config = config
        self.token_computer = TokenComputer()
        self._data_args_builder = TokenTransfersDataBuilder(self.token_computer)

    def create_transaction_for_native_token_transfer(
        self,
        sender: Address,
        receiver: Address,
        native_amount: int,
        data: Optional[str] = None,
    ) -> Transaction:
        transaction_data = data if data else ""

        transaction = Transaction(
            sender=sender,
            receiver=receiver,
            gas_limit=0,
            chain_id=self.config.chain_id,
            value=native_amount,
        )

        self.set_payload(transaction, [transaction_data])
        self.set_gas_limit(transaction=transaction, config_gas_limit=0)

        return transaction

    def create_transaction_for_esdt_token_transfer(
        self,
        sender: Address,
        receiver: Address,
        token_transfers: list[TokenTransfer],
        data: Optional[bytes] = None,
    ) -> Transaction:
        if not token_transfers:
            raise BadUsageError("No token transfer has been provided")

        if len(token_transfers) == 1:
            data_parts, extra_gas_for_transfer, receiver = self._single_transfer(sender, receiver, token_transfers[0])
        else:
            data_parts, extra_gas_for_transfer, receiver = self._multi_transfer(sender, receiver, token_transfers)

        if data:
            serializer = Serializer()
            data_parts.append(serializer.serialize([StringValue(data.decode())]))

        transaction = Transaction(
            sender=sender,
            receiver=receiver,
            gas_limit=0,
            chain_id=self.config.chain_id,
        )

        self.set_payload(transaction, data_parts)
        self.set_gas_limit(transaction=transaction, config_gas_limit=extra_gas_for_transfer)

        return transaction

    def _single_transfer(
        self, sender: Address, receiver: Address, transfer: TokenTransfer
    ) -> tuple[list[str], int, Address]:
        if self.token_computer.is_fungible(transfer.token):
            if transfer.token.identifier == EGLD_IDENTIFIER_FOR_MULTI_ESDTNFT_TRANSFER:
                data_parts = self._data_args_builder.build_args_for_multi_esdt_nft_transfer(receiver, [transfer])
                gas = self.config.gas_limit_multi_esdt_nft_transfer + ADDITIONAL_GAS_FOR_ESDT_NFT_TRANSFER
                return data_parts, gas, sender
            else:
                data_parts = self._data_args_builder.build_args_for_esdt_transfer(transfer)
                gas = self.config.gas_limit_esdt_transfer + ADDITIONAL_GAS_FOR_ESDT_TRANSFER
                return data_parts, gas, receiver

        data_parts = self._data_args_builder.build_args_for_single_esdt_nft_transfer(transfer, receiver)
        gas = self.config.gas_limit_esdt_nft_transfer + ADDITIONAL_GAS_FOR_ESDT_NFT_TRANSFER
        return data_parts, gas, sender

    def _multi_transfer(
        self, sender: Address, receiver: Address, token_transfers: list[TokenTransfer]
    ) -> tuple[list[str], int, Address]:
        data_parts = self._data_args_builder.build_args_for_multi_esdt_nft_transfer(receiver, token_transfers)
        gas = (
            self.config.gas_limit_multi_esdt_nft_transfer * len(token_transfers) + ADDITIONAL_GAS_FOR_ESDT_NFT_TRANSFER
        )
        return data_parts, gas, sender

    def create_transaction_for_transfer(
        self,
        sender: Address,
        receiver: Address,
        native_amount: Optional[int] = None,
        token_transfers: Optional[list[TokenTransfer]] = None,
        data: Optional[bytes] = None,
    ) -> Transaction:
        if (native_amount or data) and not token_transfers:
            native_amount = native_amount if native_amount else 0
            return self.create_transaction_for_native_token_transfer(
                sender=sender,
                receiver=receiver,
                native_amount=native_amount,
                data=data.decode() if data else None,
            )

        token_transfers = list(token_transfers) if token_transfers else []

        if native_amount:
            native_transfer = TokenTransfer.new_from_native_amount(native_amount)
            token_transfers.append(native_transfer)

        return self.create_transaction_for_esdt_token_transfer(
            sender=sender,
            receiver=receiver,
            token_transfers=token_transfers,
            data=data,
        )
