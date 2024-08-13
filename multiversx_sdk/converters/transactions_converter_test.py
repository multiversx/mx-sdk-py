import base64

from multiversx_sdk.converters.transactions_converter import \
    TransactionsConverter
from multiversx_sdk.core.address import Address
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transactions_outcome_parsers.resources import (
    SmartContractResult, TransactionEvent, TransactionLogs, TransactionOutcome)
from multiversx_sdk.network_providers.contract_results import \
    ContractResultItem as ContractResultItemOnNetwork
from multiversx_sdk.network_providers.contract_results import \
    ContractResults as ContractResultOnNetwork
from multiversx_sdk.network_providers.transaction_events import \
    TransactionEvent as TxEventOnNetwork
from multiversx_sdk.network_providers.transaction_events import \
    TransactionEventData as TxEventDataOnNetwork
from multiversx_sdk.network_providers.transaction_events import \
    TransactionEventTopic as TxEventTopicOnNetwork
from multiversx_sdk.network_providers.transaction_logs import \
    TransactionLogs as TxLogsOnNetwork
from multiversx_sdk.network_providers.transactions import TransactionOnNetwork


def test_transaction_converter():
    converter = TransactionsConverter()

    transaction = Transaction(
        nonce=90,
        value=123456789000000000000000000000,
        sender="erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
        receiver="erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
        sender_username="alice",
        receiver_username="bob",
        gas_price=1000000000,
        gas_limit=80000,
        data=b"hello",
        chain_id="localnet"
    )

    tx_as_dict = converter.transaction_to_dictionary(transaction)
    restored_tx = converter.dictionary_to_transaction(tx_as_dict)

    assert transaction == restored_tx


def test_transaction_from_dictionary_with_inner_transaction():
    converter = TransactionsConverter()

    inner_transaction = Transaction(
        nonce=90,
        value=123456789000000000000000000000,
        sender="erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
        receiver="erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
        sender_username="alice",
        receiver_username="bob",
        gas_limit=80000,
        data=b"hello",
        chain_id="localnet",
        relayer="erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8"
    )

    relayed_transaction = Transaction(
        nonce=77,
        sender="erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8",
        receiver="erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8",
        gas_limit=180000,
        chain_id="localnet",
        inner_transactions=[inner_transaction]
    )

    tx_as_dict = converter.transaction_to_dictionary(relayed_transaction)
    restored_tx = converter.dictionary_to_transaction(tx_as_dict)

    assert relayed_transaction == restored_tx


def test_convert_tx_on_network_to_outcome():
    converter = TransactionsConverter()

    tx_on_network = TransactionOnNetwork()
    tx_on_network.nonce = 7
    tx_on_network.function = "hello"

    event = TxEventOnNetwork()
    event.identifier = "foobar"
    event.data_payload = TxEventDataOnNetwork(b"foo")

    logs = TxLogsOnNetwork()
    logs.address = Address.new_from_bech32("erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8")
    logs.events = [event]

    tx_on_network.logs = logs

    # @too much gas provided for processing: gas provided = 596384500, gas used = 733010
    tx_event_topic = TxEventTopicOnNetwork("QHRvbyBtdWNoIGdhcyBwcm92aWRlZCBmb3IgcHJvY2Vzc2luZzogZ2FzIHByb3ZpZGVkID0gNTk2Mzg0NTAwLCBnYXMgdXNlZCA9IDczMzAxMA==")

    event = TxEventOnNetwork()
    event.identifier = "writeLog"
    event.topics = [tx_event_topic]
    event.data_payload = TxEventDataOnNetwork(base64.b64decode("QDZmNmI="))

    logs = TxLogsOnNetwork()
    logs.address = Address.new_from_bech32("erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8")
    logs.events = [event]

    contract_result_item = ContractResultItemOnNetwork()
    contract_result_item.nonce = 8
    contract_result_item.data = "@6f6b@2a"
    contract_result_item.logs = logs

    contract_result = ContractResultOnNetwork([contract_result_item])
    tx_on_network.contract_results = contract_result

    actual_tx_outcome = converter.transaction_on_network_to_outcome(tx_on_network)

    expected_tx_outcome = TransactionOutcome(
        transaction_results=[SmartContractResult(
            sender="",
            receiver="",
            data=b"@6f6b@2a",
            logs=TransactionLogs(
                address="erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8",
                events=[TransactionEvent(
                    address="",
                    identifier="writeLog",
                    topics=[b"@too much gas provided for processing: gas provided = 596384500, gas used = 733010"],
                    data_items=[base64.b64decode("QDZmNmI=")]
                )]
            )
        )],
        transaction_logs=TransactionLogs(
            address="erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8",
            events=[
                TransactionEvent(
                    address="",
                    identifier="foobar",
                    data_items=[b"foo"]
                )]
        )
    )

    assert actual_tx_outcome.logs.address == expected_tx_outcome.logs.address
    assert actual_tx_outcome.logs.events[0].identifier == expected_tx_outcome.logs.events[0].identifier
    assert actual_tx_outcome.logs.events[0].data_items == expected_tx_outcome.logs.events[0].data_items
    assert actual_tx_outcome.logs.events[0].address == expected_tx_outcome.logs.events[0].address
    assert actual_tx_outcome.logs.events[0].topics == expected_tx_outcome.logs.events[0].topics

    assert actual_tx_outcome.transaction_results[0].sender == expected_tx_outcome.transaction_results[0].sender
    assert actual_tx_outcome.transaction_results[0].receiver == expected_tx_outcome.transaction_results[0].receiver
    assert actual_tx_outcome.transaction_results[0].data == expected_tx_outcome.transaction_results[0].data
    assert actual_tx_outcome.transaction_results[0].logs.address == expected_tx_outcome.transaction_results[0].logs.address
    assert actual_tx_outcome.transaction_results[0].logs.events[0].address == expected_tx_outcome.transaction_results[0].logs.events[0].address
    assert actual_tx_outcome.transaction_results[0].logs.events[0].identifier == expected_tx_outcome.transaction_results[0].logs.events[0].identifier
    assert actual_tx_outcome.transaction_results[0].logs.events[0].data_items == expected_tx_outcome.transaction_results[0].logs.events[0].data_items
    assert actual_tx_outcome.transaction_results[0].logs.events[0].topics == expected_tx_outcome.transaction_results[0].logs.events[0].topics


def test_convert_tx_on_network_to_outcome_with_signal_error():
    converter = TransactionsConverter()

    tx_on_network = TransactionOnNetwork()
    tx_on_network.nonce = 42
    tx_on_network.function = "hello"

    event = TxEventOnNetwork()
    event.identifier = "signalError"
    event.data_payload = TxEventDataOnNetwork(b"@657865637574696f6e206661696c6564")
    event.additional_data = [TxEventDataOnNetwork("@657865637574696f6e206661696c6564".encode()), TxEventDataOnNetwork("foobar".encode())]
    event.address = Address.new_from_bech32("erd1qqqqqqqqqqqqqpgqj8k976l59n7fyth8ujl4as5uyn3twn0ha0wsge5r5x")
    first_topic = TxEventTopicOnNetwork("XmC5/yOF6ie6DD2kaJd5qPc2Ss7h2w7nvuWaxmCiiXQ=")
    second_topic = TxEventTopicOnNetwork("aW5zdWZmaWNpZW50IGZ1bmRz")
    event.topics = [first_topic, second_topic]

    logs = TxLogsOnNetwork()
    logs.address = Address.new_from_bech32("erd1qqqqqqqqqqqqqpgqj8k976l59n7fyth8ujl4as5uyn3twn0ha0wsge5r5x")
    logs.events = [event]

    contract_result_item = ContractResultItemOnNetwork()
    contract_result_item.nonce = 42
    contract_result_item.data = "@657865637574696f6e206661696c6564"
    contract_result_item.logs = logs

    contract_result = ContractResultOnNetwork([contract_result_item])
    tx_on_network.contract_results = contract_result

    actual_tx_outcome = converter.transaction_on_network_to_outcome(tx_on_network)

    expected_tx_outcome = TransactionOutcome(
        transaction_results=[SmartContractResult(
            sender="",
            receiver="",
            data="@657865637574696f6e206661696c6564".encode(),
            logs=TransactionLogs(
                address="erd1qqqqqqqqqqqqqpgqj8k976l59n7fyth8ujl4as5uyn3twn0ha0wsge5r5x",
                events=[TransactionEvent(
                    address="erd1qqqqqqqqqqqqqpgqj8k976l59n7fyth8ujl4as5uyn3twn0ha0wsge5r5x",
                    identifier="signalError",
                    topics=[
                        Address.new_from_bech32("erd1testnlersh4z0wsv8kjx39me4rmnvjkwu8dsaea7ukdvvc9z396qykv7z7").get_public_key(),
                        "insufficient funds".encode()
                    ],
                    data_items=[
                        "@657865637574696f6e206661696c6564".encode(), "foobar".encode()
                    ]
                )]
            )
        )]
    )

    assert len(actual_tx_outcome.transaction_results) == len(expected_tx_outcome.transaction_results) == 1
    assert actual_tx_outcome.transaction_results[0].sender == expected_tx_outcome.transaction_results[0].sender
    assert actual_tx_outcome.transaction_results[0].receiver == expected_tx_outcome.transaction_results[0].receiver
    assert actual_tx_outcome.transaction_results[0].data == expected_tx_outcome.transaction_results[0].data
    assert actual_tx_outcome.transaction_results[0].logs.address == expected_tx_outcome.transaction_results[0].logs.address
    assert actual_tx_outcome.transaction_results[0].logs.events[0].address == expected_tx_outcome.transaction_results[0].logs.events[0].address
    assert actual_tx_outcome.transaction_results[0].logs.events[0].identifier == expected_tx_outcome.transaction_results[0].logs.events[0].identifier
    assert actual_tx_outcome.transaction_results[0].logs.events[0].data_items == expected_tx_outcome.transaction_results[0].logs.events[0].data_items
    assert actual_tx_outcome.transaction_results[0].logs.events[0].topics == expected_tx_outcome.transaction_results[0].logs.events[0].topics
