from multiversx_sdk.network_providers.query_builder import \
    build_query_for_accounts


def test_build_query_for_accounts_no_params():
    query = build_query_for_accounts()
    assert query == ""


def test_build_query_with_size():
    query = build_query_for_accounts(size=5)
    assert query == "?size=5"


def test_build_query_for_accounts_basic_query():
    query = build_query_for_accounts(start=1, size=10, owner_address="erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
    assert query == "?from=1&size=10&ownerAddress=erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"


def test_build_query_for_accounts_optional_params():
    query = build_query_for_accounts(
        start=1,
        size=10,
        owner_address="erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
        name="name",
        tags=["tag1", "tag2"],
        sort="date",
        order="asc",
        is_smart_contract=True,
        with_owner_assets=True,
        with_deploy_info=True,
        with_tx_count=True,
        with_scr_count=True,
        exclude_tags=["tag3", "tag4"],
        has_assets=True
    )
    expected_query = (
        "?from=1&size=10&ownerAddress=erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th&name=name"
        "&tags=tag1,tag2&sort=date&order=asc&isSmartContract=true"
        "&withOwnerAssets=true&withDeployInfo=true&withTxCount=true"
        "&withScrCount=true&excludeTags=tag3,tag4&hasAssets=true"
    )
    assert query == expected_query
