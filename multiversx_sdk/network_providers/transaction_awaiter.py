import time
from typing import Callable, Optional, Protocol, Union

from multiversx_sdk.network_providers.errors import (
    ExpectedTransactionStatusNotReached, IsCompletedFieldMissingOnTransaction)
from multiversx_sdk.network_providers.transactions import TransactionOnNetwork

ONE_SECOND_IN_MILLISECONDS = 1000


class ITransactionFetcher(Protocol):
    def get_transaction(self, tx_hash: str) -> TransactionOnNetwork:
        ...


class TransactionAwaiter:
    """TransactionAwaiter allows one to await until a specific event (such as transaction completion) occurs on a given transaction."""
    default_polling_interval = 6000
    default_timeout = default_polling_interval * 15
    default_patience = 0

    def __init__(self,
                 fetcher: ITransactionFetcher,
                 polling_interval_in_milliseconds: Optional[int] = None,
                 timeout_interval_in_milliseconds: Optional[int] = None,
                 patience_time_in_milliseconds: Optional[int] = None) -> None:
        """
        Args:
            fetcher (ITransactionFetcher): Used to fetch the transaction of the network.
            polling_interval_in_milliseconds (Optional[int]): The polling interval, in milliseconds.
            timeout_interval_in_milliseconds (Optional[int]): The timeout, in milliseconds.
            patience_time_in_milliseconds (Optional[int]): The patience, an extra time (in milliseconds) to wait, after the transaction has reached its desired status. Currently there's a delay between the moment a transaction is marked as "completed" and the moment its outcome (contract results, events and logs) is available.
        """
        self.fetcher = fetcher

        if polling_interval_in_milliseconds is None:
            self.polling_interval_in_milliseconds = TransactionAwaiter.default_polling_interval
        else:
            self.polling_interval_in_milliseconds = polling_interval_in_milliseconds

        if timeout_interval_in_milliseconds is None:
            self.timeout_interval_in_milliseconds = TransactionAwaiter.default_timeout
        else:
            self.timeout_interval_in_milliseconds = timeout_interval_in_milliseconds

        if patience_time_in_milliseconds is None:
            self.patience_time_in_milliseconds = TransactionAwaiter.default_patience
        else:
            self.patience_time_in_milliseconds = patience_time_in_milliseconds

    def await_completed(self, tx_hash: str) -> TransactionOnNetwork:
        """Waits until the transaction is completely processed."""
        def is_completed(tx: TransactionOnNetwork):
            if tx.is_completed is None:
                raise IsCompletedFieldMissingOnTransaction()

            return tx.is_completed

        def do_fetch():
            return self.fetcher.get_transaction(tx_hash)

        return self._await_conditionally(
            is_satisfied=is_completed,
            do_fetch=do_fetch,
            error=ExpectedTransactionStatusNotReached()
        )

    def await_on_condition(self, tx_hash: str, condition: Callable[[TransactionOnNetwork], bool]) -> TransactionOnNetwork:
        """Waits until the condition is satisfied."""
        def do_fetch():
            return self.fetcher.get_transaction(tx_hash)

        return self._await_conditionally(
            is_satisfied=condition,
            do_fetch=do_fetch,
            error=ExpectedTransactionStatusNotReached()
        )

    def _await_conditionally(self,
                             is_satisfied: Callable[[TransactionOnNetwork], bool],
                             do_fetch: Callable[[], TransactionOnNetwork],
                             error: Exception) -> TransactionOnNetwork:
        is_condition_satisfied = False
        fetched_data: Union[TransactionOnNetwork, None] = None
        max_number_of_retries = self.timeout_interval_in_milliseconds // self.polling_interval_in_milliseconds

        number_of_retries = 0
        while number_of_retries < max_number_of_retries:
            try:
                fetched_data = do_fetch()
                is_condition_satisfied = is_satisfied(fetched_data)

                if is_condition_satisfied:
                    break
            except Exception as ex:
                raise ex

            number_of_retries += 1
            time.sleep(self.polling_interval_in_milliseconds / ONE_SECOND_IN_MILLISECONDS)

        if fetched_data is None or not is_condition_satisfied:
            raise error

        if self.patience_time_in_milliseconds:
            time.sleep(self.patience_time_in_milliseconds / ONE_SECOND_IN_MILLISECONDS)
            return do_fetch()

        return fetched_data
