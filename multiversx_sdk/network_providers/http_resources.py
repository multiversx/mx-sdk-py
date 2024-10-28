import base64
from typing import Any, Dict, Optional

from multiversx_sdk.core.address import Address, EmptyAddress
from multiversx_sdk.core.smart_contract_query import (
    SmartContractQuery, SmartContractQueryResponse)
from multiversx_sdk.core.transaction_on_network import (SmartContractResult,
                                                        TransactionEvent,
                                                        TransactionLogs,
                                                        TransactionOnNetwork)
from multiversx_sdk.core.transaction_status import TransactionStatus


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


def transaction_from_api_response(tx_hash: str, response: dict[str, Any]) -> TransactionOnNetwork:
    result = _transaction_from_network_response(tx_hash, response)

    sc_results = response.get("results", [])
    result.contract_results = [smart_contract_result_from_api_request(result) for result in sc_results]
    result.is_completed = not result.get_status().is_pending()

    return result


def transaction_from_proxy_response(
    tx_hash: str, response: dict[str, Any], process_status: Optional[TransactionStatus] = None
) -> "TransactionOnNetwork":
    result = _transaction_from_network_response(tx_hash, response)

    sc_results = response.get("smartContractResults", [])
    result.contract_results = [smart_contract_result_from_proxy_request(result) for result in sc_results]

    if process_status:
        result.status = process_status
        result.is_completed = True if result.status.is_successful() or result.status.is_failed() else False

    return result


def _transaction_from_network_response(tx_hash: str, response: dict[str, Any]) -> "TransactionOnNetwork":
    result = TransactionOnNetwork()

    result.hash = tx_hash
    result.type = response.get("type", "")
    result.nonce = response.get("nonce", 0)
    result.round = response.get("round", 0)
    result.epoch = response.get("epoch", 0)
    result.value = response.get("value", 0)

    sender = response.get("sender", "")
    result.sender = Address.new_from_bech32(sender) if sender else EmptyAddress()

    receiver = response.get("receiver", "")
    result.receiver = Address.new_from_bech32(receiver) if receiver else EmptyAddress()

    result.gas_price = response.get("gasPrice", 0)
    result.gas_limit = response.get("gasLimit", 0)

    data = response.get("data", "") or ""
    result.function = response.get("function", "")

    result.data = base64.b64decode(data).decode()
    result.status = TransactionStatus(response.get("status"))
    result.timestamp = response.get("timestamp", 0)

    result.block_nonce = response.get("blockNonce", 0)
    result.hyperblock_nonce = response.get("hyperblockNonce", 0)
    result.hyperblock_hash = response.get("hyperblockHash", "")

    result.logs = transaction_logs_from_request(response.get("logs", {}))
    result.raw_response = response

    return result


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
    topics = raw_response.get('topics', None)

    if topics is not None:
        topics = [base64.b64decode(topic) for topic in topics]
    else:
        topics = [b""]

    raw_data = base64.b64decode(raw_response.get('responseData', "").encode())

    data = raw_response.get("data", None)
    if data is not None:
        data = base64.b64decode(data.encode())
    else:
        data = b""

    additional_data = raw_response.get("additionalData", None)
    additional_data = [base64.b64decode(data.encode()) for data in additional_data] if additional_data is not None else []

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
