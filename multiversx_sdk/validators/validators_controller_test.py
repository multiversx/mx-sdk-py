from pathlib import Path

from multiversx_sdk.accounts.account import Account
from multiversx_sdk.core.address import Address
from multiversx_sdk.validators.validators_controller import ValidatorsController
from multiversx_sdk.validators.validators_signers import ValidatorsSigners
from multiversx_sdk.wallet.validator_keys import ValidatorPublicKey


class TestValidatorsController:
    testdata = Path(__file__).parent.parent / "testutils" / "testdata"
    testwallets = Path(__file__).parent.parent / "testutils" / "testwallets"
    validators_file = testwallets / "validators.pem"

    alice = Account.new_from_pem(testwallets / "alice.pem")
    reward_address = Address.new_from_bech32("erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8")

    validator_pubkey = ValidatorPublicKey.from_string(
        "e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"
    )

    controller = ValidatorsController(chain_id="localnet")

    def test_create_transaction_for_staking_using_path_to_validators_file(self):
        transaction = self.controller.create_transaction_for_staking(
            sender=self.alice,
            nonce=self.alice.nonce,
            validators_file=self.validators_file,
            amount=2500000000000000000000,
            rewards_address=self.reward_address,
        )

        assert transaction.sender.to_bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver.to_bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
        assert transaction.value == 2500000000000000000000
        assert transaction.nonce == 0
        assert transaction.gas_limit == 11029500
        assert transaction.chain_id == "localnet"
        assert transaction.version == 2
        assert transaction.options == 0
        assert transaction.guardian is None
        assert transaction.relayer is None
        assert (
            transaction.signature.hex()
            == "e9dd1159bc55bde84872f0595c9e24b0b210deb8cb02a1df7d7b0e1277436d2043437ffeaff540e11200c00417cf5ce396b3154f968ad62ab4359fb05a493b0d"
        )
        assert (
            transaction.data.decode()
            == "stake@02@f8910e47cf9464777c912e6390758bb39715fffcb861b184017920e4a807b42553f2f21e7f3914b81bcf58b66a72ab16d97013ae1cff807cefc977ef8cbf116258534b9e46d19528042d16ef8374404a89b184e0a4ee18c77c49e454d04eae8d@1865870f7f69162a2dfefd33fe232a9ca984c6f22d1ee3f6a5b34a8eb8c9f7319001f29d5a2eed85c1500aca19fa4189@1b4e60e6d100cdf234d3427494dac55fbac49856cadc86bcb13a01b9bb05a0d9143e86c186c948e7ae9e52427c9523102efe9019a2a9c06db02993f2e3e6756576ae5a3ec7c235d548bc79de1a6990e1120ae435cb48f7fc436c9f9098b92a0d@12b309791213aac8ad9f34f0d912261e30f9ab060859e4d515e020a98b91d82a7cd334e4b504bb93d6b75347cccd6318@b2a11555ce521e4944e09ab17549d85b487dcd26c84b5017a39e31a3670889ba"
        )

    def test_create_transaction_for_staking_using_validators_file(self):
        validators_file = ValidatorsSigners.new_from_pem(self.validators_file)

        transaction = self.controller.create_transaction_for_staking(
            sender=self.alice,
            nonce=self.alice.nonce,
            validators_file=validators_file,
            amount=2500000000000000000000,
            rewards_address=self.reward_address,
        )

        assert transaction.sender.to_bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver.to_bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
        assert transaction.value == 2500000000000000000000
        assert transaction.nonce == 0
        assert transaction.gas_limit == 11029500
        assert transaction.chain_id == "localnet"
        assert transaction.version == 2
        assert transaction.options == 0
        assert transaction.guardian is None
        assert transaction.relayer is None
        assert (
            transaction.signature.hex()
            == "e9dd1159bc55bde84872f0595c9e24b0b210deb8cb02a1df7d7b0e1277436d2043437ffeaff540e11200c00417cf5ce396b3154f968ad62ab4359fb05a493b0d"
        )
        assert (
            transaction.data.decode()
            == "stake@02@f8910e47cf9464777c912e6390758bb39715fffcb861b184017920e4a807b42553f2f21e7f3914b81bcf58b66a72ab16d97013ae1cff807cefc977ef8cbf116258534b9e46d19528042d16ef8374404a89b184e0a4ee18c77c49e454d04eae8d@1865870f7f69162a2dfefd33fe232a9ca984c6f22d1ee3f6a5b34a8eb8c9f7319001f29d5a2eed85c1500aca19fa4189@1b4e60e6d100cdf234d3427494dac55fbac49856cadc86bcb13a01b9bb05a0d9143e86c186c948e7ae9e52427c9523102efe9019a2a9c06db02993f2e3e6756576ae5a3ec7c235d548bc79de1a6990e1120ae435cb48f7fc436c9f9098b92a0d@12b309791213aac8ad9f34f0d912261e30f9ab060859e4d515e020a98b91d82a7cd334e4b504bb93d6b75347cccd6318@b2a11555ce521e4944e09ab17549d85b487dcd26c84b5017a39e31a3670889ba"
        )

    def test_create_transaction_for_staking_with_relayer_and_guardian(self):
        validators_file = ValidatorsSigners.new_from_pem(self.validators_file)

        transaction = self.controller.create_transaction_for_staking(
            sender=self.alice,
            nonce=self.alice.nonce,
            validators_file=validators_file,
            amount=2500000000000000000000,
            rewards_address=self.reward_address,
            guardian=Address.new_from_bech32("erd1cqqxak4wun7508e0yj9ng843r6hv4mzd0hhpjpsejkpn9wa9yq8sj7u2u5"),
            relayer=Address.new_from_bech32("erd1ssmsc9022udc8pdw7wk3hxw74jr900xg28vwpz3z60gep66fasasl2nkm4"),
        )

        assert transaction.sender.to_bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver.to_bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
        assert transaction.value == 2500000000000000000000
        assert transaction.nonce == 0
        assert transaction.gas_limit == 11129500
        assert transaction.chain_id == "localnet"
        assert transaction.version == 2
        assert transaction.options == 2
        assert transaction.guardian == Address.new_from_bech32(
            "erd1cqqxak4wun7508e0yj9ng843r6hv4mzd0hhpjpsejkpn9wa9yq8sj7u2u5"
        )
        assert transaction.relayer == Address.new_from_bech32(
            "erd1ssmsc9022udc8pdw7wk3hxw74jr900xg28vwpz3z60gep66fasasl2nkm4"
        )
        assert (
            transaction.signature.hex()
            == "0fd033bb889ea539f66e2e7e194cead88c76c98638c7734ea2d63d30ac9889b90bd248b9266f98f256992ffed48fbd80b0dc5196287f671898f18159bdbb2505"
        )
        assert (
            transaction.data.decode()
            == "stake@02@f8910e47cf9464777c912e6390758bb39715fffcb861b184017920e4a807b42553f2f21e7f3914b81bcf58b66a72ab16d97013ae1cff807cefc977ef8cbf116258534b9e46d19528042d16ef8374404a89b184e0a4ee18c77c49e454d04eae8d@1865870f7f69162a2dfefd33fe232a9ca984c6f22d1ee3f6a5b34a8eb8c9f7319001f29d5a2eed85c1500aca19fa4189@1b4e60e6d100cdf234d3427494dac55fbac49856cadc86bcb13a01b9bb05a0d9143e86c186c948e7ae9e52427c9523102efe9019a2a9c06db02993f2e3e6756576ae5a3ec7c235d548bc79de1a6990e1120ae435cb48f7fc436c9f9098b92a0d@12b309791213aac8ad9f34f0d912261e30f9ab060859e4d515e020a98b91d82a7cd334e4b504bb93d6b75347cccd6318@b2a11555ce521e4944e09ab17549d85b487dcd26c84b5017a39e31a3670889ba"
        )

    def test_create_transaction_for_topping_up(self):
        transaction = self.controller.create_transaction_for_topping_up(
            sender=self.alice,
            nonce=self.alice.nonce,
            amount=2500000000000000000000,
        )

        assert transaction.sender.to_bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver.to_bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
        assert transaction.value == 2500000000000000000000
        assert transaction.nonce == 0
        assert transaction.gas_limit == 5057500
        assert transaction.chain_id == "localnet"
        assert transaction.version == 2
        assert transaction.options == 0
        assert transaction.guardian is None
        assert transaction.relayer is None
        assert transaction.data.decode() == "stake"
        assert (
            transaction.signature.hex()
            == "ca4ebd1b9c92b0479351e9f84b0394ce15f529f4a5c056ab2dd37b923d7af81cbb7bfc8fbbea571843a797e3382795c0419f69ab357acbd9611899d39e449107"
        )

    def test_create_transaction_for_unstaking(self):
        transaction = self.controller.create_transaction_for_unstaking(
            sender=self.alice,
            nonce=7,
            public_keys=[self.validator_pubkey],
        )

        assert transaction.sender.to_bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver.to_bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
        assert transaction.value == 0
        assert transaction.nonce == 7
        assert transaction.gas_limit == 5350000
        assert transaction.chain_id == "localnet"
        assert transaction.version == 2
        assert transaction.options == 0
        assert transaction.guardian is None
        assert transaction.relayer is None
        assert (
            transaction.signature.hex()
            == "b387f3255670f17dbc4dd84bbed1f70631d2528f8f8ece7fb5c0fcc29a8b0b142583fe216c9de0086ebb69f9a50fc087ac4e5570fa2f61694df3b2cdb9389008"
        )
        assert (
            transaction.data.decode()
            == "unStake@e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"
        )

    def test_create_transaction_for_unbonding(self):
        transaction = self.controller.create_transaction_for_unbonding(
            sender=self.alice,
            nonce=7,
            public_keys=[self.validator_pubkey],
        )

        assert transaction.sender.to_bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver.to_bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
        assert transaction.value == 0
        assert transaction.nonce == 7
        assert transaction.gas_limit == 5348500
        assert transaction.chain_id == "localnet"
        assert transaction.version == 2
        assert transaction.options == 0
        assert transaction.guardian is None
        assert transaction.relayer is None
        assert (
            transaction.signature.hex()
            == "65c01d7c0ac26169d74d56612d1eab3a00c82b2f57af6b4aebbf39aa75e0f5e973d7daabb00bfad14d2f8bf63936ca9d69ef8fb76b8ac9c8ad0d2f808936930e"
        )
        assert (
            transaction.data.decode()
            == "unBond@e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"
        )

    def test_create_transaction_for_unjailing(self):
        transaction = self.controller.create_transaction_for_unjailing(
            sender=self.alice,
            nonce=7,
            public_keys=[self.validator_pubkey],
            amount=2500000000000000000000,
        )

        assert transaction.sender.to_bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver.to_bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
        assert transaction.value == 2500000000000000000000
        assert transaction.nonce == 7
        assert transaction.gas_limit == 5348500
        assert transaction.chain_id == "localnet"
        assert transaction.version == 2
        assert transaction.options == 0
        assert transaction.guardian is None
        assert transaction.relayer is None
        assert (
            transaction.signature.hex()
            == "5e682ba1e16b62971d3c6e6943ec954eb29fc31d8794d21afdd9e2c4ea5ba209a59cba8bd39c2a6ab9f80f066d558679e5b22bfca561caedbfa6a7297ad97d00"
        )
        assert (
            transaction.data.decode()
            == "unJail@e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"
        )

    def test_create_transaction_for_changing_rewards_address(self):
        transaction = self.controller.create_transaction_for_changing_rewards_address(
            sender=self.alice,
            nonce=7,
            rewards_address=self.reward_address,
        )

        assert transaction.sender.to_bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver.to_bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
        assert transaction.value == 0
        assert transaction.nonce == 7
        assert transaction.gas_limit == 5176000
        assert transaction.chain_id == "localnet"
        assert transaction.version == 2
        assert transaction.options == 0
        assert transaction.guardian is None
        assert transaction.relayer is None
        assert (
            transaction.signature.hex()
            == "565e64ea28d48150e3798e20c0a0a0294374992ed05e5153e93339b3f86acdd25db308b474dd8315a544d6e375ed9e07b01c3475bdc7986fde79eae26bd5a40c"
        )
        assert (
            transaction.data.decode()
            == "changeRewardAddress@b2a11555ce521e4944e09ab17549d85b487dcd26c84b5017a39e31a3670889ba"
        )

    def test_create_transaction_for_claiming(self):
        transaction = self.controller.create_transaction_for_claiming(
            sender=self.alice,
            nonce=7,
        )

        assert transaction.sender.to_bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver.to_bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
        assert transaction.value == 0
        assert transaction.nonce == 7
        assert transaction.gas_limit == 5057500
        assert transaction.chain_id == "localnet"
        assert transaction.version == 2
        assert transaction.options == 0
        assert transaction.guardian is None
        assert transaction.relayer is None
        assert transaction.data.decode() == "claim"
        assert (
            transaction.signature.hex()
            == "be19a2c0bf5ce1da5f72a7451bff57725161bb67a8b85e397d44570585e6b7ff40858b0d30fd9a12f06c70655b1c417389f25059e0a95dc76e488185cea68208"
        )

    def test_create_transaction_for_unstaking_nodes(self):
        transaction = self.controller.create_transaction_for_unstaking_nodes(
            sender=self.alice,
            nonce=7,
            public_keys=[self.validator_pubkey],
        )

        assert transaction.sender.to_bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver.to_bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
        assert transaction.value == 0
        assert transaction.nonce == 7
        assert transaction.gas_limit == 5357500
        assert transaction.chain_id == "localnet"
        assert transaction.version == 2
        assert transaction.options == 0
        assert transaction.guardian is None
        assert transaction.relayer is None
        assert (
            transaction.signature.hex()
            == "983b3127490949bc29e722a40a87871e88a6eb085fffb4d2801b2a79b39ff0aa395a39dc03367edb5f3858ed7ad9bea7b0c141110717cb639c45010055254606"
        )
        assert (
            transaction.data.decode()
            == "unStakeNodes@e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"
        )

    def test_create_transaction_for_unstaking_tokens(self):
        transaction = self.controller.create_transaction_for_unstaking_tokens(
            sender=self.alice,
            nonce=7,
            amount=11000000000000000000,
        )

        assert transaction.sender.to_bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver.to_bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
        assert transaction.value == 0
        assert transaction.nonce == 7
        assert transaction.gas_limit == 5095000
        assert transaction.chain_id == "localnet"
        assert transaction.version == 2
        assert transaction.options == 0
        assert transaction.guardian is None
        assert transaction.relayer is None
        assert (
            transaction.signature.hex()
            == "ed8e401e875d70bc3a62bf966fc8a9ecda2d49a851fe216f265176be5ab43040a85df55798dc828c928079573e2aa8dc52627e87c92824d8c91fdc3f3d195e0a"
        )
        assert transaction.data.decode() == "unStakeTokens@98a7d9b8314c0000"

    def test_create_transaction_for_unbonding_nodes(self):
        transaction = self.controller.create_transaction_for_unbonding_nodes(
            sender=self.alice,
            nonce=7,
            public_keys=[self.validator_pubkey],
        )

        assert transaction.sender.to_bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver.to_bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
        assert transaction.value == 0
        assert transaction.nonce == 7
        assert transaction.gas_limit == 5356000
        assert transaction.chain_id == "localnet"
        assert transaction.version == 2
        assert transaction.options == 0
        assert transaction.guardian is None
        assert transaction.relayer is None
        assert (
            transaction.signature.hex()
            == "ee261c7e7f1dc7822b31c609c570ba1b1da3e39ea68e231f2aea30ca9f70e0f61679f81739f22eee338fa9b8c14d498ca8892cde118d53b08f1440fe3737eb02"
        )
        assert (
            transaction.data.decode()
            == "unBondNodes@e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"
        )

    def test_create_transaction_for_unbonding_tokens(self):
        transaction = self.controller.create_transaction_for_unbonding_tokens(
            sender=self.alice,
            nonce=7,
            amount=20000000000000000000,
        )

        assert transaction.sender.to_bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver.to_bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
        assert transaction.value == 0
        assert transaction.nonce == 7
        assert transaction.gas_limit == 5096500
        assert transaction.chain_id == "localnet"
        assert transaction.version == 2
        assert transaction.options == 0
        assert transaction.guardian is None
        assert transaction.relayer is None
        assert (
            transaction.signature.hex()
            == "a7c96028a97d035c0068b9c2a4bbc4ee3b9613d81dfa4c388fd8a90e66f4e200e715e87a760c0a7d456f3b3a4dc225f760084477cb15ac690c9e1cb7c006f70d"
        )
        assert transaction.data.decode() == "unBondTokens@01158e460913d00000"

    def test_create_transaction_for_cleaning_registered_data(self):
        transaction = self.controller.create_transaction_for_cleaning_registered_data(
            sender=self.alice,
            nonce=7,
        )

        assert transaction.sender.to_bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver.to_bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
        assert transaction.value == 0
        assert transaction.nonce == 7
        assert transaction.gas_limit == 5078500
        assert transaction.chain_id == "localnet"
        assert transaction.version == 2
        assert transaction.options == 0
        assert transaction.guardian is None
        assert transaction.relayer is None
        assert (
            transaction.signature.hex()
            == "005c35ccf2bbffbc753c8971aba1edffb43dbad1db62a88a26d295445937bb7f84dfd26e31329f8622ec9b53c5be4a39f1dd8ab83189f2cd5211c1c8541d7b00"
        )
        assert transaction.data.decode() == "cleanRegisteredData"

    def test_create_transaction_for_restaking_unstaked_nodes(self):
        transaction = self.controller.create_transaction_for_restaking_unstaked_nodes(
            sender=self.alice,
            nonce=7,
            public_keys=[self.validator_pubkey],
        )

        assert transaction.sender.to_bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.receiver.to_bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
        assert transaction.value == 0
        assert transaction.nonce == 7
        assert transaction.gas_limit == 5369500
        assert transaction.chain_id == "localnet"
        assert transaction.version == 2
        assert transaction.options == 0
        assert transaction.guardian is None
        assert transaction.relayer is None
        assert (
            transaction.signature.hex()
            == "5f2196b81d9a72df401655becfc31e4167d89e76235f52abf506f9d9b10375b8b699339693b3f2d12552366e38ec2722a2ed50490a2beeaee0ae819d08f1ea0e"
        )
        assert (
            transaction.data.decode()
            == "reStakeUnStakedNodes@e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"
        )
