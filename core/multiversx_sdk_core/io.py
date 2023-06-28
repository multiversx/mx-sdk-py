from pathlib import Path


def read_binary_file(path: Path) -> bytes:
    try:
        return path.read_bytes()
    except Exception as err:
        raise err
