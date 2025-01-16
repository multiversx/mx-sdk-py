from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from multiversx_sdk.wallet.crypto.constants import (
    CIPHER_ALGORITHM_AES_128_CTR,
    ENCRYPTOR_VERSION,
    KEY_DERIVATION_FUNCTION_SCRYPT,
)
from multiversx_sdk.wallet.crypto.encrypted_data import (
    EncryptedData,
    KeyDerivationParams,
)
from multiversx_sdk.wallet.interfaces import IRandomness


def encrypt(data: bytes, password: str, randomness: IRandomness) -> EncryptedData:
    """
    Also see: https://github.com/multiversx/mx-sdk-js-wallet/blob/main/src/crypto/encryptor.ts
    """
    backend = default_backend()

    kdParams = KeyDerivationParams(n=4096, r=8, p=1, dklen=32)
    kdf = Scrypt(
        salt=randomness.salt,
        length=kdParams.dklen,
        n=kdParams.n,
        r=kdParams.r,
        p=kdParams.p,
        backend=backend,
    )
    derived_key = kdf.derive(bytes(password.encode()))
    derived_key_first_half = derived_key[0:16]
    derived_key_second_half = derived_key[16:32]
    cipher = Cipher(
        algorithms.AES(derived_key_first_half),
        modes.CTR(randomness.iv),
        backend=backend,
    )

    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(data) + encryptor.finalize()

    h = hmac.HMAC(derived_key_second_half, hashes.SHA256(), backend=default_backend())
    h.update(ciphertext)
    mac = h.finalize()

    encrypted_data = EncryptedData(
        id=randomness.id,
        version=ENCRYPTOR_VERSION,
        cipher=CIPHER_ALGORITHM_AES_128_CTR,
        ciphertext=ciphertext.hex(),
        iv=randomness.iv.hex(),
        kdf=KEY_DERIVATION_FUNCTION_SCRYPT,
        kdfparams=kdParams,
        salt=randomness.salt.hex(),
        mac=mac.hex(),
    )

    return encrypted_data
