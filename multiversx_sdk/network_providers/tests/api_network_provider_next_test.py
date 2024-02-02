from multiversx_sdk.network_providers.api_network_provider_next import \
    ApiProviderNext


class TestApiProviderNext:
    api = ApiProviderNext("https://devnet-multiversx.com")

    def test_get_accounts(self):
        accounts = self.api.get_accounts(size=2)

        assert len(accounts) == 2
        assert accounts[0].address == "erd1an4xpn58j7ymd58m2jznr32t0vmas75egrdfa8mta6fzvqn9tkxq4jvghn"
        assert accounts[1].address == "erd1kyle4p6chlvj0u6fyds7wj47jqwq6kh9h083kw8j76254l8u49dqepfz86"
