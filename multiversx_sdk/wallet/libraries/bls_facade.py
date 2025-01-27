import ctypes
import logging
import platform
from pathlib import Path
from typing import Optional

from multiversx_sdk.wallet.errors import LibraryNotFoundError, UnsupportedOSError


class BLSFacade:
    _library: Optional[ctypes.CDLL] = None

    def __init__(self) -> None:
        pass

    def generate_private_key(self) -> bytes:
        generate_private_key_function = self._get_library().generatePrivateKey

        output = generate_private_key_function()
        output_bytes = ctypes.string_at(output)
        private_key_hex = output_bytes.decode()
        private_key = bytes.fromhex(private_key_hex)
        return private_key

    def generate_public_key(self, private_key: bytes) -> bytes:
        generate_public_key_function = self._get_library().generatePublicKey

        output = generate_public_key_function(private_key.hex().encode())
        output_bytes = ctypes.string_at(output)
        public_key_hex = output_bytes.decode()
        public_key = bytes.fromhex(public_key_hex)
        return public_key

    def compute_message_signature(self, message: bytes, private_key: bytes) -> bytes:
        compute_message_signature_function = self._get_library().computeMessageSignature

        output = compute_message_signature_function(message.hex().encode(), private_key.hex().encode())

        output_bytes = ctypes.string_at(output)
        signature_hex = output_bytes.decode()
        signature = bytes.fromhex(signature_hex)
        return signature

    def verify_message_signature(self, public_key: bytes, message: bytes, signature: bytes) -> bool:
        verify_message_signature_function = self._get_library().verifyMessageSignature

        output = verify_message_signature_function(
            public_key.hex().encode(), message.hex().encode(), signature.hex().encode()
        )

        output_int = ctypes.c_int(output)
        return output_int.value == 1

    def _get_library(self) -> ctypes.CDLL:
        if self._library is None:
            self._library = self._load_library()

        return self._library

    def _load_library(self) -> ctypes.CDLL:
        lib_path = self._get_library_path()

        if not lib_path.exists():
            raise LibraryNotFoundError(lib_path)

        lib = ctypes.CDLL(str(lib_path), winmode=0)

        lib.generatePrivateKey.argtypes = []
        lib.generatePrivateKey.restype = ctypes.c_char_p

        lib.generatePublicKey.argtypes = [ctypes.c_char_p]
        lib.generatePublicKey.restype = ctypes.c_char_p

        lib.computeMessageSignature.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        lib.computeMessageSignature.restype = ctypes.c_char_p

        lib.verifyMessageSignature.argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
        ]
        lib.verifyMessageSignature.restype = ctypes.c_int

        logging.info(f"Loaded library: {lib_path}")

        return lib

    def _get_library_path(self):
        os_name = platform.system()
        processor = platform.processor()

        if os_name == "Windows":
            lib_name = "libbls.dll"
        elif os_name == "Darwin":
            if processor == "arm":
                lib_name = "libbls_arm64.dylib"
            else:
                lib_name = "libbls.dylib"
        elif os_name == "Linux":
            lib_name = "libbls.so"
        else:
            raise UnsupportedOSError(os_name)

        return Path(__file__).parent / lib_name
