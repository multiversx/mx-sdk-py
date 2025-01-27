class SmartContractQueryError(Exception):
    def __init__(self, return_code: str, message: str) -> None:
        super().__init__(message)
        self.return_code = return_code


class ArgumentSerializationError(Exception):
    def __init__(
        self,
        message: str = "Unable to encode arguments: unsupported format or missing ABI file",
    ) -> None:
        super().__init__(message)
