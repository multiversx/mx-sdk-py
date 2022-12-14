from erdpy_core.constants import METACHAIN_ID


def get_shard_of_pubkey(pubkey: bytes) -> int:
    num_shards = 3
    mask_high = int("11", 2)
    mask_low = int("01", 2)

    last_byte_of_pubkey = pubkey[31]

    if _is_pubkey_of_metachain(pubkey):
        return METACHAIN_ID

    shard = last_byte_of_pubkey & mask_high
    if shard > num_shards - 1:
        shard = last_byte_of_pubkey & mask_low

    return shard


def _is_pubkey_of_metachain(pubkey: bytes) -> bool:
    metachain_prefix = bytearray([0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    pubkey_prefix = pubkey[0:len(metachain_prefix)]
    if pubkey_prefix == metachain_prefix:
        return True

    zero_address = bytearray(32)
    if pubkey == zero_address:
        return True

    return False
