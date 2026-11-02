import json
from pathlib import Path
from typing import Any, Optional

import pytest

from multiversx_sdk.core import (
    Address,
    Message,
    MessageComputer,
    Transaction,
    TransactionComputer,
)
from multiversx_sdk.wallet import user_keys
from multiversx_sdk.wallet.crypto import encryptor
from multiversx_sdk.wallet.crypto.randomness import Randomness
from multiversx_sdk.wallet.errors import (
    InvalidAddressIndexError,
    InvalidKeystoreFileError,
    InvalidPemError,
)
from multiversx_sdk.wallet.pem_entry import PemEntry
from multiversx_sdk.wallet.user_keys import UserSecretKey
from multiversx_sdk.wallet.user_pem import UserPEM
from multiversx_sdk.wallet.user_signer import UserSigner
from multiversx_sdk.wallet.user_verifer import UserVerifier
from multiversx_sdk.wallet.user_wallet import UserWallet

testwallets = Path(__file__).parent.parent / "testutils" / "testwallets"
DUMMY_MNEMONIC = "moral volcano peasant pass circle pen over picture flat shop clap goat never lyrics gather prepare woman film husband gravity behind test tiger improve"


def test_user_secret_key_create():
    buffer_hex = "413f42575f7f26fad3317a778771212fdb80245850981e48b58a4f25e344e8f9"
    buffer = bytes.fromhex(buffer_hex)
    secret_key = UserSecretKey(buffer)
    secret_key_from_string = UserSecretKey.new_from_string(buffer_hex)

    assert secret_key.hex() == buffer_hex
    assert secret_key_from_string.hex() == buffer_hex


def test_user_secret_key_generate_public_key():
    assert (
        UserSecretKey.new_from_string("413f42575f7f26fad3317a778771212fdb80245850981e48b58a4f25e344e8f9")
        .generate_public_key()
        .hex()
        == "0139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1"
    )
    assert (
        UserSecretKey.new_from_string("b8ca6f8203fb4b545a8e83c5384da033c415db155b53fb5b8eba7ff5a039d639")
        .generate_public_key()
        .hex()
        == "8049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f8"
    )
    assert (
        UserSecretKey.new_from_string("e253a571ca153dc2aee845819f74bcc9773b0586edead15a94cb7235a5027436")
        .generate_public_key()
        .hex()
        == "b2a11555ce521e4944e09ab17549d85b487dcd26c84b5017a39e31a3670889ba"
    )


def test_user_signer_from_pem_file():
    pubkey = UserSigner.from_pem_file(testwallets / "alice.pem", 0).get_pubkey()
    assert Address(pubkey.buffer, "erd").to_bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"

    pubkey = UserSigner.from_pem_file(testwallets / "bob.pem", 0).get_pubkey()
    assert Address(pubkey.buffer, "erd").to_bech32() == "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"

    pubkey = UserSigner.from_pem_file(testwallets / "carol.pem", 0).get_pubkey()
    assert Address(pubkey.buffer, "erd").to_bech32() == "erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8"


def test_load_signers_from_pem():
    signers = UserSigner.from_pem_file_all(testwallets / "multipleUserKeys.pem")

    assert len(signers) == 3
    assert (
        Address(signers[0].get_pubkey().buffer, "erd").to_bech32()
        == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
    )
    assert (
        Address(signers[1].get_pubkey().buffer, "erd").to_bech32()
        == "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"
    )
    assert (
        Address(signers[2].get_pubkey().buffer, "erd").to_bech32()
        == "erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8"
    )


def test_user_wallet_to_keyfile_object_using_known_test_wallets_with_their_randomness():
    alice_secret_key = UserSecretKey.new_from_string("413f42575f7f26fad3317a778771212fdb80245850981e48b58a4f25e344e8f9")
    alice_wallet = UserWallet.from_secret_key(
        alice_secret_key,
        "password",
        Randomness(
            salt=bytes.fromhex("4903bd0e7880baa04fc4f886518ac5c672cdc745a6bd13dcec2b6c12e9bffe8d"),
            iv=bytes.fromhex("033182afaa1ebaafcde9ccc68a5eac31"),
            id="0dc10c02-b59b-4bac-9710-6b2cfa4284ba",
        ),
    )

    bob_secret_key = UserSecretKey.new_from_string("b8ca6f8203fb4b545a8e83c5384da033c415db155b53fb5b8eba7ff5a039d639")
    bob_wallet = UserWallet.from_secret_key(
        bob_secret_key,
        "password",
        Randomness(
            salt=bytes.fromhex("18304455ac2dbe2a2018bda162bd03ef95b81622e99d8275c34a6d5e6932a68b"),
            iv=bytes.fromhex("18378411e31f6c4e99f1435d9ab82831"),
            id="85fdc8a7-7119-479d-b7fb-ab4413ed038d",
        ),
    )

    carol_secret_key = UserSecretKey.new_from_string("e253a571ca153dc2aee845819f74bcc9773b0586edead15a94cb7235a5027436")
    carol_wallet = UserWallet.from_secret_key(
        carol_secret_key,
        "password",
        Randomness(
            salt=bytes.fromhex("4f2f5530ce28dc0210962589b908f52714f75c8fb79ff18bdd0024c43c7a220b"),
            iv=bytes.fromhex("258ed2b4dc506b4dc9d274b0449b0eb0"),
            id="65894f35-d142-41d2-9335-6ad02e0ed0be",
        ),
    )

    alice_saved_path = testwallets / "alice.saved.json"
    bob_saved_path = testwallets / "bob.saved.json"
    carol_saved_path = testwallets / "carol.saved.json"

    alice_wallet.save(alice_saved_path, "erd")
    bob_wallet.save(bob_saved_path, "erd")
    carol_wallet.save(carol_saved_path, "erd")

    assert alice_saved_path.read_text().strip() == (testwallets / "alice.json").read_text().strip()
    assert bob_saved_path.read_text().strip() == (testwallets / "bob.json").read_text().strip()
    assert carol_saved_path.read_text().strip() == (testwallets / "carol.json").read_text().strip()

    alice_saved_path.unlink()
    bob_saved_path.unlink()
    carol_saved_path.unlink()


def test_user_wallet_encrypt_then_decrypt():
    alice_secret_key = UserSecretKey.new_from_string("413f42575f7f26fad3317a778771212fdb80245850981e48b58a4f25e344e8f9")
    alice_wallet = UserWallet.from_secret_key(alice_secret_key, "password")
    alice_keyfile_object = alice_wallet.to_dict("erd")
    decrypted_secret_key = UserWallet.decrypt_secret_key(alice_keyfile_object, "password")
    assert decrypted_secret_key.buffer == alice_secret_key.buffer

    bob_secret_key = UserSecretKey.new_from_string("b8ca6f8203fb4b545a8e83c5384da033c415db155b53fb5b8eba7ff5a039d639")
    bob_wallet = UserWallet.from_secret_key(bob_secret_key, "password")
    bob_keyfile_object = bob_wallet.to_dict("erd")
    decrypted_secret_key = UserWallet.decrypt_secret_key(bob_keyfile_object, "password")
    assert decrypted_secret_key.buffer == bob_secret_key.buffer

    carol_secret_key = UserSecretKey.new_from_string("e253a571ca153dc2aee845819f74bcc9773b0586edead15a94cb7235a5027436")
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
        value=0,
        receiver=Address.new_from_bech32("erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"),
        sender=Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"),
        data=None,
        gas_price=1000000000,
        gas_limit=50000,
        chain_id="local-testnet",
        version=1,
        options=0,
    )

    signer = UserSigner.from_pem_file(testwallets / "alice.pem")
    verifier = UserVerifier.from_address(
        Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
    )
    transaction_computer = TransactionComputer()

    tx.signature = signer.sign(transaction_computer.compute_bytes_for_signing(tx))
    assert (
        tx.signature.hex()
        == "b56769014f2bdc5cf9fc4a05356807d71fcf8775c819b0f1b0964625b679c918ffa64862313bfef86f99b38cb84fcdb16fa33ad6eb565276616723405cd8f109"
    )
    assert verifier.verify(transaction_computer.compute_bytes_for_signing(tx), tx.signature)


def test_sign_message():
    message = Message(
        "hello".encode(),
        address=Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"),
    )
    message_computer = MessageComputer()

    signer = UserSigner.from_pem_file(testwallets / "alice.pem")
    verifier = UserVerifier.from_address(
        Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
    )

    message.signature = signer.sign(message_computer.compute_bytes_for_signing(message))
    assert (
        message.signature.hex()
        == "561bc58f1dc6b10de208b2d2c22c9a474ea5e8cabb59c3d3ce06bbda21cc46454aa71a85d5a60442bd7784effa2e062fcb8fb421c521f898abf7f5ec165e5d0f"
    )
    assert verifier.verify(message_computer.compute_bytes_for_signing(message), message.signature)


def test_user_pem_save():
    path = testwallets / "alice.pem"
    path_saved = path.with_suffix(".saved")
    content_expected = path.read_text().strip()

    pem = UserPEM.from_file(path)
    pem.save(path_saved)
    content_actual = path_saved.read_text().strip()

    assert content_actual == content_expected
    path_saved.unlink()


def test_load_secret_key_but_without_kind_field():
    keystore_path = testwallets / "withoutKind.json"
    secret_key = UserWallet.load_secret_key(keystore_path, "password")
    actual_address = (secret_key.generate_public_key().to_address("erd")).to_bech32()
    assert actual_address == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"


def test_load_secret_key_with_unecessary_address_index():
    keystore_path = testwallets / "alice.json"

    with pytest.raises(Exception, match="address_index must not be provided when kind == 'secretKey'"):
        UserWallet.load_secret_key(keystore_path, "password", 42)


def test_create_keystore_file_with_mnemonic():
    wallet = UserWallet.from_mnemonic(DUMMY_MNEMONIC, "password")
    keyfile_object = wallet.to_dict()

    assert keyfile_object["version"] == 4
    assert keyfile_object["kind"] == "mnemonic"
    assert "bech32" not in keyfile_object


def test_create_keystore_with_mnemonic_with_randomness():
    expected_dummy_wallet_json = (testwallets / "withDummyMnemonic.json").read_text()
    expected_dummy_wallet_dict = json.loads(expected_dummy_wallet_json)

    randomness = Randomness(
        id="5b448dbc-5c72-4d83-8038-938b1f8dff19",
        iv=bytes.fromhex("2da5620906634972d9a623bc249d63d4"),
        salt=bytes.fromhex("aa9e0ba6b188703071a582c10e5331f2756279feb0e2768f1ba0fd38ec77f035"),
    )

    wallet = UserWallet.from_mnemonic(DUMMY_MNEMONIC, "password", randomness)
    wallet_dict = wallet.to_dict()

    assert wallet_dict == expected_dummy_wallet_dict


def test_load_secret_key_with_mnemonic():
    keystore_path = testwallets / "withDummyMnemonic.json"

    assert (
        UserWallet.load_secret_key(keystore_path, "password", 1).generate_public_key().to_address("erd").to_bech32()
        == "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"
    )
    assert (
        UserWallet.load_secret_key(keystore_path, "password", 2).generate_public_key().to_address("erd").to_bech32()
        == "erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8"
    )
    assert (
        UserWallet.load_secret_key(keystore_path, "password", 0).generate_public_key().to_address("erd").to_bech32()
        == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
    )


@pytest.mark.parametrize(
    "address_index, expected_address",
    [
        (None, "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"),
        (0, "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"),
        (1, "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"),
        (2, "erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8"),
    ],
)
def test_user_signer_from_wallet_with_mnemonic(address_index: Optional[int], expected_address: str):
    keystore_path = testwallets / "withDummyMnemonic.json"
    signer = UserSigner.from_wallet(keystore_path, "password", address_index)

    assert signer.get_pubkey().to_address("erd").to_bech32() == expected_address
    assert signer.secret_key == UserWallet.load_secret_key(keystore_path, "password", address_index)


def test_user_signer_from_wallet_with_secret_key():
    keystore_path = testwallets / "alice.json"

    # Backwards compatible: the index is optional.
    signer = UserSigner.from_wallet(keystore_path, "password")
    assert signer.get_pubkey().to_address("erd").to_bech32() == ALICE_BECH32

    # Same as "UserWallet.load_secret_key": an index makes no sense for a keystore holding a single secret key.
    with pytest.raises(Exception, match="address_index must not be provided when kind == 'secretKey'"):
        UserSigner.from_wallet(keystore_path, "password", 1)


@pytest.mark.parametrize("address_index", [-1, 2**31])
def test_user_signer_from_wallet_with_invalid_address_index(address_index: int):
    keystore_path = testwallets / "withDummyMnemonic.json"

    with pytest.raises(InvalidAddressIndexError):
        UserSigner.from_wallet(keystore_path, "password", address_index)


def test_decrypt_secret_key_with_keystore_mnemonic():
    user_wallet = UserWallet.from_mnemonic(DUMMY_MNEMONIC, "")
    mnemonic_json = user_wallet.to_dict()

    with pytest.raises(Exception, match="Expected kind to be secretKey, but it was mnemonic"):
        UserWallet.decrypt_secret_key(mnemonic_json, "")


def test_create_keystore_with_mnemonic_requiring_nfkd_normalization(tmp_path: Path):
    # The keystore must hold the canonical (NFKD-normalized) text, so that every SDK derives the same accounts from it.
    mnemonic = DUMMY_MNEMONIC.replace(" ", "\u00a0")
    wallet = UserWallet.from_mnemonic(mnemonic, "password")
    keystore_path = tmp_path / "wallet.json"
    wallet.save(keystore_path)

    keyfile_object = json.loads(keystore_path.read_text())
    assert UserWallet.decrypt_mnemonic(keyfile_object, "password").get_text() == DUMMY_MNEMONIC
    assert (
        UserWallet.load_secret_key(keystore_path, "password", 0).generate_public_key().to_address("erd").to_bech32()
        == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
    )


def test_load_secret_key_from_keystore_holding_non_normalized_mnemonic(tmp_path: Path):
    # Keystores written by older versions may contain the raw (non-normalized) text; they must derive the standard accounts.
    mnemonic = DUMMY_MNEMONIC.replace(" ", "\u3000")
    encrypted_data = encryptor.encrypt(mnemonic.encode(), "password", Randomness())
    keystore_path = tmp_path / "wallet.json"
    UserWallet(kind="mnemonic", encrypted_data=encrypted_data).save(keystore_path)

    assert (
        UserWallet.load_secret_key(keystore_path, "password", 1).generate_public_key().to_address("erd").to_bech32()
        == "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"
    )


ALICE_SECRET_KEY = "413f42575f7f26fad3317a778771212fdb80245850981e48b58a4f25e344e8f9"
ALICE_PUBLIC_KEY = "0139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1"
ALICE_BECH32 = "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
BOB_HEX = "8049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f8"
BOB_BECH32 = "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"


def _create_alice_keyfile_object_holding(plaintext: bytes) -> dict[str, Any]:
    # A keystore with a valid MAC (as created by anyone knowing the password), with alice's address in the envelope.
    alice_public_key = UserSecretKey.new_from_string(ALICE_SECRET_KEY).generate_public_key()
    encrypted_data = encryptor.encrypt(plaintext, "password", Randomness())
    wallet = UserWallet(
        kind="secretKey", encrypted_data=encrypted_data, public_key_when_kind_is_secret_key=alice_public_key
    )
    return wallet.to_dict("erd")


def test_decrypt_secret_key_with_tampered_iv():
    # The MAC does not cover the IV: such a file decrypts (without error) to a different key, which must be rejected.
    keyfile_object = json.loads((testwallets / "alice.json").read_text())
    iv = bytearray.fromhex(keyfile_object["crypto"]["cipherparams"]["iv"])
    iv[-1] ^= 1
    keyfile_object["crypto"]["cipherparams"]["iv"] = iv.hex()

    with pytest.raises(InvalidKeystoreFileError):
        UserWallet.decrypt_secret_key(keyfile_object, "password")


def test_decrypt_secret_key_with_address_fields_of_another_account():
    keyfile_object = json.loads((testwallets / "alice.json").read_text())

    with pytest.raises(InvalidKeystoreFileError, match="the 'address' field does not match"):
        UserWallet.decrypt_secret_key({**keyfile_object, "address": BOB_HEX}, "password")

    with pytest.raises(InvalidKeystoreFileError, match="the 'bech32' field does not match"):
        UserWallet.decrypt_secret_key({**keyfile_object, "bech32": BOB_BECH32}, "password")

    with pytest.raises(InvalidKeystoreFileError, match="the 'bech32' field does not match"):
        UserWallet.decrypt_secret_key({**keyfile_object, "bech32": "not a bech32 address"}, "password")


@pytest.mark.parametrize(
    "address",
    [
        ALICE_PUBLIC_KEY.upper(),
        ALICE_PUBLIC_KEY[:32].upper() + ALICE_PUBLIC_KEY[32:],
    ],
)
def test_decrypt_secret_key_with_address_field_in_any_case(address: str):
    keyfile_object = json.loads((testwallets / "alice.json").read_text())
    assert keyfile_object["address"] == ALICE_PUBLIC_KEY

    secret_key = UserWallet.decrypt_secret_key({**keyfile_object, "address": address}, "password")
    assert secret_key.hex() == ALICE_SECRET_KEY


def test_decrypt_secret_key_with_bech32_field_in_uppercase():
    keyfile_object = json.loads((testwallets / "alice.json").read_text())

    secret_key = UserWallet.decrypt_secret_key({**keyfile_object, "bech32": ALICE_BECH32.upper()}, "password")
    assert secret_key.hex() == ALICE_SECRET_KEY


@pytest.mark.parametrize(
    "address",
    [
        "",
        "not hex",
        ALICE_PUBLIC_KEY[:-2],  # one byte short
        ALICE_PUBLIC_KEY + "00",  # one byte too long
        ALICE_PUBLIC_KEY[:-1],  # odd number of digits
        "0x" + ALICE_PUBLIC_KEY,
    ],
)
def test_decrypt_secret_key_with_malformed_address_field(address: str):
    keyfile_object = json.loads((testwallets / "alice.json").read_text())

    with pytest.raises(InvalidKeystoreFileError, match="the 'address' field does not match"):
        UserWallet.decrypt_secret_key({**keyfile_object, "address": address}, "password")


@pytest.mark.parametrize("field", ["address", "bech32"])
def test_decrypt_secret_key_with_missing_address_field(field: str):
    keyfile_object = json.loads((testwallets / "alice.json").read_text())
    del keyfile_object[field]

    with pytest.raises(InvalidKeystoreFileError, match="missing 'address' or 'bech32' field"):
        UserWallet.decrypt_secret_key(keyfile_object, "password")


@pytest.mark.parametrize("length", [0, 1, 16, 31, 33, 63, 65, 100])
def test_decrypt_secret_key_with_unexpected_plaintext_length(length: int):
    # Previously, the plaintext was silently left-padded with zeros or truncated.
    plaintext = (bytes.fromhex(ALICE_SECRET_KEY) * 4)[:length]
    keyfile_object = _create_alice_keyfile_object_holding(plaintext)

    with pytest.raises(InvalidKeystoreFileError, match=f"unexpected length of decrypted data: {length}"):
        UserWallet.decrypt_secret_key(keyfile_object, "password")


def test_decrypt_secret_key_with_wrong_embedded_public_key():
    keyfile_object = _create_alice_keyfile_object_holding(bytes.fromhex(ALICE_SECRET_KEY) + bytes.fromhex(BOB_HEX))

    with pytest.raises(InvalidKeystoreFileError, match="the embedded public key does not match"):
        UserWallet.decrypt_secret_key(keyfile_object, "password")


def test_decrypt_secret_key_holding_only_the_secret_key():
    # E.g. keystores saved by mx-sdk-go hold the secret key alone (32 bytes).
    keyfile_object = _create_alice_keyfile_object_holding(bytes.fromhex(ALICE_SECRET_KEY))
    secret_key = UserWallet.decrypt_secret_key(keyfile_object, "password")
    assert secret_key.hex() == ALICE_SECRET_KEY


def test_decrypt_secret_key_with_custom_hrp():
    secret_key = UserSecretKey.new_from_string(ALICE_SECRET_KEY)
    keyfile_object = UserWallet.from_secret_key(secret_key, "password").to_dict("test")
    assert keyfile_object["bech32"].startswith("test1")

    assert UserWallet.decrypt_secret_key(keyfile_object, "password").hex() == ALICE_SECRET_KEY


def test_load_user_pem_with_wrong_embedded_public_key():
    text = PemEntry(ALICE_BECH32, bytes.fromhex(ALICE_SECRET_KEY + BOB_HEX)).to_text()

    with pytest.raises(InvalidPemError, match="the embedded public key does not match"):
        UserPEM.from_text(text)


@pytest.mark.parametrize("length", [33, 48, 63, 65, 96])
def test_load_user_pem_with_unexpected_message_length(length: int):
    message = (bytes.fromhex(ALICE_SECRET_KEY + ALICE_PUBLIC_KEY) * 2)[:length]
    text = PemEntry(ALICE_BECH32, message).to_text()

    with pytest.raises(InvalidPemError, match="the embedded public key does not match"):
        UserPEM.from_text(text)


def test_load_user_pem_with_label_of_another_account():
    text = PemEntry(BOB_BECH32, bytes.fromhex(ALICE_SECRET_KEY + ALICE_PUBLIC_KEY)).to_text()

    with pytest.raises(InvalidPemError, match="the label \\(address\\) does not match"):
        UserPEM.from_text(text)


@pytest.mark.parametrize(
    "label, message",
    [
        (ALICE_BECH32, ALICE_SECRET_KEY),  # only the secret key
        (
            "test1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ss5hqhtr",
            ALICE_SECRET_KEY + ALICE_PUBLIC_KEY,
        ),  # custom HRP
        ("my wallet", ALICE_SECRET_KEY + ALICE_PUBLIC_KEY),  # custom label
        ("", ALICE_SECRET_KEY + ALICE_PUBLIC_KEY),  # empty label
    ],
)
def test_load_user_pem_still_supported(label: str, message: str):
    text = PemEntry(label, bytes.fromhex(message)).to_text()
    pem = UserPEM.from_text(text)

    assert pem.label == label
    assert pem.secret_key.hex() == ALICE_SECRET_KEY


@pytest.mark.parametrize("index", [3, -1, -4])
def test_load_user_pem_with_index_out_of_range(index: int):
    # Previously, negative indices silently selected entries from the end.
    with pytest.raises(IndexError, match=f"PEM entry index {index} is out of range \\(number of entries: 3\\)"):
        UserPEM.from_file(testwallets / "multipleUserKeys.pem", index)

    with pytest.raises(IndexError, match=f"PEM entry index {index} is out of range"):
        UserPEM.from_text((testwallets / "multipleUserKeys.pem").read_text(), index)


@pytest.mark.parametrize("buffer", ["a" * 32, [0] * 32, memoryview(bytes(32)), None])
def test_user_secret_key_with_wrong_type(buffer: Any):
    # Previously, e.g. a 32-characters string was accepted, but failed later, when used.
    with pytest.raises(TypeError, match="The secret key must be bytes"):
        UserSecretKey(buffer)


def test_user_secret_key_is_not_altered_through_caller_buffer():
    buffer = bytearray.fromhex(ALICE_SECRET_KEY)
    secret_key = UserSecretKey(buffer)
    buffer[0] ^= 1

    assert secret_key.hex() == ALICE_SECRET_KEY
    assert isinstance(secret_key.buffer, bytes)


def test_user_secret_key_equality():
    alice = UserSecretKey.new_from_string(ALICE_SECRET_KEY)
    alice_again = UserSecretKey(bytes.fromhex(ALICE_SECRET_KEY))
    # Differs from Alice's key only in the last byte.
    almost_alice = UserSecretKey(bytes.fromhex(ALICE_SECRET_KEY)[:-1] + b"\x00")

    assert alice == alice_again
    assert alice != almost_alice
    assert alice != UserSecretKey.new_from_string(BOB_HEX)
    assert alice != bytes.fromhex(ALICE_SECRET_KEY)
    assert alice != ALICE_SECRET_KEY


def test_user_secret_key_equality_is_constant_time(monkeypatch: pytest.MonkeyPatch):
    calls: list[tuple[bytes, bytes]] = []
    original = user_keys.hmac.compare_digest

    def spy(a: bytes, b: bytes) -> bool:
        calls.append((a, b))
        return original(a, b)

    monkeypatch.setattr(user_keys.hmac, "compare_digest", spy)

    alice = UserSecretKey.new_from_string(ALICE_SECRET_KEY)
    bob = UserSecretKey.new_from_string(BOB_HEX)

    assert alice != bob
    assert calls == [(alice.buffer, bob.buffer)]
