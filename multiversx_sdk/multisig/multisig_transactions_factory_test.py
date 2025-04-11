from pathlib import Path

import pytest

from multiversx_sdk.abi.abi import Abi
from multiversx_sdk.abi.biguint_value import BigUIntValue
from multiversx_sdk.core.address import Address
from multiversx_sdk.core.tokens import Token, TokenTransfer
from multiversx_sdk.core.transactions_factory_config import TransactionsFactoryConfig
from multiversx_sdk.multisig.multisig_transactions_factory import (
    MultisigTransactionsFactory,
)


class TestMultisigTransactionsFactory:
    testdata = Path(__file__).parent.parent / "testutils" / "testdata"
    bytecode = (testdata / "multisig-full.wasm").read_bytes()
    abi = Abi.load(testdata / "multisig-full.abi.json")

    abi_factory = MultisigTransactionsFactory(TransactionsFactoryConfig("D"), abi)
    factory = MultisigTransactionsFactory(TransactionsFactoryConfig("D"))

    def test_deploy_multisig(self):
        alice = Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
        bob = Address.new_from_bech32("erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx")

        abi_transaction = self.abi_factory.create_transaction_for_deploy(
            sender=alice,
            bytecode=self.bytecode,
            quorum=2,
            board=[alice, bob],
            gas_limit=100_000_000,
            native_transfer_amount=1000000000000000000,  # 1 EGLD
        )
        transaction = self.factory.create_transaction_for_deploy(
            sender=alice,
            bytecode=self.bytecode,
            quorum=2,
            board=[alice, bob],
            gas_limit=100_000_000,
            native_transfer_amount=1000000000000000000,  # 1 EGLD
        )
        assert transaction.sender == alice
        assert transaction.receiver == Address.new_from_bech32(
            "erd1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq6gq4hu"
        )
        assert transaction.value == 1000000000000000000
        assert transaction.gas_limit == 100_000_000
        assert transaction.chain_id == "D"
        assert (
            transaction.data.decode()
            == f"{self.bytecode.hex()}@0500@0504@02@0139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1@8049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f8"
        )
        assert abi_transaction == transaction

    def test_propose_add_board_member(self):
        alice = Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
        bob = Address.new_from_bech32("erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx")
        contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqpgq6kurkz43xq8t35kx9p8rvyz5kpxe9g7qd8ssefqjw8")

        abi_transaction = self.abi_factory.create_transaction_for_propose_add_board_member(
            sender=alice,
            contract=contract,
            board_member=bob,
            gas_limit=60_000_000,
        )
        transaction = self.factory.create_transaction_for_propose_add_board_member(
            sender=alice,
            contract=contract,
            board_member=bob,
            gas_limit=60_000_000,
        )
        assert transaction.sender == alice
        assert transaction.receiver == Address.new_from_bech32(
            "erd1qqqqqqqqqqqqqpgq6kurkz43xq8t35kx9p8rvyz5kpxe9g7qd8ssefqjw8"
        )
        assert transaction.value == 0
        assert transaction.gas_limit == 60_000_000
        assert transaction.chain_id == "D"
        assert (
            transaction.data.decode()
            == "proposeAddBoardMember@8049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f8"
        )
        assert abi_transaction == transaction

    def test_propose_add_proposer(self):
        alice = Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
        bob = Address.new_from_bech32("erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx")
        contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqpgq6kurkz43xq8t35kx9p8rvyz5kpxe9g7qd8ssefqjw8")

        abi_transaction = self.abi_factory.create_transaction_for_propose_add_proposer(
            sender=alice,
            contract=contract,
            proposer=bob,
            gas_limit=60_000_000,
        )
        transaction = self.factory.create_transaction_for_propose_add_proposer(
            sender=alice,
            contract=contract,
            proposer=bob,
            gas_limit=60_000_000,
        )
        assert transaction.sender == alice
        assert transaction.receiver == Address.new_from_bech32(
            "erd1qqqqqqqqqqqqqpgq6kurkz43xq8t35kx9p8rvyz5kpxe9g7qd8ssefqjw8"
        )
        assert transaction.value == 0
        assert transaction.gas_limit == 60_000_000
        assert transaction.chain_id == "D"
        assert (
            transaction.data.decode()
            == "proposeAddProposer@8049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f8"
        )
        assert abi_transaction == transaction

    def test_propose_remove_user(self):
        alice = Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
        bob = Address.new_from_bech32("erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx")
        contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqpgq6kurkz43xq8t35kx9p8rvyz5kpxe9g7qd8ssefqjw8")

        abi_transaction = self.abi_factory.create_transaction_for_propose_remove_user(
            sender=alice,
            contract=contract,
            user=bob,
            gas_limit=60_000_000,
        )
        transaction = self.factory.create_transaction_for_propose_remove_user(
            sender=alice,
            contract=contract,
            user=bob,
            gas_limit=60_000_000,
        )
        assert transaction.sender == alice
        assert transaction.receiver == Address.new_from_bech32(
            "erd1qqqqqqqqqqqqqpgq6kurkz43xq8t35kx9p8rvyz5kpxe9g7qd8ssefqjw8"
        )
        assert transaction.value == 0
        assert transaction.gas_limit == 60_000_000
        assert transaction.chain_id == "D"
        assert (
            transaction.data.decode()
            == "proposeRemoveUser@8049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f8"
        )
        assert abi_transaction == transaction

    def test_propose_change_quorum(self):
        alice = Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
        contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqpgq6kurkz43xq8t35kx9p8rvyz5kpxe9g7qd8ssefqjw8")

        abi_transaction = self.abi_factory.create_transaction_for_propose_change_quorum(
            sender=alice,
            contract=contract,
            quorum=10,
            gas_limit=60_000_000,
        )
        transaction = self.factory.create_transaction_for_propose_change_quorum(
            sender=alice,
            contract=contract,
            quorum=10,
            gas_limit=60_000_000,
        )
        assert transaction.sender == alice
        assert transaction.receiver == Address.new_from_bech32(
            "erd1qqqqqqqqqqqqqpgq6kurkz43xq8t35kx9p8rvyz5kpxe9g7qd8ssefqjw8"
        )
        assert transaction.value == 0
        assert transaction.gas_limit == 60_000_000
        assert transaction.chain_id == "D"
        assert transaction.data.decode() == "proposeChangeQuorum@0a"
        assert abi_transaction == transaction

    def test_deposit_without_tokens(self):
        alice = Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
        contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqpgq6kurkz43xq8t35kx9p8rvyz5kpxe9g7qd8ssefqjw8")

        with pytest.raises(Exception, match="No native token amount or token transfers provided"):
            self.abi_factory.create_transaction_for_deposit(
                sender=alice,
                contract=contract,
                gas_limit=60_000_000,
            )

        with pytest.raises(Exception, match="No native token amount or token transfers provided"):
            self.abi_factory.create_transaction_for_deposit(
                sender=alice,
                contract=contract,
                gas_limit=60_000_000,
            )

    def test_deposit_native_token(self):
        alice = Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
        contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqpgq6kurkz43xq8t35kx9p8rvyz5kpxe9g7qd8ssefqjw8")

        abi_transaction = self.abi_factory.create_transaction_for_deposit(
            sender=alice,
            contract=contract,
            gas_limit=60_000_000,
            native_token_amount=1000000000000000000,  # 1 EGLD
        )
        transaction = self.factory.create_transaction_for_deposit(
            sender=alice,
            contract=contract,
            gas_limit=60_000_000,
            native_token_amount=1000000000000000000,  # 1 EGLD
        )
        assert transaction.sender == alice
        assert transaction.receiver == Address.new_from_bech32(
            "erd1qqqqqqqqqqqqqpgq6kurkz43xq8t35kx9p8rvyz5kpxe9g7qd8ssefqjw8"
        )
        assert transaction.value == 1000000000000000000
        assert transaction.gas_limit == 60_000_000
        assert transaction.chain_id == "D"
        assert transaction.data.decode() == "deposit"
        assert abi_transaction == transaction

    def test_deposit_esdt(self):
        alice = Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
        contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqpgq6kurkz43xq8t35kx9p8rvyz5kpxe9g7qd8ssefqjw8")

        abi_transaction = self.abi_factory.create_transaction_for_deposit(
            sender=alice,
            contract=contract,
            gas_limit=60_000_000,
            token_transfers=[
                TokenTransfer(Token("ABCDEF-123456"), 100_000),
                TokenTransfer(Token("XYZQWE-987654", 7), 1),
            ],
        )
        transaction = self.factory.create_transaction_for_deposit(
            sender=alice,
            contract=contract,
            gas_limit=60_000_000,
            token_transfers=[
                TokenTransfer(Token("ABCDEF-123456"), 100_000),
                TokenTransfer(Token("XYZQWE-987654", 7), 1),
            ],
        )
        assert transaction.sender == alice
        assert transaction.receiver == alice
        assert transaction.value == 0
        assert transaction.gas_limit == 60_000_000
        assert transaction.chain_id == "D"
        assert (
            transaction.data.decode()
            == f"MultiESDTNFTTransfer@{contract.to_hex()}@02@4142434445462d313233343536@@0186a0@58595a5157452d393837363534@07@01@6465706f736974"
        )
        assert abi_transaction == transaction

    def test_deposit_native_and_esdt(self):
        alice = Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
        contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqpgq6kurkz43xq8t35kx9p8rvyz5kpxe9g7qd8ssefqjw8")

        abi_transaction = self.abi_factory.create_transaction_for_deposit(
            sender=alice,
            contract=contract,
            gas_limit=60_000_000,
            native_token_amount=1000000000000000000,
            token_transfers=[
                TokenTransfer(Token("ABCDEF-123456"), 100_000),
                TokenTransfer(Token("XYZQWE-987654", 7), 1),
            ],
        )
        transaction = self.factory.create_transaction_for_deposit(
            sender=alice,
            contract=contract,
            gas_limit=60_000_000,
            native_token_amount=1000000000000000000,
            token_transfers=[
                TokenTransfer(Token("ABCDEF-123456"), 100_000),
                TokenTransfer(Token("XYZQWE-987654", 7), 1),
            ],
        )
        assert transaction.sender == alice
        assert transaction.receiver == alice
        assert transaction.value == 0
        assert transaction.gas_limit == 60_000_000
        assert transaction.chain_id == "D"
        assert (
            transaction.data.decode()
            == f"MultiESDTNFTTransfer@{contract.to_hex()}@03@4142434445462d313233343536@@0186a0@58595a5157452d393837363534@07@01@45474c442d303030303030@@0de0b6b3a7640000@6465706f736974"
        )
        assert abi_transaction == transaction

    def test_propose_transfer_and_execute(self):
        alice = Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
        multisig = Address.new_from_bech32("erd1qqqqqqqqqqqqqpgq6kurkz43xq8t35kx9p8rvyz5kpxe9g7qd8ssefqjw8")
        contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqpgq0rffvv4vk9vesqplv9ws55fxzdfaspqa8cfszy2hms")
        amount = 1000000000000000000
        adder = Abi.load(self.testdata / "adder.abi.json")

        abi_transaction = self.abi_factory.create_transaction_for_propose_transfer_execute(
            sender=alice,
            contract=multisig,
            receiver=contract,
            native_token_amount=amount,
            gas_limit=60_000_000,
            opt_gas_limit=1_000_000,
            abi=adder,
            function="add",
            arguments=[7],
        )

        transaction = self.factory.create_transaction_for_propose_transfer_execute(
            sender=alice,
            contract=multisig,
            receiver=contract,
            native_token_amount=amount,
            gas_limit=60_000_000,
            opt_gas_limit=1_000_000,
            function="add",
            arguments=[BigUIntValue(7)],
        )
        assert transaction.sender == alice
        assert transaction.receiver == multisig
        assert transaction.value == 0
        assert transaction.gas_limit == 60_000_000
        assert transaction.chain_id == "D"
        assert (
            transaction.data.decode()
            == "proposeTransferExecute@0000000000000000050078d29632acb15998003f615d0a51261353d8041d3e13@0de0b6b3a7640000@0100000000000f4240@616464@07"
        )
        assert abi_transaction == transaction

    def test_propose_transfer_esdt_and_execute(self):
        alice = Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
        multisig = Address.new_from_bech32("erd1qqqqqqqqqqqqqpgq6kurkz43xq8t35kx9p8rvyz5kpxe9g7qd8ssefqjw8")
        contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqpgqfxlljcaalgl2qfcnxcsftheju0ts36kvl3ts3qkewe")

        abi_transaction = self.abi_factory.create_transaction_for_propose_transfer_esdt_execute(
            sender=alice,
            contract=multisig,
            receiver=contract,
            token_transfers=[TokenTransfer(Token("ALICE-5627f1"), 10)],
            gas_limit=60_000_000,
            opt_gas_limit=5_000_000,
            function="distribute",
            arguments=[],
        )

        transaction = self.factory.create_transaction_for_propose_transfer_esdt_execute(
            sender=alice,
            contract=multisig,
            receiver=contract,
            token_transfers=[TokenTransfer(Token("ALICE-5627f1"), 10)],
            gas_limit=60_000_000,
            opt_gas_limit=5_000_000,
            function="distribute",
            arguments=[],
        )
        assert abi_transaction.sender == alice
        assert abi_transaction.receiver == multisig
        assert abi_transaction.value == 0
        assert abi_transaction.gas_limit == 60_000_000
        assert abi_transaction.chain_id == "D"
        assert (
            abi_transaction.data.decode()
            == "proposeTransferExecuteEsdt@0000000000000000050049bff963bdfa3ea02713362095df32e3d708eaccfc57@0000000c414c4943452d3536323766310000000000000000000000010a@0100000000004c4b40@3634363937333734373236393632373537343635"
        )
        assert abi_transaction == transaction

    @pytest.mark.only
    def test_propose_async_call(self):
        alice = Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
        multisig = Address.new_from_bech32("erd1qqqqqqqqqqqqqpgq6kurkz43xq8t35kx9p8rvyz5kpxe9g7qd8ssefqjw8")
        contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqpgq0rffvv4vk9vesqplv9ws55fxzdfaspqa8cfszy2hms")
        adder = Abi.load(self.testdata / "adder.abi.json")

        abi_transaction = self.abi_factory.create_transaction_for_propose_async_call(
            sender=alice,
            contract=multisig,
            receiver=contract,
            gas_limit=60_000_000,
            opt_gas_limit=5_000_000,
            function="add",
            arguments=[7],
            abi=adder,
        )

        transaction = self.factory.create_transaction_for_propose_async_call(
            sender=alice,
            contract=multisig,
            receiver=contract,
            gas_limit=60_000_000,
            opt_gas_limit=5_000_000,
            function="add",
            arguments=[BigUIntValue(7)],
        )
        assert abi_transaction.sender == alice
        assert abi_transaction.receiver == multisig
        assert abi_transaction.value == 0
        assert abi_transaction.gas_limit == 60_000_000
        assert abi_transaction.chain_id == "D"
        assert (
            abi_transaction.data.decode()
            == "proposeAsyncCall@0000000000000000050078d29632acb15998003f615d0a51261353d8041d3e13@@0100000000004c4b40@616464@07"
        )
        assert abi_transaction == transaction
