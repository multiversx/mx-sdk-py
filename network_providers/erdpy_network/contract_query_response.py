from typing import Any, Dict, List
import base64


class ContractQueryResponse:
    def __init__(self):
        self.return_data: List[str] = []
        self.return_code: str = ''
        self.return_message: str = ''

    @staticmethod
    def from_http_response(payload: Dict[str, Any]) -> 'ContractQueryResponse':
        return_data = payload.get('returnData', []) or payload.get('ReturnData', [])
        return_code = payload.get('returnCode', '') or payload.get('ReturnCode', '')
        return_message = payload.get('returnMessage', '') or payload.get('ReturnMessage', '')
        # gas_remaining = payload.get('gasRemaining', 0) or payload.get('GasRemaining', 0)

        result = ContractQueryResponse()
        result.return_data = return_data
        result.return_code = return_code
        result.return_message = return_message

        return result

    def get_return_data_parts(self) -> List:
        return [base64.b64decode(item) for item in self.return_data]
