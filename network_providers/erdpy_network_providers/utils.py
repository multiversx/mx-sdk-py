def decimal_to_padded_hex(i: int) -> str:
    as_hex = f'{i:x}'
    return "0" + as_hex if len(as_hex) % 2 else as_hex


def is_padded_hex(input: str) -> bool:
    input = input or ''
    decoded_input = bytes.fromhex(input)
    encoded = decoded_input.hex()
    return encoded.upper() == input.upper()
