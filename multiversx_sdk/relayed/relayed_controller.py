from multiversx_sdk.core import Transaction, TransactionComputer
from multiversx_sdk.core.interfaces import IAccount
from multiversx_sdk.core.transactions_factory_config import \
    TransactionsFactoryConfig
from multiversx_sdk.relayed.relayed_transactions_factory import \
    RelayedTransactionsFactory


class RelayedController:
    """The transactions are created from the perspective of the relayer. The 'sender' represents the relayer."""

    def __init__(self, chain_id: str) -> None:
        self.factory = RelayedTransactionsFactory(TransactionsFactoryConfig(chain_id))
        self.tx_computer = TransactionComputer()

    def create_relayed_v1_transaction(self,
                                      sender: IAccount,
                                      nonce: int,
                                      inner_transaction: Transaction) -> Transaction:
        transaction = self.factory.create_relayed_v1_transaction(
            inner_transaction=inner_transaction,
            relayer_address=sender.address
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_relayed_v2_transaction(self,
                                      sender: IAccount,
                                      nonce: int,
                                      inner_transaction: Transaction,
                                      inner_transaction_gas_limit: int) -> Transaction:
        transaction = self.factory.create_relayed_v2_transaction(
            inner_transaction=inner_transaction,
            inner_transaction_gas_limit=inner_transaction_gas_limit,
            relayer_address=sender.address
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction
