def decimal_to_padded_hex(i: int):
    as_hex = f'{i:x}'
    return "0" + as_hex if len(as_hex) % 2 else as_hex


def is_padded_hex(input: str) -> bool:
    if len(input) % 2:
        return False
    return True
