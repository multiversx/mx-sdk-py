from pathlib import Path

import pytest

from multiversx_sdk.abi.abi import Abi
from multiversx_sdk.accounts import Account
from multiversx_sdk.core.address import Address
from multiversx_sdk.core.code_metadata import CodeMetadata
from multiversx_sdk.entrypoints import DevnetEntrypoint
from multiversx_sdk.multisig.resources import (
    ProposeAsyncCallInput,
    ProposeSCDeployFromSourceInput,
    ProposeTransferExecuteInput,
    SCDeployFromSource,
    SendAsyncCall,
    UserRole,
)

testutils = Path(__file__).parent.parent / "testutils"


class TestEntrypoint:
    entrypoint = DevnetEntrypoint()
    alice_pem = testutils / "testwallets" / "alice.pem"
    grace_pem = testutils / "testwallets" / "grace.pem"

    @pytest.mark.networkInteraction
    def test_multisig_flow(self):
        abi_multisig = Abi.load(testutils / "testdata" / "multisig-full.abi.json")
        abi_adder = Abi.load(testutils / "testdata" / "adder.abi.json")
        bytecode_path_multisig = testutils / "testdata" / "multisig-full.wasm"
        contract_to_copy_address = Address.new_from_bech32(
            "erd1qqqqqqqqqqqqqpgqsuxsgykwm6r3s5apct2g5a2rcpe7kw0ed8ssf6h9f6"
        )
        controller_multisig = self.entrypoint.create_multisig_v2_controller(abi_multisig)
        controller_adder = self.entrypoint.create_smart_contract_controller(abi_adder)

        # Alice and Grace are the (initial) board members.
        alice = Account.new_from_pem(self.alice_pem)
        grace = Account.new_from_pem(self.grace_pem)
        alice.nonce = self.entrypoint.recall_account_nonce(alice.address)
        grace.nonce = self.entrypoint.recall_account_nonce(grace.address)

        # Deploy the multisig contract.
        transaction = controller_multisig.create_transaction_for_deploy(
            sender=alice,
            nonce=alice.nonce,
            bytecode=bytecode_path_multisig,
            gas_limit=100_000_000,
            quorum=2,
            board=[alice.address, grace.address],
        )

        alice.nonce += 1

        transaction_hash = self.entrypoint.send_transaction(transaction)
        multisig_address = controller_multisig.await_completed_deploy(transaction_hash)
        print("Multisig address:", multisig_address)

        role_alice = controller_multisig.get_user_role(multisig_address, alice.address)
        role_grace = controller_multisig.get_user_role(multisig_address, grace.address)
        assert role_alice == UserRole.BOARD_MEMBER
        assert role_grace == UserRole.BOARD_MEMBER

        board_members = controller_multisig.get_all_board_members(multisig_address)
        assert board_members == [alice.address, grace.address]

        # Alice proposes a deploy of the adder contract.
        transaction = controller_multisig.create_transaction_for_propose_deploy_contract_from_source(
            sender=alice,
            nonce=alice.nonce,
            contract=multisig_address,
            gas_limit=30_000_000,
            input=ProposeSCDeployFromSourceInput(
                native_transfer_amount=0,
                contract_to_copy=contract_to_copy_address,
                code_metadata=CodeMetadata(),
                arguments=[7],
                abi=abi_adder,
            ),
        )

        alice.nonce += 1

        transaction_hash = self.entrypoint.send_transaction(transaction)
        action_id = controller_multisig.await_completed_execute_propose_any(transaction_hash)
        print("Action ID (deploy the adder contract):", action_id)

        # Grace signs the action.
        transaction = controller_multisig.create_transaction_for_sign(
            sender=grace, nonce=grace.nonce, contract=multisig_address, gas_limit=30_000_000, action_id=action_id
        )

        grace.nonce += 1

        transaction_hash = self.entrypoint.send_transaction(transaction)
        self.entrypoint.await_transaction_completed(transaction_hash)

        # Query information about the action.
        signer_count = controller_multisig.get_action_signer_count(multisig_address, action_id)
        valid_signer_count = controller_multisig.get_action_valid_signer_count(multisig_address, action_id)
        signers = controller_multisig.get_action_signers(multisig_address, action_id)

        assert signer_count == 2
        assert valid_signer_count == 2
        assert signers == [alice.address, grace.address]

        [action_full_info] = controller_multisig.get_pending_actions_full_info(multisig_address)
        print("Action full info:", action_full_info)
        assert action_full_info.action_id == action_id
        assert action_full_info.group_id == 0
        assert action_full_info.signers == [alice.address, grace.address]
        assert action_full_info.action_data.discriminant == 8
        assert isinstance(action_full_info.action_data, SCDeployFromSource)
        assert action_full_info.action_data.amount == 0
        assert action_full_info.action_data.source == contract_to_copy_address
        assert action_full_info.action_data.code_metadata == CodeMetadata().serialize()
        assert action_full_info.action_data.arguments == [bytes([7])]

        # Alice performs the action.
        transaction = controller_multisig.create_transaction_for_perform_action(
            sender=alice, nonce=alice.nonce, contract=multisig_address, gas_limit=30_000_000, action_id=action_id
        )

        alice.nonce += 1

        transaction_hash = self.entrypoint.send_transaction(transaction)
        adder_address = controller_multisig.await_completed_execute_perform(transaction_hash)
        print("Adder address:", adder_address)
        assert adder_address is not None

        # Query the adder contract.
        [value] = controller_adder.query(contract=adder_address, function="getSum", arguments=[])

        print("Value of adder::getSum():", value)
        assert value == 7

        # Alice proposes to add a value to the adder contract.
        transaction = controller_multisig.create_transaction_for_propose_async_call(
            sender=alice,
            nonce=alice.nonce,
            contract=multisig_address,
            gas_limit=30_000_000,
            input=ProposeAsyncCallInput.new_for_transfer_execute(
                to=adder_address,
                native_transfer_amount=0,
                token_transfers=[],
                function="add",
                arguments=[7],
                abi=abi_adder,
            ),
        )

        alice.nonce += 1

        transaction_hash = self.entrypoint.send_transaction(transaction)
        action_id = controller_multisig.await_completed_execute_propose_any(transaction_hash)
        print("Action ID (call adder::add()):", action_id)

        # Grace signs the action.
        transaction = controller_multisig.create_transaction_for_sign(
            sender=grace, nonce=grace.nonce, contract=multisig_address, gas_limit=30_000_000, action_id=action_id
        )

        grace.nonce += 1

        transaction_hash = self.entrypoint.send_transaction(transaction)
        self.entrypoint.await_transaction_completed(transaction_hash)

        [action_full_info] = controller_multisig.get_pending_actions_full_info(multisig_address)
        print("Action full info:", action_full_info)
        assert action_full_info.action_id == action_id
        assert action_full_info.group_id == 0
        assert action_full_info.signers == [alice.address, grace.address]
        assert action_full_info.action_data.discriminant == 7
        assert isinstance(action_full_info.action_data, SendAsyncCall)
        assert action_full_info.action_data.data.to == adder_address
        assert action_full_info.action_data.data.egld_amount == 0
        assert action_full_info.action_data.data.endpoint_name == b"add"
        assert action_full_info.action_data.data.arguments == [bytes([7])]
        assert action_full_info.action_data.data.opt_gas_limit is None

        # Alice performs the action.
        transaction = controller_multisig.create_transaction_for_perform_action(
            sender=alice, nonce=alice.nonce, contract=multisig_address, gas_limit=30_000_000, action_id=action_id
        )

        alice.nonce += 1

        transaction_hash = self.entrypoint.send_transaction(transaction)
        _ = controller_multisig.await_completed_execute_perform(transaction_hash)

        # Query the adder contract.
        [value] = controller_adder.query(contract=adder_address, function="getSum", arguments=[])

        print("Value of adder::getSum():", value)
        assert value == 14

        # Alice proposes to add a value to the adder contract (with transfer and execute).
        transaction = controller_multisig.create_transaction_for_propose_transfer_execute(
            sender=alice,
            nonce=alice.nonce,
            contract=multisig_address,
            gas_limit=30_000_000,
            input=ProposeTransferExecuteInput.new_for_transfer_execute(
                to=adder_address,
                native_transfer_amount=0,
                function="add",
                arguments=[7],
                abi=abi_adder,
            ),
        )

        alice.nonce += 1

        transaction_hash = self.entrypoint.send_transaction(transaction)
        action_id = controller_multisig.await_completed_execute_propose_any(transaction_hash)
        print("Action ID (call adder::add()):", action_id)

        # Grace signs the action.
        transaction = controller_multisig.create_transaction_for_sign(
            sender=grace, nonce=grace.nonce, contract=multisig_address, gas_limit=30_000_000, action_id=action_id
        )

        grace.nonce += 1

        transaction_hash = self.entrypoint.send_transaction(transaction)
        self.entrypoint.await_transaction_completed(transaction_hash)

        # Alice performs the action.
        transaction = controller_multisig.create_transaction_for_perform_action(
            sender=alice, nonce=alice.nonce, contract=multisig_address, gas_limit=30_000_000, action_id=action_id
        )

        alice.nonce += 1

        transaction_hash = self.entrypoint.send_transaction(transaction)
        _ = controller_multisig.await_completed_execute_perform(transaction_hash)

        # Query the adder contract.
        [value] = controller_adder.query(contract=adder_address, function="getSum", arguments=[])

        print("Value of adder::getSum():", value)
        assert value == 21
