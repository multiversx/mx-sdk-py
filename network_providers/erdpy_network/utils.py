def decimal_to_padded_hex(i):
    as_hex = f'{i:x}'
    return "0" + as_hex if len(as_hex) % 2 else as_hex
