from typing import Any

import pytest
from cryptography.hazmat.primitives import hmac

from multiversx_sdk.wallet.crypto import EncryptedData, Randomness, decryptor, encryptor
from multiversx_sdk.wallet.errors import (
    InvalidKeystoreFileError,
    InvalidKeystoreFilePasswordError,
)


def _encrypt(data: bytes) -> EncryptedData:
    return encryptor.encrypt(data, "password", Randomness())


def test_encrypt_then_decrypt():
    encrypted_data = _encrypt(b"hello")
    assert decryptor.decrypt(encrypted_data, "password") == b"hello"


@pytest.mark.parametrize(
    "param, value",
    [
        ("n", 0),
        ("n", 1),
        ("n", 4095),  # not a power of 2
        ("n", 2**19),
        ("r", 0),
        ("r", -1),
        ("r", 9),
        ("p", 0),
        ("p", -1),
        ("p", 5),
        ("p", 64),
        ("dklen", 0),
        ("dklen", 16),
        ("dklen", 31),
        ("dklen", 33),
        ("dklen", 64),
    ],
)
def test_decrypt_with_unsupported_key_derivation_params(param: str, value: int):
    encrypted_data = _encrypt(b"hello")
    setattr(encrypted_data.kdfparams, param, value)

    with pytest.raises(InvalidKeystoreFileError, match=f"unsupported scrypt parameter: {param} = {value}"):
        decryptor.decrypt(encrypted_data, "password")


@pytest.mark.parametrize("value", [4096.0, "4096", True, None])
def test_decrypt_with_key_derivation_params_of_wrong_type(value: Any):
    encrypted_data = _encrypt(b"hello")
    encrypted_data.kdfparams.n = value

    with pytest.raises(InvalidKeystoreFileError, match="scrypt parameters must be integers"):
        decryptor.decrypt(encrypted_data, "password")


@pytest.mark.parametrize("n, r, p", [(2, 1, 1), (2**18, 2, 1), (4096, 8, 4)])
def test_decrypt_with_key_derivation_params_within_bounds(n: int, r: int, p: int):
    # The parameters are accepted, so the key derivation runs; then, the MAC check fails (the params differ from the ones used at encryption).
    encrypted_data = _encrypt(b"hello")
    encrypted_data.kdfparams.n = n
    encrypted_data.kdfparams.r = r
    encrypted_data.kdfparams.p = p

    with pytest.raises(InvalidKeystoreFilePasswordError):
        decryptor.decrypt(encrypted_data, "password")


@pytest.mark.parametrize("iv_length", [0, 8, 15, 17, 32])
def test_decrypt_with_unexpected_iv_length(iv_length: int):
    encrypted_data = _encrypt(b"hello")
    encrypted_data.iv = "00" * iv_length

    with pytest.raises(InvalidKeystoreFileError, match=f"unexpected length of IV: {iv_length}"):
        decryptor.decrypt(encrypted_data, "password")


def test_decrypt_with_wrong_password():
    encrypted_data = _encrypt(b"hello")

    with pytest.raises(InvalidKeystoreFilePasswordError):
        decryptor.decrypt(encrypted_data, "wrong password")


@pytest.mark.parametrize(
    "mac",
    [
        "",
        "00" * 32,
        "00" * 31,
        "00" * 33,
    ],
)
def test_decrypt_with_wrong_mac(mac: str):
    encrypted_data = _encrypt(b"hello")
    encrypted_data.mac = mac

    with pytest.raises(InvalidKeystoreFilePasswordError):
        decryptor.decrypt(encrypted_data, "password")


@pytest.mark.parametrize("position", [0, 15, 31])
def test_decrypt_with_mac_altered_in_a_single_byte(position: int):
    encrypted_data = _encrypt(b"hello")
    mac = bytearray.fromhex(encrypted_data.mac)
    mac[position] ^= 1
    encrypted_data.mac = mac.hex()

    with pytest.raises(InvalidKeystoreFilePasswordError):
        decryptor.decrypt(encrypted_data, "password")


def test_decrypt_compares_mac_in_constant_time(monkeypatch: pytest.MonkeyPatch):
    calls: list[bytes] = []
    original = hmac.HMAC.verify

    def spy(self: hmac.HMAC, signature: bytes) -> None:
        calls.append(signature)
        original(self, signature)

    monkeypatch.setattr(hmac.HMAC, "verify", spy)

    encrypted_data = _encrypt(b"hello")
    assert decryptor.decrypt(encrypted_data, "password") == b"hello"
    assert calls == [bytes.fromhex(encrypted_data.mac)]
