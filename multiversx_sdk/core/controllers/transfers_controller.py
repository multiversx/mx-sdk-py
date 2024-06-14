from typing import Optional, Protocol, Sequence, Union

from multiversx_sdk.core.interfaces import IAddress
from multiversx_sdk.core.tokens import TokenTransfer
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transaction_computer import TransactionComputer
from multiversx_sdk.core.transactions_factories.transactions_factory_config import \
    TransactionsFactoryConfig
from multiversx_sdk.core.transactions_factories.transfer_transactions_factory import \
    TransferTransactionsFactory


class INetworkConfig(Protocol):
    chain_id: str


class INetworkProvider(Protocol):
    def get_network_config(self) -> INetworkConfig:
        ...


class IAccount(Protocol):
    address: IAddress

    def sign(self, data: bytes) -> bytes:
        ...


class TransfersController:
    def __init__(self, network_provider: INetworkProvider) -> None:
        self.chain_id: Union[str, None] = None
        self.factory: Union[TransferTransactionsFactory, None] = None
        self.provider = network_provider
        self.tx_computer = TransactionComputer()

    def create_transaction_for_native_token_transfer(self,
                                                     sender: IAccount,
                                                     nonce: int,
                                                     receiver: IAddress,
                                                     native_transfer_amount: int = 0,
                                                     data: Optional[bytes] = None) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_native_token_transfer(  # type: ignore
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
                                                   receiver: IAddress,
                                                   token_transfers: Sequence[TokenTransfer]) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_esdt_token_transfer(  # type: ignore
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
                                        receiver: IAddress,
                                        native_transfer_amount: Optional[int] = None,
                                        token_transfers: Optional[Sequence[TokenTransfer]] = None,
                                        data: Optional[bytes] = None) -> Transaction:
        self._ensure_factory_is_initialized()

        if native_transfer_amount and token_transfers:
            raise Exception("Can't send both native token and esdt tokens.")

        if native_transfer_amount:
            transaction = self.factory.create_transaction_for_native_token_transfer(  # type: ignore
                sender=sender.address,
                receiver=receiver,
                native_amount=native_transfer_amount,
                data=data.decode() if data else None
            )
        elif token_transfers:
            if data:
                raise Exception("Can't set data field when sending esdt tokens.")

            transaction = self.factory.create_transaction_for_esdt_token_transfer(  # type: ignore
                sender=sender.address,
                receiver=receiver,
                token_transfers=token_transfers
            )
        else:
            raise Exception("No native token amount provided or no token transfers provided.")

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def _ensure_factory_is_initialized(self):
        if self.factory is None:
            self.chain_id = self.provider.get_network_config().chain_id
            config = TransactionsFactoryConfig(self.chain_id)
            self.factory = TransferTransactionsFactory(config)
