from pathlib import Path

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.transactions_factory_config import TransactionsFactoryConfig
from multiversx_sdk.validators.validators_signers import ValidatorsSigners
from multiversx_sdk.validators.validators_transactions_factory import (
    ValidatorsTransactionsFactory,
)
from multiversx_sdk.wallet.validator_keys import ValidatorPublicKey


class TestValidatorsTransactionsFactory:
    testdata = Path(__file__).parent.parent / "testutils" / "testdata"
    testwallets = Path(__file__).parent.parent / "testutils" / "testwallets"
    validators_file = testwallets / "validators.pem"

    alice = Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
    reward_address = Address.new_from_bech32("erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8")

    validator_pubkey = ValidatorPublicKey.from_string(
        "e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"
    )

    factory = ValidatorsTransactionsFactory(TransactionsFactoryConfig("D"))

    def test_create_transaction_for_staking_using_path_to_validators_file(self):
        transaction = self.factory.create_transaction_for_staking(
            sender=self.alice,
            validators_file=self.validators_file,
            amount=2500000000000000000000,
            rewards_address=self.reward_address,
        )

        assert transaction.sender.to_bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver.to_bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
        assert transaction.value == 2500000000000000000000
        assert transaction.nonce == 0
        assert transaction.gas_limit == 11029500
        assert transaction.chain_id == "D"
        assert transaction.version == 2
        assert transaction.options == 0
        assert (
            transaction.data.decode()
            == "stake@02@f8910e47cf9464777c912e6390758bb39715fffcb861b184017920e4a807b42553f2f21e7f3914b81bcf58b66a72ab16d97013ae1cff807cefc977ef8cbf116258534b9e46d19528042d16ef8374404a89b184e0a4ee18c77c49e454d04eae8d@1865870f7f69162a2dfefd33fe232a9ca984c6f22d1ee3f6a5b34a8eb8c9f7319001f29d5a2eed85c1500aca19fa4189@1b4e60e6d100cdf234d3427494dac55fbac49856cadc86bcb13a01b9bb05a0d9143e86c186c948e7ae9e52427c9523102efe9019a2a9c06db02993f2e3e6756576ae5a3ec7c235d548bc79de1a6990e1120ae435cb48f7fc436c9f9098b92a0d@12b309791213aac8ad9f34f0d912261e30f9ab060859e4d515e020a98b91d82a7cd334e4b504bb93d6b75347cccd6318@b2a11555ce521e4944e09ab17549d85b487dcd26c84b5017a39e31a3670889ba"
        )

    def test_create_transaction_for_staking_using_validators_file(self):
        validators_file = ValidatorsSigners.new_from_pem(self.validators_file)

        transaction = self.factory.create_transaction_for_staking(
            sender=self.alice,
            validators_file=validators_file,
            amount=2500000000000000000000,
            rewards_address=self.reward_address,
        )

        assert transaction.sender.to_bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver.to_bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
        assert transaction.value == 2500000000000000000000
        assert transaction.nonce == 0
        assert transaction.gas_limit == 11029500
        assert transaction.chain_id == "D"
        assert transaction.version == 2
        assert transaction.options == 0
        assert (
            transaction.data.decode()
            == "stake@02@f8910e47cf9464777c912e6390758bb39715fffcb861b184017920e4a807b42553f2f21e7f3914b81bcf58b66a72ab16d97013ae1cff807cefc977ef8cbf116258534b9e46d19528042d16ef8374404a89b184e0a4ee18c77c49e454d04eae8d@1865870f7f69162a2dfefd33fe232a9ca984c6f22d1ee3f6a5b34a8eb8c9f7319001f29d5a2eed85c1500aca19fa4189@1b4e60e6d100cdf234d3427494dac55fbac49856cadc86bcb13a01b9bb05a0d9143e86c186c948e7ae9e52427c9523102efe9019a2a9c06db02993f2e3e6756576ae5a3ec7c235d548bc79de1a6990e1120ae435cb48f7fc436c9f9098b92a0d@12b309791213aac8ad9f34f0d912261e30f9ab060859e4d515e020a98b91d82a7cd334e4b504bb93d6b75347cccd6318@b2a11555ce521e4944e09ab17549d85b487dcd26c84b5017a39e31a3670889ba"
        )

    def test_create_transaction_for_topping_up(self):
        transaction = self.factory.create_transaction_for_topping_up(
            sender=self.alice,
            amount=2500000000000000000000,
        )

        assert transaction.sender.to_bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver.to_bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
        assert transaction.value == 2500000000000000000000
        assert transaction.nonce == 0
        assert transaction.gas_limit == 5057500
        assert transaction.chain_id == "D"
        assert transaction.version == 2
        assert transaction.options == 0
        assert transaction.data.decode() == "stake"

    def test_create_transaction_for_unstaking(self):
        transaction = self.factory.create_transaction_for_unstaking(
            sender=self.alice,
            public_keys=[self.validator_pubkey],
        )

        assert transaction.sender.to_bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver.to_bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
        assert transaction.value == 0
        assert transaction.nonce == 0
        assert transaction.gas_limit == 5350000
        assert transaction.chain_id == "D"
        assert transaction.version == 2
        assert transaction.options == 0
        assert (
            transaction.data.decode()
            == "unStake@e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"
        )

    def test_create_transaction_for_unbonding(self):
        transaction = self.factory.create_transaction_for_unbonding(
            sender=self.alice,
            public_keys=[self.validator_pubkey],
        )

        assert transaction.sender.to_bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver.to_bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
        assert transaction.value == 0
        assert transaction.nonce == 0
        assert transaction.gas_limit == 5348500
        assert transaction.chain_id == "D"
        assert transaction.version == 2
        assert transaction.options == 0
        assert (
            transaction.data.decode()
            == "unBond@e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"
        )

    def test_create_transaction_for_unjailing(self):
        transaction = self.factory.create_transaction_for_unjailing(
            sender=self.alice,
            public_keys=[self.validator_pubkey],
            amount=2500000000000000000000,
        )

        assert transaction.sender.to_bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver.to_bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
        assert transaction.value == 2500000000000000000000
        assert transaction.nonce == 0
        assert transaction.gas_limit == 5348500
        assert transaction.chain_id == "D"
        assert transaction.version == 2
        assert transaction.options == 0
        assert (
            transaction.data.decode()
            == "unJail@e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"
        )

    def test_create_transaction_for_changing_rewards_address(self):
        transaction = self.factory.create_transaction_for_changing_rewards_address(
            sender=self.alice,
            rewards_address=self.reward_address,
        )

        assert transaction.sender.to_bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver.to_bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
        assert transaction.value == 0
        assert transaction.nonce == 0
        assert transaction.gas_limit == 5176000
        assert transaction.chain_id == "D"
        assert transaction.version == 2
        assert transaction.options == 0
        assert (
            transaction.data.decode()
            == "changeRewardAddress@b2a11555ce521e4944e09ab17549d85b487dcd26c84b5017a39e31a3670889ba"
        )

    def test_create_transaction_for_claiming(self):
        transaction = self.factory.create_transaction_for_claiming(sender=self.alice)

        assert transaction.sender.to_bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver.to_bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
        assert transaction.value == 0
        assert transaction.nonce == 0
        assert transaction.gas_limit == 5057500
        assert transaction.chain_id == "D"
        assert transaction.version == 2
        assert transaction.options == 0
        assert transaction.data.decode() == "claim"

    def test_create_transaction_for_unstaking_nodes(self):
        transaction = self.factory.create_transaction_for_unstaking_nodes(
            sender=self.alice,
            public_keys=[self.validator_pubkey],
        )

        assert transaction.sender.to_bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver.to_bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
        assert transaction.value == 0
        assert transaction.nonce == 0
        assert transaction.gas_limit == 5357500
        assert transaction.chain_id == "D"
        assert transaction.version == 2
        assert transaction.options == 0
        assert (
            transaction.data.decode()
            == "unStakeNodes@e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"
        )

    def test_create_transaction_for_unstaking_tokens(self):
        transaction = self.factory.create_transaction_for_unstaking_tokens(
            sender=self.alice,
            amount=11000000000000000000,
        )

        assert transaction.sender.to_bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver.to_bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
        assert transaction.value == 0
        assert transaction.nonce == 0
        assert transaction.gas_limit == 5095000
        assert transaction.chain_id == "D"
        assert transaction.version == 2
        assert transaction.options == 0
        assert transaction.data.decode() == "unStakeTokens@98a7d9b8314c0000"

    def test_create_transaction_for_unbonding_nodes(self):
        transaction = self.factory.create_transaction_for_unbonding_nodes(
            sender=self.alice,
            public_keys=[self.validator_pubkey],
        )

        assert transaction.sender.to_bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver.to_bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
        assert transaction.value == 0
        assert transaction.nonce == 0
        assert transaction.gas_limit == 5356000
        assert transaction.chain_id == "D"
        assert transaction.version == 2
        assert transaction.options == 0
        assert (
            transaction.data.decode()
            == "unBondNodes@e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"
        )

    def test_create_transaction_for_unbonding_tokens(self):
        transaction = self.factory.create_transaction_for_unbonding_tokens(
            sender=self.alice,
            amount=20000000000000000000,
        )

        assert transaction.sender.to_bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver.to_bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
        assert transaction.value == 0
        assert transaction.nonce == 0
        assert transaction.gas_limit == 5096500
        assert transaction.chain_id == "D"
        assert transaction.version == 2
        assert transaction.options == 0
        assert transaction.data.decode() == "unBondTokens@01158e460913d00000"

    def test_create_transaction_for_cleaning_registered_data(self):
        transaction = self.factory.create_transaction_for_cleaning_registered_data(sender=self.alice)

        assert transaction.sender.to_bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver.to_bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
        assert transaction.value == 0
        assert transaction.nonce == 0
        assert transaction.gas_limit == 5078500
        assert transaction.chain_id == "D"
        assert transaction.version == 2
        assert transaction.options == 0
        assert transaction.data.decode() == "cleanRegisteredData"

    def test_create_transaction_for_restaking_unstaked_nodes(self):
        transaction = self.factory.create_transaction_for_restaking_unstaked_nodes(
            sender=self.alice,
            public_keys=[self.validator_pubkey],
        )

        assert transaction.sender.to_bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver.to_bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
        assert transaction.value == 0
        assert transaction.nonce == 0
        assert transaction.gas_limit == 5369500
        assert transaction.chain_id == "D"
        assert transaction.version == 2
        assert transaction.options == 0
        assert (
            transaction.data.decode()
            == "reStakeUnStakedNodes@e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"
        )
