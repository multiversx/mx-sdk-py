from typing import List, Optional


class SmartContractQuery:
    def __init__(
            self,
            contract: str,
            function: str,
            arguments: List[bytes],
            caller: Optional[str] = None,
            value: Optional[int] = None
    ) -> None:
        self.contract = contract
        self.function = function
        self.arguments = arguments
        self.caller = caller
        self.value = value


class SmartContractQueryResponse:
    def __init__(
            self,
            function: str,
            return_code: str,
            return_message: str,
            return_data_parts: List[bytes]
    ) -> None:
        self.function = function
        self.return_code = return_code
        self.return_message = return_message
        self.return_data_parts = return_data_parts
