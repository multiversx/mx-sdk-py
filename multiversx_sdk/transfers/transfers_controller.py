from typing import Optional

from multiversx_sdk.core import Address, TokenTransfer, Transaction
from multiversx_sdk.core.base_controller import BaseController
from multiversx_sdk.core.interfaces import IAccount
from multiversx_sdk.core.transactions_factory_config import TransactionsFactoryConfig
from multiversx_sdk.transfers.transfer_transactions_factory import (
    TransferTransactionsFactory,
)


class TransfersController(BaseController):
    def __init__(self, chain_id: str) -> None:
        self.factory = TransferTransactionsFactory(TransactionsFactoryConfig(chain_id))

    def create_transaction_for_native_token_transfer(
        self,
        sender: IAccount,
        nonce: int,
        receiver: Address,
        native_transfer_amount: int = 0,
        data: Optional[bytes] = None,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_native_token_transfer(
            sender=sender.address,
            receiver=receiver,
            native_amount=native_transfer_amount,
            data=data.decode() if data else None,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_esdt_token_transfer(
        self,
        sender: IAccount,
        nonce: int,
        receiver: Address,
        token_transfers: list[TokenTransfer],
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_esdt_token_transfer(
            sender=sender.address, receiver=receiver, token_transfers=token_transfers
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_transfer(
        self,
        sender: IAccount,
        nonce: int,
        receiver: Address,
        native_transfer_amount: Optional[int] = None,
        token_transfers: Optional[list[TokenTransfer]] = None,
        data: Optional[bytes] = None,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_transfer(
            sender=sender.address,
            receiver=receiver,
            native_amount=native_transfer_amount,
            token_transfers=token_transfers,
            data=data,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction
