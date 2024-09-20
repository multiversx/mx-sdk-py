from multiversx_sdk.core.address import Address
from multiversx_sdk.core.serializer import arg_to_string
from multiversx_sdk.core.transactions_factories.token_management_transactions_factory import (
    TokenManagementTransactionsFactory, TokenType)
from multiversx_sdk.core.transactions_factories.transactions_factory_config import \
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
        token_type=TokenType.FNG,
        num_decimals=2
    )

    assert transaction.data
    assert transaction.data.decode() == "registerAndSetAllRoles@54455354@54455354@464e47@02"
    assert transaction.sender == frank.to_bech32()
    assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction.value == 50000000000000000


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
        can_upgrade=False,
        can_add_special_roles=False
    )

    assert transaction.data
    assert transaction.data.decode() == "issue@4652414e4b@4652414e4b@64@@63616e467265657a65@74727565@63616e57697065@74727565@63616e5061757365@74727565@63616e4368616e67654f776e6572@74727565@63616e55706772616465@66616c7365@63616e4164645370656369616c526f6c6573@66616c7365"
    assert transaction.sender == frank.to_bech32()
    assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction.value == 50000000000000000


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
        can_upgrade=False,
        can_add_special_roles=False
    )

    assert transaction.data
    assert transaction.data.decode() == "issueSemiFungible@4652414e4b@4652414e4b@63616e467265657a65@74727565@63616e57697065@74727565@63616e5061757365@74727565@63616e5472616e736665724e4654437265617465526f6c65@74727565@63616e4368616e67654f776e6572@74727565@63616e55706772616465@66616c7365@63616e4164645370656369616c526f6c6573@66616c7365"
    assert transaction.sender == frank.to_bech32()
    assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction.value == 50000000000000000


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
        can_upgrade=False,
        can_add_special_roles=False
    )

    assert transaction.data
    assert transaction.data.decode() == "issueNonFungible@4652414e4b@4652414e4b@63616e467265657a65@74727565@63616e57697065@74727565@63616e5061757365@74727565@63616e5472616e736665724e4654437265617465526f6c65@74727565@63616e4368616e67654f776e6572@74727565@63616e55706772616465@66616c7365@63616e4164645370656369616c526f6c6573@66616c7365"
    assert transaction.sender == frank.to_bech32()
    assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction.value == 50000000000000000


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
        can_upgrade=False,
        can_add_special_roles=False
    )

    assert transaction.data
    assert transaction.data.decode() == "registerMetaESDT@4652414e4b@4652414e4b@0a@63616e467265657a65@74727565@63616e57697065@74727565@63616e5061757365@74727565@63616e5472616e736665724e4654437265617465526f6c65@74727565@63616e4368616e67654f776e6572@74727565@63616e55706772616465@66616c7365@63616e4164645370656369616c526f6c6573@66616c7365"
    assert transaction.sender == frank.to_bech32()
    assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction.value == 50000000000000000


def test_create_transaction_for_setting_special_role_on_non_fungible_token():
    transaction = factory.create_transaction_for_setting_special_role_on_non_fungible_token(
        sender=frank,
        user=grace,
        token_identifier="FRANK-11ce3e",
        add_role_nft_create=True,
        add_role_nft_burn=False,
        add_role_nft_update_attributes=True,
        add_role_nft_add_uri=True,
        add_role_esdt_transfer_role=False,
        add_role_esdt_modify_creator=True,
        add_role_nft_recreate=True
    )

    assert transaction.data
    assert transaction.data.decode() == "setSpecialRole@4652414e4b2d313163653365@1e8a8b6b49de5b7be10aaa158a5a6a4abb4b56cc08f524bb5e6cd5f211ad3e13@45534454526f6c654e4654437265617465@45534454526f6c654e465455706461746541747472696275746573@45534454526f6c654e4654416464555249@45534454526f6c654d6f6469667943726561746f72@45534454526f6c654e46545265637265617465"
    assert transaction.sender == frank.to_bech32()
    assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction.value == 0


def test_create_transaction_for_unsetting_special_role_on_non_fungible_token():
    transaction = factory.create_transaction_for_unsetting_special_role_on_non_fungible_token(
        sender=frank,
        user=grace,
        token_identifier="FRANK-11ce3e",
        remove_role_nft_burn=False,
        remove_role_nft_update_attributes=True,
        remove_role_nft_remove_uri=True,
        remove_role_esdt_transfer_role=False,
        remove_role_esdt_modify_creator=True,
        remove_role_nft_recreate=True
    )

    assert transaction.data
    assert transaction.data.decode() == "unSetSpecialRole@4652414e4b2d313163653365@1e8a8b6b49de5b7be10aaa158a5a6a4abb4b56cc08f524bb5e6cd5f211ad3e13@45534454526f6c654e465455706461746541747472696275746573@45534454526f6c654e4654416464555249@45534454526f6c654d6f6469667943726561746f72@45534454526f6c654e46545265637265617465"
    assert transaction.sender == frank.to_bech32()
    assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction.value == 0


def test_set_roles_on_nft():
    transaction = factory.create_transaction_for_setting_special_role_on_non_fungible_token(
        sender=frank,
        user=grace,
        token_identifier="FRANK-11ce3e",
        add_role_esdt_transfer_role=True
    )

    assert transaction.data
    assert transaction.data.decode() == "setSpecialRole@4652414e4b2d313163653365@1e8a8b6b49de5b7be10aaa158a5a6a4abb4b56cc08f524bb5e6cd5f211ad3e13@455344545472616e73666572526f6c65"
    assert transaction.sender == frank.to_bech32()
    assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction.value == 0

    transaction = factory.create_transaction_for_setting_special_role_on_non_fungible_token(
        sender=frank,
        user=grace,
        token_identifier="FRANK-11ce3e",
        add_role_nft_create=True,
        add_role_nft_burn=True,
        add_role_nft_update_attributes=True,
        add_role_nft_update=True,
        add_role_esdt_modify_royalties=True,
        add_role_esdt_set_new_uri=True,
        add_role_esdt_modify_creator=True,
        add_role_nft_recreate=True,
        add_role_esdt_transfer_role=True,
        add_role_nft_add_uri=True
    )
    assert transaction.data.decode() == "setSpecialRole@4652414e4b2d313163653365@1e8a8b6b49de5b7be10aaa158a5a6a4abb4b56cc08f524bb5e6cd5f211ad3e13@45534454526f6c654e4654437265617465@45534454526f6c654e46544275726e@45534454526f6c654e465455706461746541747472696275746573@45534454526f6c654e4654416464555249@455344545472616e73666572526f6c65@45534454526f6c654e4654557064617465@45534454526f6c654d6f64696679526f79616c74696573@45534454526f6c655365744e6577555249@45534454526f6c654d6f6469667943726561746f72@45534454526f6c654e46545265637265617465"


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
    assert transaction.value == 0


def test_create_transaction_for_setting_special_role_on_fungible_token():
    mint_role_as_hex = arg_to_string("ESDTRoleLocalMint")

    transaction = factory.create_transaction_for_setting_special_role_on_fungible_token(
        sender=frank,
        user=grace,
        token_identifier="FRANK-11ce3e",
        add_role_local_mint=True,
        add_role_local_burn=False,
        add_role_esdt_transfer_role=False
    )

    assert transaction.data
    assert transaction.data.decode() == f"setSpecialRole@4652414e4b2d313163653365@1e8a8b6b49de5b7be10aaa158a5a6a4abb4b56cc08f524bb5e6cd5f211ad3e13@{mint_role_as_hex}"
    assert transaction.sender == frank.to_bech32()
    assert transaction.value == 0


def test_create_transaction_for_unsetting_special_role_on_fungible_token():
    mint_role_as_hex = arg_to_string("ESDTRoleLocalMint")

    transaction = factory.create_transaction_for_unsetting_special_role_on_fungible_token(
        sender=frank,
        user=grace,
        token_identifier="FRANK-11ce3e",
        remove_role_local_mint=True,
        remove_role_local_burn=False,
        remove_role_esdt_transfer_role=False
    )

    assert transaction.data
    assert transaction.data.decode() == f"unSetSpecialRole@4652414e4b2d313163653365@1e8a8b6b49de5b7be10aaa158a5a6a4abb4b56cc08f524bb5e6cd5f211ad3e13@{mint_role_as_hex}"
    assert transaction.sender == frank.to_bech32()
    assert transaction.value == 0


def test_set_all_roles_on_fungible_token():
    mint_role_as_hex = arg_to_string("ESDTRoleLocalMint")
    burn_role_as_hex = arg_to_string("ESDTRoleLocalBurn")
    transfer_role_as_hex = arg_to_string("ESDTTransferRole")

    transaction = factory.create_transaction_for_setting_special_role_on_fungible_token(
        sender=frank,
        user=grace,
        token_identifier="FRANK-11ce3e",
        add_role_local_mint=True,
        add_role_local_burn=True,
        add_role_esdt_transfer_role=True
    )

    assert transaction.data
    assert transaction.data.decode() == f"setSpecialRole@4652414e4b2d313163653365@1e8a8b6b49de5b7be10aaa158a5a6a4abb4b56cc08f524bb5e6cd5f211ad3e13@{mint_role_as_hex}@{burn_role_as_hex}@{transfer_role_as_hex}"
    assert transaction.sender == frank.to_bech32()
    assert transaction.value == 0


def test_create_transaction_for_setting_special_role_on_semi_fungible_token():
    transaction = factory.create_transaction_for_setting_special_role_on_semi_fungible_token(
        sender=frank,
        user=grace,
        token_identifier="FRANK-11ce3e",
        add_role_nft_create=True,
        add_role_nft_burn=True,
        add_role_nft_add_quantity=True,
        add_role_esdt_transfer_role=True,
    )

    assert transaction.data
    assert transaction.data.decode() == "setSpecialRole@4652414e4b2d313163653365@1e8a8b6b49de5b7be10aaa158a5a6a4abb4b56cc08f524bb5e6cd5f211ad3e13@45534454526f6c654e4654437265617465@45534454526f6c654e46544275726e@45534454526f6c654e46544164645175616e74697479@455344545472616e73666572526f6c65"
    assert transaction.sender == frank.to_bech32()
    assert transaction.value == 0


def test_create_transaction_for_unsetting_special_role_on_semi_fungible_token():
    transaction = factory.create_transaction_for_unsetting_special_role_on_semi_fungible_token(
        sender=frank,
        user=grace,
        token_identifier="FRANK-11ce3e",
        remove_role_nft_burn=True,
        remove_role_nft_add_quantity=True,
        remove_role_esdt_transfer_role=True,
    )

    assert transaction.data
    assert transaction.data.decode() == "unSetSpecialRole@4652414e4b2d313163653365@1e8a8b6b49de5b7be10aaa158a5a6a4abb4b56cc08f524bb5e6cd5f211ad3e13@45534454526f6c654e46544275726e@45534454526f6c654e46544164645175616e74697479@455344545472616e73666572526f6c65"
    assert transaction.sender == frank.to_bech32()
    assert transaction.value == 0


def test_create_transaction_for_pausing():
    transaction = factory.create_transaction_for_pausing(
        sender=frank,
        token_identifier="FRANK-11ce3e",
    )

    assert transaction.data
    assert transaction.data.decode() == "pause@4652414e4b2d313163653365"
    assert transaction.sender == frank.to_bech32()
    assert transaction.value == 0


def test_create_transaction_for_unpausing():
    transaction = factory.create_transaction_for_unpausing(
        sender=frank,
        token_identifier="FRANK-11ce3e",
    )

    assert transaction.data
    assert transaction.data.decode() == "unPause@4652414e4b2d313163653365"
    assert transaction.sender == frank.to_bech32()
    assert transaction.value == 0


def test_create_transaction_for_freezing():
    transaction = factory.create_transaction_for_freezing(
        sender=frank,
        user=grace,
        token_identifier="FRANK-11ce3e",
    )

    assert transaction.data
    assert transaction.data.decode() == "freeze@4652414e4b2d313163653365@1e8a8b6b49de5b7be10aaa158a5a6a4abb4b56cc08f524bb5e6cd5f211ad3e13"
    assert transaction.sender == frank.to_bech32()
    assert transaction.value == 0


def test_create_transaction_for_unfreezing():
    transaction = factory.create_transaction_for_unfreezing(
        sender=frank,
        user=grace,
        token_identifier="FRANK-11ce3e",
    )

    assert transaction.data
    assert transaction.data.decode() == "unFreeze@4652414e4b2d313163653365@1e8a8b6b49de5b7be10aaa158a5a6a4abb4b56cc08f524bb5e6cd5f211ad3e13"
    assert transaction.sender == frank.to_bech32()
    assert transaction.value == 0


def test_create_transaction_for_local_minting():
    transaction = factory.create_transaction_for_local_minting(
        sender=frank,
        token_identifier="FRANK-11ce3e",
        supply_to_mint=10
    )

    assert transaction.data
    assert transaction.data.decode() == "ESDTLocalMint@4652414e4b2d313163653365@0a"
    assert transaction.sender == frank.to_bech32()
    assert transaction.value == 0


def test_create_transaction_for_local_burning():
    transaction = factory.create_transaction_for_local_burning(
        sender=frank,
        token_identifier="FRANK-11ce3e",
        supply_to_burn=10
    )

    assert transaction.data
    assert transaction.data.decode() == "ESDTLocalBurn@4652414e4b2d313163653365@0a"
    assert transaction.sender == frank.to_bech32()
    assert transaction.value == 0


def test_create_transaction_for_updating_attributes():
    transaction = factory.create_transaction_for_updating_attributes(
        sender=frank,
        token_identifier="FRANK-11ce3e",
        token_nonce=10,
        attributes=bytes("test", "utf-8"),
    )

    assert transaction.data
    assert transaction.data.decode() == "ESDTNFTUpdateAttributes@4652414e4b2d313163653365@0a@74657374"
    assert transaction.sender == frank.to_bech32()
    assert transaction.value == 0


def test_create_transaction_for_adding_quantity():
    transaction = factory.create_transaction_for_adding_quantity(
        sender=frank,
        token_identifier="FRANK-11ce3e",
        token_nonce=10,
        quantity_to_add=10
    )

    assert transaction.data
    assert transaction.data.decode() == "ESDTNFTAddQuantity@4652414e4b2d313163653365@0a@0a"
    assert transaction.sender == frank.to_bech32()
    assert transaction.value == 0


def test_create_transaction_for_burning_quantity():
    transaction = factory.create_transaction_for_burning_quantity(
        sender=frank,
        token_identifier="FRANK-11ce3e",
        token_nonce=10,
        quantity_to_burn=10
    )

    assert transaction.data
    assert transaction.data.decode() == "ESDTNFTBurn@4652414e4b2d313163653365@0a@0a"
    assert transaction.sender == frank.to_bech32()
    assert transaction.value == 0


def test_create_transaction_for_setting_burn_role_globally():
    transaction = factory.create_transaction_for_setting_burn_role_globally(
        sender=frank,
        token_identifier="FRANK-11ce3e",
    )

    assert transaction.data
    assert transaction.data.decode() == "setBurnRoleGlobally@4652414e4b2d313163653365"
    assert transaction.sender == frank.to_bech32()
    assert transaction.value == 0


def test_create_transaction_for_unsetting_burn_role_globally():
    transaction = factory.create_transaction_for_unsetting_burn_role_globally(
        sender=frank,
        token_identifier="FRANK-11ce3e",
    )

    assert transaction.data
    assert transaction.data.decode() == "unsetBurnRoleGlobally@4652414e4b2d313163653365"
    assert transaction.sender == frank.to_bech32()
    assert transaction.value == 0


def test_create_transaction_for_wiping():
    transaction = factory.create_transaction_for_wiping(
        sender=frank,
        user=grace,
        token_identifier="FRANK-11ce3e"
    )

    assert transaction.data
    assert transaction.data.decode() == "wipe@4652414e4b2d313163653365@1e8a8b6b49de5b7be10aaa158a5a6a4abb4b56cc08f524bb5e6cd5f211ad3e13"
    assert transaction.sender == frank.to_bech32()
    assert transaction.value == 0


def test_create_transaction_for_modifying_royalties():
    transaction = factory.create_transaction_for_modifying_royalties(
        sender=alice,
        token_identifier="TEST-123456",
        token_nonce=1,
        new_royalties=1234
    )

    assert transaction.data.decode() == "ESDTModifyRoyalties@544553542d313233343536@01@04d2"
    assert transaction.sender == alice.to_bech32()
    assert transaction.receiver == alice.to_bech32()
    assert transaction.value == 0
    assert transaction.gas_limit == 60_125_000


def test_create_transaction_for_setting_new_uris():
    transaction = factory.create_transaction_for_setting_new_uris(
        sender=alice,
        token_identifier="TEST-123456",
        token_nonce=1,
        new_uris=["firstURI", "secondURI"]
    )

    assert transaction.data.decode() == "ESDTSetNewURIs@544553542d313233343536@01@6669727374555249@7365636f6e64555249"
    assert transaction.sender == alice.to_bech32()
    assert transaction.receiver == alice.to_bech32()
    assert transaction.value == 0
    assert transaction.gas_limit == 60_164_000


def test_create_transaction_for_modifying_creator():
    transaction = factory.create_transaction_for_modifying_creator(
        sender=alice,
        token_identifier="TEST-123456",
        token_nonce=1,
    )

    assert transaction.data.decode() == "ESDTModifyCreator@544553542d313233343536@01"
    assert transaction.sender == alice.to_bech32()
    assert transaction.receiver == alice.to_bech32()
    assert transaction.value == 0
    assert transaction.gas_limit == 60_114_500


def test_create_transaction_for_updating_metadata():
    transaction = factory.create_transaction_for_updating_metadata(
        sender=alice,
        token_identifier="TEST-123456",
        token_nonce=1,
        new_token_name="Test",
        new_royalties=1234,
        new_hash="abba",
        new_attributes=b"test",
        new_uris=["firstURI", "secondURI"]
    )

    assert transaction.data.decode() == "ESDTMetaDataUpdate@544553542d313233343536@01@54657374@04d2@61626261@74657374@6669727374555249@7365636f6e64555249"
    assert transaction.sender == alice.to_bech32()
    assert transaction.receiver == alice.to_bech32()
    assert transaction.value == 0
    assert transaction.gas_limit == 60_218_000


def test_create_transaction_for_recreating_metadata():
    transaction = factory.create_transaction_for_nft_metadata_recreate(
        sender=alice,
        token_identifier="TEST-123456",
        token_nonce=1,
        new_token_name="Test",
        new_royalties=1234,
        new_hash="abba",
        new_attributes=b"test",
        new_uris=["firstURI", "secondURI"]
    )

    assert transaction.data.decode() == "ESDTMetaDataRecreate@544553542d313233343536@01@54657374@04d2@61626261@74657374@6669727374555249@7365636f6e64555249"
    assert transaction.sender == alice.to_bech32()
    assert transaction.receiver == alice.to_bech32()
    assert transaction.value == 0
    assert transaction.gas_limit == 60_221_000


def test_create_transaction_for_changing_to_dynamic():
    transaction = factory.create_transaction_for_changing_token_to_dynamic(
        sender=alice,
        token_identifier="TEST-123456"
    )

    assert transaction.data.decode() == "changeToDynamic@544553542d313233343536"
    assert transaction.sender == alice.to_bech32()
    assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction.value == 0
    assert transaction.gas_limit == 60_107_000


def test_create_transaction_for_updating_token_id():
    transaction = factory.create_transaction_for_updating_token_id(
        sender=alice,
        token_identifier="TEST-123456"
    )

    assert transaction.data.decode() == "updateTokenID@544553542d313233343536"
    assert transaction.sender == alice.to_bech32()
    assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction.value == 0
    assert transaction.gas_limit == 60_104_000


def test_create_transaction_for_registering_dynamic():
    transaction = factory.create_transaction_for_registering_dynamic_token(
        sender=alice,
        token_name="Test",
        token_ticker="TEST-123456",
        token_type=TokenType.FNG
    )

    assert transaction.data.decode() == "registerDynamic@54657374@544553542d313233343536@464e47"
    assert transaction.sender == alice.to_bech32()
    assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction.value == 50000000000000000
    assert transaction.gas_limit == 60_131_000


def test_create_transaction_for_registering_and_setting_all_roles():
    transaction = factory.create_transaction_for_registering_dynamic_and_setting_roles(
        sender=alice,
        token_name="Test",
        token_ticker="TEST-123456",
        token_type=TokenType.FNG
    )

    assert transaction.data.decode() == "registerAndSetAllRolesDynamic@54657374@544553542d313233343536@464e47"
    assert transaction.sender == alice.to_bech32()
    assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert transaction.value == 50000000000000000
    assert transaction.gas_limit == 60_152_000
