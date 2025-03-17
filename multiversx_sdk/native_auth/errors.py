class NativeAuthClientError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class NativeAuthInvalidConfigError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class NativeAuthInvalidWildcardOriginError(Exception):
    def __init__(self, origin: str):
        super().__init__(f"Invalid wildcard origin: {origin}")


class NativeAuthInvalidTokenError(Exception):
    def __init__(self):
        super().__init__("The provided token in not a NativeAuth token.")


class NativeAuthInvalidTokenTtlError(Exception):
    def __init__(self, current_ttl: int, max_ttl: int):
        super().__init__(f"The provided TTL: {current_ttl} is larger than the maximum allowed TTL: {max_ttl}.")


class NativeAuthOriginNotAcceptedError(Exception):
    def __init__(self, origin: str):
        super().__init__(f"The origin: {origin} is not accepted.")


class NativeAuthInvalidBlockHashError(Exception):
    def __init__(self, block_hash: str):
        super().__init__(f"Invalid block hash: {block_hash}")


class NativeAuthTokenExpiredError(Exception):
    def __init__(self):
        super().__init__("The provided token has expired.")


class NativeAuthInvalidSignatureError(Exception):
    def __init__(self):
        super().__init__("The provided signature is invalid.")


class NativeAuthInvalidImpersonateError(Exception):
    def __init__(self):
        super().__init__("Invalid impersonate.")
