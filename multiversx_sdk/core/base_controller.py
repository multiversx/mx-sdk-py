from typing import Optional

from multiversx_sdk.core.constants import (
    EXTRA_GAS_LIMIT_FOR_GUARDED_TRANSACTIONS,
    EXTRA_GAS_LIMIT_FOR_RELAYED_TRANSACTIONS,
)
from multiversx_sdk.core.interfaces import IAccount
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transaction_computer import TransactionComputer


class BaseController:
    """This is the base class for all controllers. **Internal use only.**"""

    def _set_version_and_options_for_hash_signing(self, sender: IAccount, transaction: Transaction):
        """If the Account has the `use_hash_signing` flag set to `True`, this method will set the correct `version` and `options` properties of `Transaction`."""
        if sender.use_hash_signing:
            transaction_computer = TransactionComputer()
            transaction_computer.apply_options_for_hash_signing(transaction)

    def _add_extra_gas_limit_if_required(self, transaction: Transaction):
        """In case of guarded or relayed transactions, extra gas limit is added."""
        if transaction.guardian:
            transaction.gas_limit += EXTRA_GAS_LIMIT_FOR_GUARDED_TRANSACTIONS

        if transaction.relayer:
            transaction.gas_limit += EXTRA_GAS_LIMIT_FOR_RELAYED_TRANSACTIONS

    def _set_transaction_gas_options(
        self,
        transaction: Transaction,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ):
        if gas_price:
            transaction.gas_price = gas_price

        if gas_limit:
            transaction.gas_limit = gas_limit
        else:
            self._add_extra_gas_limit_if_required(transaction)

    def _set_version_and_options_for_guardian(self, transaction: Transaction):
        if transaction.guardian:
            transaction_computer = TransactionComputer()
            transaction_computer.apply_guardian(transaction, transaction.guardian)
