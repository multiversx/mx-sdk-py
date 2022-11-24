from pathlib import Path
from typing import Tuple

import nacl.encoding
import nacl.signing
from erdpy_core import Address

from erdpy_wallet import pem


def generate_user_keypair() -> Tuple[bytes, bytes]:
    signing_key = nacl.signing.SigningKey.generate()
    secret_key = bytes(signing_key)
    pubkey_bytes = bytes(signing_key.verify_key)
    return secret_key, pubkey_bytes


def generate_user_pem_file(pem_file: Path) -> None:
    secret_key, pubkey = generate_user_keypair()
    address = Address(pubkey)
    pem.write(pem_file, secret_key, pubkey, name=address.bech32())
