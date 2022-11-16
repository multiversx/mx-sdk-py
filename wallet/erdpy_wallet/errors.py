class ErrUnknownCipher(Exception):
    def __init__(self, name: str):
        super().__init__(f"Unknown cipher: {name}.")


class ErrUnknownDerivationFunction(Exception):
    def __init__(self):
        super().__init__("Unknown key derivation function.")


class ErrInvalidKeystoreFilePassword(Exception):
    def __init__(self):
        super().__init__("Provided keystore file password is invalid.")


class ErrCannotSign(Exception):
    def __init__(self) -> None:
        super().__init__("Cannot sign object.")


class ErrBadMnemonicLength(Exception):
    def __init__(self, actual: int, expected: int) -> None:
        super().__init__(f"Bad mnemonic length: actual = {actual}, expected = {expected}")
