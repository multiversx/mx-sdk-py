class UnsuportedFileTypeError(Exception):
    def __init__(self, file_type: str) -> None:
        super().__init__(f"File type not supported: `{file_type}`. Use pem or keystore files.")


class BadUsageError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class InvalidNetworkProviderKindError(Exception):
    def __init__(self) -> None:
        super().__init__("Invalid network provider kind. Choose between `api` and `proxy`.")
