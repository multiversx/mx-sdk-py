import base64
from typing import Any, Dict, Optional

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.smart_contract_query import (
    SmartContractQuery, SmartContractQueryResponse)
from multiversx_sdk.core.transaction_on_network import (SmartContractResult,
                                                        TransactionEvent,
                                                        TransactionLogs,
                                                        TransactionOnNetwork)
from multiversx_sdk.core.transaction_status import TransactionStatus
from multiversx_sdk.network_providers.resources import (BlockOnNetwork,
                                                        EmptyAddress,
                                                        NetworkConfig,
                                                        NetworkStatus)


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


def vm_query_response_to_smart_contract_query_response(
        raw_response: Dict[str, Any],
        function: str) -> SmartContractQueryResponse:
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
    result.contract_results = [smart_contract_result_from_api_response(result) for result in sc_results]
    result.is_completed = result.status.is_completed

    return result


def transaction_from_proxy_response(
    tx_hash: str, response: dict[str, Any], process_status: Optional[TransactionStatus] = None
) -> "TransactionOnNetwork":
    result = _transaction_from_network_response(tx_hash, response)

    sc_results = response.get("smartContractResults", [])
    result.contract_results = [smart_contract_result_from_proxy_response(result) for result in sc_results]

    if process_status:
        result.status = process_status
        result.is_completed = result.status.is_completed

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
    result.status = TransactionStatus(response.get("status", ""))
    result.timestamp = response.get("timestamp", 0)
    result.block_nonce = response.get("blockNonce", 0)
    result.hyperblock_nonce = response.get("hyperblockNonce", 0)
    result.hyperblock_hash = response.get("hyperblockHash", "")

    result.logs = transaction_logs_from_response(response.get("logs", {}))
    result.raw_response = response

    return result


def transaction_logs_from_response(raw_response: dict[str, Any]) -> TransactionLogs:
    address = raw_response.get('address', "")

    events = raw_response.get('events', [])
    events = [transaction_events_from_response(event) for event in events]

    return TransactionLogs(
        address=address,
        events=events
    )


def transaction_events_from_response(raw_response: dict[str, Any]) -> TransactionEvent:
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
    additional_data = [base64.b64decode(data.encode())
                       for data in additional_data] if additional_data is not None else []

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


def smart_contract_result_from_api_response(raw_response: dict[str, Any]) -> SmartContractResult:
    sc_result = _smart_contract_result_from_response(raw_response)
    data = raw_response.get("data", "")
    sc_result.data = base64.b64decode(data.encode())
    return sc_result


def smart_contract_result_from_proxy_response(raw_response: dict[str, Any]) -> SmartContractResult:
    sc_result = _smart_contract_result_from_response(raw_response)
    sc_result.data = raw_response.get("data", "").encode()
    return sc_result


def _smart_contract_result_from_response(raw_response: dict[str, Any]) -> SmartContractResult:
    sender = raw_response.get("sender", "")
    receiver = raw_response.get("receiver", "")
    logs = transaction_logs_from_response(raw_response.get("logs", {}))

    return SmartContractResult(
        raw=raw_response,
        sender=sender,
        receiver=receiver,
        logs=logs
    )


def network_config_from_response(raw_response: dict[str, Any]) -> NetworkConfig:
    chain_id = raw_response.get('erd_chain_id', '')
    gas_per_data_byte = raw_response.get('erd_gas_per_data_byte', 0)
    gas_price_modifier = float(raw_response.get('erd_gas_price_modifier', 0))
    min_gas_limit = raw_response.get('erd_min_gas_limit', 0)
    min_gas_price = raw_response.get('erd_min_gas_price', 0)
    extra_gas_limit_guarded_tx = raw_response.get('erd_extra_gas_limit_guarded_tx', 0)
    num_shards = raw_response.get('erd_num_shards_without_meta', 0)
    round_duration = raw_response.get('erd_round_duration', 0)
    rounds_per_epoch = raw_response.get('erd_rounds_per_epoch', 0)
    genesis_timestamp = raw_response.get('erd_start_time', 0)

    return NetworkConfig(
        raw=raw_response,
        chain_id=chain_id,
        gas_per_data_byte=gas_per_data_byte,
        gas_price_modifier=gas_price_modifier,
        min_gas_limit=min_gas_limit,
        min_gas_price=min_gas_price,
        extra_gas_limit_for_guarded_transactions=extra_gas_limit_guarded_tx,
        num_shards=num_shards,
        round_duration=round_duration,
        num_rounds_per_epoch=rounds_per_epoch,
        genesis_timestamp=genesis_timestamp
    )


def network_status_from_response(raw_response: dict[str, Any]) -> NetworkStatus:
    block_timestamp = raw_response.get('erd_block_timestamp', 0)
    block_nonce = raw_response.get('erd_nonce', 0)
    highest_final_nonce = raw_response.get('erd_highest_final_nonce', 0)
    current_round = raw_response.get('erd_current_round', 0)
    currernt_epoch = raw_response.get('erd_epoch_number', 0)

    return NetworkStatus(
        raw=raw_response,
        block_timestamp=block_timestamp,
        block_nonce=block_nonce,
        highest_final_block_nonce=highest_final_nonce,
        current_round=current_round,
        current_epoch=currernt_epoch
    )


def block_from_response(raw_response: dict[str, Any]) -> BlockOnNetwork:
    shard = raw_response.get("shard", 0)
    nonce = raw_response.get("nonce", 0)
    hash = raw_response.get("hash", "")
    previous_hash = raw_response.get("prevBlockHash", "")
    timestamp = raw_response.get("timestamp", 0)
    round = raw_response.get("round", 0)
    epoch = raw_response.get("epoch", 0)

    return BlockOnNetwork(
        raw=raw_response,
        shard=shard,
        nonce=nonce,
        hash=bytes.fromhex(hash),
        previous_hash=bytes.fromhex(previous_hash),
        timestamp=timestamp,
        round=round,
        epoch=epoch
    )
