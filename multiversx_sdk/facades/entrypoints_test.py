from pathlib import Path

import pytest

from multiversx_sdk.abi.abi import Abi
from multiversx_sdk.controllers.multisig_v2_resources import \
    ProposeSCDeployFromSourceInput
from multiversx_sdk.core.address import Address
from multiversx_sdk.core.code_metadata import CodeMetadata
from multiversx_sdk.facades.account import Account
from multiversx_sdk.facades.entrypoints import DevnetEntrypoint

testutils = Path(__file__).parent.parent / "testutils"


class TestEntrypoint:
    entrypoint = DevnetEntrypoint()
    alice_pem = testutils / "testwallets" / "alice.pem"
    bob_pem = testutils / "testwallets" / "bob.pem"

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

        assert transaction.signature.hex() == "69bc7d1777edd0a901e6cf94830475716205c5efdf2fd44d4be31badead59fc8418b34f0aa3b2c80ba14aed5edd30031757d826af58a1abb690a0bee89ba9309"

    @pytest.mark.networkInteraction
    def test_contract_flow(self):
        abi = Abi.load(testutils / "testdata" / "adder.abi.json")
        sender = Account.new_from_pem(self.alice_pem)
        sender.nonce = self.entrypoint.recall_account_nonce(sender.address)

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

        contract_address = Address.new_from_bech32(outcome.contracts[0].address)

        transaction = controller.create_transaction_for_execute(
            sender=sender,
            nonce=sender.get_nonce_then_increment(),
            contract=contract_address,
            gas_limit=10_000_000,
            function="add",
            arguments=[7]
        )

        tx_hash = self.entrypoint.send_transaction(transaction)
        self.entrypoint.await_completed_transaction(tx_hash)

        query_result = controller.query_contract(
            contract=contract_address,
            function="getSum",
            arguments=[]
        )

        assert len(query_result) == 1
        assert query_result[0] == 7

    def test_create_relayed_transaction(self):
        tranasfer_controller = self.entrypoint.create_transfers_controller()
        sender = Account.new_from_pem(self.alice_pem)
        sender.nonce = 77777

        bob_pem = testutils / "testwallets" / "bob.pem"
        relayer = Account.new_from_pem(bob_pem)
        relayer.nonce = 7

        transaction = tranasfer_controller.create_transaction_for_transfer(
            sender=sender,
            nonce=sender.get_nonce_then_increment(),
            receiver=sender.address,
            native_transfer_amount=0,
            data="hello".encode(),
        )
        transaction.relayer = relayer.address.to_bech32()

        relayed_controller = self.entrypoint.create_relayed_controller()
        relayed_transaction = relayed_controller.create_relayed_v3_transaction(
            sender=relayer,
            nonce=relayer.get_nonce_then_increment(),
            inner_transactions=[transaction]
        )

        assert len(relayed_transaction.inner_transactions) == 1
        assert relayed_transaction.sender == relayed_transaction.inner_transactions[0].relayer
        assert relayed_transaction.chain_id == "D"

    @pytest.mark.networkInteraction
    def test_multisig_flow(self):
        abi = Abi.load(testutils / "testdata" / "multisig-full.abi.json")
        abi_adder = Abi.load(testutils / "testdata" / "adder.abi.json")
        bytecode_path = testutils / "testdata" / "multisig-full.wasm"
        contract_to_copy_address = Address.new_from_bech32("erd1qqqqqqqqqqqqqpgqsuxsgykwm6r3s5apct2g5a2rcpe7kw0ed8ssf6h9f6")
        controller = self.entrypoint.create_multisig_v2_controller(abi)

        alice = Account.new_from_pem(self.alice_pem)
        bob = Account.new_from_pem(self.bob_pem)
        alice.nonce = self.entrypoint.recall_account_nonce(alice.address)
        bob.nonce = self.entrypoint.recall_account_nonce(bob.address)

        transaction = controller.create_transaction_for_deploy(
            sender=alice,
            nonce=alice.nonce,
            bytecode=bytecode_path,
            gas_limit=100_000_000,
            quorum=2,
            board=[alice.address, bob.address]
        )

        alice.nonce += 1

        transaction_hash = self.entrypoint.send_transaction(transaction)
        multisig_address = controller.await_completed_deploy(transaction_hash)

        print("Multisig address:", multisig_address)

        transaction = controller.create_transaction_for_propose_deploy_contract_from_source(
            sender=alice,
            nonce=alice.nonce,
            contract=multisig_address,
            gas_limit=30_000_000,
            input=ProposeSCDeployFromSourceInput(
                native_transfer_amount=0,
                contract_to_copy=contract_to_copy_address,
                code_metadata=CodeMetadata(),
                arguments=[7],
                abi=abi_adder
            )
        )

        alice.nonce += 1

        transaction_hash = self.entrypoint.send_transaction(transaction)
        action_id = controller.await_completed_execute_propose_any(transaction_hash)
        print("Action ID:", action_id)

        transaction = controller.create_transaction_for_sign(
            sender=bob,
            nonce=bob.nonce,
            contract=multisig_address,
            gas_limit=30_000_000,
            action_id=action_id
        )

        bob.nonce += 1

        transaction_hash = self.entrypoint.send_transaction(transaction)
        self.entrypoint.await_completed_transaction(transaction_hash)

        transaction = controller.create_transaction_for_perform_action(
            sender=alice,
            nonce=alice.nonce,
            contract=multisig_address,
            gas_limit=30_000_000,
            action_id=action_id
        )

        alice.nonce += 1

        transaction_hash = self.entrypoint.send_transaction(transaction)
        addresses = controller.await_completed_execute_perform(transaction_hash)
        print("Output of perform:", addresses)

