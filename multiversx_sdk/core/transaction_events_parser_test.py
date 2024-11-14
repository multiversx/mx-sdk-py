from pathlib import Path
from types import SimpleNamespace

import pytest

from multiversx_sdk.abi.abi import Abi
from multiversx_sdk.abi.abi_definition import AbiDefinition
from multiversx_sdk.abi.serializer import Serializer
from multiversx_sdk.abi.small_int_values import U64Value
from multiversx_sdk.core.address import Address
from multiversx_sdk.core.transaction_events_parser import \
    TransactionEventsParser
from multiversx_sdk.core.transaction_on_network import (
    TransactionEvent, TransactionLogs, find_events_by_first_topic,
    find_events_by_identifier)
from multiversx_sdk.network_providers import ApiNetworkProvider
from multiversx_sdk.testutils.mock_transaction_on_network import (
    get_empty_smart_contract_result, get_empty_transaction_on_network)

testdata = Path(__file__).parent.parent / "testutils" / "testdata"


def test_parse_events_minimalistic():
    abi = Abi.load(testdata / "esdt-safe.abi.json")
    parser = TransactionEventsParser(abi=abi)
    values = parser.parse_events(
        events=[
            TransactionEvent(
                raw={},
                address=Address.empty(),
                identifier="transferOverMaxAmount",
                topics=["transferOverMaxAmount".encode(), bytes([0x2a]), bytes([0x2b])],
                data=b"",
                additional_data=[]
            )
        ]
    )
    assert len(values) == 1
    assert values[0] == SimpleNamespace(
        batch_id=42,
        tx_id=43
    )


def test_parse_esdt_safe_deposit_event():
    abi = Abi.load(testdata / "esdt-safe.abi.json")
    parser = TransactionEventsParser(abi=abi)

    transaction = get_empty_transaction_on_network()

    logs = TransactionLogs(
        address=Address.empty(),
        events=[
            TransactionEvent(
                raw={},
                address=Address.empty(),
                identifier="",
                topics=[
                    bytes.fromhex("6465706f736974"),
                    bytes.fromhex("726cc2d4b46dd6bd74a4c84d02715bf85cae76318cab81bc09e7c261d4149a67"),
                    bytes.fromhex("0000000c5745474c442d30316534396400000000000000000000000164")
                ],
                data=b"",
                additional_data=[bytes.fromhex("00000000000003db000000")]
            )
        ]
    )

    sc_result = get_empty_smart_contract_result()
    sc_result.data = bytes.fromhex("4036663662")
    sc_result.logs = logs
    transaction.smart_contract_results = [sc_result]

    events = find_events_by_first_topic(transaction, "deposit")
    parsed = parser.parse_events(events)

    assert len(parsed) == 1
    assert parsed[0] == SimpleNamespace(
        dest_address=Address.new_from_bech32(
            "erd1wfkv9495dhtt6a9yepxsyu2mlpw2ua333j4cr0qfulpxr4q5nfnshgyqun").get_public_key(),
        tokens=[SimpleNamespace(
            token_identifier="WEGLD-01e49d",
            token_nonce=0,
            amount=100
        )],
        event_data=SimpleNamespace(
            tx_nonce=987,
            opt_function=None,
            opt_arguments=None,
            opt_gas_limit=None,
        )
    )


def test_parse_multisig_start_perform_action():
    abi = Abi.load(testdata / "multisig-full.abi.json")
    parser = TransactionEventsParser(abi=abi)

    sc_result = get_empty_smart_contract_result()
    sc_result.data = data = bytes.fromhex("4036663662")
    transaction = get_empty_transaction_on_network()
    transaction.smart_contract_results = [sc_result]
    transaction.logs = TransactionLogs(address=Address.empty(), events=[TransactionEvent(
        raw={},
        address=Address.empty(),
        identifier="performAction",
        topics=[bytes.fromhex("7374617274506572666f726d416374696f6e")],
        data=b"",
        additional_data=[bytes.fromhex(
            "00000001000000000500000000000000000500d006f73c4221216fa679bc559005584c4f1160e569e1000000000000000003616464000000010000000107000000010139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1")]
    )])

    events = find_events_by_first_topic(transaction, "startPerformAction")
    parsed = parser.parse_events(events)
    data = parsed[0].data

    assert data == SimpleNamespace(
        action_id=1,
        group_id=0,
        action_data=SimpleNamespace(
            **{
                "0": SimpleNamespace(
                    to=Address.new_from_bech32(
                        "erd1qqqqqqqqqqqqqpgq6qr0w0zzyysklfneh32eqp2cf383zc89d8sstnkl60").get_public_key(),
                    egld_amount=0,
                    opt_gas_limit=None,
                    endpoint_name=b'add',
                    arguments=[bytes.fromhex("07")]
                ),
                '__discriminant__': 5
            }
        ),
        signers=[Address.new_from_bech32(
            "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th").get_public_key()]
    )


def test_parse_event_with_multi_values():
    abi_definition = AbiDefinition.from_dict(
        {
            "events": [
                {
                    "identifier": "doFoobar",
                    "inputs": [
                        {
                            "name": "a",
                            "type": "multi<u8, utf-8 string, u8, utf-8 string>",
                            "indexed": True,
                        },
                        {
                            "name": "b",
                            "type": "multi<utf-8 string, u8>",
                            "indexed": True,
                        },
                        {
                            "name": "c",
                            "type": "u8",
                            "indexed": False,
                        },
                    ],
                },
            ]
        }
    )
    abi = Abi(abi_definition)
    parser = TransactionEventsParser(abi=abi)
    serializer = Serializer()
    first_value, second_value, third_value = serializer.serialize_to_parts(
        [U64Value(42), U64Value(43), U64Value(44)]
    )

    parsed = parser.parse_event(
        TransactionEvent(
            raw={},
            address=Address.empty(),
            identifier="foobar",
            topics=[
                "doFoobar".encode(),
                first_value,
                "test".encode(),
                second_value,
                "test".encode(),
                "test".encode(),
                third_value,
            ],
            data=b"",
            additional_data=[first_value]
        )
    )

    assert parsed == SimpleNamespace(
        a=[42, "test", 43, "test"],
        b=["test", 44],
        c=42
    )


def test_parse_esdt_safe_deposit_event_without_first_topic():
    abi = Abi.load(testdata / "esdt-safe.abi.json")
    parser = TransactionEventsParser(abi=abi)

    transaction = get_empty_transaction_on_network()

    logs = TransactionLogs(
        address=Address.empty(),
        events=[
            TransactionEvent(
                raw={},
                address=Address.empty(),
                identifier="deposit",
                topics=[
                    bytes.fromhex(""),
                    bytes.fromhex("726cc2d4b46dd6bd74a4c84d02715bf85cae76318cab81bc09e7c261d4149a67"),
                    bytes.fromhex("0000000c5745474c442d30316534396400000000000000000000000164")
                ],
                data=b"",
                additional_data=[bytes.fromhex("00000000000003db000000")]
            )
        ]
    )

    sc_result = get_empty_smart_contract_result()
    sc_result.data = bytes.fromhex("4036663662")
    sc_result.logs = logs
    transaction.smart_contract_results = [sc_result]

    events = find_events_by_identifier(transaction, "deposit")
    parsed = parser.parse_events(events)

    assert len(parsed) == 1
    assert parsed[0] == SimpleNamespace(
        dest_address=Address.new_from_bech32(
            "erd1wfkv9495dhtt6a9yepxsyu2mlpw2ua333j4cr0qfulpxr4q5nfnshgyqun").get_public_key(),
        tokens=[SimpleNamespace(
            token_identifier="WEGLD-01e49d",
            token_nonce=0,
            amount=100
        )],
        event_data=SimpleNamespace(
            tx_nonce=987,
            opt_function=None,
            opt_arguments=None,
            opt_gas_limit=None,
        )
    )


@pytest.mark.networkInteraction
def test_multisig_start_perform_action():
    api = ApiNetworkProvider("https://devnet-api.multiversx.com")

    # Test was set up as follows:
    # Deploy multisig
    # mxpy contract deploy --bytecode=./multisig-full.wasm --gas-limit=100000000 --recall-nonce --arguments 2 erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx --proxy=https://devnet-gateway.multiversx.com --pem=erd1test.pem --send
    # Call "proposeTransferExecute"
    # mxpy contract call erd1qqqqqqqqqqqqqpgqnquyu4atwjz89p8vd8k0k7sz5qaeyfj2396qmek84v --function proposeTransferExecute --gas-limit=20000000 --recall-nonce --arguments erd1r69gk66fmedhhcg24g2c5kn2f2a5k4kvpr6jfw67dn2lyydd8cfswy6ede 1000000000000000000 0x00 --proxy=https://devnet-gateway.multiversx.com --pem=alice.pem --send
    # Call "sign"
    # mxpy contract call erd1qqqqqqqqqqqqqpgqnquyu4atwjz89p8vd8k0k7sz5qaeyfj2396qmek84v --function sign --gas-limit=20000000 --recall-nonce --arguments 1 --proxy=https://devnet-gateway.multiversx.com --pem=bob.pem --send
    # Call "deposit"
    # mxpy contract call erd1qqqqqqqqqqqqqpgqnquyu4atwjz89p8vd8k0k7sz5qaeyfj2396qmek84v --function deposit --gas-limit=20000000 --recall-nonce --value 1000000000000000000 --proxy=https://devnet-gateway.multiversx.com --pem=alice.pem --send
    # Call "performAction"
    # mxpy contract call erd1qqqqqqqqqqqqqpgqnquyu4atwjz89p8vd8k0k7sz5qaeyfj2396qmek84v --function performAction --gas-limit=20000000 --recall-nonce --arguments 1 --proxy=https://devnet-gateway.multiversx.com --pem=alice.pem --send
    transaction_on_network = api.get_transaction("6651b983d494d69d94ce3efb3ae1604480af7c17780ab58daa09a9e5cc1d86c8")

    abi = Abi.load(testdata / "multisig-full.abi.json")
    events_parser = TransactionEventsParser(abi)

    events = find_events_by_first_topic(transaction_on_network, "startPerformAction")
    parsed_event = events_parser.parse_event(events[0])

    assert parsed_event.data == SimpleNamespace(
        action_id=1,
        group_id=0,
        action_data=SimpleNamespace(
            **{
                "0": SimpleNamespace(
                    **{
                        'to': Address.new_from_bech32("erd1r69gk66fmedhhcg24g2c5kn2f2a5k4kvpr6jfw67dn2lyydd8cfswy6ede").get_public_key(),
                        'egld_amount': 1000000000000000000,
                        'opt_gas_limit': None,
                        'endpoint_name': b'',
                        'arguments': []
                    }
                ),
                '__discriminant__': 5
            },
        ),
        signers=[Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th").get_public_key(),
                 Address.new_from_bech32("erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx").get_public_key()]
    )
