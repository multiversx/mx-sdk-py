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


class ErrBadMnemonic(Exception):
    def __init__(self) -> None:
        super().__init__("Bad mnemonic")


class ErrBadSecretKeyLength(Exception):
    def __init__(self) -> None:
        super().__init__("Bad length of secret key")


class ErrBadPublicKeyLength(Exception):
    def __init__(self) -> None:
        super().__init__("Bad length of public key")


class ErrMclSignerPathNotDefined(Exception):
    def __init__(self) -> None:
        super().__init__("MCL_SIGNER_PATH isn't defined.")


class ErrMclNotImplemented(Exception):
    def __init__(self) -> None:
        super().__init__("Not yet implemented in the external MCL tool.")
