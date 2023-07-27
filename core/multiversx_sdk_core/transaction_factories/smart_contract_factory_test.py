from pathlib import Path

from multiversx_sdk_core.address import Address
from multiversx_sdk_core.constants import CONTRACT_DEPLOY_ADDRESS
from multiversx_sdk_core.transaction_factories.smart_contract_factory import \
    SmartContractFactory
from multiversx_sdk_core.transaction_factories.transaction_factory_config import \
    TransactionFactoryConfig


class TestSmartContract:
    config = TransactionFactoryConfig("D")
    factory = SmartContractFactory(config)

    def test_smart_contract_deploy(self):
        sender = Address.from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
        contract = Path(__file__).parent.parent / "testutils" / "testdata" / "adder.wasm"
        gas_limit = 6000000
        args = [0]

        transaction = self.factory.create_transaction_intent_for_deploy(
            sender=sender,
            bytecode=contract,
            gas_limit=gas_limit,
            arguments=args
        )

        assert transaction.sender == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver == CONTRACT_DEPLOY_ADDRESS
        assert transaction.gas_limit == 6000000
        assert transaction.data
        assert transaction.value == "0"

    def test_smart_contract_call(self):
        sender = Address.from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
        contract = Address.from_bech32("erd1qqqqqqqqqqqqqpgqhy6nl6zq07rnzry8uyh6rtyq0uzgtk3e69fqgtz9l4")
        function = "add"
        gas_limit = 6000000
        args = [7]

        transaction = self.factory.create_transaction_intent_for_execute(
            sender=sender,
            contract_address=contract,
            function=function,
            gas_limit=gas_limit,
            arguments=args
        )

        assert transaction.sender == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver == contract.bech32()
        assert transaction.gas_limit == 6000000
        assert transaction.data
        assert transaction.data.decode() == "add@07"
        assert transaction.value == "0"

    def test_smart_contract_upgrade(self):
        sender = Address.from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
        contract_address = Address.from_bech32("erd1qqqqqqqqqqqqqpgqhy6nl6zq07rnzry8uyh6rtyq0uzgtk3e69fqgtz9l4")
        contract = Path(__file__).parent.parent / "testutils" / "testdata" / "adder.wasm"
        gas_limit = 6000000
        args = [0]

        transaction = self.factory.create_transaction_for_upgrade(
            sender=sender,
            contract=contract_address,
            bytecode=contract,
            gas_limit=gas_limit,
            arguments=args
        )

        assert transaction.sender == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver == "erd1qqqqqqqqqqqqqpgqhy6nl6zq07rnzry8uyh6rtyq0uzgtk3e69fqgtz9l4"
        assert transaction.gas_limit == 6000000
        assert transaction.data
        assert transaction.data.decode().startswith("upgradeContract@")
        assert transaction.value == "0"
