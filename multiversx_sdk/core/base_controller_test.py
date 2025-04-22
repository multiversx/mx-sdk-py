from pathlib import Path

from multiversx_sdk.accounts.account import Account
from multiversx_sdk.core.address import Address
from multiversx_sdk.core.base_controller import BaseController
from multiversx_sdk.core.transaction import Transaction


class TestBaseController:
    controller = BaseController()

    def test_version_and_options_for_hash_signing(self):
        testwallets = Path(__file__).parent.parent / "testutils" / "testwallets"
        alice = Account.new_from_pem(testwallets / "alice.pem")
        alice.use_hash_signing = True

        transaction = Transaction(
            sender=alice.address,
            receiver=Address.new_from_bech32("erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"),
            gas_limit=50_000,
            chain_id="D",
            version=1,
            options=0,
        )

        self.controller._set_version_and_options_for_hash_signing(sender=alice, transaction=transaction)  # type: ignore
        assert transaction.version == 2
        assert transaction.options == 1

    def test_add_extra_gas_limit(self):
        transaction = Transaction(
            sender=Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"),
            receiver=Address.new_from_bech32("erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"),
            gas_limit=50_000,
            chain_id="D",
            guardian=Address.new_from_bech32("erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8"),
            relayer=Address.new_from_bech32("erd1kdl46yctawygtwg2k462307dmz2v55c605737dp3zkxh04sct7asqylhyv"),
        )

        self.controller._add_extra_gas_limit_if_required(transaction=transaction)  # type: ignore
        assert transaction.gas_limit == 150_000

    def test_set_version_and_options_for_guardian(self):
        transaction = Transaction(
            sender=Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"),
            receiver=Address.new_from_bech32("erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"),
            gas_limit=50_000,
            chain_id="D",
            guardian=Address.new_from_bech32("erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8"),
            version=1,
            options=0,
        )

        self.controller._set_version_and_options_for_guardian(transaction=transaction)  # type: ignore
        assert transaction.version == 2
        assert transaction.options == 2
