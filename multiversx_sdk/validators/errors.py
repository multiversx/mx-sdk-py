class ValidatorsFileNotFoundError(Exception):
    def __init__(self, file: str) -> None:
        super().__init__(f"No validators file found at: {file}")


class CannotReadValidatorsDataError(Exception):
    def __init__(self, file: str) -> None:
        super().__init__(f"Cannot read validators data for file: {file}")
