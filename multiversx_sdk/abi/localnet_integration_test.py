from decimal import Decimal
from pathlib import Path

import pytest

from multiversx_sdk.abi.abi import Abi, AbiDefinition
from multiversx_sdk.abi.managed_decimal_value import ManagedDecimalValue
from multiversx_sdk.accounts.account import Account
from multiversx_sdk.network_providers.proxy_network_provider import ProxyNetworkProvider
from multiversx_sdk.smart_contracts.smart_contract_controller import SmartContractController
from multiversx_sdk.testutils.wallets import load_wallets


@pytest.mark.skip("Requires localnet")
class TestLocalnetInteraction:
    wallets = load_wallets()
    alice = wallets["alice"]
    testdata = Path(__file__).parent.parent / "testutils" / "testdata"

    def test_managed_decimal(self):
        abi_definition = AbiDefinition.from_dict(
            {
                "endpoints": [
                    {
                        "name": "returns_egld_decimal",
                        "mutability": "mutable",
                        "payableInTokens": ["EGLD"],
                        "inputs": [],
                        "outputs": [{"type": "ManagedDecimal<18>"}],
                    },
                    {
                        "name": "managed_decimal_addition",
                        "mutability": "mutable",
                        "inputs": [
                            {"name": "first", "type": "ManagedDecimal<2>"},
                            {"name": "second", "type": "ManagedDecimal<2>"},
                        ],
                        "outputs": [{"type": "ManagedDecimal<2>"}],
                    },
                    {
                        "name": "managed_decimal_ln",
                        "mutability": "mutable",
                        "inputs": [{"name": "x", "type": "ManagedDecimal<9>"}],
                        "outputs": [{"type": "ManagedDecimalSigned<9>"}],
                    },
                    {
                        "name": "managed_decimal_addition_var",
                        "mutability": "mutable",
                        "inputs": [
                            {"name": "first", "type": "ManagedDecimal<usize>"},
                            {"name": "second", "type": "ManagedDecimal<usize>"},
                        ],
                        "outputs": [{"type": "ManagedDecimal<usize>"}],
                    },
                    {
                        "name": "managed_decimal_ln_var",
                        "mutability": "mutable",
                        "inputs": [{"name": "x", "type": "ManagedDecimal<usize>"}],
                        "outputs": [{"type": "ManagedDecimalSigned<9>"}],
                    },
                ]
            }
        )

        abi = Abi(abi_definition)

        proxy = ProxyNetworkProvider("http://localhost:7950")
        sc_controller = SmartContractController(
            chain_id="localnet",
            network_provider=proxy,
            abi=abi,
        )

        alice = Account(self.alice.secret_key)
        alice.nonce = proxy.get_account(alice.address).nonce

        # deploy contract
        deploy_tx = sc_controller.create_transaction_for_deploy(
            sender=alice,
            nonce=alice.get_nonce_then_increment(),
            bytecode=self.testdata / "basic-features.wasm",
            gas_limit=600_000_000,
            arguments=[],
        )

        deploy_tx_hash = proxy.send_transaction(deploy_tx)
        deploy_outcome = sc_controller.await_completed_deploy(deploy_tx_hash)
        assert deploy_outcome.return_code == "ok"

        contract = deploy_outcome.contracts[0].address

        # return egld decimals
        return_egld_transaction = sc_controller.create_transaction_for_execute(
            sender=alice,
            nonce=alice.get_nonce_then_increment(),
            contract=contract,
            gas_limit=100_000_000,
            function="returns_egld_decimal",
            arguments=[],
            native_transfer_amount=1,
        )

        tx_hash = proxy.send_transaction(return_egld_transaction)
        outcome = sc_controller.await_completed_execute(tx_hash)
        assert outcome.return_code == "ok"
        assert len(outcome.values) == 1
        assert outcome.values[0] == Decimal("0.000000000000000001")

        # addition with const decimals
        addition_transaction = sc_controller.create_transaction_for_execute(
            sender=alice,
            nonce=alice.get_nonce_then_increment(),
            contract=contract,
            gas_limit=100_000_000,
            function="managed_decimal_addition",
            arguments=[ManagedDecimalValue("2.5", 2), ManagedDecimalValue("2.7", 2)],
        )

        tx_hash = proxy.send_transaction(addition_transaction)
        outcome = sc_controller.await_completed_execute(tx_hash)
        assert outcome.return_code == "ok"
        assert len(outcome.values) == 1
        assert outcome.values[0] == Decimal("5.2")

        # log
        md_ln_transaction = sc_controller.create_transaction_for_execute(
            sender=alice,
            nonce=alice.get_nonce_then_increment(),
            contract=contract,
            gas_limit=100_000_000,
            function="managed_decimal_ln",
            arguments=[ManagedDecimalValue("23", 9)],
        )

        tx_hash = proxy.send_transaction(md_ln_transaction)
        outcome = sc_controller.await_completed_execute(tx_hash)
        assert outcome.return_code == "ok"
        assert len(outcome.values) == 1
        assert outcome.values[0] == Decimal("3.135553845")

        # addition var decimals
        addition_var_transaction = sc_controller.create_transaction_for_execute(
            sender=alice,
            nonce=alice.get_nonce_then_increment(),
            contract=contract,
            gas_limit=50_000_000,
            function="managed_decimal_addition_var",
            arguments=[ManagedDecimalValue("4", 2, True), ManagedDecimalValue("5", 2, True)],
        )

        tx_hash = proxy.send_transaction(addition_var_transaction)
        outcome = sc_controller.await_completed_execute(tx_hash)
        assert outcome.return_code == "ok"
        assert len(outcome.values) == 1
        assert outcome.values[0] == Decimal("9")

        # ln var
        ln_var_transaction = sc_controller.create_transaction_for_execute(
            sender=alice,
            nonce=alice.get_nonce_then_increment(),
            contract=contract,
            gas_limit=50_000_000,
            function="managed_decimal_ln_var",
            arguments=[ManagedDecimalValue("23", 9, True)],
        )

        tx_hash = proxy.send_transaction(ln_var_transaction)
        outcome = sc_controller.await_completed_execute(tx_hash)
        assert outcome.return_code == "ok"
        assert len(outcome.values) == 1
        assert outcome.values[0] == Decimal("3.135553845")
