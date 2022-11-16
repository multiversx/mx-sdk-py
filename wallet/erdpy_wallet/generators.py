from pathlib import Path

import nacl.encoding
import nacl.signing
from erdpy_core import Address
from mnemonic import Mnemonic

from erdpy_wallet import pem
from erdpy_wallet.constants import BIP39_STRENGTH


def generate_mnemonic() -> str:
    mnemo = Mnemonic("english")
    words = mnemo.generate(strength=BIP39_STRENGTH)
    return words


def generate_pair():
    signing_key = nacl.signing.SigningKey.generate()
    secret_key = bytes(signing_key)
    pubkey_bytes = bytes(signing_key.verify_key)
    return secret_key, pubkey_bytes


def generate_pem_file(pem_file: Path) -> None:
    secret_key, pubkey = generate_pair()
    address = Address(pubkey)
    pem.write(pem_file, secret_key, pubkey, name=address.bech32())
