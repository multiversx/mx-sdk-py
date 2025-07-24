# from pathlib import Path

# import pytest

# from multiversx_sdk.abi.abi import Abi
# from multiversx_sdk.abi.bigint_value import BigIntValue
# from multiversx_sdk.accounts.account import Account
# from multiversx_sdk.core.address import Address
# from multiversx_sdk.gas_estimator.gas_limit_estimator import GasLimitEstimator
# from multiversx_sdk.multisig.multisig_controller import MultisigController
# from multiversx_sdk.network_providers.proxy_network_provider import ProxyNetworkProvider
# from multiversx_sdk.smart_contracts.smart_contract_controller import (
#     SmartContractController,
# )


# @pytest.mark.skip
# class TestGasEstimatorOnChain:
#     testutils = Path(__file__).parent.parent / "testutils"
#     testdata = testutils / "testdata"
#     testwallets = testutils / "testwallets"

#     alice = Account.new_from_pem(testwallets / "alice.pem")
#     bob = Account.new_from_pem(testwallets / "bob.pem")
#     user = Account.new_from_pem(testwallets / "user.pem")

#     multisig_wasm = testdata / "multisig-full.wasm"
#     multisig_abi = testdata / "multisig-full.abi.json"

#     proxy = ProxyNetworkProvider(url="http://192.168.50.99:8079")
#     gas_estimator = GasLimitEstimator(network_provider=proxy, gas_multiplier=1.1)

#     abi = Abi.load(multisig_abi)
#     contract_address = Address.new_from_bech32("erd1qqqqqqqqqqqqqpgqeglcgq2s5um0pzknxxspugslw3f8k7ue9ncs7hmlqj")

#     adder_address = Address.new_from_bech32("erd1qqqqqqqqqqqqqpgqm5w98z3ruk43gwd3rs0hyzk92y0wzee59ncsx0wp6m")

#     controller = MultisigController(
#         chain_id="D",
#         network_provider=proxy,
#         abi=abi,
#         gas_limit_estimator=gas_estimator,
#     )

#     def test_deploy_contract(self):
#         self.user.nonce = self.proxy.get_account(self.user.address).nonce
#         transaction = self.controller.create_transaction_for_deploy(
#             sender=self.user,
#             nonce=self.user.get_nonce_then_increment(),
#             bytecode=self.multisig_wasm,
#             quorum=2,
#             board=[self.alice.address, self.user.address],
#         )

#         # estimated_gas = transaction.gas_limit
#         # tx_hash = self.proxy.send_transaction(transaction)
#         # print(tx_hash.hex())

#     def test_upgrade_contract(self):
#         self.user.nonce = self.proxy.get_account(self.user.address).nonce
#         transaction = self.controller.create_transaction_for_propose_contract_upgrade_from_source(
#             sender=self.user,
#             nonce=self.user.get_nonce_then_increment(),
#             contract=self.contract_address,
#             contract_to_upgrade=self.contract_address,
#             contract_to_copy=Address.new_from_bech32("erd1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq6gq4hu"),
#         )

#         # estimated_gas = transaction.gas_limit
#         tx_hash = self.proxy.send_transaction(transaction)
#         print(tx_hash.hex())

#     def test_deposit(self):
#         self.bob.nonce = self.proxy.get_account(self.bob.address).nonce
#         transaction = self.controller.create_transaction_for_deposit(
#             sender=self.bob,
#             nonce=self.bob.get_nonce_then_increment(),
#             contract=self.contract_address,
#             native_token_amount=1_000_000_000_000_000_00,
#         )

#         # estimated_gas = transaction.gas_limit
#         # tx_hash = self.proxy.send_transaction(transaction)
#         # print(tx_hash.hex())

#     # @pytest.mark.only
#     def test_sign(self):
#         self.user.nonce = self.proxy.get_account(self.user.address).nonce
#         transaction = self.controller.create_transaction_for_sign_action(
#             sender=self.user,
#             nonce=self.user.get_nonce_then_increment(),
#             contract=self.contract_address,
#             action_id=1,
#         )
#         print(transaction.gas_limit)

#         # estimated_gas = transaction.gas_limit
#         tx_hash = self.proxy.send_transaction(transaction)

#     # @pytest.mark.only
#     def test_sign_and_perform(self):
#         self.alice.nonce = self.proxy.get_account(self.alice.address).nonce
#         transaction = self.controller.create_transaction_for_sign_and_perform(
#             sender=self.alice,
#             nonce=self.alice.get_nonce_then_increment(),
#             contract=self.contract_address,
#             action_id=1,
#         )

#         # estimated_gas = transaction.gas_limit
#         tx_hash = self.proxy.send_transaction(transaction)

#     # @pytest.mark.only
#     def test_deploy_adder(self):
#         self.user.nonce = self.proxy.get_account(self.user.address).nonce
#         controller = SmartContractController(
#             chain_id="D",
#             network_provider=self.proxy,
#             gas_limit_estimator=self.gas_estimator,
#         )
#         transaction = controller.create_transaction_for_deploy(
#             sender=self.user,
#             nonce=self.user.get_nonce_then_increment(),
#             bytecode=self.testdata / "adder.wasm",
#             arguments=[BigIntValue(0)],
#         )

#         # estimated_gas = transaction.gas_limit
#         tx_hash = self.proxy.send_transaction(transaction)
#         # print(tx_hash.hex())

#     # @pytest.mark.only
#     def test_upgrade_adder(self):
#         self.user.nonce = self.proxy.get_account(self.user.address).nonce
#         controller = SmartContractController(
#             chain_id="D",
#             network_provider=self.proxy,
#             gas_limit_estimator=self.gas_estimator,
#         )
#         transaction = controller.create_transaction_for_upgrade(
#             sender=self.user,
#             nonce=self.user.get_nonce_then_increment(),
#             contract=self.adder_address,
#             bytecode=self.testdata / "adder.wasm",
#             arguments=[BigIntValue(0)],
#         )

#         # estimated_gas = transaction.gas_limit
#         tx_hash = self.proxy.send_transaction(transaction)
#         # print(tx_hash.hex())
