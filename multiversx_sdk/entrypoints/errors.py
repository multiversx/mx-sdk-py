class BadUsageError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class InvalidNetworkProviderKindError(Exception):
    def __init__(self) -> None:
        super().__init__("Invalid network provider kind. Choose between `api` and `proxy`.")
