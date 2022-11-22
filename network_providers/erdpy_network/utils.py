def dec_to_padded_hex(i):
    return "0" + f"{i:x}" if len(f"{i:x}") % 2 else f"{i:x}"
