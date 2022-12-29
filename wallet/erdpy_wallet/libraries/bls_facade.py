import ctypes
import logging
import platform
from pathlib import Path
from typing import Optional


class BLSFacade:
    _library: Optional[ctypes.CDLL] = None

    def __init__(self) -> None:
        pass

    def generate_private_key(self) -> bytes:
        function = self._get_library().generatePrivateKey

        output = function()
        output_bytes = ctypes.string_at(output)
        private_key_hex = output_bytes.decode()
        private_key = bytes.fromhex(private_key_hex)
        return private_key

    def generate_public_key(self, private_key: bytes) -> bytes:
        function = self._get_library().generatePublicKey

        output = function(private_key.hex().encode())
        output_bytes = ctypes.string_at(output)
        public_key_hex = output_bytes.decode()
        public_key = bytes.fromhex(public_key_hex)
        return public_key

    def compute_message_signature(self, message: bytes, private_key: bytes) -> bytes:
        function = self._get_library().computeMessageSignature

        output = function(
            message.hex().encode(),
            private_key.hex().encode()
        )

        output_bytes = ctypes.string_at(output)
        signature_hex = output_bytes.decode()
        signature = bytes.fromhex(signature_hex)
        return signature

    def verify_message_signature(self, public_key: bytes, message: bytes, signature: bytes) -> bool:
        function = self._get_library().verifyMessageSignature

        output = function(
            public_key.hex().encode(),
            message.hex().encode(),
            signature.hex().encode()
        )

        output_int = ctypes.c_int(output)
        return output_int.value == 1

    def _get_library(self) -> ctypes.CDLL:
        if self._library is None:
            self._library = self._load_library()

        return self._library

    def _load_library(self) -> ctypes.CDLL:
        path = self._get_library_path()
        library = ctypes.cdll.LoadLibrary(str(path))

        library.generatePrivateKey.argtypes = []
        library.generatePrivateKey.restype = ctypes.c_char_p

        library.generatePublicKey.argtypes = [ctypes.c_char_p]
        library.generatePublicKey.restype = ctypes.c_char_p

        library.computeMessageSignature.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        library.computeMessageSignature.restype = ctypes.c_char_p

        library.verifyMessageSignature.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
        library.verifyMessageSignature.restype = ctypes.c_int

        logging.info(f"Loaded library: {path}")

        return library

    def _get_library_path(self):
        os_name = platform.system()
        lib_name = "libbls.dylib" if os_name == "Darwin" else "libbls.so"
        return Path(__file__).parent / lib_name
