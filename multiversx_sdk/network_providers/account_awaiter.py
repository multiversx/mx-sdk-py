import logging
import time
from typing import Callable, Optional, Protocol, Union

from multiversx_sdk.core.address import Address
from multiversx_sdk.network_providers.constants import (
    DEFAULT_ACCOUNT_AWAITING_PATIENCE_IN_MILLISECONDS,
    DEFAULT_ACCOUNT_AWAITING_POLLING_TIMEOUT_IN_MILLISECONDS,
    DEFAULT_ACCOUNT_AWAITING_TIMEOUT_IN_MILLISECONDS,
    ONE_SECOND_IN_MILLISECONDS,
)
from multiversx_sdk.network_providers.errors import (
    ExpectedAccountConditionNotReachedError,
)
from multiversx_sdk.network_providers.resources import AccountOnNetwork

logger = logging.getLogger("account_awaiter")


class IAccountFetcher(Protocol):
    def get_account(self, address: Address) -> AccountOnNetwork: ...


class AccountAwaiter:
    """AccountAwaiter allows one to await until a specific event occurs on a given address."""

    def __init__(
        self,
        fetcher: IAccountFetcher,
        polling_interval_in_milliseconds: Optional[int] = None,
        timeout_interval_in_milliseconds: Optional[int] = None,
        patience_time_in_milliseconds: Optional[int] = None,
    ) -> None:
        """
        Args:
            fetcher (IAccountFetcher): Used to fetch the account of the network.
            polling_interval_in_milliseconds (Optional[int]): The polling interval, in milliseconds.
            timeout_interval_in_milliseconds (Optional[int]): The timeout, in milliseconds.
            patience_time_in_milliseconds (Optional[int]): The patience, an extra time (in milliseconds) to wait, after the account has reached its desired condition.
        """
        self.fetcher = fetcher

        if polling_interval_in_milliseconds is None:
            self.polling_interval_in_milliseconds = DEFAULT_ACCOUNT_AWAITING_POLLING_TIMEOUT_IN_MILLISECONDS
        else:
            self.polling_interval_in_milliseconds = polling_interval_in_milliseconds

        if timeout_interval_in_milliseconds is None:
            self.timeout_interval_in_milliseconds = DEFAULT_ACCOUNT_AWAITING_TIMEOUT_IN_MILLISECONDS
        else:
            self.timeout_interval_in_milliseconds = timeout_interval_in_milliseconds

        if patience_time_in_milliseconds is None:
            self.patience_time_in_milliseconds = DEFAULT_ACCOUNT_AWAITING_PATIENCE_IN_MILLISECONDS
        else:
            self.patience_time_in_milliseconds = patience_time_in_milliseconds

    def await_on_condition(self, address: Address, condition: Callable[[AccountOnNetwork], bool]) -> AccountOnNetwork:
        """Waits until the condition is satisfied."""

        def do_fetch():
            return self.fetcher.get_account(address)

        return self._await_conditionally(
            is_satisfied=condition,
            do_fetch=do_fetch,
            error=ExpectedAccountConditionNotReachedError(),
        )

    def _await_conditionally(
        self,
        is_satisfied: Callable[[AccountOnNetwork], bool],
        do_fetch: Callable[[], AccountOnNetwork],
        error: Exception,
    ) -> AccountOnNetwork:
        is_condition_satisfied = False
        fetched_data: Union[AccountOnNetwork, None] = None
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
