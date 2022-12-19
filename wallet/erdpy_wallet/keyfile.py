import base64
import os
from binascii import b2a_base64, hexlify, unhexlify
from typing import Any, Dict, Tuple, Union
from uuid import uuid4

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from erdpy_core import Address

from erdpy_wallet.errors import (ErrInvalidKeystoreFilePassword,
                                 ErrUnknownCipher,
                                 ErrUnknownDerivationFunction)
from erdpy_wallet.interfaces import IUserWalletRandomness


# References:
# Thanks for this implementation @flyingbasalt
# https://github.com/flyingbasalt/erdkeys
def load_from_key_file_object(keystore: Dict[str, Any], password: str) -> Tuple[str, bytes]:
    backend = default_backend()

    # derive the decryption key
    kdf_name = keystore['crypto']['kdf']
    if kdf_name != 'scrypt':
        raise ErrUnknownDerivationFunction()

    salt = unhexlify(keystore['crypto']['kdfparams']['salt'])
    dklen = keystore['crypto']['kdfparams']['dklen']
    n = keystore['crypto']['kdfparams']['n']
    p = keystore['crypto']['kdfparams']['p']
    r = keystore['crypto']['kdfparams']['r']

    kdf = Scrypt(salt=salt, length=dklen, n=n, r=r, p=p, backend=backend)
    key = kdf.derive(bytes(password.encode()))

    # decrypt the secret key with half of the decryption key
    cipher_name = keystore['crypto']['cipher']
    if cipher_name != 'aes-128-ctr':
        raise ErrUnknownCipher(name=cipher_name)

    iv = unhexlify(keystore['crypto']['cipherparams']['iv'])
    ciphertext = unhexlify(keystore['crypto']['ciphertext'])
    decryption_key = key[0:16]

    cipher = Cipher(algorithms.AES(decryption_key), modes.CTR(iv), backend=backend)
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    pemified_secret_key = b2a_base64(hexlify(plaintext))

    hmac_key = key[16:32]
    h = hmac.HMAC(hmac_key, hashes.SHA256(), backend=backend)
    h.update(ciphertext)
    mac = h.finalize()

    if mac != unhexlify(keystore['crypto']['mac']):
        raise ErrInvalidKeystoreFilePassword()

    address_bech32 = keystore['bech32']
    secret_key = ''.join([pemified_secret_key[i:i + 64].decode() for i in range(0, len(pemified_secret_key), 64)])

    key_hex = base64.b64decode(secret_key).decode()
    key_bytes = bytes.fromhex(key_hex)

    secret_key = key_bytes[:32]

    return address_bech32, secret_key


def convert_to_keyfile_object(secret_key: bytes, pubkey: bytes, password: str, randomness: Union[None, IUserWalletRandomness], address_hrp: str) -> Dict[str, Any]:
    salt = os.urandom(32) if randomness is None else randomness.salt
    iv = os.urandom(16) if randomness is None else randomness.iv
    uid = str(uuid4()) if randomness is None else randomness.id

    backend = default_backend()

    # derive the encryption key
    kdf = Scrypt(salt=salt, length=32, n=4096, r=8, p=1, backend=backend)
    key = kdf.derive(bytes(password.encode()))

    # encrypt the secret key with half of the encryption key
    ciphertext = make_cyphertext(backend, key, iv, secret_key + pubkey)

    hmac_key = key[16:32]
    h = hmac.HMAC(hmac_key, hashes.SHA256(), backend=default_backend())
    h.update(ciphertext)
    mac = h.finalize()

    data = _format_key_json(uid, pubkey, iv, ciphertext, salt, mac, address_hrp)
    return data


def make_cyphertext(backend: Any, key: bytes, iv: bytes, data: bytes):
    encryption_key = key[0:16]
    cipher = Cipher(algorithms.AES(encryption_key), modes.CTR(iv), backend=backend)
    encryptor = cipher.encryptor()
    return encryptor.update(data) + encryptor.finalize()


# erdjs implementation:
# https://github.com/ElrondNetwork/elrond-sdk-erdjs/blob/main/src/walletcore/userWallet.ts
def _format_key_json(uid: str, pubkey: bytes, iv: bytes, ciphertext: bytes, salt: bytes, mac: bytes, address_hrp: str) -> Dict[str, Any]:
    address = Address(pubkey, address_hrp)

    return {
        'version': 4,
        'id': uid,
        'address': address.hex(),
        'bech32': address.bech32(),
        'crypto': {
            'cipher': 'aes-128-ctr',
            'cipherparams': {
                'iv': hexlify(iv).decode()
            },
            'ciphertext': hexlify(ciphertext).decode(),
            'kdf': 'scrypt',
            'kdfparams': {
                'dklen': 32,
                'n': 4096,
                'p': 1,
                'r': 8,
                'salt': hexlify(salt).decode(),
            },
            'mac': hexlify(mac).decode(),
        }
    }
