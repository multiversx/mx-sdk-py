import json
import os
from pathlib import Path

from multiversx_sdk_core import Address, AddressConverter, Message, Transaction

from multiversx_sdk_wallet.crypto.randomness import Randomness
from multiversx_sdk_wallet.user_keys import UserSecretKey
from multiversx_sdk_wallet.user_pem import UserPEM
from multiversx_sdk_wallet.user_signer import UserSigner
from multiversx_sdk_wallet.user_verifer import UserVerifier
from multiversx_sdk_wallet.user_wallet import UserWallet

DUMMY_MNEMONIC = "moral volcano peasant pass circle pen over picture flat shop clap goat never lyrics gather prepare woman film husband gravity behind test tiger improve"


def test_user_secret_key_create():
    buffer_hex = "413f42575f7f26fad3317a778771212fdb80245850981e48b58a4f25e344e8f9"
    buffer = bytes.fromhex(buffer_hex)
    secret_key = UserSecretKey(buffer)
    secret_key_from_string = UserSecretKey.from_string(buffer_hex)

    assert secret_key.hex() == buffer_hex
    assert secret_key_from_string.hex() == buffer_hex


def test_user_secret_key_generate_public_key():
    assert UserSecretKey.from_string("413f42575f7f26fad3317a778771212fdb80245850981e48b58a4f25e344e8f9").generate_public_key().hex() == "0139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1"
    assert UserSecretKey.from_string("b8ca6f8203fb4b545a8e83c5384da033c415db155b53fb5b8eba7ff5a039d639").generate_public_key().hex() == "8049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f8"
    assert UserSecretKey.from_string("e253a571ca153dc2aee845819f74bcc9773b0586edead15a94cb7235a5027436").generate_public_key().hex() == "b2a11555ce521e4944e09ab17549d85b487dcd26c84b5017a39e31a3670889ba"


def test_from_pem_file():
    converter = AddressConverter()

    pubkey = UserSigner.from_pem_file(Path("./multiversx_sdk_wallet/testdata/alice.pem"), 0).get_pubkey()
    assert converter.pubkey_to_bech32(pubkey.buffer) == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"

    pubkey = UserSigner.from_pem_file(Path("./multiversx_sdk_wallet/testdata/bob.pem"), 0).get_pubkey()
    assert converter.pubkey_to_bech32(pubkey.buffer) == "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"

    pubkey = UserSigner.from_pem_file(Path("./multiversx_sdk_wallet/testdata/carol.pem"), 0).get_pubkey()
    assert converter.pubkey_to_bech32(pubkey.buffer) == "erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8"


def test_user_wallet_to_keyfile_object_using_known_test_wallets_with_their_randomness():
    alice_secret_key = UserSecretKey.from_string("413f42575f7f26fad3317a778771212fdb80245850981e48b58a4f25e344e8f9")
    alice_wallet = UserWallet.from_secret_key(alice_secret_key, "password", Randomness(
        salt=bytes.fromhex("4903bd0e7880baa04fc4f886518ac5c672cdc745a6bd13dcec2b6c12e9bffe8d"),
        iv=bytes.fromhex("033182afaa1ebaafcde9ccc68a5eac31"),
        id="0dc10c02-b59b-4bac-9710-6b2cfa4284ba"
    ))

    bob_secret_key = UserSecretKey.from_string("b8ca6f8203fb4b545a8e83c5384da033c415db155b53fb5b8eba7ff5a039d639")
    bob_wallet = UserWallet.from_secret_key(bob_secret_key, "password", Randomness(
        salt=bytes.fromhex("18304455ac2dbe2a2018bda162bd03ef95b81622e99d8275c34a6d5e6932a68b"),
        iv=bytes.fromhex("18378411e31f6c4e99f1435d9ab82831"),
        id="85fdc8a7-7119-479d-b7fb-ab4413ed038d"
    ))

    carol_secret_key = UserSecretKey.from_string("e253a571ca153dc2aee845819f74bcc9773b0586edead15a94cb7235a5027436")
    carol_wallet = UserWallet.from_secret_key(carol_secret_key, "password", Randomness(
        salt=bytes.fromhex("4f2f5530ce28dc0210962589b908f52714f75c8fb79ff18bdd0024c43c7a220b"),
        iv=bytes.fromhex("258ed2b4dc506b4dc9d274b0449b0eb0"),
        id="65894f35-d142-41d2-9335-6ad02e0ed0be"
    ))

    with open("./multiversx_sdk_wallet/testdata/alice.json") as f:
        assert json.load(f) == alice_wallet.to_dict("erd")

    with open("./multiversx_sdk_wallet/testdata/bob.json") as f:
        assert json.load(f) == bob_wallet.to_dict("erd")

    with open("./multiversx_sdk_wallet/testdata/carol.json") as f:
        assert json.load(f) == carol_wallet.to_dict("erd")


def test_user_wallet_encrypt_then_decrypt():
    alice_secret_key = UserSecretKey.from_string("413f42575f7f26fad3317a778771212fdb80245850981e48b58a4f25e344e8f9")
    alice_wallet = UserWallet.from_secret_key(alice_secret_key, "password")
    alice_keyfile_object = alice_wallet.to_dict("erd")
    decrypted_secret_key = UserWallet.decrypt_secret_key(alice_keyfile_object, "password")
    assert decrypted_secret_key.buffer == alice_secret_key.buffer

    bob_secret_key = UserSecretKey.from_string("b8ca6f8203fb4b545a8e83c5384da033c415db155b53fb5b8eba7ff5a039d639")
    bob_wallet = UserWallet.from_secret_key(bob_secret_key, "password")
    bob_keyfile_object = bob_wallet.to_dict("erd")
    decrypted_secret_key = UserWallet.decrypt_secret_key(bob_keyfile_object, "password")
    assert decrypted_secret_key.buffer == bob_secret_key.buffer

    carol_secret_key = UserSecretKey.from_string("e253a571ca153dc2aee845819f74bcc9773b0586edead15a94cb7235a5027436")
    carol_wallet = UserWallet.from_secret_key(carol_secret_key, "password")
    carol_keyfile_object = carol_wallet.to_dict("erd")
    decrypted_secret_key = UserWallet.decrypt_secret_key(carol_keyfile_object, "password")
    assert decrypted_secret_key.buffer == carol_secret_key.buffer


def test_sign_transaction():
    """
    Also see: https://github.com/multiversx/mx-chain-go/blob/master/examples/construction_test.go
    """

    tx = Transaction(
        nonce=89,
        value="0",
        receiver=Address.from_bech32("erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"),
        sender=Address.from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"),
        data=None,
        gas_price=1000000000,
        gas_limit=50000,
        chain_id="local-testnet",
        version=1,
        options=0
    )

    signer = UserSigner.from_pem_file(Path("./multiversx_sdk_wallet/testdata/alice.pem"))
    verifier = UserVerifier.from_address(Address.from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"))

    tx.signature = signer.sign(tx)
    assert tx.signature.hex() == "b56769014f2bdc5cf9fc4a05356807d71fcf8775c819b0f1b0964625b679c918ffa64862313bfef86f99b38cb84fcdb16fa33ad6eb565276616723405cd8f109"
    assert verifier.verify(tx)


def test_sign_message():
    message = Message.from_string("hello")

    signer = UserSigner.from_pem_file(Path("./multiversx_sdk_wallet/testdata/alice.pem"))
    verifier = UserVerifier.from_address(Address.from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"))

    message.signature = signer.sign(message)
    assert message.signature.hex() == "66dd503199222d3104cb5381da953b14c895ca564579f98934c4e54a45d75f097da2a0c30060c0e7d014928b8e54509335cadc69b2bb1940cd59bd0c1bb80b0b"
    assert verifier.verify(message)


def test_pem_save():
    path = Path("./multiversx_sdk_wallet/testdata/alice.pem")
    path_saved = path.with_suffix(".saved")

    with open(path) as f:
        content_expected = f.read().strip()

    pem = UserPEM.from_file(path)
    pem.save(path_saved)

    with open(path_saved) as f:
        content_actual = f.read().strip()

    assert content_actual == content_expected
    os.remove(path_saved)


def test_decrypt_secret_key_from_file_but_without_kind_field():
    keystore_path = Path("./multiversx_sdk_wallet/testdata/withoutKind.json")
    secret_key = UserWallet.decrypt_secret_key_from_file(keystore_path, "password")
    actual_address = Address(secret_key.generate_public_key().buffer, "erd").bech32()
    assert actual_address == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"


def test_create_keystore_file_with_mnemonic():
    wallet = UserWallet.from_mnemonic(DUMMY_MNEMONIC, "password")
    keyfile_object = wallet.to_dict()

    assert keyfile_object["version"] == 4
    assert keyfile_object["kind"] == "mnemonic"
    assert "bech32" not in keyfile_object


def test_create_keystore_with_mnemonic_with_randomness():
    expected_dummy_wallet_json = Path("./multiversx_sdk_wallet/testdata/withDummyMnemonic.json").read_text()
    expected_dummy_wallet_dict = json.loads(expected_dummy_wallet_json)

    randomness = Randomness(
        id="5b448dbc-5c72-4d83-8038-938b1f8dff19",
        iv=bytes.fromhex("2da5620906634972d9a623bc249d63d4"),
        salt=bytes.fromhex("aa9e0ba6b188703071a582c10e5331f2756279feb0e2768f1ba0fd38ec77f035")
    )

    wallet = UserWallet.from_mnemonic(DUMMY_MNEMONIC, "password", randomness)
    wallet_dict = wallet.to_dict()

    assert wallet_dict == expected_dummy_wallet_dict


def test_decrypt_keystore_file_with_mnemonic():
    keystore_path = Path("./multiversx_sdk_wallet/testdata/withDummyMnemonic.json")
    mnemonic = UserWallet.decrypt_mnemonic_from_file(keystore_path, "password")

    assert mnemonic.get_text() == DUMMY_MNEMONIC
    assert mnemonic.derive_key(0).generate_public_key().to_address("erd").bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
    assert mnemonic.derive_key(1).generate_public_key().to_address("erd").bech32() == "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"
    assert mnemonic.derive_key(2).generate_public_key().to_address("erd").bech32() == "erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8"
