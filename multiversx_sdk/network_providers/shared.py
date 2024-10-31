from typing import Union


def convert_tx_hash_to_string(tx_hash: Union[bytes, str]) -> str:
    if isinstance(tx_hash, bytes):
        return tx_hash.hex()
    return tx_hash
