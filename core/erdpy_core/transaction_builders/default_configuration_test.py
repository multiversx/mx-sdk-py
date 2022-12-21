from erdpy_core.transaction_builders.default_configuration import \
    DefaultTransactionBuildersConfiguration


def test_default_configuration():
    config = DefaultTransactionBuildersConfiguration(chain_id="D")

    assert config.chain_id == "D"
    assert config.min_gas_price == 1000000000
    assert config.min_gas_limit == 50000
    assert config.gas_limit_per_byte == 1500
