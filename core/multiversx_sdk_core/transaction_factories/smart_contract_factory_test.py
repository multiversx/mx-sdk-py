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
        guardian = Address.from_bech32("erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx")
        nonce = 777
        contract = Path(__file__).parent.parent / "testutils" / "testdata" / "adder.wasm"
        gas_limit = 6000000
        args = [0]

        transaction = self.factory.deploy(
            deployer=sender,
            nonce=nonce,
            bytecode_path=contract,
            gas_limit=gas_limit,
            arguments=args,
            guardian=guardian
        )

        assert transaction.chainID == "D"
        assert transaction.nonce == 777
        assert transaction.sender.bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver.bech32() == CONTRACT_DEPLOY_ADDRESS
        assert transaction.guardian
        assert transaction.guardian.bech32() == "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"
        assert transaction.gas_limit == 6000000
        assert transaction.signature == b''

    def test_smart_contract_call(self):
        sender = Address.from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
        guardian = Address.from_bech32("erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx")
        nonce = 777
        contract = Address.from_bech32("erd1qqqqqqqqqqqqqpgqhy6nl6zq07rnzry8uyh6rtyq0uzgtk3e69fqgtz9l4")
        function = "add"
        gas_limit = 6000000
        args = [7]

        transaction = self.factory.execute(
            sender=sender,
            contract_address=contract,
            function=function,
            gas_limit=gas_limit,
            nonce=nonce,
            arguments=args,
            guardian=guardian
        )

        assert transaction.chainID == "D"
        assert transaction.nonce == 777
        assert transaction.sender.bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver.bech32() == contract.bech32()
        assert transaction.guardian
        assert transaction.guardian.bech32() == "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"
        assert str(transaction.data) == "add@07"
        assert transaction.value == 0

    def test_smart_contract_upgrade(self):
        sender = Address.from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
        guardian = Address.from_bech32("erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx")
        nonce = 777
        contract_address = Address.from_bech32("erd1qqqqqqqqqqqqqpgqhy6nl6zq07rnzry8uyh6rtyq0uzgtk3e69fqgtz9l4")
        contract = Path(__file__).parent.parent / "testutils" / "testdata" / "adder.wasm"
        gas_limit = 6000000
        args = [0]

        transaction = self.factory.upgrade(
            sender=sender,
            contract=contract_address,
            bytecode_path=contract,
            gas_limit=gas_limit,
            arguments=args,
            nonce=nonce,
            guardian=guardian
        )

        assert transaction.chainID == "D"
        assert transaction.nonce == 777
        assert transaction.sender.bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver.bech32() == "erd1qqqqqqqqqqqqqpgqhy6nl6zq07rnzry8uyh6rtyq0uzgtk3e69fqgtz9l4"
        assert transaction.guardian
        assert transaction.guardian.bech32() == "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"
        assert transaction.gas_limit == 6000000
        assert transaction.signature == b''
        assert str(transaction.data).startswith("upgradeContract@")
