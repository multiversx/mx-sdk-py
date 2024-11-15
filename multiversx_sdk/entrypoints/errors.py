class InvalidNetworkProviderKindError(Exception):
    def __init__(self) -> None:
        super().__init__("Invalid network provider kind. Choose between `api` and `proxy`.")
