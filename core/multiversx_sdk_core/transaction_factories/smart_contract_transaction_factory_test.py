from pathlib import Path

from multiversx_sdk_core.address import Address
from multiversx_sdk_core.constants import CONTRACT_DEPLOY_ADDRESS
from multiversx_sdk_core.tokens import Token, TokenTransfer
from multiversx_sdk_core.transaction_factories.smart_contract_transactions_factory import \
    SmartContractTransactionsFactory
from multiversx_sdk_core.transaction_factories.transactions_factory_config import \
    TransactionsFactoryConfig


class TestSmartContractTransactionsFactory:
    config = TransactionsFactoryConfig("D")
    factory = SmartContractTransactionsFactory(config)

    def test_create_transaction_for_deploy(self):
        sender = Address.from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
        contract = Path(__file__).parent.parent / "testutils" / "testdata" / "adder.wasm"
        gas_limit = 6000000
        args = [0]

        transaction = self.factory.create_transaction_for_deploy(
            sender=sender,
            bytecode=contract,
            gas_limit=gas_limit,
            arguments=args
        )

        assert transaction.sender == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver == CONTRACT_DEPLOY_ADDRESS
        assert transaction.data
        assert transaction.gas_limit == gas_limit
        assert transaction.amount == 0

    def test_create_transaction_for_execute_and_tranfer_native_token(self):
        sender = Address.from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
        contract = Address.from_bech32("erd1qqqqqqqqqqqqqpgqhy6nl6zq07rnzry8uyh6rtyq0uzgtk3e69fqgtz9l4")
        function = "add"
        gas_limit = 6000000
        args = [7]
        egld_amount = 1000000000000000000

        transaction = self.factory.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function=function,
            gas_limit=gas_limit,
            arguments=args,
            native_transfer_amount=egld_amount
        )

        assert transaction.sender == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver == "erd1qqqqqqqqqqqqqpgqhy6nl6zq07rnzry8uyh6rtyq0uzgtk3e69fqgtz9l4"
        assert transaction.gas_limit == gas_limit
        assert transaction.data
        assert transaction.data.decode() == "add@07"
        assert transaction.amount == 1000000000000000000

    def test_create_transaction_for_execute_and_send_single_esdt(self):
        sender = Address.from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
        contract = Address.from_bech32("erd1qqqqqqqqqqqqqpgqhy6nl6zq07rnzry8uyh6rtyq0uzgtk3e69fqgtz9l4")
        function = "dummy"
        gas_limit = 6000000
        args = [7]
        token = Token("FOO-6ce17b", 0)
        transfer = TokenTransfer(token, 10)

        hex_foo = "464f4f2d366365313762"
        hex_dummy_function = "64756d6d79"

        transaction = self.factory.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function=function,
            gas_limit=gas_limit,
            arguments=args,
            token_transfers=[transfer]
        )

        assert transaction.sender == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver == "erd1qqqqqqqqqqqqqpgqhy6nl6zq07rnzry8uyh6rtyq0uzgtk3e69fqgtz9l4"
        assert transaction.gas_limit == gas_limit
        assert transaction.data
        assert transaction.data.decode() == f"ESDTTransfer@{hex_foo}@0a@{hex_dummy_function}@07"
        assert transaction.amount == 0

    def test_create_transaction_for_execute_and_send_multiple_esdts(self):
        sender = Address.from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
        contract = Address.from_bech32("erd1qqqqqqqqqqqqqpgqak8zt22wl2ph4tswtyc39namqx6ysa2sd8ss4xmlj3")
        function = "dummy"
        gas_limit = 6000000
        args = [7]

        foo_token = Token("FOO-6ce17b", 0)
        foo_transfer = TokenTransfer(foo_token, 10)

        bar_token = Token("BAR-5bc08f", 0)
        bar_transfer = TokenTransfer(bar_token, 3140)

        hex_foo = "464f4f2d366365313762"
        hex_bar = "4241522d356263303866"
        hex_dummy_function = "64756d6d79"

        transaction = self.factory.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function=function,
            gas_limit=gas_limit,
            arguments=args,
            token_transfers=[foo_transfer, bar_transfer]
        )

        assert transaction.sender == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.gas_limit == gas_limit
        assert transaction.data
        assert transaction.data.decode() == f"MultiESDTNFTTransfer@{contract.hex()}@02@{hex_foo}@@0a@{hex_bar}@@0c44@{hex_dummy_function}@07"
        assert transaction.amount == 0

    def test_create_transaction_for_execute_and_send_single_nft(self):
        sender = Address.from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
        contract = Address.from_bech32("erd1qqqqqqqqqqqqqpgqhy6nl6zq07rnzry8uyh6rtyq0uzgtk3e69fqgtz9l4")
        function = "dummy"
        gas_limit = 6000000
        args = [7]
        token = Token("MOS-b9b4b2", 1)
        transfer = TokenTransfer(token, 1)

        hex_token = "4d4f532d623962346232"
        hex_dummy_function = "64756d6d79"

        transaction = self.factory.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function=function,
            gas_limit=gas_limit,
            arguments=args,
            token_transfers=[transfer]
        )

        assert transaction.sender == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.gas_limit == gas_limit
        assert transaction.data
        assert transaction.data.decode() == f"ESDTNFTTransfer@{hex_token}@01@01@{contract.hex()}@{hex_dummy_function}@07"
        assert transaction.amount == 0

    def test_create_transaction_for_execute_and_send_multiple_nfts(self):
        sender = Address.from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
        contract = Address.from_bech32("erd1qqqqqqqqqqqqqpgqhy6nl6zq07rnzry8uyh6rtyq0uzgtk3e69fqgtz9l4")
        function = "dummy"
        gas_limit = 6000000
        args = [7]

        first_token = Token("MOS-b9b4b2", 1)
        first_transfer = TokenTransfer(first_token, 1)
        second_token = Token("MOS-b9b4b2", 42)
        second_transfer = TokenTransfer(second_token, 1)

        hex_token = "4d4f532d623962346232"
        hex_dummy_function = "64756d6d79"

        transaction = self.factory.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function=function,
            gas_limit=gas_limit,
            arguments=args,
            token_transfers=[first_transfer, second_transfer]
        )

        assert transaction.sender == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.gas_limit == gas_limit
        assert transaction.data
        assert transaction.data.decode() == f"MultiESDTNFTTransfer@{contract.hex()}@02@{hex_token}@01@01@{hex_token}@2a@01@{hex_dummy_function}@07"
        assert transaction.amount == 0

    def test_create_transaction_for_upgrade(self):
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
        assert transaction.data
        assert transaction.data.decode().startswith("upgradeContract@")
        assert transaction.gas_limit == gas_limit
        assert transaction.amount == 0
