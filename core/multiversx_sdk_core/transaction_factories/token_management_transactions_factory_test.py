from multiversx_sdk_core import Address
from multiversx_sdk_core.transaction_factories.token_management_transactions_factory import (
    RegisterAndSetAllRolesTokenType, TokenManagementTransactionsFactory)
from multiversx_sdk_core.transaction_factories.transactions_factory_config import \
    TransactionsFactoryConfig

frank = Address.new_from_bech32("erd1kdl46yctawygtwg2k462307dmz2v55c605737dp3zkxh04sct7asqylhyv")
grace = Address.new_from_bech32("erd1r69gk66fmedhhcg24g2c5kn2f2a5k4kvpr6jfw67dn2lyydd8cfswy6ede")
alice = Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
factory = TokenManagementTransactionsFactory(TransactionsFactoryConfig("T"))


def test_create_transaction_for_registering_and_setting_roles():
    transaction = factory.create_transaction_for_registering_and_setting_roles(
        sender=frank,
        token_name="TEST",
        token_ticker="TEST",
        token_type=RegisterAndSetAllRolesTokenType.FNG,
        num_decimals=2
    )

    assert transaction.data
    assert transaction.data.decode() == "registerAndSetAllRoles@54455354@54455354@464e47@02"
    assert transaction.sender == frank.to_bech32()
    assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction.amount == 50000000000000000


def test_create_transaction_for_issuing_fungible():
    transaction = factory.create_transaction_for_issuing_fungible(
        sender=frank,
        token_name="FRANK",
        token_ticker="FRANK",
        initial_supply=100,
        num_decimals=0,
        can_freeze=True,
        can_wipe=True,
        can_pause=True,
        can_change_owner=True,
        can_upgrade=True,
        can_add_special_roles=True
    )

    assert transaction.data
    assert transaction.data.decode() == "issue@4652414e4b@4652414e4b@64@@63616e467265657a65@74727565@63616e57697065@74727565@63616e5061757365@74727565@63616e4368616e67654f776e6572@74727565@63616e55706772616465@74727565@63616e4164645370656369616c526f6c6573@74727565"
    assert transaction.sender == frank.to_bech32()
    assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction.amount == 50000000000000000


def test_create_transaction_for_issuing_semi_fungible():
    transaction = factory.create_transaction_for_issuing_semi_fungible(
        sender=frank,
        token_name="FRANK",
        token_ticker="FRANK",
        can_freeze=True,
        can_wipe=True,
        can_pause=True,
        can_transfer_nft_create_role=True,
        can_change_owner=True,
        can_upgrade=True,
        can_add_special_roles=True
    )

    assert transaction.data
    assert transaction.data.decode() == "issueSemiFungible@4652414e4b@4652414e4b@63616e467265657a65@74727565@63616e57697065@74727565@63616e5061757365@74727565@63616e5472616e736665724e4654437265617465526f6c65@74727565@63616e4368616e67654f776e6572@74727565@63616e55706772616465@74727565@63616e4164645370656369616c526f6c6573@74727565"
    assert transaction.sender == frank.to_bech32()
    assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction.amount == 50000000000000000


def test_create_transaction_for_issuing_non_fungible():
    transaction = factory.create_transaction_for_issuing_non_fungible(
        sender=frank,
        token_name="FRANK",
        token_ticker="FRANK",
        can_freeze=True,
        can_wipe=True,
        can_pause=True,
        can_transfer_nft_create_role=True,
        can_change_owner=True,
        can_upgrade=True,
        can_add_special_roles=True
    )

    assert transaction.data
    assert transaction.data.decode() == "issueNonFungible@4652414e4b@4652414e4b@63616e467265657a65@74727565@63616e57697065@74727565@63616e5061757365@74727565@63616e5472616e736665724e4654437265617465526f6c65@74727565@63616e4368616e67654f776e6572@74727565@63616e55706772616465@74727565@63616e4164645370656369616c526f6c6573@74727565"
    assert transaction.sender == frank.to_bech32()
    assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction.amount == 50000000000000000


def test_create_transaction_for_registering_meta_esdt():
    transaction = factory.create_transaction_for_registering_meta_esdt(
        sender=frank,
        token_name="FRANK",
        token_ticker="FRANK",
        num_decimals=10,
        can_freeze=True,
        can_wipe=True,
        can_pause=True,
        can_transfer_nft_create_role=True,
        can_change_owner=True,
        can_upgrade=True,
        can_add_special_roles=True
    )

    assert transaction.data
    assert transaction.data.decode() == "registerMetaESDT@4652414e4b@4652414e4b@0a@63616e467265657a65@74727565@63616e57697065@74727565@63616e5061757365@74727565@63616e5472616e736665724e4654437265617465526f6c65@74727565@63616e4368616e67654f776e6572@74727565@63616e55706772616465@74727565@63616e4164645370656369616c526f6c6573@74727565"
    assert transaction.sender == frank.to_bech32()
    assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction.amount == 50000000000000000


def test_create_transaction_for_setting_special_role_on_non_fungible_token():
    transaction = factory.create_transaction_for_setting_special_role_on_non_fungible_token(
        sender=frank,
        user=grace,
        token_identifier="FRANK-11ce3e",
        add_role_nft_create=True,
        add_role_nft_burn=False,
        add_role_nft_update_attributes=True,
        add_role_nft_add_uri=True,
        add_role_esdt_transfer_role=False
    )

    assert transaction.data
    assert transaction.data.decode() == "setSpecialRole@4652414e4b2d313163653365@1e8a8b6b49de5b7be10aaa158a5a6a4abb4b56cc08f524bb5e6cd5f211ad3e13@45534454526f6c654e4654437265617465@45534454526f6c654e465455706461746541747472696275746573@45534454526f6c654e4654416464555249"
    assert transaction.sender == frank.to_bech32()
    assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction.amount == 0


def test_create_transaction_for_creating_nft():
    transaction = factory.create_transaction_for_creating_nft(
        sender=grace,
        token_identifier="FRANK-aa9e8d",
        initial_quantity=1,
        name="test",
        royalties=1000,
        hash="abba",
        attributes=bytes("test", "utf-8"),
        uris=["a", "b"]
    )

    assert transaction.data
    assert transaction.data.decode() == "ESDTNFTCreate@4652414e4b2d616139653864@01@74657374@03e8@61626261@74657374@61@62"
    assert transaction.sender == grace.to_bech32()
    assert transaction.receiver == grace.to_bech32()
    assert transaction.amount == 0
