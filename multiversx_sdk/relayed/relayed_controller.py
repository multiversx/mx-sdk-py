import logging

from multiversx_sdk.core import Transaction
from multiversx_sdk.core.base_controller import BaseController
from multiversx_sdk.core.interfaces import IAccount
from multiversx_sdk.core.transactions_factory_config import TransactionsFactoryConfig
from multiversx_sdk.relayed.relayed_transactions_factory import (
    RelayedTransactionsFactory,
)

logger = logging.getLogger("relayed_controller")


class RelayedController(BaseController):
    """
    The Relayed Transactions V1 and V2 will soon be deprecated from the network. Please use Relayed Transactions V3 instead.
    The transactions are created from the perspective of the relayer. The 'sender' represents the relayer.
    """

    def __init__(self, chain_id: str) -> None:
        logger.warning("RelayedController is deprecated. Please use Relayed Transactions V3 instead.")
        self.factory = RelayedTransactionsFactory(TransactionsFactoryConfig(chain_id))

    def create_relayed_v1_transaction(
        self, sender: IAccount, nonce: int, inner_transaction: Transaction
    ) -> Transaction:
        transaction = self.factory.create_relayed_v1_transaction(
            inner_transaction=inner_transaction, relayer_address=sender.address
        )

        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._add_extra_gas_limit_if_required(transaction)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_relayed_v2_transaction(
        self,
        sender: IAccount,
        nonce: int,
        inner_transaction: Transaction,
        inner_transaction_gas_limit: int,
    ) -> Transaction:
        transaction = self.factory.create_relayed_v2_transaction(
            inner_transaction=inner_transaction,
            inner_transaction_gas_limit=inner_transaction_gas_limit,
            relayer_address=sender.address,
        )

        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._add_extra_gas_limit_if_required(transaction)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction
