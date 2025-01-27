from multiversx_sdk.core.address import Address
from multiversx_sdk.core.transaction_on_network import (
    SmartContractResult,
    TransactionLogs,
    TransactionOnNetwork,
)
from multiversx_sdk.core.transaction_status import TransactionStatus


def get_empty_transaction_on_network() -> TransactionOnNetwork:
    """
    Returns an 'empty' TransactionOnNetwork. All fields are set to the default values.
    **Only** used in tests.
    """
    return TransactionOnNetwork(
        raw={},
        sender=Address.empty(),
        receiver=Address.empty(),
        hash=b"",
        nonce=-1,
        round=-1,
        epoch=-1,
        timestamp=0,
        block_hash=b"",
        miniblock_hash=b"",
        sender_shard=-1,
        receiver_shard=-1,
        value=0,
        gas_limit=0,
        gas_price=0,
        function="",
        data=b"",
        version=-1,
        options=-1,
        signature=b"",
        status=TransactionStatus(""),
        smart_contract_results=[get_empty_smart_contract_result()],
        logs=get_empty_transaction_logs(),
    )


def get_empty_smart_contract_result() -> SmartContractResult:
    """
    Returns an 'empty' SmartContractResult. All fields are set to the default values.
    **Only** used in tests.
    """
    return SmartContractResult(
        raw={},
        sender=Address.empty(),
        receiver=Address.empty(),
        data=b"",
        logs=get_empty_transaction_logs(),
    )


def get_empty_transaction_logs() -> TransactionLogs:
    """
    Returns an 'empty' TransactionLogs. All fields are set to the default values.
    **Only** used in tests.
    """
    return TransactionLogs(address=Address.empty(), events=[])
