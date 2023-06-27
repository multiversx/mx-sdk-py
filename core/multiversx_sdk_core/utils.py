from pathlib import Path

from multiversx_sdk_core.errors import ErrBadFile


def read_binary_file(path: Path) -> bytes:
    try:
        with open(path, 'rb') as binary_file:
            return binary_file.read()
    except Exception as err:
        raise ErrBadFile(str(path), err)
