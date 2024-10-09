import base64
from typing import Any, Dict

from multiversx_sdk.core.smart_contract_query import (
    SmartContractQuery, SmartContractQueryResponse)
from multiversx_sdk.core.transaction_outcome import (SmartContractResult,
                                                     TransactionEvent,
                                                     TransactionLogs)


def smart_contract_query_to_vm_query_request(query: SmartContractQuery) -> Dict[str, Any]:
    request: Dict[str, Any] = {
        'scAddress': query.contract,
        'funcName': query.function,
        'value': str(query.value if query.value else 0),
        'args': [arg.hex() for arg in query.arguments]
    }

    if query.caller:
        request['caller'] = query.caller

    return request


def vm_query_response_to_smart_contract_query_response(raw_response: Dict[str, Any], function: str) -> SmartContractQueryResponse:
    return_data = raw_response.get('returnData', []) or raw_response.get('ReturnData', [])
    return_code = raw_response.get('returnCode', '') or raw_response.get('ReturnCode', '')
    return_message = raw_response.get('returnMessage', '') or raw_response.get('ReturnMessage', '')

    return SmartContractQueryResponse(
        function=function,
        return_code=return_code,
        return_message=return_message,
        return_data_parts=[base64.b64decode(item) for item in return_data]
    )


def transaction_logs_from_request(raw_response: dict[str, Any]) -> TransactionLogs:
    address = raw_response.get('address', "")

    events = raw_response.get('events', [])
    events = [transaction_events_from_request(event) for event in events]

    return TransactionLogs(
        address=address,
        events=events
    )


def transaction_events_from_request(raw_response: dict[str, Any]) -> TransactionEvent:
    address = raw_response.get('address', '')
    identifier = raw_response.get('identifier', '')
    topics = [base64.b64decode(topic.encode()) for topic in raw_response.get('topics', [])]

    raw_data = base64.b64decode(raw_response.get('responseData', "").encode())
    data = base64.b64decode(raw_response.get("data", "").encode())

    additional_data = raw_response.get("additionalData", [])
    additional_data = [base64.b64decode(data.encode()) for data in additional_data]

    if len(additional_data) == 0:
        if raw_data:
            additional_data.append(raw_data)

    return TransactionEvent(
        raw=raw_response,
        address=address,
        identifier=identifier,
        topics=topics,
        data=data,
        additional_data=additional_data
    )


def smart_contract_result_from_api_request(raw_response: dict[str, Any]) -> SmartContractResult:
    sc_result = _smart_contract_result_from_request(raw_response)
    data = raw_response.get("data", "")
    sc_result.data = base64.b64decode(data.encode())
    return sc_result


def smart_contract_result_from_proxy_request(raw_response: dict[str, Any]) -> SmartContractResult:
    sc_result = _smart_contract_result_from_request(raw_response)
    sc_result.data = raw_response.get("data", "").encode()
    return sc_result


def _smart_contract_result_from_request(raw_response: dict[str, Any]) -> SmartContractResult:
    sender = raw_response.get("sender", "")
    receiver = raw_response.get("receiver", "")
    logs = transaction_logs_from_request(raw_response.get("logs", {}))

    return SmartContractResult(
        raw=raw_response,
        sender=sender,
        receiver=receiver,
        logs=logs
    )
