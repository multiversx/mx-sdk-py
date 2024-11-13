from typing import Optional

from multiversx_sdk.core import (Address, TokenTransfer, Transaction,
                                 TransactionComputer)
from multiversx_sdk.core.interfaces import IAccount
from multiversx_sdk.core.transactions_factory_config import \
    TransactionsFactoryConfig
from multiversx_sdk.transfers.transfer_transactions_factory import \
    TransferTransactionsFactory


class TransfersController:
    def __init__(self, chain_id: str) -> None:
        self.factory = TransferTransactionsFactory(TransactionsFactoryConfig(chain_id))
        self.tx_computer = TransactionComputer()

    def create_transaction_for_native_token_transfer(self,
                                                     sender: IAccount,
                                                     nonce: int,
                                                     receiver: Address,
                                                     native_transfer_amount: int = 0,
                                                     data: Optional[bytes] = None) -> Transaction:
        transaction = self.factory.create_transaction_for_native_token_transfer(
            sender=sender.address,
            receiver=receiver,
            native_amount=native_transfer_amount,
            data=data.decode() if data else None
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_esdt_token_transfer(self,
                                                   sender: IAccount,
                                                   nonce: int,
                                                   receiver: Address,
                                                   token_transfers: list[TokenTransfer]) -> Transaction:
        transaction = self.factory.create_transaction_for_esdt_token_transfer(
            sender=sender.address,
            receiver=receiver,
            token_transfers=token_transfers
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_transfer(self,
                                        sender: IAccount,
                                        nonce: int,
                                        receiver: Address,
                                        native_transfer_amount: Optional[int] = None,
                                        token_transfers: Optional[list[TokenTransfer]] = None,
                                        data: Optional[bytes] = None) -> Transaction:
        transaction = self.factory.create_transaction_for_transfer(
            sender=sender.address,
            receiver=receiver,
            native_amount=native_transfer_amount,
            token_transfers=token_transfers,
            data=data
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction