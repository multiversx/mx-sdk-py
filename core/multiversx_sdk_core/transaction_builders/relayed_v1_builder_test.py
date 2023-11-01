import pytest

from multiversx_sdk_core import TokenPayment
from multiversx_sdk_core.address import Address
from multiversx_sdk_core.errors import ErrInvalidRelayerV1BuilderArguments
from multiversx_sdk_core.testutils.wallets import load_wallets
from multiversx_sdk_core.transaction import Transaction, TransactionComputer
from multiversx_sdk_core.transaction_builders.relayed_v1_builder import \
    RelayedTransactionV1Builder


class NetworkConfig:
    def __init__(self) -> None:
        self.min_gas_limit = 50_000
        self.gas_per_data_byte = 1_500
        self.gas_price_modifier = 0.01
        self.chain_id = "T"


class TestRelayedV1Builder:
    wallets = load_wallets()
    alice = wallets["alice"]
    bob = wallets["bob"]
    frank = wallets["frank"]
    grace = wallets["grace"]
    carol = wallets["carol"]
    transaction_computer = TransactionComputer()

    def test_without_arguments(self):
        relayed_builder = RelayedTransactionV1Builder()

        with pytest.raises(ErrInvalidRelayerV1BuilderArguments):
            relayed_builder.build()

        inner_transaction = Transaction(
            chain_id="1",
            sender=self.alice.label,
            receiver="erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u",
            gas_limit=10000000,
            nonce=15,
            data=b"getContractConfig"
        )
        relayed_builder.set_inner_transaction(inner_transaction)

        with pytest.raises(ErrInvalidRelayerV1BuilderArguments):
            relayed_builder.build()

        network_config = NetworkConfig()
        relayed_builder.set_network_config(network_config)

        with pytest.raises(ErrInvalidRelayerV1BuilderArguments):
            relayed_builder.build()

    def test_compute_relayed_v1_tx(self):
        network_config = NetworkConfig()

        inner_tx = Transaction(
            chain_id=network_config.chain_id,
            sender=self.bob.label,
            receiver="erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u",
            gas_limit=60000000,
            nonce=198,
            data=b"getContractConfig"
        )
        # version is set to 1 to match the test in sdk-js-core
        inner_tx.version = 1
        inner_tx.signature = self.bob.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(inner_tx))

        relayed_builder = RelayedTransactionV1Builder()
        relayed_builder.set_inner_transaction(inner_tx)
        relayed_builder.set_relayer_nonce(2627)
        relayed_builder.set_network_config(network_config)
        relayed_builder.set_relayer_address(Address.new_from_bech32(self.alice.label))

        relayed_tx = relayed_builder.build()

        # version is set to 1 to match the test in sdk-js-core
        relayed_tx.version = 1

        relayed_tx.signature = self.alice.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(relayed_tx))

        assert relayed_tx.nonce == 2627
        assert relayed_tx.data.decode() == "relayedTx@7b226e6f6e6365223a3139382c2273656e646572223a2267456e574f65576d6d413063306a6b71764d354241707a61644b46574e534f69417643575163776d4750673d222c227265636569766572223a22414141414141414141414141415141414141414141414141414141414141414141414141414141432f2f383d222c2276616c7565223a302c226761735072696365223a313030303030303030302c226761734c696d6974223a36303030303030302c2264617461223a225a3256305132397564484a68593352446232356d6157633d222c227369676e6174757265223a2239682b6e6742584f5536776674315464437368534d4b3454446a5a32794f74686336564c576e3478724d5a706248427738677a6c6659596d362b766b505258303764634a562b4745635462616a7049692b5a5a5942773d3d222c22636861696e4944223a2256413d3d222c2276657273696f6e223a317d"
        assert relayed_tx.signature.hex() == "c7d2c3b971f44eca676c10624d3c4319f8898af159f003e1e59f446cb75e5a294c9f0758d800e04d3daff11e67d20c4c1f85fd54aad6deb947ef391e6dd09d07"

    def test_compute_guarded_inner_tx(self):
        network_config = NetworkConfig()

        inner_tx = Transaction(
            chain_id=network_config.chain_id,
            sender=self.bob.label,
            receiver="erd1qqqqqqqqqqqqqpgq54tsxmej537z9leghvp69hfu4f8gg5eu396q83gnnz",
            gas_limit=60000000,
            nonce=198,
            data=b"getContractConfig",
            guardian=self.grace.label,
            version=2,
            options=2
        )
        inner_tx.signature = self.bob.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(inner_tx))
        inner_tx.guardian_signature = bytes.fromhex("c72e08622c86d9b6889fb9f33eed75c6a04a940daa012825464c6ccaad71640cfcf5c4d38b36fb0575345bbec90daeb2db7a423bfb5253cef0ddc5c87d1b5f04")

        relayed_builder = RelayedTransactionV1Builder()
        relayed_builder.set_inner_transaction(inner_tx)
        relayed_builder.set_relayer_nonce(2627)
        relayed_builder.set_network_config(network_config)
        relayed_builder.set_relayer_address(Address.new_from_bech32(self.alice.label))

        relayed_tx = relayed_builder.build()
        # version is set to 1 to match the test in sdk-js-core
        relayed_tx.version = 1

        relayed_tx.signature = self.alice.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(relayed_tx))

        assert relayed_tx.nonce == 2627
        assert relayed_tx.data.decode() == "relayedTx@7b226e6f6e6365223a3139382c2273656e646572223a2267456e574f65576d6d413063306a6b71764d354241707a61644b46574e534f69417643575163776d4750673d222c227265636569766572223a22414141414141414141414146414b565841323879704877692f79693741364c64504b704f68464d386958513d222c2276616c7565223a302c226761735072696365223a313030303030303030302c226761734c696d6974223a36303030303030302c2264617461223a225a3256305132397564484a68593352446232356d6157633d222c227369676e6174757265223a224b4b78324f33383655725135416b4f465258307578327933446a384853334b373038487174344668377161557669424550716c45614e746e6158706a6f2f333651476d4a456934784435457a6c6f4f677a634d4442773d3d222c22636861696e4944223a2256413d3d222c2276657273696f6e223a322c226f7074696f6e73223a322c22677561726469616e223a22486f714c61306e655733766843716f56696c70715372744c5673774939535337586d7a563868477450684d3d222c22677561726469616e5369676e6174757265223a227879344959697947326261496e376e7a507531317871424b6c4132714153676c526b7873797131785a417a3839635454697a6237425855305737374a44613679323370434f2f745355383777336358496652746642413d3d227d"
        assert relayed_tx.signature.hex() == "f3db6318406f01ef807f04039e33563f97c2eabc1c8a59b6e412429725f03242cba679c717b734cb06859ef8e14349edf1db5eb1a9b3d36697b922475ae7ea07"

    def test_guarded_inner_tx_and_guarded_relayed_tx(self):
        network_config = NetworkConfig()

        inner_tx = Transaction(
            chain_id=network_config.chain_id,
            sender=self.bob.label,
            receiver="erd1qqqqqqqqqqqqqpgq54tsxmej537z9leghvp69hfu4f8gg5eu396q83gnnz",
            gas_limit=60000000,
            nonce=198,
            data=b"addNumber",
            guardian=self.grace.label,
            version=2,
            options=2
        )
        inner_tx.signature = self.bob.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(inner_tx))
        inner_tx.guardian_signature = bytes.fromhex("b12d08732c86d9b6889fb9f33eed65c6a04a960daa012825464c6ccaad71640cfcf5c4d38b36fb0575345bbec90daeb2db7a423bfb5253cef0ddc5c87d1b5f04")

        relayed_builder = RelayedTransactionV1Builder()
        relayed_builder.set_inner_transaction(inner_tx)
        relayed_builder.set_relayer_nonce(2627)
        relayed_builder.set_network_config(network_config)
        relayed_builder.set_relayer_address(Address.new_from_bech32(self.alice.label))
        relayed_builder.set_relayed_transaction_version(2)
        relayed_builder.set_relayed_transaction_options(2)
        relayed_builder.set_relayed_transaction_guardian(Address.new_from_bech32(self.frank.label))

        relayed_tx = relayed_builder.build()
        relayed_tx.signature = self.alice.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(relayed_tx))

        relayed_tx.guardian_signature = bytes.fromhex("d32c08722c86d9b6889fb9f33eed65c6a04a970daa012825464c6ccaad71640cfcf5c4d38b36fb0575345bbec90daeb2db7a423bfb5253cef0ddc5c87d1b5f04")

        assert relayed_tx.nonce == 2627
        assert relayed_tx.data.decode() == "relayedTx@7b226e6f6e6365223a3139382c2273656e646572223a2267456e574f65576d6d413063306a6b71764d354241707a61644b46574e534f69417643575163776d4750673d222c227265636569766572223a22414141414141414141414146414b565841323879704877692f79693741364c64504b704f68464d386958513d222c2276616c7565223a302c226761735072696365223a313030303030303030302c226761734c696d6974223a36303030303030302c2264617461223a225957526b546e5674596d5679222c227369676e6174757265223a223469724d4b4a656d724d375174344e7635487633544c44683775654779487045564c4371674a3677652f7a662b746a4933354975573452633458543451533433475333356158386c6a533834324a38426854645043673d3d222c22636861696e4944223a2256413d3d222c2276657273696f6e223a322c226f7074696f6e73223a322c22677561726469616e223a22486f714c61306e655733766843716f56696c70715372744c5673774939535337586d7a563868477450684d3d222c22677561726469616e5369676e6174757265223a227353304963797947326261496e376e7a5075316c7871424b6c6732714153676c526b7873797131785a417a3839635454697a6237425855305737374a44613679323370434f2f745355383777336358496652746642413d3d227d"
        assert relayed_tx.signature.hex() == "15fe39045685625d0f1742e34ba7679d225d49fc1f1f2ab363b7e78beddb8d278d11f5658a0d0e996d28ba77c49bc6d614b62a4eb7e74f363546ecaa2a84d905"

    def test_compute_relayedV1_with_usernames(self):
        network_config = NetworkConfig()

        inner_tx = Transaction(
            chain_id=network_config.chain_id,
            sender=self.carol.label,
            receiver=self.alice.label,
            gas_limit=50000,
            sender_username="carol",
            receiver_username="alice",
            nonce=208,
            amount=TokenPayment.egld_from_amount(1).amount_as_integer
        )
        # version is set to 1 to match the test in sdk-js-core
        inner_tx.version = 1
        inner_tx.signature = self.carol.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(inner_tx))

        builder = RelayedTransactionV1Builder()
        builder.set_inner_transaction(inner_tx)
        builder.set_relayer_nonce(715)
        builder.set_network_config(network_config)
        builder.set_relayer_address(Address.new_from_bech32(self.frank.label))

        relayed_tx = builder.build()

        # version is set to 1 to match the test in sdk-js-core
        relayed_tx.version = 1

        relayed_tx.signature = self.frank.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(relayed_tx))

        assert relayed_tx.nonce == 715
        assert relayed_tx.data.decode() == "relayedTx@7b226e6f6e6365223a3230382c2273656e646572223a227371455656633553486b6c45344a717864556e59573068397a536249533141586f3534786f32634969626f3d222c227265636569766572223a2241546c484c76396f686e63616d433877673970645168386b77704742356a6949496f3349484b594e6165453d222c2276616c7565223a313030303030303030303030303030303030302c226761735072696365223a313030303030303030302c226761734c696d6974223a35303030302c2264617461223a22222c227369676e6174757265223a22744d616d736b6f315a574b526663594e4b5673793463797879643335764b754844576a3548706172344167734c2b4a4e585642545a574c754467384867514254476d724a6b49443133637050614c55322f38626644513d3d222c22636861696e4944223a2256413d3d222c2276657273696f6e223a312c22736e64557365724e616d65223a22593246796232773d222c22726376557365724e616d65223a22595778705932553d227d"
        assert relayed_tx.signature.hex() == "0fbab023085551b7c497e5c52f64df802cb518ebaac93f8897e5cca25a8aff447565fa96570f7b547f7c0d0fceb2c7d12bcb5f37fa92c79725d9b2c69039f00d"
