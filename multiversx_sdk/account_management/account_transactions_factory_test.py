from multiversx_sdk.account_management.account_controller import \
    AccountTransactionsFactory
from multiversx_sdk.core.address import Address
from multiversx_sdk.core.transactions_factory_config import \
    TransactionsFactoryConfig


class TestAccountTransactionsFactory:
    config = TransactionsFactoryConfig("D")
    factory = AccountTransactionsFactory(config)

    def test_save_key_value(self):
        sender = Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
        pairs: dict[bytes, bytes] = {}
        key = "key0".encode()
        value = "value0".encode()
        pairs[key] = value

        tx = self.factory.create_transaction_for_saving_key_value(
            sender=sender,
            key_value_pairs=pairs
        )

        assert tx.sender.to_bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert tx.receiver.to_bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert tx.data.decode() == "SaveKeyValue@6b657930@76616c756530"
        assert tx.gas_limit == 271000

    def test_set_guardian(self):
        sender = Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
        guardian = Address.new_from_bech32("erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx")
        service_id = "MultiversXTCSService"

        tx = self.factory.create_transaction_for_setting_guardian(
            sender=sender,
            guardian_address=guardian,
            service_id=service_id
        )

        assert tx.sender.to_bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert tx.receiver.to_bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert tx.data.decode() == "SetGuardian@8049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f8@4d756c7469766572735854435353657276696365"
        assert tx.gas_limit == 475500

    def test_guard_account(self):
        sender = Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
        tx = self.factory.create_transaction_for_guarding_account(sender)

        assert tx.sender.to_bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert tx.receiver.to_bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert tx.data.decode() == "GuardAccount"
        assert tx.gas_limit == 318000

    def test_unguard_account(self):
        sender = Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
        guardian = Address.new_from_bech32("erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx")
        tx = self.factory.create_transaction_for_unguarding_account(sender, guardian)

        assert tx.sender.to_bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert tx.receiver.to_bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert tx.data.decode() == "UnGuardAccount"
        assert tx.gas_limit == 321000
        assert tx.guardian == guardian
