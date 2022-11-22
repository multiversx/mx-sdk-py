from typing import Any, Dict


class ContractQueryResponse:
    def __init__(self):
        self.return_data: str = ''
        self.return_code: str = ''
        self.return_message: str = ''
        self.gas_used: int = 0

    @staticmethod
    def from_http_response(payload: Dict[str, Any]) -> 'ContractQueryResponse':
        return_data = payload.get('returnData', '') or payload.get('ReturnData', '')
        return_code = payload.get('returnCode', '') or payload.get('ReturnCode', '')
        return_message = payload.get('returnMessage', '') or payload.get('ReturnMessage', '')
        gas_remaining = payload.get('gasRemaining', 0) or payload.get('GasRemaining', 0)
        gas_used = 0

        result = ContractQueryResponse()
        result.return_data = return_data
        result.return_code = return_code
        result.return_message = return_message
        result.gas_used = gas_used

        return result
