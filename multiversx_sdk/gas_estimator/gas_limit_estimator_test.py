from multiversx_sdk.core.address import Address
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transaction_status import TransactionStatus
from multiversx_sdk.gas_estimator.gas_limit_estimator import GasLimitEstimator
from multiversx_sdk.network_providers.resources import TransactionCostResponse
from multiversx_sdk.testutils.mock_network_provider import MockNetworkProvider


class TestGasLimitEstimator:
    def test_gas_limit_estimator(self):
        provider = MockNetworkProvider()
        provider.mock_transaction_cost_response = TransactionCostResponse(
            raw={},
            gas_limit=50000,
            status=TransactionStatus("success"),
        )

        gas_estimator = GasLimitEstimator(provider)
        transaction = Transaction(
            sender=Address.empty(),
            receiver=Address.empty(),
            chain_id="D",
            gas_limit=0,
            value=100000000,
        )

        estimated_gas_limit = gas_estimator.estimate_gas_limit(transaction)
        assert estimated_gas_limit == 50000

    def test_gas_limit_estimator_with_multiplier(self):
        provider = MockNetworkProvider()
        provider.mock_transaction_cost_response = TransactionCostResponse(
            raw={},
            gas_limit=50000,
            status=TransactionStatus("success"),
        )

        gas_estimator = GasLimitEstimator(provider, 1.5)
        transaction = Transaction(
            sender=Address.empty(),
            receiver=Address.empty(),
            chain_id="D",
            gas_limit=0,
            value=100000000,
        )

        estimated_gas_limit = gas_estimator.estimate_gas_limit(transaction)
        assert estimated_gas_limit == 75000

    def test_ensure_integer_value_gas_limit_estimator_with_multiplier(self):
        provider = MockNetworkProvider()
        provider.mock_transaction_cost_response = TransactionCostResponse(
            raw={},
            gas_limit=50000,
            status=TransactionStatus("success"),
        )

        gas_estimator = GasLimitEstimator(provider, 1.98765)
        transaction = Transaction(
            sender=Address.empty(),
            receiver=Address.empty(),
            chain_id="D",
            gas_limit=0,
            value=100000000,
        )

        estimated_gas_limit = gas_estimator.estimate_gas_limit(transaction)
        assert estimated_gas_limit == 99382
