from typing import Optional, Protocol

from multiversx_sdk.core.constants import ARGS_SEPARATOR
from multiversx_sdk.core.interfaces import IGasLimitEstimator
from multiversx_sdk.core.transaction import Transaction


class IConfig(Protocol):
    min_gas_limit: int
    gas_limit_per_byte: int


class BaseFactory:
    """Base class for factories in the MultiversX SDK. **Internal use only.**"""

    def __init__(self, config: IConfig, gas_limit_estimator: Optional[IGasLimitEstimator] = None):
        self.config = config
        self.gas_limit_estimator = gas_limit_estimator

    def set_payload(self, transaction: Transaction, data_parts: list[str]):
        data = ARGS_SEPARATOR.join(data_parts)
        transaction.data = data.encode("utf-8")

    def set_gas_limit(
        self,
        transaction: Transaction,
        gas_limit: Optional[int] = None,
        config_gas_limit: Optional[int] = None,
    ):
        """
        Sets the gas limit for the transaction.

        Args:
            gas_limit: Optional gas limit to set. This is the value provided by the user.
            config_gas_limit: Optional gas limit from the configuration. This is computed internally based on some config values.
        """
        if gas_limit is not None:
            transaction.gas_limit = gas_limit
        elif self.gas_limit_estimator:
            transaction.gas_limit = self.gas_limit_estimator.estimate_gas_limit(transaction)
        elif config_gas_limit is not None:
            data_movement_gas = self.config.min_gas_limit + self.config.gas_limit_per_byte * len(transaction.data)
            transaction.gas_limit = data_movement_gas + config_gas_limit
        else:
            raise Exception("Gas limit must be provided or a gas limit estimator must be set.")
