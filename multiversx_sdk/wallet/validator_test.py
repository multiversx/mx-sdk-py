import os
from pathlib import Path
from typing import Any

import pytest

from multiversx_sdk.wallet.errors import (
    CannotSignError,
    InvalidPublicKeyLengthError,
    InvalidSecretKeyError,
    InvalidSecretKeyLengthError,
)
from multiversx_sdk.wallet.pem_entry import PemEntry
from multiversx_sdk.wallet.validator_keys import ValidatorPublicKey, ValidatorSecretKey
from multiversx_sdk.wallet.validator_pem import ValidatorPEM
from multiversx_sdk.wallet.validator_signer import ValidatorSigner
from multiversx_sdk.wallet.validator_verifier import ValidatorVerifier

testwallets = Path(__file__).parent.parent / "testutils" / "testwallets"


def test_validator_secret_key_generate_public_key():
    assert (
        ValidatorSecretKey.from_string("7cff99bd671502db7d15bc8abc0c9a804fb925406fbdd50f1e4c17a4cd774247")
        .generate_public_key()
        .hex()
        == "e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"
    )


def test_sign_message():
    signer = ValidatorSigner.from_pem_file(testwallets / "validatorKey00.pem")
    message = b"hello"
    signature = signer.sign(message)
    assert (
        signature.hex()
        == "84fd0a3a9d4f1ea2d4b40c6da67f9b786284a1c3895b7253fec7311597cda3f757862bb0690a92a13ce612c33889fd86"
    )


def test_verify_message():
    verifier = ValidatorVerifier.from_string(
        "e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"
    )

    message = b"hello"
    signature = bytes.fromhex(
        "84fd0a3a9d4f1ea2d4b40c6da67f9b786284a1c3895b7253fec7311597cda3f757862bb0690a92a13ce612c33889fd86"
    )

    assert verifier.verify(message, signature)

    invalid_signature = bytes.fromhex(
        "94fd0a3a9d4f1ea2d4b40c6da67f9b786284a1c3895b7253fec7311597cda3f757862bb0690a92a13ce612c33889fd86"
    )
    assert verifier.verify(message, invalid_signature) is False


def test_pem_save():
    path = testwallets / "validatorKey00.pem"
    path_saved = path.with_suffix(".saved")

    with open(path) as f:
        content_expected = f.read().strip()

    pem = ValidatorPEM.from_file(path)
    pem.save(path_saved)

    with open(path_saved) as f:
        content_actual = f.read().strip()

    assert content_actual == content_expected
    os.remove(path_saved)


def test_validator_secret_key_rejects_zero_key():
    with pytest.raises(InvalidSecretKeyError):
        ValidatorSecretKey(bytes(32))

    with pytest.raises(InvalidSecretKeyError):
        ValidatorSecretKey(bytearray(32))


@pytest.mark.parametrize("buffer", ["a" * 32, "\x00" * 32, [1] * 32, memoryview(b"\x01" * 32), None, 42])
def test_validator_secret_key_rejects_non_bytes(buffer: Any):
    # Previously, e.g. a 32-characters string was accepted, then failed later, when used.
    with pytest.raises(TypeError, match="The secret key must be bytes"):
        ValidatorSecretKey(buffer)


@pytest.mark.parametrize("length", [0, 31, 33, 64])
def test_validator_secret_key_rejects_wrong_length(length: int):
    with pytest.raises(InvalidSecretKeyLengthError):
        ValidatorSecretKey(b"\x01" * length)

    with pytest.raises(InvalidSecretKeyLengthError):
        ValidatorSecretKey(bytearray(b"\x01" * length))


def test_validator_secret_key_from_bytearray_is_copied():
    expected = ValidatorSecretKey.generate()
    buffer = bytearray(expected.buffer)

    secret_key = ValidatorSecretKey(buffer)
    assert type(secret_key.buffer) is bytes
    assert secret_key.buffer == expected.buffer

    # Altering the caller's buffer (even to the zero key, which crashes the native library) must not affect the key.
    buffer[:] = bytes(32)
    assert secret_key.buffer == expected.buffer
    assert secret_key.generate_public_key().hex() == expected.generate_public_key().hex()
    assert secret_key.sign(b"hello") == expected.sign(b"hello")


def test_load_pem_with_zero_secret_key():
    # Previously, such a file was loaded, then computing the public key crashed the whole process (Go panic).
    text = PemEntry("foo", bytes(32)).to_text()

    with pytest.raises(InvalidSecretKeyError):
        ValidatorPEM.from_text(text)


def test_sign_empty_message():
    # The native library refuses to sign an empty message. Previously, an empty signature was returned (without error).
    signer = ValidatorSigner.from_pem_file(testwallets / "validatorKey00.pem")

    with pytest.raises(CannotSignError):
        signer.sign(b"")

    assert len(signer.sign(b"\x00")) == 48


def test_sign_and_generate_public_key_with_out_of_range_key():
    # Not a valid scalar of the BLS12-381 curve: the native library returns an empty result, which must not be taken as a signature.
    secret_key = ValidatorSecretKey(bytes([0xFF] * 32))
    signer = ValidatorSigner(secret_key)

    with pytest.raises(CannotSignError):
        secret_key.sign(b"hello")

    with pytest.raises(CannotSignError):
        signer.sign(b"hello")

    with pytest.raises(InvalidSecretKeyError):
        secret_key.generate_public_key()

    with pytest.raises(InvalidSecretKeyError):
        signer.get_pubkey()


@pytest.mark.parametrize(
    "buffer",
    [bytes(32), bytes(33), bytes(32) + b"\x01"],
    ids=["zero-key", "zero-key-33-bytes", "zero-key-then-nonzero-byte"],
)
def test_sign_and_generate_public_key_with_key_altered_after_construction(buffer: bytes):
    # Longer buffers starting with 32 zero bytes crash some builds of the native library (just as the zero key does).
    secret_key = ValidatorSecretKey.generate()
    secret_key.buffer = buffer

    with pytest.raises(CannotSignError):
        secret_key.sign(b"hello")

    with pytest.raises(InvalidSecretKeyError):
        secret_key.generate_public_key()


@pytest.mark.parametrize("index", [4, -1])
def test_load_validator_pem_with_index_out_of_range(index: int):
    # Previously, negative indices silently selected entries from the end.
    with pytest.raises(IndexError, match=f"PEM entry index {index} is out of range \\(number of entries: 4\\)"):
        ValidatorPEM.from_file(testwallets / "multipleValidatorKeys.pem", index)


# 32 bytes is the length of a secret key, 48 bytes the length of a signature.
@pytest.mark.parametrize("length", [0, 32, 48, 95, 97, 192])
def test_validator_public_key_with_wrong_length(length: int):
    # Previously, "InvalidSecretKeyLengthError" ("Bad length of secret key") was raised, although no secret key is involved.
    with pytest.raises(InvalidPublicKeyLengthError, match="Bad length of public key"):
        ValidatorPublicKey(bytes(length))

    with pytest.raises(InvalidPublicKeyLengthError, match="Bad length of public key"):
        ValidatorPublicKey.from_string("ab" * length)

    with pytest.raises(InvalidPublicKeyLengthError, match="Bad length of public key"):
        ValidatorVerifier.from_string("ab" * length)


def test_validator_public_key_with_expected_length():
    secret_key = ValidatorSecretKey.from_string("7cff99bd671502db7d15bc8abc0c9a804fb925406fbdd50f1e4c17a4cd774247")
    public_key_hex = secret_key.generate_public_key().hex()

    assert ValidatorPublicKey(bytes.fromhex(public_key_hex)).hex() == public_key_hex
    assert ValidatorPublicKey.from_string(public_key_hex).hex() == public_key_hex
