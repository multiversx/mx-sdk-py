from typing import Any, Union


def convert_tx_hash_to_string(tx_hash: Union[bytes, str]) -> str:
    if isinstance(tx_hash, bytes):
        return tx_hash.hex()
    return tx_hash


def convert_boolean_query_params_to_lowercase(query_params: dict[str, Any]) -> dict[str, Any]:
    return {key: str(value).lower() if isinstance(value, bool) else value for key, value in query_params.items()}
