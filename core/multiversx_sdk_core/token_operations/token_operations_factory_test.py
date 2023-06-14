

from multiversx_sdk_core import Address
from multiversx_sdk_core.token_operations.token_operations_factory import \
    TokenOperationsFactory
from multiversx_sdk_core.token_operations.token_operations_factory_config import \
    TokenOperationsFactoryConfig

frank = Address.from_bech32("erd1kdl46yctawygtwg2k462307dmz2v55c605737dp3zkxh04sct7asqylhyv")
grace = Address.from_bech32("erd1r69gk66fmedhhcg24g2c5kn2f2a5k4kvpr6jfw67dn2lyydd8cfswy6ede")
factory = TokenOperationsFactory(TokenOperationsFactoryConfig("T"))


def test_issue_fungible():
    transaction = factory.issue_fungible(
        issuer=frank,
        token_name="FRANK",
        token_ticker="FRANK",
        initial_supply=100,
        num_decimals=0,
        can_freeze=True,
        can_wipe=True,
        can_pause=True,
        can_change_owner=True,
        can_upgrade=True,
        can_add_special_roles=True,
        transaction_nonce=42
    )

    assert str(transaction.data) == "issue@4652414e4b@4652414e4b@64@@63616e467265657a65@74727565@63616e57697065@74727565@63616e5061757365@74727565@63616e4368616e67654f776e6572@74727565@63616e55706772616465@74727565@63616e4164645370656369616c526f6c6573@74727565"
    assert transaction.nonce == 42
    assert transaction.sender.bech32() == frank.bech32()
    assert transaction.receiver.bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
