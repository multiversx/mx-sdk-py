from multiversx_sdk.core.interfaces import IAccount
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transaction_computer import TransactionComputer


class BaseController:
    """This is the base class for all controllers. **Internal use only**."""

    def _set_version_and_options_for_hash_signing(self, sender: IAccount, transaction: Transaction):
        """If the Account has the `use_hash_signing` flag set to `True`, this method will set the correct `version` and `options` properties of `Transaction`."""
        if sender.use_hash_signing:
            transaction_computer = TransactionComputer()
            transaction_computer.apply_options_for_hash_signing(transaction)
