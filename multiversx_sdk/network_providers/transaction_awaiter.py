import logging
import time
from typing import Callable, Optional, Protocol, Union

from multiversx_sdk.core.transaction_on_network import TransactionOnNetwork
from multiversx_sdk.network_providers.constants import (
    DEFAULT_TRANSACTION_AWAITING_PATIENCE_IN_MILLISECONDS,
    DEFAULT_TRANSACTION_AWAITING_POLLING_TIMEOUT_IN_MILLISECONDS,
    DEFAULT_TRANSACTION_AWAITING_TIMEOUT_IN_MILLISECONDS,
    ONE_SECOND_IN_MILLISECONDS,
)
from multiversx_sdk.network_providers.errors import (
    ExpectedTransactionStatusNotReachedError,
    TransactionFetchingError,
)

logger = logging.getLogger("transaction_awaiter")


class ITransactionFetcher(Protocol):
    def get_transaction(self, transaction_hash: Union[bytes, str]) -> TransactionOnNetwork: ...


class TransactionAwaiter:
    """TransactionAwaiter allows one to await until a specific event (such as transaction completion) occurs on a given transaction."""

    def __init__(
        self,
        fetcher: ITransactionFetcher,
        polling_interval_in_milliseconds: Optional[int] = None,
        timeout_interval_in_milliseconds: Optional[int] = None,
        patience_time_in_milliseconds: Optional[int] = None,
    ) -> None:
        """
        Args:
            fetcher (ITransactionFetcher): Used to fetch the transaction of the network.
            polling_interval_in_milliseconds (Optional[int]): The polling interval, in milliseconds.
            timeout_interval_in_milliseconds (Optional[int]): The timeout, in milliseconds.
            patience_time_in_milliseconds (Optional[int]): The patience, an extra time (in milliseconds) to wait, after the transaction has reached its desired status. Currently there's a delay between the moment a transaction is marked as "completed" and the moment its outcome (contract results, events and logs) is available.
        """
        self.fetcher = fetcher

        if polling_interval_in_milliseconds is None:
            self.polling_interval_in_milliseconds = DEFAULT_TRANSACTION_AWAITING_POLLING_TIMEOUT_IN_MILLISECONDS
        else:
            self.polling_interval_in_milliseconds = polling_interval_in_milliseconds

        if timeout_interval_in_milliseconds is None:
            self.timeout_interval_in_milliseconds = DEFAULT_TRANSACTION_AWAITING_TIMEOUT_IN_MILLISECONDS
        else:
            self.timeout_interval_in_milliseconds = timeout_interval_in_milliseconds

        if patience_time_in_milliseconds is None:
            self.patience_time_in_milliseconds = DEFAULT_TRANSACTION_AWAITING_PATIENCE_IN_MILLISECONDS
        else:
            self.patience_time_in_milliseconds = patience_time_in_milliseconds

    def await_completed(self, transaction_hash: Union[str, bytes]) -> TransactionOnNetwork:
        """Waits until the transaction is completely processed."""

        def is_completed(tx: TransactionOnNetwork):
            return tx.status.is_completed

        def do_fetch():
            return self.fetcher.get_transaction(transaction_hash)

        return self._await_conditionally(
            is_satisfied=is_completed,
            do_fetch=do_fetch,
            error=ExpectedTransactionStatusNotReachedError(),
        )

    def await_on_condition(
        self,
        transaction_hash: Union[str, bytes],
        condition: Callable[[TransactionOnNetwork], bool],
    ) -> TransactionOnNetwork:
        """Waits until the condition is satisfied."""

        def do_fetch():
            return self.fetcher.get_transaction(transaction_hash)

        return self._await_conditionally(
            is_satisfied=condition,
            do_fetch=do_fetch,
            error=ExpectedTransactionStatusNotReachedError(),
        )

    def _await_conditionally(
        self,
        is_satisfied: Callable[[TransactionOnNetwork], bool],
        do_fetch: Callable[[], TransactionOnNetwork],
        error: Exception,
    ) -> TransactionOnNetwork:
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
            except TransactionFetchingError:
                logger.warning("Couldn't fetch transaction. Retrying...")
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
