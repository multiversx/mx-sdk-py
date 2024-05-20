import pytest

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.errors import ErrInvalidRelayerV1BuilderArguments
from multiversx_sdk.core.token_payment import TokenPayment
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transaction_builders.relayed_v1_builder import \
    RelayedTransactionV1Builder
from multiversx_sdk.core.transaction_computer import TransactionComputer
from multiversx_sdk.testutils.wallets import load_wallets


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
        inner_tx.signature = self.bob.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(inner_tx))

        relayed_builder = RelayedTransactionV1Builder()
        relayed_builder.set_inner_transaction(inner_tx)
        relayed_builder.set_relayer_nonce(2627)
        relayed_builder.set_network_config(network_config)
        relayed_builder.set_relayer_address(Address.new_from_bech32(self.alice.label))

        relayed_tx = relayed_builder.build()
        relayed_tx.signature = self.alice.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(relayed_tx))

        assert relayed_tx.nonce == 2627
        assert relayed_tx.data.decode() == "relayedTx@7b226e6f6e6365223a3139382c2273656e646572223a2267456e574f65576d6d413063306a6b71764d354241707a61644b46574e534f69417643575163776d4750673d222c227265636569766572223a22414141414141414141414141415141414141414141414141414141414141414141414141414141432f2f383d222c2276616c7565223a302c226761735072696365223a313030303030303030302c226761734c696d6974223a36303030303030302c2264617461223a225a3256305132397564484a68593352446232356d6157633d222c227369676e6174757265223a2272525455544858677a4273496e4f6e454b6b7869642b354e66524d486e33534948314673746f577352434c434b3258514c41614f4e704449346531476173624c5150616130566f364144516d4f2b52446b6f364a43413d3d222c22636861696e4944223a2256413d3d222c2276657273696f6e223a327d"
        assert relayed_tx.signature.hex() == "128e7cdc14c2b9beee2f3ff7a7fa5d1f5ef31a654a0c92e223c90ab28265fa277d306f23a06536248cf9573e828017004fb639617fade4d68a37524aafca710d"

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
        inner_tx.guardian_signature = self.grace.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(inner_tx))

        relayed_builder = RelayedTransactionV1Builder()
        relayed_builder.set_inner_transaction(inner_tx)
        relayed_builder.set_relayer_nonce(2627)
        relayed_builder.set_network_config(network_config)
        relayed_builder.set_relayer_address(Address.new_from_bech32(self.alice.label))

        relayed_tx = relayed_builder.build()
        relayed_tx.signature = self.alice.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(relayed_tx))

        assert relayed_tx.nonce == 2627
        assert relayed_tx.data.decode() == "relayedTx@7b226e6f6e6365223a3139382c2273656e646572223a2267456e574f65576d6d413063306a6b71764d354241707a61644b46574e534f69417643575163776d4750673d222c227265636569766572223a22414141414141414141414146414b565841323879704877692f79693741364c64504b704f68464d386958513d222c2276616c7565223a302c226761735072696365223a313030303030303030302c226761734c696d6974223a36303030303030302c2264617461223a225a3256305132397564484a68593352446232356d6157633d222c227369676e6174757265223a224b4b78324f33383655725135416b4f465258307578327933446a384853334b373038487174344668377161557669424550716c45614e746e6158706a6f2f333651476d4a456934784435457a6c6f4f677a634d4442773d3d222c22636861696e4944223a2256413d3d222c2276657273696f6e223a322c226f7074696f6e73223a322c22677561726469616e223a22486f714c61306e655733766843716f56696c70715372744c5673774939535337586d7a563868477450684d3d222c22677561726469616e5369676e6174757265223a222b5431526f4833625a792f54423177342b6a365155477258645637457577553073753948646551626453515269463953757a686d634b705463526d58595252366c534c6652394931624d7134674730436538363741513d3d227d"
        assert relayed_tx.signature.hex() == "39cff9d5100e290fbc7361cb6e2402261caf864257b4116f150e0c61e7869155dff8361fa5449431eb7a8ed847c01ba9b3b5ebafe5fac1a3d40c64829d827e00"

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
        inner_tx.guardian_signature = self.grace.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(inner_tx))

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
        relayed_tx.guardian_signature = self.frank.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(inner_tx))

        assert relayed_tx.nonce == 2627
        assert relayed_tx.data.decode() == "relayedTx@7b226e6f6e6365223a3139382c2273656e646572223a2267456e574f65576d6d413063306a6b71764d354241707a61644b46574e534f69417643575163776d4750673d222c227265636569766572223a22414141414141414141414146414b565841323879704877692f79693741364c64504b704f68464d386958513d222c2276616c7565223a302c226761735072696365223a313030303030303030302c226761734c696d6974223a36303030303030302c2264617461223a225957526b546e5674596d5679222c227369676e6174757265223a223469724d4b4a656d724d375174344e7635487633544c44683775654779487045564c4371674a3677652f7a662b746a4933354975573452633458543451533433475333356158386c6a533834324a38426854645043673d3d222c22636861696e4944223a2256413d3d222c2276657273696f6e223a322c226f7074696f6e73223a322c22677561726469616e223a22486f714c61306e655733766843716f56696c70715372744c5673774939535337586d7a563868477450684d3d222c22677561726469616e5369676e6174757265223a2270424754394e674a78307539624c56796b654d78786a454865374269696c37764932324a46676f32787a6e2f496e3032463769546563356b44395045324f747065386c475335412b532f4a36417762576834446744673d3d227d"
        assert relayed_tx.signature.hex() == "8ede1bbeed96b102344dffeac12c2592c62b7313cdeb132e8c8bf11d2b1d3bb8189d257a6dbcc99e222393d9b9ec77656c349dae97a32e68bdebd636066bf706"

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
            value=TokenPayment.egld_from_amount(1).amount_as_integer
        )
        inner_tx.signature = self.carol.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(inner_tx))

        builder = RelayedTransactionV1Builder()
        builder.set_inner_transaction(inner_tx)
        builder.set_relayer_nonce(715)
        builder.set_network_config(network_config)
        builder.set_relayer_address(Address.new_from_bech32(self.frank.label))

        relayed_tx = builder.build()
        relayed_tx.signature = self.frank.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(relayed_tx))

        assert relayed_tx.nonce == 715
        assert relayed_tx.data.decode() == "relayedTx@7b226e6f6e6365223a3230382c2273656e646572223a227371455656633553486b6c45344a717864556e59573068397a536249533141586f3534786f32634969626f3d222c227265636569766572223a2241546c484c76396f686e63616d433877673970645168386b77704742356a6949496f3349484b594e6165453d222c2276616c7565223a313030303030303030303030303030303030302c226761735072696365223a313030303030303030302c226761734c696d6974223a35303030302c2264617461223a22222c227369676e6174757265223a226a33427a6469554144325963517473576c65707663664a6f75657a48573063316b735a424a4d6339573167435450512b6870636759457858326f6f367a4b5654347464314b4b6f79783841526a346e336474576c44413d3d222c22636861696e4944223a2256413d3d222c2276657273696f6e223a322c22736e64557365724e616d65223a22593246796232773d222c22726376557365724e616d65223a22595778705932553d227d"
        assert relayed_tx.signature.hex() == "3787d640e5a579e7977a4a1bcdd435ad11855632fa4a414a06fbf8355692d1a58d76ef0adbdd6ccd6bd3c329f36bd53c180d4873ec1a6c558e659aeb9ab92d00"
