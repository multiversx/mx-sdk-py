from pathlib import Path

import pytest

from multiversx_sdk.abi.abi import Abi
from multiversx_sdk.accounts import Account
from multiversx_sdk.entrypoints.entrypoints import DevnetEntrypoint

testutils = Path(__file__).parent.parent / "testutils"


class TestEntrypoint:
    entrypoint = DevnetEntrypoint()
    alice_pem = testutils / "testwallets" / "alice.pem"
    grace_pem = testutils / "testwallets" / "grace.pem"

    def test_native_transfer(self):
        controller = self.entrypoint.create_transfers_controller()
        sender = Account.new_from_pem(self.alice_pem)
        sender.nonce = 77777

        transaction = controller.create_transaction_for_transfer(
            sender=sender,
            nonce=sender.get_nonce_then_increment(),
            receiver=sender.address,
            native_transfer_amount=0,
            data="hello".encode()
        )

        assert transaction.signature.hex(
        ) == "69bc7d1777edd0a901e6cf94830475716205c5efdf2fd44d4be31badead59fc8418b34f0aa3b2c80ba14aed5edd30031757d826af58a1abb690a0bee89ba9309"

    def test_native_transfer_with_guardian_and_relayer(self):
        grace = Account.new_from_pem(self.grace_pem)
        controller = self.entrypoint.create_transfers_controller()
        sender = Account.new_from_pem(self.alice_pem)
        sender.nonce = 77777

        transaction = controller.create_transaction_for_transfer(
            sender=sender,
            nonce=sender.get_nonce_then_increment(),
            receiver=sender.address,
            native_transfer_amount=0,
            data="hello".encode(),
            guardian=grace.address,
            relayer=grace.address
        )

        assert transaction.guardian == grace.address
        assert transaction.relayer == grace.address
        assert transaction.guardian_signature == b""
        assert transaction.relayer_signature == b""

    @pytest.mark.networkInteraction
    def test_contract_flow(self):
        sender = Account.new_from_pem(self.grace_pem)
        sender.nonce = self.entrypoint.recall_account_nonce(sender.address)

        abi = Abi.load(testutils / "testdata" / "adder.abi.json")
        controller = self.entrypoint.create_smart_contract_controller(abi)

        bytecode = (testutils / "testdata" / "adder.wasm").read_bytes()
        transaction = controller.create_transaction_for_deploy(
            sender=sender,
            nonce=sender.get_nonce_then_increment(),
            bytecode=bytecode,
            gas_limit=10_000_000,
            arguments=[0]
        )

        tx_hash = self.entrypoint.send_transaction(transaction)
        outcome = controller.await_completed_deploy(tx_hash)

        assert len(outcome.contracts) == 1

        contract_address = outcome.contracts[0].address

        transaction = controller.create_transaction_for_execute(
            sender=sender,
            nonce=sender.get_nonce_then_increment(),
            contract=contract_address,
            gas_limit=10_000_000,
            function="add",
            arguments=[7]
        )

        tx_hash = self.entrypoint.send_transaction(transaction)
        self.entrypoint.await_transaction_completed(tx_hash)

        query_result = controller.query(
            contract=contract_address,
            function="getSum",
            arguments=[]
        )

        assert len(query_result) == 1
        assert query_result[0] == 7

    def test_get_account_factory_and_create_transaction(self):
        sender = Account.new_from_pem(self.alice_pem)
        sender.nonce = self.entrypoint.recall_account_nonce(sender.address)

        factory = self.entrypoint.create_account_transactions_factory()
        transaction = factory.create_transaction_for_saving_key_value(
            sender=sender.address,
            key_value_pairs={"key".encode(): "pair".encode()}
        )

        assert transaction.chain_id == "D"

    def test_create_account(self):
        account = self.entrypoint.create_account()
        assert account.address
        assert len(account.secret_key.get_bytes()) == 32
        assert len(account.public_key.get_bytes()) == 32
