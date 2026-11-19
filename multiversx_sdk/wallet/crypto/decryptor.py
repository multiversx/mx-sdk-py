from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from multiversx_sdk.wallet.crypto.constants import (
    CIPHER_ALGORITHM_AES_128_CTR,
    KEY_DERIVATION_FUNCTION_SCRYPT,
    RANDOM_IV_LENGTH,
    SCRYPT_DKLEN,
    SCRYPT_MAX_N,
    SCRYPT_MAX_P,
    SCRYPT_MAX_R,
)
from multiversx_sdk.wallet.crypto.encrypted_data import (
    EncryptedData,
    KeyDerivationParams,
)
from multiversx_sdk.wallet.errors import (
    InvalidKeystoreFileError,
    InvalidKeystoreFilePasswordError,
    UnknownCipherError,
    UnknownDerivationFunctionError,
)


def decrypt(encrypted_data: EncryptedData, password: str) -> bytes:
    """
    Also see: https://github.com/multiversx/mx-sdk-js-wallet/blob/main/src/crypto/decryptor.ts
    """
    backend = default_backend()

    if encrypted_data.kdf != KEY_DERIVATION_FUNCTION_SCRYPT:
        raise UnknownDerivationFunctionError()

    if encrypted_data.cipher != CIPHER_ALGORITHM_AES_128_CTR:
        raise UnknownCipherError(name=encrypted_data.cipher)

    # The parameters come from the (possibly untrusted) file, and the key derivation runs before the MAC check.
    _validate_key_derivation_params(encrypted_data.kdfparams)

    salt = bytes.fromhex(encrypted_data.salt)
    iv = bytes.fromhex(encrypted_data.iv)
    ciphertext = bytes.fromhex(encrypted_data.ciphertext)

    if len(iv) != RANDOM_IV_LENGTH:
        raise InvalidKeystoreFileError(f"unexpected length of IV: {len(iv)}")

    kdf = Scrypt(
        salt=salt,
        length=encrypted_data.kdfparams.dklen,
        n=encrypted_data.kdfparams.n,
        r=encrypted_data.kdfparams.r,
        p=encrypted_data.kdfparams.p,
        backend=backend,
    )

    derived_key = kdf.derive(bytes(password.encode()))
    derived_key_first_half = derived_key[0:16]
    derived_key_second_half = derived_key[16:32]

    h = hmac.HMAC(derived_key_second_half, hashes.SHA256(), backend=backend)
    h.update(ciphertext)
    actual_mac = bytes.fromhex(encrypted_data.mac)

    # "verify" compares in constant time (the "hmac" module of "cryptography" has no "compare_digest").
    try:
        h.verify(actual_mac)
    except InvalidSignature:
        raise InvalidKeystoreFilePasswordError() from None

    cipher = Cipher(algorithms.AES(derived_key_first_half), modes.CTR(iv), backend=backend)
    decryptor = cipher.decryptor()
    data = decryptor.update(ciphertext) + decryptor.finalize()

    return data


def _validate_key_derivation_params(params: KeyDerivationParams) -> None:
    n, r, p, dklen = params.n, params.r, params.p, params.dklen

    # "type() is int" also rejects booleans.
    if not all(type(value) is int for value in [n, r, p, dklen]):
        raise InvalidKeystoreFileError("scrypt parameters must be integers")

    # "n" must be a power of 2.
    if not (2 <= n <= SCRYPT_MAX_N and n & (n - 1) == 0):
        raise InvalidKeystoreFileError(f"unsupported scrypt parameter: n = {n}")

    if not 1 <= r <= SCRYPT_MAX_R:
        raise InvalidKeystoreFileError(f"unsupported scrypt parameter: r = {r}")

    if not 1 <= p <= SCRYPT_MAX_P:
        raise InvalidKeystoreFileError(f"unsupported scrypt parameter: p = {p}")

    # A shorter derived key would shorten (or empty) the MAC key, so that a wrong password would go undetected.
    if dklen != SCRYPT_DKLEN:
        raise InvalidKeystoreFileError(f"unsupported scrypt parameter: dklen = {dklen}")
