from typing import Any


class GenericError(Exception):
    def __init__(self, url: str, data: Any):
        super().__init__(f"Url = [{url}], error = {data}")
        self.url = url
        self.data = data
