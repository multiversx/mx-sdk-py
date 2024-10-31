from typing import Union


def convert_tx_hash_to_string(tx_hash: Union[bytes, str]) -> str:
    if isinstance(tx_hash, bytes):
        return tx_hash.hex()
    return tx_hash


def decimal_to_padded_hex(i: int) -> str:
    as_hex = f'{i:x}'
    return "0" + as_hex if len(as_hex) % 2 else as_hex
