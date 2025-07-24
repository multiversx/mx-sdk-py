from typing import Optional, Protocol

from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.gas_estimator.errors import GasLimitEstimationError
from multiversx_sdk.network_providers.resources import TransactionCostResponse


class INetworkProvider(Protocol):
    def estimate_transaction_cost(self, transaction: Transaction) -> TransactionCostResponse: ...


class GasLimitEstimator:
    def __init__(self, network_provider: INetworkProvider, gas_multiplier: Optional[float] = None):
        """
        Initializes the gas limit estimator.

        Args:
            network_provider: The network provider for making API calls.
            gas_multiplier: Optional multiplier to adjust the estimated gas limit (default: 1.2).
        """
        self.network_provider = network_provider
        self.gas_multiplier = gas_multiplier if gas_multiplier is not None else 1.2

    def estimate_gas_limit(self, transaction: Transaction) -> int:
        """
        Estimates the gas limit for the given transaction.

        Args:
            transaction: The transaction object to estimate gas for.

        Returns:
            int: The estimated gas limit, adjusted by the gas multiplier.
        """
        try:
            cost_response = self.network_provider.estimate_transaction_cost(transaction)
            return int(cost_response.gas_limit * self.gas_multiplier)
        except Exception as e:
            raise GasLimitEstimationError(e)
