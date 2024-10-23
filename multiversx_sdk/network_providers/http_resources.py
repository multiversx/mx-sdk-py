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
from multiversx_sdk.network_providers.resources import (
    AccountOnNetwork, AccountStorage, AccountStorageEntry, BlockCoordinates,
    BlockOnNetwork, EmptyAddress, NetworkConfig, NetworkStatus,
    TransactionCostResponse)


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


def account_from_response(raw_response: dict[str, Any]) -> AccountOnNetwork:
    account: dict[str, Any] = raw_response.get('account', {})
    block_info: dict[str, Any] = raw_response.get("blockInfo", {})

    address = account.get("address", "")
    owner_address = account.get("ownerAddress", "")
    nonce = account.get("nonce", 0)
    balance = int(account.get("balance", 0))
    developer_reward = int(account.get("developerReward", 0))
    code = bytes.fromhex(account.get("code", ""))
    username = account.get("username", "")

    code_hash = account.get("codeHash", "")
    code_hash = base64.b64decode(code_hash) if code_hash else b""

    is_guarded = account.get("isGuarded", False)
    is_upgradeable = account.get("isUpgradeable", False)
    is_readable = account.get("isReadable", False)
    is_payable = account.get("isPayable", False)
    is_payable_by_sc = account.get("isPayableBySmartContract", False)

    block_nonce = block_info.get("nonce", 0)
    block_hash = block_info.get("hash", "")
    block_root_hash = block_info.get("rootHash", "")
    block_coordinates = BlockCoordinates(
        nonce=block_nonce,
        hash=bytes.fromhex(block_hash),
        root_hash=bytes.fromhex(block_root_hash)
    )

    return AccountOnNetwork(
        raw=raw_response,
        address=address,
        nonce=nonce,
        balance=balance,
        is_guarded=is_guarded,
        username=username,
        contract_code_hash=code_hash,
        contract_code=code,
        contract_developer_reward=developer_reward,
        contract_owner_address=owner_address,
        is_contract_upgradable=is_upgradeable,
        is_contract_readable=is_readable,
        is_contract_payable=is_payable,
        is_contract_payable_by_contract=is_payable_by_sc,
        block_coordinates=block_coordinates
    )


def account_storage_from_response(raw_response: dict[str, Any]) -> AccountStorage:
    pairs: dict[str, Any] = raw_response.get('pairs', {})
    block_info: dict[str, Any] = raw_response.get("blockInfo", {})

    entries: list[AccountStorageEntry] = []
    for key, value in pairs.items():
        decoded_key = bytes.fromhex(str(key))
        decoded_value = bytes.fromhex(str(value))

        entries.append(
            AccountStorageEntry(
                raw={key: value},
                key=decoded_key.decode(),
                value=decoded_value
            )
        )

    block_nonce = block_info.get("nonce", 0)
    block_hash = block_info.get("hash", "")
    block_root_hash = block_info.get("rootHash", "")
    block_coordinates = BlockCoordinates(
        nonce=block_nonce,
        hash=bytes.fromhex(block_hash),
        root_hash=bytes.fromhex(block_root_hash)
    )

    return AccountStorage(
        raw=raw_response,
        entries=entries,
        block_coordinates=block_coordinates
    )


def account_storage_entry_from_response(raw_response: dict[str, Any], key: str) -> AccountStorageEntry:
    value = raw_response.get("value", "")
    return AccountStorageEntry(
        raw=raw_response,
        key=key,
        value=bytes.fromhex(value)
    )


def transaction_cost_estimation_from_response(raw_response: dict[str, Any]) -> TransactionCostResponse:
    cost = raw_response.get("txGasUnits", 0)
    return TransactionCostResponse(
        raw=raw_response,
        gas_limit=cost,
        status=TransactionStatus("")
    )


def transactions_from_send_multiple_response(raw_response: dict[str, Any],
                                             initial_txs_sent: int) -> tuple[int, list[bytes]]:
    num_sent = raw_response.get("numOfSentTxs", 0)
    tx_hashes: dict[str, Any] = raw_response.get("txsHashes", {})

    hashes: list[bytes] = []
    for i in range(initial_txs_sent):
        tx_hash = tx_hashes.get(str(i), "")
        hashes.append(bytes.fromhex(tx_hash))

    return (num_sent, hashes)
