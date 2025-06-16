import base64
from pathlib import Path

from multiversx_sdk.abi.abi import Abi
from multiversx_sdk.abi.biguint_value import BigUIntValue
from multiversx_sdk.abi.small_int_values import U32Value
from multiversx_sdk.accounts.account import Account
from multiversx_sdk.core.address import Address
from multiversx_sdk.core.tokens import Token, TokenTransfer
from multiversx_sdk.multisig.multisig_controller import MultisigController
from multiversx_sdk.multisig.resources import (
    AddBoardMember,
    AddProposer,
    ChangeQuorum,
    EsdtTokenPayment,
    RemoveUser,
    SCDeployFromSource,
    SCUpgradeFromSource,
    SendAsyncCall,
    SendTransferExecuteEgld,
    SendTransferExecuteEsdt,
    UserRole,
)
from multiversx_sdk.network_providers.api_network_provider import ApiNetworkProvider
from multiversx_sdk.smart_contracts.smart_contract_query import (
    SmartContractQueryResponse,
)
from multiversx_sdk.testutils.mock_network_provider import MockNetworkProvider
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

    def test_discard_action(self):
        transaction = self.controller.create_transaction_for_discard_action(
            sender=self.john,
            nonce=self.john.get_nonce_then_increment(),
            contract=self.contract,
            action_id=7,
            gas_limit=60_000_000,
        )
        assert transaction.sender == self.john.address
        assert transaction.receiver == self.contract
        assert transaction.value == 0
        assert transaction.gas_limit == 60_000_000
        assert transaction.chain_id == "D"
        assert transaction.data.decode() == "discardAction@07"

    def test_discard_batch(self):
        transaction = self.controller.create_transaction_for_discard_batch(
            sender=self.john,
            nonce=self.john.get_nonce_then_increment(),
            contract=self.contract,
            actions_ids=[7, 8],
            gas_limit=60_000_000,
        )
        assert transaction.sender == self.john.address
        assert transaction.receiver == self.contract
        assert transaction.value == 0
        assert transaction.gas_limit == 60_000_000
        assert transaction.chain_id == "D"
        assert transaction.data.decode() == "discardBatch@07@08"

    def test_get_quorum(self):
        network_provider = MockNetworkProvider()
        controller = MultisigController(chain_id="D", network_provider=network_provider, abi=self.multisig_abi)

        contract_query_response = SmartContractQueryResponse(
            function="getQuorum",
            return_code="ok",
            return_message="",
            return_data_parts=[bytes.fromhex("03")],
        )
        network_provider.mock_query_contract_on_function("getQuorum", contract_query_response)

        response = controller.get_quorum(self.contract)
        assert response == 3

    def test_get_num_board_members(self):
        network_provider = MockNetworkProvider()
        controller = MultisigController(chain_id="D", network_provider=network_provider, abi=self.multisig_abi)

        contract_query_response = SmartContractQueryResponse(
            function="getNumBoardMembers",
            return_code="ok",
            return_message="",
            return_data_parts=[bytes.fromhex("02")],
        )
        network_provider.mock_query_contract_on_function("getNumBoardMembers", contract_query_response)

        response = controller.get_num_board_members(self.contract)
        assert response == 2

    def test_get_num_groups(self):
        network_provider = MockNetworkProvider()
        controller = MultisigController(chain_id="D", network_provider=network_provider, abi=self.multisig_abi)

        contract_query_response = SmartContractQueryResponse(
            function="getNumGroups",
            return_code="ok",
            return_message="",
            return_data_parts=[bytes.fromhex("05")],
        )
        network_provider.mock_query_contract_on_function("getNumGroups", contract_query_response)

        response = controller.get_num_groups(self.contract)
        assert response == 5

    def test_get_num_proposers(self):
        network_provider = MockNetworkProvider()
        controller = MultisigController(chain_id="D", network_provider=network_provider, abi=self.multisig_abi)

        contract_query_response = SmartContractQueryResponse(
            function="getNumProposers",
            return_code="ok",
            return_message="",
            return_data_parts=[bytes.fromhex("04")],
        )
        network_provider.mock_query_contract_on_function("getNumProposers", contract_query_response)

        response = controller.get_num_proposers(self.contract)
        assert response == 4

    def test_get_action_group(self):
        network_provider = MockNetworkProvider()
        controller = MultisigController(chain_id="D", network_provider=network_provider, abi=self.multisig_abi)

        contract_query_response = SmartContractQueryResponse(
            function="getActionGroup",
            return_code="ok",
            return_message="",
            return_data_parts=[bytes.fromhex("02")],
        )
        network_provider.mock_query_contract_on_function("getActionGroup", contract_query_response)

        response = controller.get_action_group(contract=self.contract, group_id=5)
        assert len(response) == 1
        assert response == [2]

    def test_get_last_group_action_id(self):
        network_provider = MockNetworkProvider()
        controller = MultisigController(chain_id="D", network_provider=network_provider, abi=self.multisig_abi)

        contract_query_response = SmartContractQueryResponse(
            function="getLastGroupActionId",
            return_code="ok",
            return_message="",
            return_data_parts=[bytes.fromhex("07")],
        )
        network_provider.mock_query_contract_on_function("getLastGroupActionId", contract_query_response)

        response = controller.get_last_group_action_id(contract=self.contract)
        assert response == 7

    def test_get_action_last_index(self):
        network_provider = MockNetworkProvider()
        controller = MultisigController(chain_id="D", network_provider=network_provider, abi=self.multisig_abi)

        contract_query_response = SmartContractQueryResponse(
            function="getActionLastIndex",
            return_code="ok",
            return_message="",
            return_data_parts=[bytes.fromhex("42")],
        )
        network_provider.mock_query_contract_on_function("getActionLastIndex", contract_query_response)

        response = controller.get_action_last_index(contract=self.contract)
        assert response == 66

    def test_is_action_signed(self):
        network_provider = MockNetworkProvider()
        controller = MultisigController(chain_id="D", network_provider=network_provider, abi=self.multisig_abi)

        contract_query_response = SmartContractQueryResponse(
            function="signed",
            return_code="ok",
            return_message="",
            return_data_parts=[bytes.fromhex("01")],  # 1 = True
        )
        network_provider.mock_query_contract_on_function("signed", contract_query_response)

        response = controller.is_signed_by(
            contract=self.contract,
            user=Address.new_from_bech32("erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"),
            action_id=42,
        )
        assert response == 1

    def test_action_is_not_signed(self):
        network_provider = MockNetworkProvider()
        controller = MultisigController(chain_id="D", network_provider=network_provider, abi=self.multisig_abi)

        contract_query_response = SmartContractQueryResponse(
            function="signed",
            return_code="ok",
            return_message="",
            return_data_parts=[bytes.fromhex("00")],  # 0 = False
        )
        network_provider.mock_query_contract_on_function("signed", contract_query_response)

        response = controller.is_signed_by(
            contract=self.contract,
            user=Address.new_from_bech32("erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"),
            action_id=42,
        )
        assert response == 0

    def test_quorum_reached(self):
        network_provider = MockNetworkProvider()
        controller = MultisigController(chain_id="D", network_provider=network_provider, abi=self.multisig_abi)

        contract_query_response = SmartContractQueryResponse(
            function="quorumReached",
            return_code="ok",
            return_message="",
            return_data_parts=[bytes.fromhex("01")],  # 1 = True
        )
        network_provider.mock_query_contract_on_function("quorumReached", contract_query_response)

        response = controller.is_quorum_reached(
            contract=self.contract,
            action_id=42,
        )
        assert response == 1

    def test_quorum_not_reached(self):
        network_provider = MockNetworkProvider()
        controller = MultisigController(chain_id="D", network_provider=network_provider, abi=self.multisig_abi)

        contract_query_response = SmartContractQueryResponse(
            function="quorumReached",
            return_code="ok",
            return_message="",
            return_data_parts=[bytes.fromhex("00")],  # 0 = False
        )
        network_provider.mock_query_contract_on_function("quorumReached", contract_query_response)

        response = controller.is_quorum_reached(
            contract=self.contract,
            action_id=42,
        )
        assert response == 0

    def test_get_user_role(self):
        network_provider = MockNetworkProvider()
        controller = MultisigController(chain_id="D", network_provider=network_provider, abi=self.multisig_abi)

        contract_query_response = SmartContractQueryResponse(
            function="userRole",
            return_code="ok",
            return_message="",
            return_data_parts=[bytes.fromhex("01")],  # 0 = False
        )
        network_provider.mock_query_contract_on_function("userRole", contract_query_response)

        response = controller.get_user_role(
            contract=self.contract,
            user=Address.new_from_bech32("erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"),
        )
        assert response == UserRole(1)

    def test_get_all_board_members(self):
        network_provider = MockNetworkProvider()
        controller = MultisigController(chain_id="D", network_provider=network_provider, abi=self.multisig_abi)

        board_members = [
            Address.new_from_bech32("erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"),
            Address.new_from_bech32("erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8"),
        ]

        contract_query_response = SmartContractQueryResponse(
            function="getAllBoardMembers",
            return_code="ok",
            return_message="",
            return_data_parts=[member.get_public_key() for member in board_members],
        )
        network_provider.mock_query_contract_on_function("getAllBoardMembers", contract_query_response)

        response = controller.get_all_board_members(contract=self.contract)
        assert len(response) == 2
        assert response == board_members

    def test_get_all_proposers(self):
        network_provider = MockNetworkProvider()
        controller = MultisigController(chain_id="D", network_provider=network_provider, abi=self.multisig_abi)

        proposers = [
            Address.new_from_bech32("erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"),
            Address.new_from_bech32("erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8"),
        ]

        contract_query_response = SmartContractQueryResponse(
            function="getAllProposers",
            return_code="ok",
            return_message="",
            return_data_parts=[proposer.get_public_key() for proposer in proposers],
        )
        network_provider.mock_query_contract_on_function("getAllProposers", contract_query_response)

        response = controller.get_all_proposers(contract=self.contract)
        assert len(response) == 2
        assert response == proposers

    def test_get_action_data(self):
        """Get action data for SendTransferExecuteEgld"""

        network_provider = MockNetworkProvider()
        controller = MultisigController(chain_id="D", network_provider=network_provider, abi=self.multisig_abi)

        contract_query_response = SmartContractQueryResponse(
            function="getActionData",
            return_code="ok",
            return_message="",
            return_data_parts=[
                bytes.fromhex(
                    "0500000000000000000500d006f73c4221216fa679bc559005584c4f1160e569e1000000012a0000000003616464000000010000000107"
                )
            ],
        )
        network_provider.mock_query_contract_on_function("getActionData", contract_query_response)

        response = controller.get_action_data(contract=self.contract, action_id=42)
        assert isinstance(response, SendTransferExecuteEgld)
        assert response.data.to == Address.new_from_bech32(
            "erd1qqqqqqqqqqqqqpgq6qr0w0zzyysklfneh32eqp2cf383zc89d8sstnkl60"
        )
        assert response.data.endpoint_name == "add"
        assert response.data.arguments == [b"\x07"]
        assert response.data.egld_amount == 42
        assert response.data.opt_gas_limit is None

    def test_get_pending_action_full_info(self):
        network_provider = MockNetworkProvider()
        controller = MultisigController(chain_id="D", network_provider=network_provider, abi=self.multisig_abi)

        contract_query_response = SmartContractQueryResponse(
            function="getPendingActionFullInfo",
            return_code="ok",
            return_message="",
            return_data_parts=[
                bytes.fromhex(
                    base64.b64decode(
                        "AAAAAQAAAAAFgEnWOeWmmA0c0jkqvM5BApzadKFWNSOiAvCWQcwmGPgAAAAIDeC2s6dkAAABAAAAAAF9eEAAAAAAAAAAAAAAAAEBOUcu/2iGdxqYLzCD2l1CHyTCkYHmOIgijcgcpg1p4Q=="
                    ).hex()
                ),
                bytes.fromhex(
                    base64.b64decode(
                        "AAAAAgAAAAAHAAAAAAAAAAAFAHjSljKssVmYAD9hXQpRJhNT2AQdPhMAAAAIDeC2s6dkAAABAAAAAAOThwAAAAABCgAAAAIAAAABDQAAAAENAAAAAQE5Ry7/aIZ3GpgvMIPaXUIfJMKRgeY4iCKNyBymDWnh"
                    ).hex()
                ),
            ],
        )
        network_provider.mock_query_contract_on_function("getPendingActionFullInfo", contract_query_response)

        response = controller.get_pending_actions_full_info(contract=self.contract)
        assert len(response) == 2

    def test_get_action_data_for_async_call(self):
        network_provider = MockNetworkProvider()
        controller = MultisigController(chain_id="D", network_provider=network_provider, abi=self.multisig_abi)

        contract_query_response = SmartContractQueryResponse(
            function="getActionData",
            return_code="ok",
            return_message="",
            return_data_parts=[
                bytes.fromhex(
                    "07000000000000000005006b377098db7314c48a30485081249fa0053e0a867d18000000000100000000004c4b4000000003616464000000010000000107"
                )
            ],
        )
        network_provider.mock_query_contract_on_function("getActionData", contract_query_response)

        response = controller.get_action_data(contract=self.contract, action_id=42)
        assert isinstance(response, SendAsyncCall)
        assert response.data.to == Address.new_from_bech32(
            "erd1qqqqqqqqqqqqqpgqdvmhpxxmwv2vfz3sfpggzfyl5qznuz5x05vq5y37ql"
        )
        assert response.data.endpoint_name == "add"
        assert response.data.arguments == [b"\x07"]
        assert response.data.egld_amount == 0
        assert response.data.opt_gas_limit == 5_000_000

    def test_get_action_data_for_send_transfer_execute_esdt(self):
        network_provider = MockNetworkProvider()
        controller = MultisigController(chain_id="D", network_provider=network_provider, abi=self.multisig_abi)

        contract_query_response = SmartContractQueryResponse(
            function="getActionData",
            return_code="ok",
            return_message="",
            return_data_parts=[
                bytes.fromhex(
                    base64.b64decode(
                        "BgAAAAAAAAAABQBJv/ljvfo+oCcTNiCV3zLj1wjqzPxXAAAAAQAAAAxBTElDRS01NjI3ZjEAAAAAAAAAAAAAAAEKAQAAAAAATEtAAAAAFDY0Njk3Mzc0NzI2OTYyNzU3NDY1AAAAAA=="
                    ).hex()
                )
            ],
        )
        network_provider.mock_query_contract_on_function("getActionData", contract_query_response)

        response = controller.get_action_data(contract=self.contract, action_id=42)
        assert isinstance(response, SendTransferExecuteEsdt)
        assert response.data.to == Address.new_from_bech32(
            "erd1qqqqqqqqqqqqqpgqfxlljcaalgl2qfcnxcsftheju0ts36kvl3ts3qkewe"
        )
        assert response.data.endpoint_name == "distribute"
        assert response.data.arguments == []
        assert response.data.tokens == [EsdtTokenPayment("ALICE-5627f1", 0, 10)]
        assert response.data.opt_gas_limit == 5_000_000

    def test_get_action_data_for_add_board_member(self):
        network_provider = MockNetworkProvider()
        controller = MultisigController(chain_id="D", network_provider=network_provider, abi=self.multisig_abi)

        contract_query_response = SmartContractQueryResponse(
            function="getActionData",
            return_code="ok",
            return_message="",
            return_data_parts=[bytes.fromhex(base64.b64decode("AYBJ1jnlppgNHNI5KrzOQQKc2nShVjUjogLwlkHMJhj4").hex())],
        )
        network_provider.mock_query_contract_on_function("getActionData", contract_query_response)

        response = controller.get_action_data(contract=self.contract, action_id=42)
        assert isinstance(response, AddBoardMember)
        assert response.address == Address.new_from_bech32(
            "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"
        )

    def test_get_action_data_for_add_proposer(self):
        network_provider = MockNetworkProvider()
        controller = MultisigController(chain_id="D", network_provider=network_provider, abi=self.multisig_abi)

        contract_query_response = SmartContractQueryResponse(
            function="getActionData",
            return_code="ok",
            return_message="",
            return_data_parts=[bytes.fromhex(base64.b64decode("AoBJ1jnlppgNHNI5KrzOQQKc2nShVjUjogLwlkHMJhj4").hex())],
        )
        network_provider.mock_query_contract_on_function("getActionData", contract_query_response)

        response = controller.get_action_data(contract=self.contract, action_id=42)
        assert isinstance(response, AddProposer)
        assert response.address == Address.new_from_bech32(
            "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"
        )

    def test_get_action_data_for_sc_deploy_from_source(self):
        network_provider = MockNetworkProvider()
        controller = MultisigController(chain_id="D", network_provider=network_provider, abi=self.multisig_abi)

        contract_query_response = SmartContractQueryResponse(
            function="getActionData",
            return_code="ok",
            return_message="",
            return_data_parts=[
                bytes.fromhex(
                    base64.b64decode(
                        "CAAAAAexorwuxQAAAAAAAAAAAAAFAIcNBBLO3ocYU6HC1Ip1Q8Bz6zn5aeEFAAAAAAEAAAABBw=="
                    ).hex()
                )
            ],
        )
        network_provider.mock_query_contract_on_function("getActionData", contract_query_response)

        response = controller.get_action_data(contract=self.contract, action_id=42)
        assert isinstance(response, SCDeployFromSource)
        assert response.source == Address.new_from_bech32(
            "erd1qqqqqqqqqqqqqpgqsuxsgykwm6r3s5apct2g5a2rcpe7kw0ed8ssf6h9f6"
        )
        assert response.amount == 50_000_000_000_000_000
        assert response.code_metadata == bytes([0x05, 0x00])

    def test_get_action_data_for_sc_upgrade_from_source(self):
        network_provider = MockNetworkProvider()
        controller = MultisigController(chain_id="D", network_provider=network_provider, abi=self.multisig_abi)

        contract_query_response = SmartContractQueryResponse(
            function="getActionData",
            return_code="ok",
            return_message="",
            return_data_parts=[
                bytes.fromhex(
                    base64.b64decode(
                        "CQAAAAAAAAAABQB+Jc5t66x0jYa105MSCrHrAqRtWBZ5AAAAB7GivC7FAAAAAAAAAAAAAAUAar0cOjeU2gFgK4VawD54IeZjjsgWeQUAAAAAAA=="
                    ).hex()
                )
            ],
        )
        network_provider.mock_query_contract_on_function("getActionData", contract_query_response)

        response = controller.get_action_data(contract=self.contract, action_id=42)
        assert isinstance(response, SCUpgradeFromSource)
        assert response.source == Address.new_from_bech32(
            "erd1qqqqqqqqqqqqqpgqd273cw3hjndqzcpts4dvq0ncy8nx8rkgzeusnefvaq"
        )
        assert response.amount == 50_000_000_000_000_000
        assert response.code_metadata == bytes([0x05, 0x00])

    def test_get_action_data_for_change_quorum(self):
        network_provider = MockNetworkProvider()
        controller = MultisigController(chain_id="D", network_provider=network_provider, abi=self.multisig_abi)

        contract_query_response = SmartContractQueryResponse(
            function="getActionData",
            return_code="ok",
            return_message="",
            return_data_parts=[bytes.fromhex(base64.b64decode("BAAAAAI=").hex())],
        )
        network_provider.mock_query_contract_on_function("getActionData", contract_query_response)

        response = controller.get_action_data(contract=self.contract, action_id=42)
        assert isinstance(response, ChangeQuorum)
        assert response.quorum == 2

    def test_get_action_data_for_remove_user(self):
        network_provider = MockNetworkProvider()
        controller = MultisigController(chain_id="D", network_provider=network_provider, abi=self.multisig_abi)

        contract_query_response = SmartContractQueryResponse(
            function="getActionData",
            return_code="ok",
            return_message="",
            return_data_parts=[bytes.fromhex(base64.b64decode("A4BJ1jnlppgNHNI5KrzOQQKc2nShVjUjogLwlkHMJhj4").hex())],
        )
        network_provider.mock_query_contract_on_function("getActionData", contract_query_response)

        response = controller.get_action_data(contract=self.contract, action_id=42)
        assert isinstance(response, RemoveUser)
        assert response.address == Address.new_from_bech32(
            "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"
        )

    def test_get_action_signers(self):
        network_provider = MockNetworkProvider()
        controller = MultisigController(chain_id="D", network_provider=network_provider, abi=self.multisig_abi)

        contract_query_response = SmartContractQueryResponse(
            function="getActionSigners",
            return_code="ok",
            return_message="",
            return_data_parts=[
                bytes.fromhex(
                    "8049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f8b2a11555ce521e4944e09ab17549d85b487dcd26c84b5017a39e31a3670889ba"
                )
            ],
        )
        network_provider.mock_query_contract_on_function("getActionSigners", contract_query_response)

        response = controller.get_action_signers(contract=self.contract, action_id=42)
        assert len(response) == 2
        assert response[0] == Address.new_from_bech32("erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx")
        assert response[1] == Address.new_from_bech32("erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8")

    def test_get_action_signers_count(self):
        network_provider = MockNetworkProvider()
        controller = MultisigController(chain_id="D", network_provider=network_provider, abi=self.multisig_abi)

        contract_query_response = SmartContractQueryResponse(
            function="getActionSignerCount",
            return_code="ok",
            return_message="",
            return_data_parts=[bytes.fromhex("04")],
        )
        network_provider.mock_query_contract_on_function("getActionSignerCount", contract_query_response)

        response = controller.get_action_signer_count(contract=self.contract, action_id=42)
        assert response == 4

    def test_get_action_valid_signers_count(self):
        network_provider = MockNetworkProvider()
        controller = MultisigController(chain_id="D", network_provider=network_provider, abi=self.multisig_abi)

        contract_query_response = SmartContractQueryResponse(
            function="getActionValidSignerCount",
            return_code="ok",
            return_message="",
            return_data_parts=[bytes.fromhex("04")],
        )
        network_provider.mock_query_contract_on_function("getActionValidSignerCount", contract_query_response)

        response = controller.get_action_valid_signer_count(contract=self.contract, action_id=42)
        assert response == 4

    def test_propose_add_board_member(self):
        bob = Address.new_from_bech32("erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx")

        transaction = self.controller.create_transaction_for_propose_add_board_member(
            sender=self.john,
            nonce=self.john.get_nonce_then_increment(),
            contract=self.contract,
            board_member=bob,
            gas_limit=60_000_000,
        )
        assert transaction.sender == self.john.address
        assert transaction.receiver == self.contract
        assert transaction.value == 0
        assert transaction.gas_limit == 60_000_000
        assert transaction.chain_id == "D"
        assert (
            transaction.data.decode()
            == "proposeAddBoardMember@8049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f8"
        )

    def test_propose_add_proposer(self):
        bob = Address.new_from_bech32("erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx")

        transaction = self.controller.create_transaction_for_propose_add_proposer(
            sender=self.john,
            nonce=self.john.get_nonce_then_increment(),
            contract=self.contract,
            proposer=bob,
            gas_limit=60_000_000,
        )
        assert transaction.sender == self.john.address
        assert transaction.receiver == self.contract
        assert transaction.value == 0
        assert transaction.gas_limit == 60_000_000
        assert transaction.chain_id == "D"
        assert (
            transaction.data.decode()
            == "proposeAddProposer@8049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f8"
        )

    def test_propose_remove_user(self):
        bob = Address.new_from_bech32("erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx")

        transaction = self.controller.create_transaction_for_propose_remove_user(
            sender=self.john,
            nonce=self.john.get_nonce_then_increment(),
            contract=self.contract,
            user=bob,
            gas_limit=60_000_000,
        )
        assert transaction.sender == self.john.address
        assert transaction.receiver == self.contract
        assert transaction.value == 0
        assert transaction.gas_limit == 60_000_000
        assert transaction.chain_id == "D"
        assert (
            transaction.data.decode()
            == "proposeRemoveUser@8049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f8"
        )

    def test_propose_change_quorum(self):
        transaction = self.controller.create_transaction_for_propose_change_quorum(
            sender=self.john,
            nonce=self.john.get_nonce_then_increment(),
            contract=self.contract,
            new_quorum=10,
            gas_limit=60_000_000,
        )
        assert transaction.sender == self.john.address
        assert transaction.receiver == self.contract
        assert transaction.value == 0
        assert transaction.gas_limit == 60_000_000
        assert transaction.chain_id == "D"
        assert transaction.data.decode() == "proposeChangeQuorum@0a"

    def test_propose_transfer_and_execute(self):
        contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqpgq0rffvv4vk9vesqplv9ws55fxzdfaspqa8cfszy2hms")
        amount = 1000000000000000000

        transaction = self.controller.create_transaction_for_propose_transfer_execute(
            sender=self.john,
            nonce=self.john.get_nonce_then_increment(),
            contract=self.contract,
            receiver=contract,
            native_token_amount=amount,
            gas_limit=60_000_000,
            opt_gas_limit=1_000_000,
            function="add",
            arguments=[BigUIntValue(7)],
        )
        assert transaction.sender == self.john.address
        assert transaction.receiver == self.contract
        assert transaction.value == 0
        assert transaction.gas_limit == 60_000_000
        assert transaction.chain_id == "D"
        assert (
            transaction.data.decode()
            == "proposeTransferExecute@0000000000000000050078d29632acb15998003f615d0a51261353d8041d3e13@0de0b6b3a7640000@0100000000000f4240@616464@07"
        )

    def test_propose_transfer_egld_without_execute(self):
        contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqpgq0rffvv4vk9vesqplv9ws55fxzdfaspqa8cfszy2hms")
        amount = 1000000000000000000

        transaction = self.controller.create_transaction_for_propose_transfer_execute(
            sender=self.john,
            nonce=self.john.get_nonce_then_increment(),
            contract=self.contract,
            receiver=contract,
            native_token_amount=amount,
            gas_limit=60_000_000,
        )
        assert transaction.sender == self.john.address
        assert transaction.receiver == self.contract
        assert transaction.value == 0
        assert transaction.gas_limit == 60_000_000
        assert transaction.chain_id == "D"
        assert (
            transaction.data.decode()
            == "proposeTransferExecute@0000000000000000050078d29632acb15998003f615d0a51261353d8041d3e13@0de0b6b3a7640000@"
        )

    def test_propose_transfer_execute_esdt(self):
        contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqpgqfxlljcaalgl2qfcnxcsftheju0ts36kvl3ts3qkewe")

        transaction = self.controller.create_transaction_for_propose_transfer_execute_esdt(
            sender=self.john,
            nonce=self.john.get_nonce_then_increment(),
            contract=self.contract,
            receiver=contract,
            token_transfers=[TokenTransfer(Token("ALICE-5627f1"), 10)],
            gas_limit=60_000_000,
            opt_gas_limit=5_000_000,
            function="distribute",
            arguments=[],
        )
        assert transaction.sender == self.john.address
        assert transaction.receiver == self.contract
        assert transaction.value == 0
        assert transaction.gas_limit == 60_000_000
        assert transaction.chain_id == "D"
        assert (
            transaction.data.decode()
            == "proposeTransferExecuteEsdt@0000000000000000050049bff963bdfa3ea02713362095df32e3d708eaccfc57@0000000c414c4943452d3536323766310000000000000000000000010a@0100000000004c4b40@64697374726962757465"
        )

    def test_propose_async_call(self):
        contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqpgqdvmhpxxmwv2vfz3sfpggzfyl5qznuz5x05vq5y37ql")

        transaction = self.controller.create_transaction_for_propose_async_call(
            sender=self.john,
            nonce=self.john.get_nonce_then_increment(),
            contract=self.contract,
            receiver=contract,
            gas_limit=60_000_000,
            opt_gas_limit=5_000_000,
            function="add",
            arguments=[BigUIntValue(7)],
        )
        assert transaction.sender == self.john.address
        assert transaction.receiver == self.contract
        assert transaction.value == 0
        assert transaction.gas_limit == 60_000_000
        assert transaction.chain_id == "D"
        assert (
            transaction.data.decode()
            == "proposeAsyncCall@000000000000000005006b377098db7314c48a30485081249fa0053e0a867d18@@0100000000004c4b40@616464@07"
        )

    def test_propose_sc_deploy_from_source(self):
        adder_abi = Abi.load(self.testdata / "adder.abi.json")
        contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqpgqsuxsgykwm6r3s5apct2g5a2rcpe7kw0ed8ssf6h9f6")

        transaction = self.controller.create_transaction_for_propose_contract_deploy_from_source(
            sender=self.john,
            nonce=self.john.get_nonce_then_increment(),
            contract=self.contract,
            gas_limit=60_000_000,
            contract_to_copy=contract,
            native_token_amount=50000000000000000,
            abi=adder_abi,
            arguments=[0],
            is_readable=True,
            is_upgradeable=True,
            is_payable=False,
            is_payable_by_sc=False,
        )
        assert transaction.sender == self.john.address
        assert transaction.receiver == self.contract
        assert transaction.value == 0
        assert transaction.gas_limit == 60_000_000
        assert transaction.chain_id == "D"
        assert (
            transaction.data.decode()
            == "proposeSCDeployFromSource@b1a2bc2ec50000@00000000000000000500870d0412cede871853a1c2d48a7543c073eb39f969e1@0500@"
        )

    def test_propose_sc_upgrade_from_source(self):
        contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqpgqsuxsgykwm6r3s5apct2g5a2rcpe7kw0ed8ssf6h9f6")
        contract_to_copy = Address.new_from_bech32("erd1qqqqqqqqqqqqqpgqsuxsgykwm6r3s5apct2g5a2rcpe7kw0ed8ssf6h9f6")

        transaction = self.controller.create_transaction_for_propose_contract_upgrade_from_source(
            sender=self.john,
            nonce=self.john.get_nonce_then_increment(),
            contract=self.contract,
            contract_to_upgrade=contract,
            gas_limit=60_000_000,
            contract_to_copy=contract_to_copy,
            arguments=[BigUIntValue()],
            native_token_amount=50000000000000000,
            is_readable=True,
            is_upgradeable=True,
            is_payable=False,
            is_payable_by_sc=False,
        )
        assert transaction.sender == self.john.address
        assert transaction.receiver == self.contract
        assert transaction.value == 0
        assert transaction.gas_limit == 60_000_000
        assert transaction.chain_id == "D"
        assert (
            transaction.data.decode()
            == "proposeSCUpgradeFromSource@00000000000000000500870d0412cede871853a1c2d48a7543c073eb39f969e1@b1a2bc2ec50000@00000000000000000500870d0412cede871853a1c2d48a7543c073eb39f969e1@0500@"
        )

    def test_sign_action(self):
        transaction = self.controller.create_transaction_for_sign_action(
            sender=self.john,
            nonce=self.john.get_nonce_then_increment(),
            contract=self.contract,
            action_id=7,
            gas_limit=1_000_000,
        )
        assert transaction.sender == self.john.address
        assert transaction.receiver == self.contract
        assert transaction.value == 0
        assert transaction.gas_limit == 1_000_000
        assert transaction.chain_id == "D"
        assert transaction.data.decode() == "sign@07"

    def test_sign_batch(self):
        transaction = self.controller.create_transaction_for_sign_batch(
            sender=self.john,
            nonce=self.john.get_nonce_then_increment(),
            contract=self.contract,
            batch_id=7,
            gas_limit=1_000_000,
        )
        assert transaction.sender == self.john.address
        assert transaction.receiver == self.contract
        assert transaction.value == 0
        assert transaction.gas_limit == 1_000_000
        assert transaction.chain_id == "D"
        assert transaction.data.decode() == "signBatch@07"

    def test_sign_and_perform(self):
        transaction = self.controller.create_transaction_for_sign_and_perform(
            sender=self.john,
            nonce=self.john.get_nonce_then_increment(),
            contract=self.contract,
            action_id=7,
            gas_limit=1_000_000,
        )
        assert transaction.sender == self.john.address
        assert transaction.receiver == self.contract
        assert transaction.value == 0
        assert transaction.gas_limit == 1_000_000
        assert transaction.chain_id == "D"
        assert transaction.data.decode() == "signAndPerform@07"

    def test_sign_batch_and_perform(self):
        transaction = self.controller.create_transaction_for_sign_batch_and_perform(
            sender=self.john,
            nonce=self.john.get_nonce_then_increment(),
            contract=self.contract,
            batch_id=7,
            gas_limit=1_000_000,
        )
        assert transaction.sender == self.john.address
        assert transaction.receiver == self.contract
        assert transaction.value == 0
        assert transaction.gas_limit == 1_000_000
        assert transaction.chain_id == "D"
        assert transaction.data.decode() == "signBatchAndPerform@07"

    def test_unsign_action(self):
        transaction = self.controller.create_transaction_for_unsign_action(
            sender=self.john,
            nonce=self.john.get_nonce_then_increment(),
            contract=self.contract,
            action_id=7,
            gas_limit=1_000_000,
        )
        assert transaction.sender == self.john.address
        assert transaction.receiver == self.contract
        assert transaction.value == 0
        assert transaction.gas_limit == 1_000_000
        assert transaction.chain_id == "D"
        assert transaction.data.decode() == "unsign@07"

    def test_unsign_batch(self):
        transaction = self.controller.create_transaction_for_unsign_batch(
            sender=self.john,
            nonce=self.john.get_nonce_then_increment(),
            contract=self.contract,
            batch_id=7,
            gas_limit=1_000_000,
        )
        assert transaction.sender == self.john.address
        assert transaction.receiver == self.contract
        assert transaction.value == 0
        assert transaction.gas_limit == 1_000_000
        assert transaction.chain_id == "D"
        assert transaction.data.decode() == "unsignBatch@07"

    def test_unsign_for_outdated_board_members(self):
        transaction = self.controller.create_transaction_for_unsign_for_outdated_board_members(
            sender=self.john,
            nonce=self.john.get_nonce_then_increment(),
            contract=self.contract,
            action_id=7,
            outdated_board_members=[1, 2],
            gas_limit=1_000_000,
        )
        assert transaction.sender == self.john.address
        assert transaction.receiver == self.contract
        assert transaction.value == 0
        assert transaction.gas_limit == 1_000_000
        assert transaction.chain_id == "D"
        assert transaction.data.decode() == "unsignForOutdatedBoardMembers@07@01@02"

    def test_perform_action(self):
        transaction = self.controller.create_transaction_for_perform_action(
            sender=self.john,
            nonce=self.john.get_nonce_then_increment(),
            contract=self.contract,
            action_id=7,
            gas_limit=1_000_000,
        )
        assert transaction.sender == self.john.address
        assert transaction.receiver == self.contract
        assert transaction.value == 0
        assert transaction.gas_limit == 1_000_000
        assert transaction.chain_id == "D"
        assert transaction.data.decode() == "performAction@07"

    def test_perform_batch(self):
        transaction = self.controller.create_transaction_for_perform_batch(
            sender=self.john,
            nonce=self.john.get_nonce_then_increment(),
            contract=self.contract,
            batch_id=7,
            gas_limit=1_000_000,
        )
        assert transaction.sender == self.john.address
        assert transaction.receiver == self.contract
        assert transaction.value == 0
        assert transaction.gas_limit == 1_000_000
        assert transaction.chain_id == "D"
        assert transaction.data.decode() == "performBatch@07"

    def test_create_transaction_for_execute(self):
        transaction = self.controller.create_transaction_for_execute(
            sender=self.john,
            nonce=self.john.get_nonce_then_increment(),
            contract=self.contract,
            function="discardAction",
            arguments=[U32Value(7)],
            gas_limit=1_000_000,
        )
        assert transaction.sender == self.john.address
        assert transaction.receiver == self.contract
        assert transaction.value == 0
        assert transaction.gas_limit == 1_000_000
        assert transaction.chain_id == "D"
        assert transaction.data.decode() == "discardAction@07"

    def test_get_action_valid_signers_count_query(self):
        network_provider = MockNetworkProvider()
        controller = MultisigController(chain_id="D", network_provider=network_provider, abi=self.multisig_abi)

        contract_query_response = SmartContractQueryResponse(
            function="getActionValidSignerCount",
            return_code="ok",
            return_message="",
            return_data_parts=[bytes.fromhex("04")],
        )
        network_provider.mock_query_contract_on_function("getActionValidSignerCount", contract_query_response)

        [response] = controller.query(
            contract=self.contract,
            function="getActionValidSignerCount",
            arguments=[U32Value(42)],
        )
        assert response == 4
