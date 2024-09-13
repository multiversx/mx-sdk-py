import base64
from typing import Any, Dict

from multiversx_sdk.core.smart_contract_query import (
    SmartContractQuery, SmartContractQueryResponse)


def smart_contract_query_to_dictionary(query: SmartContractQuery) -> Dict[str, Any]:
    request: Dict[str, Any] = {
        'scAddress': query.contract,
        'funcName': query.function,
        'value': str(query.value if query.value else 0),
        'args': [arg.hex() for arg in query.arguments]
    }
    caller = query.caller

    if caller:
        request['caller'] = caller

    return request


def raw_query_response_to_smart_contract_query_response(raw_response: Dict[str, Any], function: str) -> SmartContractQueryResponse:
    return_data = raw_response.get('returnData', []) or raw_response.get('ReturnData', [])
    return_code = raw_response.get('returnCode', '') or raw_response.get('ReturnCode', '')
    return_message = raw_response.get('returnMessage', '') or raw_response.get('ReturnMessage', '')

    return SmartContractQueryResponse(
        function=function,
        return_code=return_code,
        return_message=return_message,
        return_data_parts=[base64.b64decode(item) for item in return_data]
    )
