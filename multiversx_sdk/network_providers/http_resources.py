import base64
from typing import Any, Optional, Union

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.code_metadata import CodeMetadata
from multiversx_sdk.core.tokens import Token
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transaction_on_network import (
    SmartContractResult,
    TransactionEvent,
    TransactionLogs,
    TransactionOnNetwork,
)
from multiversx_sdk.core.transaction_status import TransactionStatus
from multiversx_sdk.network_providers.resources import (
    AccountOnNetwork,
    AccountStorage,
    AccountStorageEntry,
    BlockCoordinates,
    BlockOnNetwork,
    FungibleTokenMetadata,
    NetworkConfig,
    NetworkStatus,
    TokenAmountOnNetwork,
    TokensCollectionMetadata,
    TransactionCostResponse,
)
from multiversx_sdk.smart_contracts.smart_contract_query import (
    SmartContractQuery,
    SmartContractQueryResponse,
)


def smart_contract_query_to_vm_query_request(
    query: SmartContractQuery,
) -> dict[str, Any]:
    request: dict[str, Any] = {
        "scAddress": query.contract.to_bech32(),
        "funcName": query.function,
        "value": str(query.value if query.value else 0),
        "args": [arg.hex() for arg in query.arguments],
    }

    if query.caller:
        request["caller"] = query.caller.to_bech32()

    return request


def vm_query_response_to_smart_contract_query_response(
    raw_response: dict[str, Any], function: str
) -> SmartContractQueryResponse:
    return_data = raw_response.get("returnData", []) or raw_response.get("ReturnData", [])
    return_code = raw_response.get("returnCode", "") or raw_response.get("ReturnCode", "")
    return_message = raw_response.get("returnMessage", "") or raw_response.get("ReturnMessage", "")

    return SmartContractQueryResponse(
        function=function,
        return_code=return_code,
        return_message=return_message,
        return_data_parts=[base64.b64decode(item) for item in return_data],
    )


def transaction_from_api_response(tx_hash: str, response: dict[str, Any]) -> TransactionOnNetwork:
    sender = Address.new_from_bech32(response.get("sender", ""))
    receiver = Address.new_from_bech32(response.get("receiver", ""))
    hash = bytes.fromhex(tx_hash)
    nonce = response.get("nonce", -1)
    round = response.get("round", -1)
    epoch = response.get("epoch", -1)
    timestamp = response.get("timestamp", 0)
    block_hash = bytes.fromhex(response.get("blockHash", ""))
    miniblock_hash = bytes.fromhex(response.get("miniBlockHash", ""))
    sender_shard = response.get("senderShard", -1)
    receiver_shard = response.get("receiverShard", -1)
    value = int(response.get("value", 0))
    gas_limit = response.get("gasLimit", 0)
    gas_price = response.get("gasPrice", 0)
    function = response.get("function", "")
    data = base64.b64decode(response.get("data", "") or "")
    version = response.get("version", -1)
    options = response.get("options", -1)
    signature = bytes.fromhex(response.get("signature", ""))
    status = TransactionStatus(response.get("status", ""))
    logs = transaction_logs_from_response(response.get("logs", {}))

    sc_results = response.get("results", [])
    smart_contract_results = [smart_contract_result_from_api_response(result) for result in sc_results]

    return TransactionOnNetwork(
        raw=response,
        sender=sender,
        receiver=receiver,
        hash=hash,
        nonce=nonce,
        round=round,
        epoch=epoch,
        timestamp=timestamp,
        block_hash=block_hash,
        miniblock_hash=miniblock_hash,
        sender_shard=sender_shard,
        receiver_shard=receiver_shard,
        value=value,
        gas_limit=gas_limit,
        gas_price=gas_price,
        function=function,
        data=data,
        version=version,
        options=options,
        signature=signature,
        status=status,
        smart_contract_results=smart_contract_results,
        logs=logs,
    )


def transaction_from_proxy_response(
    tx_hash: str,
    response: dict[str, Any],
    process_status: Optional[TransactionStatus] = None,
) -> "TransactionOnNetwork":
    sender = Address.new_from_bech32(response.get("sender", ""))
    receiver = Address.new_from_bech32(response.get("receiver", ""))
    hash = bytes.fromhex(tx_hash)
    nonce = response.get("nonce", -1)
    round = response.get("round", -1)
    epoch = response.get("epoch", -1)
    timestamp = response.get("timestamp", 0)
    block_hash = bytes.fromhex(response.get("blockHash", ""))
    miniblock_hash = bytes.fromhex(response.get("miniblockHash", ""))
    sender_shard = response.get("sourceShard", -1)
    receiver_shard = response.get("destinationShard", -1)
    value = int(response.get("value", 0))
    gas_limit = response.get("gasLimit", 0)
    gas_price = response.get("gasPrice", 0)
    function = response.get("function", "")
    data = base64.b64decode(response.get("data", "") or "")
    version = response.get("version", -1)
    options = response.get("options", -1)
    signature = bytes.fromhex(response.get("signature", ""))
    status = TransactionStatus(response.get("status", ""))
    logs = transaction_logs_from_response(response.get("logs", {}))

    sc_results = response.get("smartContractResults", [])
    smart_contract_results = [smart_contract_result_from_proxy_response(result) for result in sc_results]

    if process_status:
        status = process_status

    return TransactionOnNetwork(
        raw=response,
        sender=sender,
        receiver=receiver,
        hash=hash,
        nonce=nonce,
        round=round,
        epoch=epoch,
        timestamp=timestamp,
        block_hash=block_hash,
        miniblock_hash=miniblock_hash,
        sender_shard=sender_shard,
        receiver_shard=receiver_shard,
        value=value,
        gas_limit=gas_limit,
        gas_price=gas_price,
        function=function,
        data=data,
        version=version,
        options=options,
        signature=signature,
        status=status,
        smart_contract_results=smart_contract_results,
        logs=logs,
    )


def transaction_logs_from_response(raw_response: dict[str, Any]) -> TransactionLogs:
    address = _convert_bech32_to_address(raw_response.get("address", ""))

    events = raw_response.get("events", [])
    events = [transaction_events_from_response(event) for event in events]

    return TransactionLogs(address=address, events=events)


def _convert_bech32_to_address(address: str) -> Address:
    if address:
        return Address.new_from_bech32(address)
    return Address.empty()


def transaction_events_from_response(raw_response: dict[str, Any]) -> TransactionEvent:
    address = _convert_bech32_to_address(raw_response.get("address", ""))

    identifier = raw_response.get("identifier", "")
    topics = raw_response.get("topics", None)

    if topics is not None:
        topics = [base64.b64decode(topic) for topic in topics]
    else:
        topics = [b""]

    raw_data = base64.b64decode(raw_response.get("responseData", "").encode())

    data = raw_response.get("data", None)
    if data is not None:
        data = base64.b64decode(data.encode())
    else:
        data = b""

    additional_data = raw_response.get("additionalData", None)
    additional_data = (
        [base64.b64decode(data.encode()) for data in additional_data] if additional_data is not None else []
    )

    if len(additional_data) == 0:
        if raw_data:
            additional_data.append(raw_data)

    return TransactionEvent(
        raw=raw_response,
        address=address,
        identifier=identifier,
        topics=topics,
        data=data,
        additional_data=additional_data,
    )


def transaction_from_simulate_response(original_tx: Transaction, raw_response: dict[str, Any]) -> TransactionOnNetwork:
    status = TransactionStatus(raw_response.get("status", ""))
    tx_hash = bytes.fromhex(raw_response.get("hash", ""))

    sc_results: list[SmartContractResult] = []
    results = raw_response.get("scResults", {})
    for hash in results:
        sc_result = smart_contract_result_from_proxy_response(results[hash])
        sc_results.append(sc_result)

    return TransactionOnNetwork(
        raw=raw_response,
        sender=original_tx.sender,
        receiver=original_tx.receiver,
        hash=tx_hash,
        nonce=original_tx.nonce,
        round=-1,
        epoch=-1,
        timestamp=0,
        block_hash=b"",
        miniblock_hash=b"",
        sender_shard=-1,
        receiver_shard=-1,
        value=original_tx.value,
        gas_limit=original_tx.gas_limit,
        gas_price=original_tx.gas_price,
        function="",
        data=original_tx.data,
        version=original_tx.version,
        options=original_tx.options,
        signature=original_tx.signature,
        status=status,
        smart_contract_results=sc_results,
        logs=TransactionLogs(address=Address.empty(), events=[]),
    )


def smart_contract_result_from_api_response(raw_response: dict[str, Any]) -> SmartContractResult:
    sender = _convert_bech32_to_address(raw_response.get("sender", ""))
    receiver = _convert_bech32_to_address(raw_response.get("receiver", ""))
    logs = transaction_logs_from_response(raw_response.get("logs", {}))

    data = raw_response.get("data", "")
    data = base64.b64decode(data.encode())

    return SmartContractResult(raw=raw_response, sender=sender, receiver=receiver, data=data, logs=logs)


def smart_contract_result_from_proxy_response(raw_response: dict[str, Any]) -> SmartContractResult:
    sender = _convert_bech32_to_address(raw_response.get("sender", ""))
    receiver = _convert_bech32_to_address(raw_response.get("receiver", ""))
    logs = transaction_logs_from_response(raw_response.get("logs", {}))
    data = raw_response.get("data", "").encode()

    return SmartContractResult(raw=raw_response, sender=sender, receiver=receiver, data=data, logs=logs)


def network_config_from_response(raw_response: dict[str, Any]) -> NetworkConfig:
    chain_id = raw_response.get("erd_chain_id", "")
    gas_per_data_byte = raw_response.get("erd_gas_per_data_byte", 0)
    gas_price_modifier = float(raw_response.get("erd_gas_price_modifier", 0))
    min_gas_limit = raw_response.get("erd_min_gas_limit", 0)
    min_gas_price = raw_response.get("erd_min_gas_price", 0)
    extra_gas_limit_guarded_tx = raw_response.get("erd_extra_gas_limit_guarded_tx", 0)
    num_shards = raw_response.get("erd_num_shards_without_meta", 0)
    round_duration = raw_response.get("erd_round_duration", 0)
    rounds_per_epoch = raw_response.get("erd_rounds_per_epoch", 0)
    genesis_timestamp = raw_response.get("erd_start_time", 0)

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
        genesis_timestamp=genesis_timestamp,
    )


def network_status_from_response(raw_response: dict[str, Any]) -> NetworkStatus:
    block_timestamp = raw_response.get("erd_block_timestamp", 0)
    block_nonce = raw_response.get("erd_nonce", 0)
    highest_final_nonce = raw_response.get("erd_highest_final_nonce", 0)
    current_round = raw_response.get("erd_current_round", 0)
    currernt_epoch = raw_response.get("erd_epoch_number", 0)

    return NetworkStatus(
        raw=raw_response,
        block_timestamp=block_timestamp,
        block_nonce=block_nonce,
        highest_final_block_nonce=highest_final_nonce,
        current_round=current_round,
        current_epoch=currernt_epoch,
    )


def block_from_response(raw_response: dict[str, Any]) -> BlockOnNetwork:
    shard = raw_response.get("shard", 0)
    nonce = raw_response.get("nonce", 0)
    hash = raw_response.get("hash", "")
    previous_hash = raw_response.get("prevBlockHash", "") or raw_response.get("prevHash", "")
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
        epoch=epoch,
    )


def account_from_proxy_response(raw_response: dict[str, Any]) -> AccountOnNetwork:
    account: dict[str, Any] = raw_response.get("account", {})
    block_coordinates = _get_block_coordinates_from_raw_response(raw_response)

    address = Address.new_from_bech32(account.get("address", ""))
    owner_address = _get_address_or_none(account.get("ownerAddress", ""))

    nonce = account.get("nonce", 0)
    balance = int(account.get("balance", 0))
    developer_reward = int(account.get("developerReward", 0))
    code = bytes.fromhex(account.get("code", ""))
    username = account.get("username", "")

    code_hash = account.get("codeHash", "")
    code_hash = base64.b64decode(code_hash) if code_hash else b""
    is_guarded = account.get("isGuarded", False)

    code_metadata = account.get("codeMetadata", None)

    is_upgradeable = False
    is_readable = False
    is_payable = False
    is_payable_by_sc = False

    if code_metadata is not None:
        code_metadata = base64.b64decode(code_metadata)
        metadata = CodeMetadata.new_from_bytes(code_metadata)

        is_upgradeable = metadata.upgradeable
        is_readable = metadata.readable
        is_payable = metadata.payable
        is_payable_by_sc = metadata.payable_by_contract

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
        block_coordinates=block_coordinates,
    )


def _get_address_or_none(address: str) -> Union[Address, None]:
    if address:
        return Address.new_from_bech32(address)
    return None


def account_from_api_response(raw_response: dict[str, Any]) -> AccountOnNetwork:
    address = Address.new_from_bech32(raw_response.get("address", ""))
    owner_address = _get_address_or_none(raw_response.get("ownerAddress", ""))

    nonce = raw_response.get("nonce", 0)
    balance = int(raw_response.get("balance", 0))
    developer_reward = int(raw_response.get("developerReward", 0))
    code = bytes.fromhex(raw_response.get("code", ""))
    username = raw_response.get("username", "")

    code_hash = raw_response.get("codeHash", "")
    code_hash = base64.b64decode(code_hash) if code_hash else b""
    is_guarded = raw_response.get("isGuarded", False)

    is_upgradeable = bool(raw_response.get("isUpgradeable", False))
    is_readable = bool(raw_response.get("isReadable", False))
    is_payable = bool(raw_response.get("isPayable", False))
    is_payable_by_sc = bool(raw_response.get("isPayableBySmartContract", False))

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
    )


def account_storage_from_response(raw_response: dict[str, Any]) -> AccountStorage:
    pairs: dict[str, Any] = raw_response.get("pairs", {})
    block_coordinates = _get_block_coordinates_from_raw_response(raw_response)

    entries: list[AccountStorageEntry] = []
    for key, value in pairs.items():
        decoded_key = bytes.fromhex(str(key))
        decoded_value = bytes.fromhex(str(value))

        entries.append(
            AccountStorageEntry(
                raw={key: value},
                key=decoded_key.decode(errors="ignore"),
                value=decoded_value,
            )
        )

    return AccountStorage(raw=raw_response, entries=entries, block_coordinates=block_coordinates)


def account_storage_entry_from_response(raw_response: dict[str, Any], key: str) -> AccountStorageEntry:
    value = raw_response.get("value", "")
    return AccountStorageEntry(raw=raw_response, key=key, value=bytes.fromhex(value))


def transaction_cost_estimation_from_response(raw_response: dict[str, Any]) -> TransactionCostResponse:
    cost = raw_response.get("txGasUnits", 0)
    return TransactionCostResponse(raw=raw_response, gas_limit=cost, status=TransactionStatus(""))


def transactions_from_send_multiple_response(
    raw_response: dict[str, Any], initial_txs_sent: int
) -> tuple[int, list[bytes]]:
    num_sent = raw_response.get("numOfSentTxs", 0)
    tx_hashes: dict[str, Any] = raw_response.get("txsHashes", {})

    hashes: list[bytes] = []
    for i in range(initial_txs_sent):
        tx_hash = tx_hashes.get(str(i), "")
        hashes.append(bytes.fromhex(tx_hash))

    return (num_sent, hashes)


def token_amount_on_network_from_proxy_response(raw_response: dict[str, Any]) -> TokenAmountOnNetwork:
    token_data: dict[str, Any] = raw_response.get("tokenData", {})
    block_coordinates = _get_block_coordinates_from_raw_response(raw_response)

    identifier = token_data.get("tokenIdentifier", "")
    balance = int(token_data.get("balance", "0"))
    nonce = token_data.get("nonce", 0)
    token = Token(identifier, nonce)
    attributes = base64.b64decode(token_data.get("attributes", ""))

    return TokenAmountOnNetwork(
        raw=raw_response,
        token=token,
        amount=balance,
        attributes=attributes,
        block_coordinates=block_coordinates,
    )


def token_amount_from_api_response(raw_response: dict[str, Any]) -> TokenAmountOnNetwork:
    identifier = raw_response.get("identifier", "")
    nonce = raw_response.get("nonce", 0)
    amount = int(raw_response.get("balance", 0))
    attributes = base64.b64decode(raw_response.get("attributes", ""))

    return TokenAmountOnNetwork(raw=raw_response, token=Token(identifier, nonce), amount=amount, attributes=attributes)


def token_amounts_from_proxy_response(raw_response: dict[str, Any]) -> list[TokenAmountOnNetwork]:
    tokens = raw_response.get("esdts", {})
    block_coordinates = _get_block_coordinates_from_raw_response(raw_response)

    result: list[TokenAmountOnNetwork] = []
    for item in tokens:
        token_data: dict[str, Any] = tokens[item]
        identifier = token_data.get("tokenIdentifier", "")
        balance = int(token_data.get("balance", "0"))
        nonce = token_data.get("nonce", 0)
        token = Token(identifier, nonce)
        attributes = base64.b64decode(token_data.get("attributes", ""))

        result.append(
            TokenAmountOnNetwork(
                raw={item: token_data},
                token=token,
                amount=balance,
                attributes=attributes,
                block_coordinates=block_coordinates,
            )
        )

    return result


def definition_of_fungible_token_from_query_response(
    raw_response: list[bytes], identifier: str, address_hrp: str
) -> FungibleTokenMetadata:
    token_name, _, owner, _, _, *properties_buffers = raw_response
    properties = _parse_token_properties(properties_buffers)

    name = token_name.decode()
    ticker = identifier
    owner = Address(owner, address_hrp)
    decimals = properties.get("NumDecimals", 0)

    return FungibleTokenMetadata(
        raw={"returnDataParts": [item.hex() for item in raw_response]},
        identifier=identifier,
        name=name,
        ticker=ticker,
        owner=owner.to_bech32(),
        decimals=decimals,
    )


def definition_of_fungible_token_from_api_response(raw_response: dict[str, Any]) -> FungibleTokenMetadata:
    name = raw_response.get("name", "")
    ticker = raw_response.get("ticker", "")
    owner = raw_response.get("owner", "")
    identifier = raw_response.get("identifier", "")
    decimals = raw_response.get("decimals", 0)

    return FungibleTokenMetadata(
        raw=raw_response,
        identifier=identifier,
        name=name,
        ticker=ticker,
        owner=owner,
        decimals=decimals,
    )


def definition_of_tokens_collection_from_query_response(
    raw_response: list[bytes], identifier: str, address_hrp: str
) -> TokensCollectionMetadata:
    token_name, token_type, owner, _, _, *properties_buffers = raw_response
    properties = _parse_token_properties(properties_buffers)

    collection = identifier
    type = token_type.decode()
    name = token_name.decode()
    ticker = collection
    owner = Address(owner, address_hrp)
    decimals = properties.get("NumDecimals", 0)

    return TokensCollectionMetadata(
        raw={"returnDataParts": [item.hex() for item in raw_response]},
        collection=collection,
        type=type,
        name=name,
        ticker=ticker,
        owner=owner.to_bech32(),
        decimals=decimals,
    )


def definition_of_tokens_collection_from_api_response(raw_response: dict[str, Any]) -> TokensCollectionMetadata:
    collection = raw_response.get("collection", "")
    type = raw_response.get("type", "")
    name = raw_response.get("name", "")
    ticker = raw_response.get("ticker", "")
    owner = raw_response.get("owner", "")
    decimals = raw_response.get("decimals", 0)

    return TokensCollectionMetadata(
        collection=collection,
        type=type,
        raw=raw_response,
        name=name,
        ticker=ticker,
        owner=owner,
        decimals=decimals,
    )


# the token properties have this format:
# e.g.1. "4e756d446563696d616c732d36", which decodes to: "NumDecimals-6"
# e.g.2. "49735061757365642d66616c7365", which decodes to: "IsPaused-false"
def _parse_token_properties(properties_buffer: list[bytes]) -> dict[str, Any]:
    properties: dict[str, Any] = {}

    for buffer in properties_buffer:
        name, value = buffer.decode().split("-")
        properties[name] = _parse_value_of_token_property(value)

    return properties


def _parse_value_of_token_property(value: str) -> Any:
    if value == "true":
        return True
    elif value == "false":
        return False
    else:
        return int(value)


def _get_block_coordinates_from_raw_response(raw_response: dict[str, Any]) -> BlockCoordinates:
    block_info: dict[str, Any] = raw_response.get("blockInfo", {})

    block_nonce = block_info.get("nonce", 0)
    block_hash = block_info.get("hash", "")
    block_root_hash = block_info.get("rootHash", "")

    return BlockCoordinates(
        nonce=block_nonce,
        hash=bytes.fromhex(block_hash),
        root_hash=bytes.fromhex(block_root_hash),
    )
