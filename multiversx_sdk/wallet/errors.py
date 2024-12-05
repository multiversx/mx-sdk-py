from pathlib import Path


class UnknownCipherError(Exception):
    def __init__(self, name: str):
        super().__init__(f"Unknown cipher: {name}.")


class UnknownDerivationFunctionError(Exception):
    def __init__(self):
        super().__init__("Unknown key derivation function.")


class InvalidKeystoreFilePasswordError(Exception):
    def __init__(self):
        super().__init__("Provided keystore file password is invalid.")


class CannotSignError(Exception):
    def __init__(self) -> None:
        super().__init__("Cannot sign object.")


class InvalidMnemonicError(Exception):
    def __init__(self) -> None:
        super().__init__("Bad mnemonic")


class InvalidSecretKeyLengthError(Exception):
    def __init__(self) -> None:
        super().__init__("Bad length of secret key")


class InvalidPublicKeyLengthError(Exception):
    def __init__(self) -> None:
        super().__init__("Bad length of public key")


class LibraryNotFoundError(Exception):
    def __init__(self, path: Path) -> None:
        super().__init__(f"Library not found: {path}")


class UnsupportedOSError(Exception):
    def __init__(self, os_name: str) -> None:
        super().__init__(f"Unsupported OS: {os_name}")
