
from erdpy_core.address import Address
from erdpy_core.transaction_builders.default_configuration import \
    DefaultTransactionBuildersConfiguration
from erdpy_core.transaction_builders.esdt_builders import ESDTIssueBuilder

dummyConfig = DefaultTransactionBuildersConfiguration(chain_id="D")


def test_esdt_issue_builder():
    issuer = Address.from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")

    builder = ESDTIssueBuilder(
        config=dummyConfig,
        issuer=issuer,
        token_name="FOO",
        token_ticker="FOO",
        initial_supply=1000000000000,
        num_decimals=8,
        can_freeze=True,
        can_mint=True,
        can_upgrade=True
    )

    payload = builder.build_payload()
    tx = builder.build()

    assert payload.data == b"issue@464f4f@464f4f@e8d4a51000@08@63616e467265657a65@74727565@63616e4d696e74@74727565@63616e55706772616465@74727565"
    assert tx.chainID == "D"
    assert tx.sender == issuer
    assert tx.receiver.bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert tx.gas_limit == 50000 + payload.length() * 1500 + 60000000
    assert tx.data.encoded() == payload.encoded()
