from pathlib import Path

from multiversx_sdk_core.address import Address
from multiversx_sdk_core.constants import CONTRACT_DEPLOY_ADDRESS
from multiversx_sdk_core.transaction_factories.smart_contract_factory import \
    SmartContractTransactionIntentsFactory
from multiversx_sdk_core.transaction_factories.transaction_factory_config import \
    TransactionFactoryConfig


class TestSmartContract:
    config = TransactionFactoryConfig("D")
    factory = SmartContractTransactionIntentsFactory(config)

    def test_create_transaction_intent_for_deploy(self):
        sender = Address.from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
        contract = Path(__file__).parent.parent / "testutils" / "testdata" / "adder.wasm"
        gas_limit = 6000000
        args = [0]

        intent = self.factory.create_transaction_intent_for_deploy(
            sender=sender,
            bytecode=contract,
            gas_limit=gas_limit,
            arguments=args
        )

        assert intent.sender == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert intent.receiver == CONTRACT_DEPLOY_ADDRESS
        assert intent.data
        assert intent.gas_limit == 6000000 + 50000 + 1500 * len(intent.data)
        assert intent.value == 0

    def test_create_transaction_intent_for_execute(self):
        sender = Address.from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
        contract = Address.from_bech32("erd1qqqqqqqqqqqqqpgqhy6nl6zq07rnzry8uyh6rtyq0uzgtk3e69fqgtz9l4")
        function = "add"
        gas_limit = 6000000
        args = [7]

        intent = self.factory.create_transaction_intent_for_execute(
            sender=sender,
            contract_address=contract,
            function=function,
            gas_limit=gas_limit,
            arguments=args
        )

        assert intent.sender == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert intent.receiver == contract.bech32()
        assert intent.gas_limit == 6059000
        assert intent.data
        assert intent.data.decode() == "add@07"
        assert intent.value == 0

    def test_create_transaction_intent_for_upgrade(self):
        sender = Address.from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
        contract_address = Address.from_bech32("erd1qqqqqqqqqqqqqpgqhy6nl6zq07rnzry8uyh6rtyq0uzgtk3e69fqgtz9l4")
        contract = Path(__file__).parent.parent / "testutils" / "testdata" / "adder.wasm"
        gas_limit = 6000000
        args = [0]

        intent = self.factory.create_transaction_intent_for_upgrade(
            sender=sender,
            contract=contract_address,
            bytecode=contract,
            gas_limit=gas_limit,
            arguments=args
        )

        assert intent.sender == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert intent.receiver == "erd1qqqqqqqqqqqqqpgqhy6nl6zq07rnzry8uyh6rtyq0uzgtk3e69fqgtz9l4"
        assert intent.data
        assert intent.data.decode().startswith("upgradeContract@")
        assert intent.gas_limit == 6000000 + 50000 + 1500 * len(intent.data)
        assert intent.value == 0
