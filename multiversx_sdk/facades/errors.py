class UnsuportedFileTypeError(Exception):
    def __init__(self, file_type: str) -> None:
        super().__init__(f"File type not supported: `{file_type}`. Use pem or keystore files.")
