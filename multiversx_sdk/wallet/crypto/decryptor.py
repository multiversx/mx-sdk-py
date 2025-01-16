from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from multiversx_sdk.wallet.crypto.constants import (
    CIPHER_ALGORITHM_AES_128_CTR,
    KEY_DERIVATION_FUNCTION_SCRYPT,
)
from multiversx_sdk.wallet.crypto.encrypted_data import EncryptedData
from multiversx_sdk.wallet.errors import (
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

    salt = bytes.fromhex(encrypted_data.salt)
    iv = bytes.fromhex(encrypted_data.iv)
    ciphertext = bytes.fromhex(encrypted_data.ciphertext)

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
    computed_mac = h.finalize()
    actual_mac = bytes.fromhex(encrypted_data.mac)

    if computed_mac != actual_mac:
        raise InvalidKeystoreFilePasswordError()

    cipher = Cipher(algorithms.AES(derived_key_first_half), modes.CTR(iv), backend=backend)
    decryptor = cipher.decryptor()
    data = decryptor.update(ciphertext) + decryptor.finalize()

    return data
