from pathlib import Path

import pytest

from multiversx_sdk.core.constants import \
    MIN_TRANSACTION_VERSION_THAT_SUPPORTS_OPTIONS
from multiversx_sdk.core.errors import BadUsageError, NotEnoughGasError
from multiversx_sdk.core.proto.transaction_serializer import ProtoSerializer
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transaction_computer import TransactionComputer
from multiversx_sdk.testutils.wallets import load_wallets
from multiversx_sdk.wallet import UserSecretKey
from multiversx_sdk.wallet.user_pem import UserPEM
from multiversx_sdk.wallet.user_verifer import UserVerifier


class NetworkConfig:
    def __init__(self, min_gas_limit: int = 50000) -> None:
        self.min_gas_limit = min_gas_limit
        self.gas_per_data_byte = 1500
        self.gas_price_modifier = 0.01
        self.chain_id = "D"


class TestTransaction:
    wallets = load_wallets()
    alice = wallets["alice"]
    bob = wallets["bob"]
    carol = wallets["carol"]
    transaction_computer = TransactionComputer()

    def test_serialize_for_signing(self):
        sender = "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        receiver = "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"

        transaction = Transaction(
            nonce=89,
            sender=sender,
            receiver=receiver,
            value=0,
            gas_limit=50000,
            gas_price=1000000000,
            chain_id="D",
            version=1
        )
        serialized_tx = self.transaction_computer.compute_bytes_for_signing(transaction)
        assert serialized_tx.decode() == r"""{"nonce":89,"value":"0","receiver":"erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx","sender":"erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th","gasPrice":1000000000,"gasLimit":50000,"chainID":"D","version":1}"""

        transaction = Transaction(
            nonce=90,
            sender=sender,
            receiver=receiver,
            value=1000000000000000000,
            data=b"hello",
            gas_limit=70000,
            gas_price=1000000000,
            chain_id="D",
            version=1
        )
        serialized_tx = self.transaction_computer.compute_bytes_for_signing(transaction)
        assert serialized_tx.decode() == r"""{"nonce":90,"value":"1000000000000000000","receiver":"erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx","sender":"erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th","gasPrice":1000000000,"gasLimit":70000,"data":"aGVsbG8=","chainID":"D","version":1}"""

    def test_with_usernames(self):
        transaction = Transaction(
            chain_id="T",
            sender=self.carol.label,
            receiver=self.alice.label,
            nonce=204,
            gas_limit=50000,
            sender_username="carol",
            receiver_username="alice",
            value=1000000000000000000
        )

        transaction.signature = self.carol.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(transaction))
        assert transaction.signature.hex() == "51e6cd78fb3ab4b53ff7ad6864df27cb4a56d70603332869d47a5cf6ea977c30e696103e41e8dddf2582996ad335229fdf4acb726564dbc1a0bc9e705b511f06"

    def test_compute_transaction_hash(self):
        transaction = Transaction(
            sender="erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
            receiver="erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
            gas_limit=100000,
            chain_id="D",
            nonce=17243,
            value=1000000000000,
            data=b"testtx",
            version=2,
            signature=bytes.fromhex("eaa9e4dfbd21695d9511e9754bde13e90c5cfb21748a339a79be11f744c71872e9fe8e73c6035c413f5f08eef09e5458e9ea6fc315ff4da0ab6d000b450b2a07")
        )
        tx_hash = self.transaction_computer.compute_transaction_hash(transaction)
        assert tx_hash.hex() == "169b76b752b220a76a93aeebc462a1192db1dc2ec9d17e6b4d7b0dcc91792f03"

    def test_compute_transaction_hash_with_usernames(self):
        transaction = Transaction(
            sender="erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
            receiver="erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
            gas_limit=100000,
            chain_id="D",
            nonce=17244,
            value=1000000000000,
            data=b"testtx",
            version=2,
            sender_username="alice",
            receiver_username="alice",
            signature=bytes.fromhex("807bcd7de5553ea6dfc57c0510e84d46813c5963d90fec50991c500091408fcf6216dca48dae16a579a1611ed8b2834bae8bd0027dc17eb557963f7151b82c07")
        )
        tx_hash = self.transaction_computer.compute_transaction_hash(transaction)
        assert tx_hash.hex() == "41b5acf7ebaf4a9165a64206b6ebc02021b3adda55ffb2a2698aac2e7004dc29"

    def test_compute_transaction_fee_insufficient(self):
        transaction = Transaction(
            sender="erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
            receiver="erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
            gas_limit=50000,
            chain_id="D",
            data=b"toolittlegaslimit",
        )

        with pytest.raises(NotEnoughGasError):
            self.transaction_computer.compute_transaction_fee(transaction, NetworkConfig())

    def test_compute_transaction_fee(self):
        transaction = Transaction(
            sender="erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
            receiver="erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
            gas_price=500,
            gas_limit=20,
            chain_id="D",
        )

        computed_gas = self.transaction_computer.compute_transaction_fee(transaction, NetworkConfig(min_gas_limit=10))
        assert computed_gas == 5050

    def test_compute_transaction_fee_with_data_field(self):
        transaction = Transaction(
            sender="erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
            receiver="erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
            gas_price=500,
            gas_limit=12010,
            chain_id="D",
            data=b"testdata"
        )

        computed_gas = self.transaction_computer.compute_transaction_fee(transaction, NetworkConfig(min_gas_limit=10))
        assert computed_gas == 6005000

    def test_compute_transaction_with_guardian_fields(self):

        sender_secret_key_hex = "3964a58b0debd802f67239c30aa2b3a75fff1842c203587cb590d03d20e32415"
        sender_secret_key = UserSecretKey(bytes.fromhex(sender_secret_key_hex))

        transaction = Transaction(
            sender="erd1fp4zaxvyc8jh99vauwns99kvs9tn0k6cwrr0zpyz2jvyurcepuhsfzvlar",
            receiver="erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
            gas_limit=139000,
            gas_price=1000000000,
            chain_id="D",
            nonce=2,
            value=1000000000000000000,
            data=b"this is a test transaction",
            version=2,
            options=2,
            guardian="erd1nn8apn09vmf72l7kzr3nd90rr5r2q74he7hseghs3v68c5p7ud2qhhwf96",
            guardian_signature=bytes.fromhex("487150c26d38a01fe19fbe26dac20ec2b42ec3abf5763a47a508e62bcd6ad3437c4d404684442e864a1dbad446dc0f852889a09f0650b5fdb55f4ee18147920d")
        )

        transaction.signature = sender_secret_key.sign(self.transaction_computer.compute_bytes_for_signing(transaction))
        assert transaction.signature.hex() == "51434089b93d34ce5dfe9f7c8aa764e5654ed36ee9c54d465ce87d4399d71cf0745ca6c9c680727cf2788a5efbfebdbeececfa7b7497186c64975b7e6eb9f808"

        tx_hash = self.transaction_computer.compute_transaction_hash(transaction)
        assert tx_hash.hex() == "14a1ea3b73212efdcf4e66543b5e089437e72b8b069330312a0975f31e6c8a93"

    # this test was done to mimic the one in mx-chain-go
    def test_compute_transaction_with_dummy_guardian(self):
        alice_private_key_hex = "413f42575f7f26fad3317a778771212fdb80245850981e48b58a4f25e344e8f9"
        alice_secret_key = UserSecretKey(bytes.fromhex(alice_private_key_hex))

        transaction = Transaction(
            sender="erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
            receiver="erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
            gas_limit=150000,
            chain_id="local-testnet",
            gas_price=1000000000,
            data=b"test data field",
            version=2,
            options=2,
            nonce=92,
            value=123456789000000000000000000000,
            guardian="erd1x23lzn8483xs2su4fak0r0dqx6w38enpmmqf2yrkylwq7mfnvyhsxqw57y",
            guardian_signature=bytes([0] * 64)
        )

        transaction.signature = alice_secret_key.sign(self.transaction_computer.compute_bytes_for_signing(transaction))
        assert transaction.signature.hex() == "e574d78b19e1481a6b9575c162e66f2f906a3178aec537509356385c4f1a5330a9b73a87a456fc6d7041e93b5f8a1231a92fb390174872a104a0929215600c0c"

        proto_serializer = ProtoSerializer()
        serialized = proto_serializer.serialize_transaction(transaction)
        assert serialized.hex() == "085c120e00018ee90ff6181f3761632000001a208049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f82a200139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1388094ebdc0340f093094a0f746573742064617461206669656c64520d6c6f63616c2d746573746e657458026240e574d78b19e1481a6b9575c162e66f2f906a3178aec537509356385c4f1a5330a9b73a87a456fc6d7041e93b5f8a1231a92fb390174872a104a0929215600c0c6802722032a3f14cf53c4d0543954f6cf1bda0369d13e661dec095107627dc0f6d33612f7a4000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"

        tx_hash = self.transaction_computer.compute_transaction_hash(transaction)
        assert tx_hash.hex() == "242022e9dcfa0ee1d8199b0043314dbda8601619f70069ebc441b9f03349a35c"

    def test_tx_computer_has_options_set(self):
        tx = Transaction(
            sender="erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
            receiver="erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
            gas_limit=50000,
            chain_id="D",
            options=3
        )

        assert self.transaction_computer.has_options_set_for_guarded_transaction(tx)
        assert self.transaction_computer.has_options_set_for_hash_signing(tx)

    def test_tx_computer_apply_guardian(self):
        tx = Transaction(
            sender="erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
            receiver="erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
            gas_limit=200000,
            chain_id="D",
            version=1,
            options=1
        )

        self.transaction_computer.apply_guardian(
            transaction=tx,
            guardian="erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"
        )

        assert tx.version == 2
        assert tx.options == 3
        assert tx.guardian == "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"

    def test_sign_transaction_by_hash(self):
        parent = Path(__file__).parent.parent
        pem = UserPEM.from_file(parent / "testutils" / "testwallets" / "alice.pem")

        tx = Transaction(
            sender="erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
            receiver="erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
            value=0,
            gas_limit=50000,
            version=2,
            options=1,
            chain_id="integration tests chain ID",
            nonce=89
        )
        serialized = self.transaction_computer.compute_hash_for_signing(tx)
        tx.signature = pem.secret_key.sign(serialized)

        assert tx.signature.hex() == "f0c81f2393b1ec5972c813f817bae8daa00ade91c6f75ea604ab6a4d2797aca4378d783023ff98f1a02717fe4f24240cdfba0b674ee9abb18042203d713bc70a"

    def test_apply_guardian_with_hash_signing(self):
        tx = Transaction(
            sender="erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
            receiver="erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
            value=0,
            gas_limit=50000,
            version=1,
            chain_id="localnet",
            nonce=89
        )

        self.transaction_computer.apply_options_for_hash_signing(tx)
        assert tx.version == 2
        assert tx.options == 1

        self.transaction_computer.apply_guardian(transaction=tx, guardian=self.carol.label)
        assert tx.version == 2
        assert tx.options == 3

    def test_ensure_transaction_is_valid(self):
        tx = Transaction(
            sender="invalid_sender",
            receiver=self.bob.label,
            gas_limit=50000,
            chain_id=""
        )

        with pytest.raises(BadUsageError, match="Invalid `sender` field. Should be the bech32 address of the sender."):
            self.transaction_computer.compute_bytes_for_signing(tx)

        tx.sender = self.alice.label
        with pytest.raises(BadUsageError, match="The `chainID` field is not set"):
            self.transaction_computer.compute_bytes_for_signing(tx)

        tx.chain_id = "localnet"
        tx.version = 1
        tx.options = 2
        with pytest.raises(BadUsageError, match=f"Non-empty transaction options requires transaction version >= {MIN_TRANSACTION_VERSION_THAT_SUPPORTS_OPTIONS}"):
            self.transaction_computer.compute_bytes_for_signing(tx)

        self.transaction_computer.apply_options_for_hash_signing(tx)
        assert tx.version == 2
        assert tx.options == 3

    def test_compute_bytes_for_verifying_signature(self):
        tx = Transaction(
            sender=self.alice.label,
            receiver=self.bob.label,
            gas_limit=50000,
            chain_id="D",
            nonce=7
        )

        tx.signature = self.alice.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(tx))

        user_verifier = UserVerifier(self.alice.public_key)
        is_signed_by_alice = user_verifier.verify(
            data=self.transaction_computer.compute_bytes_for_verifying(tx),
            signature=tx.signature
        )

        wrong_verifier = UserVerifier(self.bob.public_key)
        is_signed_by_bob = wrong_verifier.verify(
            data=self.transaction_computer.compute_bytes_for_verifying(tx),
            signature=tx.signature
        )

        assert is_signed_by_alice == True
        assert is_signed_by_bob == False

    def test_compute_bytes_for_verifying_transaction_signed_by_hash(self):
        tx = Transaction(
            sender=self.alice.label,
            receiver=self.bob.label,
            gas_limit=50000,
            chain_id="D",
            nonce=7
        )
        self.transaction_computer.apply_options_for_hash_signing(tx)
        tx.signature = self.alice.secret_key.sign(self.transaction_computer.compute_hash_for_signing(tx))

        user_verifier = UserVerifier(self.alice.public_key)
        is_signed_by_alice = user_verifier.verify(
            data=self.transaction_computer.compute_bytes_for_verifying(tx),
            signature=tx.signature
        )

        wrong_verifier = UserVerifier(self.bob.public_key)
        is_signed_by_bob = wrong_verifier.verify(
            data=self.transaction_computer.compute_bytes_for_verifying(tx),
            signature=tx.signature
        )

        assert is_signed_by_alice == True
        assert is_signed_by_bob == False
