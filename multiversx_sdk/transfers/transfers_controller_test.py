from pathlib import Path

import pytest

from multiversx_sdk.accounts.account import Account
from multiversx_sdk.core.address import Address
from multiversx_sdk.core.tokens import Token, TokenTransfer
from multiversx_sdk.entrypoints.entrypoints import DevnetEntrypoint
from multiversx_sdk.wallet.user_keys import UserSecretKey


@pytest.mark.networkInteraction
class TestTransfersController:
    john = Account(UserSecretKey(bytes.fromhex("bdf3c95c4b0bcbacd828b148231a10c25f93286befe92077b5d096055fb4e96a")))
    mike = Address.new_from_bech32("erd1uv40ahysflse896x4ktnh6ecx43u7cmy9wnxnvcyp7deg299a4sq6vaywa")
    grace = Account.new_from_pem(Path(__file__).parent.parent / "testutils" / "testwallets" / "grace.pem")
    heidi = Account.new_from_pem(Path(__file__).parent.parent / "testutils" / "testwallets" / "heidi.pem")
    usdc = "USDC-350c4e"

    entrypoint = DevnetEntrypoint(kind="proxy", with_gas_limit_estimator=True)
    proxy = entrypoint.create_network_provider()
    controller = entrypoint.create_transfers_controller()

    def test_send_relayed_with_no_native_balance(self):
        self.john.nonce = self.entrypoint.recall_account_nonce(self.john.address)
        transaction = self.controller.create_transaction_for_transfer(
            sender=self.john,
            nonce=self.john.get_nonce_then_increment(),
            receiver=self.mike,
            token_transfers=[TokenTransfer(Token(self.usdc), 7)],
            data="hello".encode(),
            relayer=self.grace.address,
        )
        transaction.relayer_signature = self.grace.sign_transaction(transaction)

        assert transaction.sender.to_bech32() == "erd1th3kjm4yjd25lwewe4m5akuqsappqdml8jxuneasnavj7752veysa2sylq"
        assert transaction.receiver.to_bech32() == self.mike.to_bech32()
        assert transaction.chain_id == "D"
        assert transaction.gas_limit == 373_501
        assert transaction.data.decode() == "ESDTTransfer@555344432d333530633465@07@68656c6c6f"

    def test_send_guarded_transaction(self):
        self.heidi.nonce = self.entrypoint.recall_account_nonce(self.heidi.address)
        guardian = Address.new_from_bech32("erd1ssrnya4hsq4kajk0n340eznm27e5s2cz62vyadquku006mf7ur0qtl99l0")

        transaction = self.controller.create_transaction_for_transfer(
            sender=self.heidi,
            nonce=self.heidi.get_nonce_then_increment(),
            receiver=self.mike,
            data="hello".encode(),
            guardian=guardian,
        )

        assert transaction.sender.to_bech32() == "erd1dc3yzxxeq69wvf583gw0h67td226gu2ahpk3k50qdgzzym8npltq7ndgha"
        assert transaction.receiver.to_bech32() == self.mike.to_bech32()
        assert transaction.chain_id == "D"
        assert transaction.gas_limit == 107_500
        assert transaction.data.decode() == "hello"
        assert transaction.guardian == guardian
