from pathlib import Path

from multiversx_sdk.abi.abi import Abi
from multiversx_sdk.core.transactions_outcome_parsers.resources import \
    TransactionEvent
from multiversx_sdk.core.transactions_outcome_parsers.transaction_events_parser import \
    TransactionEventsParser

testdata = Path(__file__).parent.parent.parent / "testutils" / "testdata"


def test_parse_events_minimalistic():
    abi = Abi.load(testdata / "esdt-safe.abi.json")
    parser = TransactionEventsParser(abi=abi)

    values = parser.parse_events(
        events=[
            TransactionEvent(
                identifier="transferOverMaxAmount",
                topics=["transferOverMaxAmount".encode(), bytes([0x2a]), bytes([0x2b])]
            )
        ]
    )

    assert len(values) == 1
    assert values[0] == {"batch_id": 42, "tx_id": 43}
