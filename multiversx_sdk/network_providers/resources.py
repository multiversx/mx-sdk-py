from typing import Any, Dict, List


class GenericResponse:
    def __init__(self, data: Any) -> None:
        self.__dict__.update(data)

    def get(self, key: str, default: Any = None) -> Any:
        return self.__dict__.get(key, default)

    def to_dictionary(self) -> Dict[str, Any]:
        return self.__dict__


class EmptyAddress:
    def to_bech32(self) -> str:
        return ""

    def to_hex(self) -> str:
        return ""


class SmartContractResult:
    def __init__(self, raw: Dict[str, Any]) -> None:
        self.raw = raw
        self.return_message = self._parse_return_message()
        self.arguments = self._parse_arguments()
        self.parsed_log = Log(raw.get("logs", {}))

    def _parse_return_message(self) -> str:
        try:
            data_parts = self._parse_data_parts()
            return_message_encoded = data_parts[0]
            return_message = bytes.fromhex(return_message_encoded).decode("ascii")
            return return_message
        except:
            return ""

    def _parse_arguments(self) -> List[str]:
        try:
            data_parts = self._parse_data_parts()
            arguments = data_parts[1:]
            return arguments
        except:
            return []

    def _parse_data_parts(self) -> List[str]:
        data: str = self.raw.get("data", "").lstrip("@")
        return data.split("@")

    def to_dictionary(self) -> Dict[str, Any]:
        result: Dict[str, Any] = dict()
        result.update(self.raw)
        result["parsed"] = {
            "returnMessage": self.return_message,
            "arguments": self.arguments,
            "log": self.parsed_log
        }

        return result


class Log:
    def __init__(self, raw: Dict[str, Any]) -> None:
        self.raw = raw


class SimulateResponse:
    def __init__(self, response: GenericResponse) -> None:
        result: Dict[str, Any] = response.get("result") or dict()
        contract_results: Dict[str, Any] = result.get("scResults") or dict()

        self.raw = response.to_dictionary()
        self.parsed_contract_results = [SmartContractResult(item) for item in contract_results.values()]

    def to_dictionary(self) -> Dict[str, Any]:
        result: Dict[str, Any] = dict()
        result.update(self.raw)
        result["parsed"] = dict()

        if self.parsed_contract_results:
            result["parsed"]["smartContractResults"] = self.parsed_contract_results

        return result
