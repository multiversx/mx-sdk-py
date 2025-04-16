from pathlib import Path

from multiversx_sdk.abi.abi import Abi
from multiversx_sdk.accounts.account import Account
from multiversx_sdk.core.address import Address
from multiversx_sdk.core.tokens import Token, TokenTransfer
from multiversx_sdk.multisig.multisig_transactions_controller import MultisigController
from multiversx_sdk.network_providers.api_network_provider import ApiNetworkProvider
from multiversx_sdk.testutils.utils import create_network_providers_config


class TestMultisigController:
    testdata = Path(__file__).parent.parent / "testutils" / "testdata"
    testwallets = Path(__file__).parent.parent / "testutils" / "testwallets"
    multisig_bytecode = (testdata / "multisig-full.wasm").read_bytes()
    multisig_abi = Abi.load(testdata / "multisig-full.abi.json")
    network_provider = ApiNetworkProvider(
        url="https://devnet-api.multiversx.com", config=create_network_providers_config()
    )
    controller = MultisigController(chain_id="D", network_provider=network_provider, abi=multisig_abi)
    john = Account.new_from_pem(testwallets / "user.pem")
    john.nonce = network_provider.get_account(john.address).nonce
    bob = Account.new_from_pem(testwallets / "bob.pem")
    contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqpgqe832k3l6d02ww7l9cvqum25539nmmdxa9ncsdutjuf")

    def test_deploy_contract(self):
        transaction = self.controller.create_transaction_for_deploy(
            sender=self.john,
            nonce=self.john.get_nonce_then_increment(),
            bytecode=self.multisig_bytecode,
            quorum=2,
            board=[self.john.address, self.bob.address],
            gas_limit=100_000_000,
        )
        assert transaction.sender == self.john.address
        assert transaction.receiver == Address.new_from_bech32(
            "erd1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq6gq4hu"
        )
        assert transaction.value == 0
        assert transaction.gas_limit == 100_000_000
        assert transaction.chain_id == "D"
        assert (
            transaction.data.decode()
            == f"{self.multisig_bytecode.hex()}@0500@0504@02@3fb81f4303be6f7377350b8a595f94b13fd6cbce4c4c7d2c63e9e1f8f0d42cf1@8049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f8"
        )

    def test_deposit_native_token(self):
        transaction = self.controller.create_transaction_for_deposit(
            sender=self.john,
            nonce=self.john.get_nonce_then_increment(),
            contract=self.contract,
            gas_limit=60_000_000,
            native_token_amount=1000000000000000000,  # 1 EGLD
        )
        assert transaction.sender == self.john.address
        assert transaction.receiver == Address.new_from_bech32(
            "erd1qqqqqqqqqqqqqpgqe832k3l6d02ww7l9cvqum25539nmmdxa9ncsdutjuf"
        )
        assert transaction.value == 1000000000000000000
        assert transaction.gas_limit == 60_000_000
        assert transaction.chain_id == "D"
        assert transaction.data.decode() == "deposit"

    def test_deposit_esdt(self):
        transaction = self.controller.create_transaction_for_deposit(
            sender=self.john,
            nonce=self.john.get_nonce_then_increment(),
            contract=self.contract,
            gas_limit=60_000_000,
            token_transfers=[
                TokenTransfer(Token("MYTKN-a584f9"), 100_000),
                TokenTransfer(Token("SFT-1bc261", 1), 1),
            ],
        )
        assert transaction.sender == self.john.address
        assert transaction.receiver == self.john.address
        assert transaction.value == 0
        assert transaction.gas_limit == 60_000_000
        assert transaction.chain_id == "D"
        assert (
            transaction.data.decode()
            == f"MultiESDTNFTTransfer@{self.contract.to_hex()}@02@4d59544b4e2d613538346639@@0186a0@5346542d316263323631@01@01@6465706f736974"
        )
