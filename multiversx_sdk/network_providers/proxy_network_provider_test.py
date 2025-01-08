import pytest
import requests

from multiversx_sdk.core import (Address, Token, Transaction,
                                 TransactionComputer, TransactionOnNetwork,
                                 TransactionStatus)
from multiversx_sdk.network_providers.config import NetworkProviderConfig
from multiversx_sdk.network_providers.http_resources import block_from_response
from multiversx_sdk.network_providers.proxy_network_provider import \
    ProxyNetworkProvider
from multiversx_sdk.network_providers.resources import TokenAmountOnNetwork
from multiversx_sdk.smart_contracts.smart_contract_query import \
    SmartContractQuery
from multiversx_sdk.testutils.wallets import load_wallets


@pytest.mark.networkInteraction
class TestProxy:
    proxy = ProxyNetworkProvider("https://devnet-gateway.multiversx.com")

    def test_get_network_config(self):
        result = self.proxy.get_network_config()

        assert result.chain_id == "D"
        assert result.gas_per_data_byte == 1500
        assert result.round_duration == 6000
        assert result.min_gas_limit == 50000
        assert result.min_gas_price == 1_000_000_000
        assert result.raw

    def test_get_network_status(self):
        result = self.proxy.get_network_status()

        assert result.block_nonce
        assert result.current_round
        assert result.block_timestamp
        assert result.current_epoch
        assert result.highest_final_block_nonce
        assert result.raw

    def test_get_block(self):
        shard=1
        
        block_hash=bytes.fromhex("ded535cc0afb2dc5f9787e9560dc48d0b83564a3f994a390b228d894d854699f")
        result_by_hash = self.proxy.get_block(shard=shard, block_hash=block_hash)

        block_nonce=5949242
        result_by_nonce = self.proxy.get_block(shard=shard, block_nonce=block_nonce)

        assert result_by_hash.hash == bytes.fromhex("ded535cc0afb2dc5f9787e9560dc48d0b83564a3f994a390b228d894d854699f")
        assert result_by_hash.nonce == 5949242
        assert result_by_hash.shard == 1
        assert result_by_hash.timestamp == 1730112578
        assert result_by_hash == result_by_nonce

    def test_get_latest_block(self):
        result = self.proxy.get_latest_block()
        assert result

    def test_get_account(self):
        address = Address.new_from_bech32(
            "erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl"
        )
        result = self.proxy.get_account(address)

        assert result.address.to_bech32() == "erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl"
        assert not result.username
        assert result.contract_owner_address is None

        address = Address.new_from_bech32(
            "erd1qqqqqqqqqqqqqpgq076flgeualrdu5jyyj60snvrh7zu4qrg05vqez5jen"
        )
        result = self.proxy.get_account(address)

        assert result.address.to_bech32() == "erd1qqqqqqqqqqqqqpgq076flgeualrdu5jyyj60snvrh7zu4qrg05vqez5jen"
        assert not result.username
        assert result.contract_owner_address == Address.new_from_bech32(
            "erd1wzx0tak22f2me4g7wpxfae2w3htfue7khrg28fy6wu8x9hzq05vqm8qhnm")
        assert result.is_contract_payable is False
        assert result.is_contract_readable

    def test_get_account_storage(self):
        address = Address.new_from_bech32("erd1qqqqqqqqqqqqqpgq076flgeualrdu5jyyj60snvrh7zu4qrg05vqez5jen")
        result = self.proxy.get_account_storage(address)

        assert len(result.entries) == 1
        assert result.entries[0].key == "sum"
        assert result.entries[0].value

    def test_get_account_storage_entry(self):
        address = Address.new_from_bech32("erd1qqqqqqqqqqqqqpgq076flgeualrdu5jyyj60snvrh7zu4qrg05vqez5jen")
        result = self.proxy.get_account_storage_entry(address=address, entry_key="sum")

        assert result.key == "sum"
        assert result.value

    def test_get_token_of_account(self):
        address = Address.new_from_bech32(
            "erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl"
        )
        result = self.proxy.get_token_of_account(address, Token("TEST-ff155e"))

        assert result.token.identifier == "TEST-ff155e"
        assert result.amount == 99999999999980000

        result = self.proxy.get_token_of_account(
            address, Token("NFTEST-ec88b8", 1)
        )

        assert result.amount == 1
        assert result.token.nonce == 1
        assert result.token.identifier == "NFTEST-ec88b8"

    def test_get_fungible_tokens_of_account(self):
        address = Address.new_from_bech32(
            "erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl"
        )
        tokens = self.proxy.get_fungible_tokens_of_account(address)
        assert len(tokens)

        filtered: list[TokenAmountOnNetwork] = list(filter(lambda x: x.token.identifier == "TEST-ff155e", tokens))
        assert len(filtered) == 1
        assert filtered[0].token.identifier == "TEST-ff155e"
        assert filtered[0].amount == 99999999999980000

    def test_get_non_fungible_tokens_of_account(self):
        address = Address.new_from_bech32(
            "erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl"
        )
        tokens = self.proxy.get_non_fungible_tokens_of_account(address)
        assert len(tokens)

        filtered: list[TokenAmountOnNetwork] = list(filter(lambda x: x.token.identifier == "NFTEST-ec88b8-01", tokens))
        assert len(filtered) == 1
        assert filtered[0].token.identifier == "NFTEST-ec88b8-01"
        assert filtered[0].token.nonce == 1
        assert filtered[0].amount == 1

    def test_get_transaction_status(self):
        result = self.proxy.get_transaction_status(
            bytes.fromhex("9d47c4b4669cbcaa26f5dec79902dd20e55a0aa5f4b92454a74e7dbd0183ad6c")
        )
        assert result.status == "success"

    def test_query_contract(self):
        query = SmartContractQuery(
            contract=Address.new_from_bech32("erd1qqqqqqqqqqqqqpgqqy34h7he2ya6qcagqre7ur7cc65vt0mxrc8qnudkr4"),
            function="getSum",
            arguments=[]
        )
        result = self.proxy.query_contract(query)
        assert len(result.return_data_parts) == 1

    def test_get_definition_of_fungible_token(self):
        result = self.proxy.get_definition_of_fungible_token("TEST-ff155e")

        assert result.identifier == "TEST-ff155e"
        assert result.owner == "erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl"
        assert result.decimals == 6
        assert len(result.raw["returnDataParts"])

    def test_get_definition_of_token_collection(self):
        result = self.proxy.get_definition_of_tokens_collection("NFTEST-ec88b8")

        assert result.collection == "NFTEST-ec88b8"
        assert result.owner == "erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl"
        assert result.type == "NonFungibleESDT"
        assert result.decimals == 0
        assert len(result.raw["returnDataParts"])

    def test_get_transaction(self):
        transaction = self.proxy.get_transaction(
            "9d47c4b4669cbcaa26f5dec79902dd20e55a0aa5f4b92454a74e7dbd0183ad6c"
        )

        assert transaction.nonce == 0
        assert transaction.epoch == 348
        assert transaction.hash.hex() == "9d47c4b4669cbcaa26f5dec79902dd20e55a0aa5f4b92454a74e7dbd0183ad6c"
        assert transaction.status.is_completed
        assert transaction.sender.to_bech32() == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.smart_contract_results == []

    def test_get_transaction_with_events(self):
        transaction = self.proxy.get_transaction(
            bytes.fromhex("6fe05e4ca01d42c96ae5182978a77fe49f26bcc14aac95ad4f19618173f86ddb")
        )
        assert transaction.logs
        assert transaction.logs.events
        assert len(transaction.logs.events) == 2
        assert len(transaction.logs.events[0].topics) == 8
        assert transaction.logs.events[0].topics[0].hex() == "544553542d666631353565"
        assert transaction.logs.events[0].topics[1].hex() == ""
        assert transaction.logs.events[0].topics[2].hex() == "63616e4368616e67654f776e6572"

    def test_get_sc_invoking_tx(self):
        transaction = self.proxy.get_transaction(
            "6fe05e4ca01d42c96ae5182978a77fe49f26bcc14aac95ad4f19618173f86ddb"
        )

        assert transaction.status.is_completed
        assert len(transaction.smart_contract_results) > 0
        assert transaction.data.decode() == "issue@54455354546f6b656e@54455354@016345785d8a0000@06@63616e4368616e67654f776e6572@74727565@63616e55706772616465@74727565@63616e4164645370656369616c526f6c6573@74727565"
        assert sum([r.raw.get("isRefund", False) for r in transaction.smart_contract_results]) == 1

    def test_send_transaction(self):
        transaction = Transaction(
            sender=Address.new_from_bech32("erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl"),
            receiver=Address.new_from_bech32("erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl"),
            gas_limit=50000,
            chain_id="D",
            value=5000000000000000000,
            nonce=100,
            gas_price=1000000000,
            version=2,
            signature=bytes.fromhex(
                "faf50b8368cb2c20597dad671a14aa76d4c65937d6e522c64946f16ad6a250262463e444596fa7ee2af1273f6ad0329d43af48d1ae5f3b295bc8f48fdba41a05"
            )
        )
        expected_hash = ("fc914860c1d137ed8baa602e561381f97c7bad80d150c5bf90760d3cfd3a4cea")
        assert self.proxy.send_transaction(transaction) == bytes.fromhex(expected_hash)

    def test_send_transaction_with_data(self):
        transaction = Transaction(
            sender=Address.new_from_bech32("erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl"),
            receiver=Address.new_from_bech32("erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl"),
            gas_limit=70000,
            chain_id="D",
            nonce=105,
            gas_price=1000000000,
            version=2,
            data=b"foo",
            signature=bytes.fromhex(
                "7a8bd08351bac6b1113545f5a896cb0b63806abd93d639bc4d16bfbc82c7b514f68ed7b36c743f4c3d2d1e1d3cb356824041d51dfe587a149f6fc9ab0dd9c408"
            )
        )
        expected_hash = ("4dc7d4e18c0cf9ca7f17677ef0ac3d1363528e892996b518bee909bb17cf7929")
        assert self.proxy.send_transaction(transaction) == bytes.fromhex(expected_hash)

    def test_send_transactions(self):
        first_tx = Transaction(
            sender=Address.new_from_bech32("erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl"),
            receiver=Address.new_from_bech32("erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl"),
            gas_limit=50000,
            chain_id="D",
            nonce=103,
            gas_price=1000000000,
            version=2,
            signature=bytes.fromhex(
                "498d5abb9f8eb69cc75f24320e8929dadbfa855ffac220d5e92175a83be68e0437801af3a1411e3d839738230097a1c38da5c8c4df3f345defc5d40300675900"
            )
        )

        invalid_tx = Transaction(
            sender=Address.new_from_bech32("erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl"),
            receiver=Address.new_from_bech32("erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl"),
            gas_limit=50000,
            chain_id="D",
            nonce=77
        )

        last_tx = Transaction(
            sender=Address.new_from_bech32("erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl"),
            receiver=Address.new_from_bech32("erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl"),
            gas_limit=50000,
            chain_id="D",
            nonce=104,
            gas_price=1000000000,
            version=2,
            signature=bytes.fromhex(
                "341a2f3b738fbd20692e3bbd1cb36cb5f4ce9c0a9acc0cf4322269c0fcf34fd6bb59cd94062a9a4730e47f41b1ef3e29b69c6ab2a2a4dca9c9a7724681bc1708"
            )
        )

        transactions = [first_tx, invalid_tx, last_tx]

        expected_hashes = [
            bytes.fromhex("61b4f2561fc57bfb8b8971ed23cd64259b664bc0404ea7a0449def8ceef24b08"),
            bytes.fromhex(""),
            bytes.fromhex("30274b60b5635f981fa89ccfe726a34ca7121caa5d34123021c77a5c64cc9163"),
        ]

        num_txs, hashes = self.proxy.send_transactions(transactions)
        assert num_txs == 2
        assert hashes == expected_hashes

    def test_simulate_transaction(self):
        bob = load_wallets()["bob"]
        tx_computer = TransactionComputer()

        transaction = Transaction(
            sender=Address.new_from_bech32(bob.label),
            receiver=Address.new_from_bech32(bob.label),
            gas_limit=50000,
            chain_id="D",
            signature=bytes.fromhex("".join(["0"] * 128))
        )
        nonce = self.proxy.get_account(Address.new_from_bech32(bob.label)).nonce
        transaction.nonce = nonce

        tx_on_network = self.proxy.simulate_transaction(transaction)
        assert tx_on_network.status == TransactionStatus("success")

        transaction.signature = bob.secret_key.sign(tx_computer.compute_bytes_for_signing(transaction))

        tx_on_network = self.proxy.simulate_transaction(transaction=transaction, check_signature=True)
        assert tx_on_network.status == TransactionStatus("success")

        transaction = Transaction(
            sender=Address.new_from_bech32(bob.label),
            receiver=Address.new_from_bech32("erd1qqqqqqqqqqqqqpgq076flgeualrdu5jyyj60snvrh7zu4qrg05vqez5jen"),
            gas_limit=10000000,
            chain_id="D",
            data=b"add@07",
            nonce=nonce,
            signature=bytes.fromhex("".join(["0"] * 128))
        )
        tx_on_network = self.proxy.simulate_transaction(transaction)

        assert tx_on_network.status == TransactionStatus("success")
        assert len(tx_on_network.smart_contract_results) == 1
        assert tx_on_network.smart_contract_results[0].sender.to_bech32(
        ) == "erd1qqqqqqqqqqqqqpgq076flgeualrdu5jyyj60snvrh7zu4qrg05vqez5jen"
        assert tx_on_network.smart_contract_results[0].receiver.to_bech32() == bob.label
        assert tx_on_network.smart_contract_results[0].data == b"@6f6b"

        transaction.signature = bob.secret_key.sign(tx_computer.compute_bytes_for_signing(transaction))

        tx_on_network = self.proxy.simulate_transaction(transaction=transaction, check_signature=True)

        assert tx_on_network.status == TransactionStatus("success")
        assert len(tx_on_network.smart_contract_results) == 1
        assert tx_on_network.smart_contract_results[0].sender.to_bech32(
        ) == "erd1qqqqqqqqqqqqqpgq076flgeualrdu5jyyj60snvrh7zu4qrg05vqez5jen"
        assert tx_on_network.smart_contract_results[0].receiver.to_bech32() == bob.label
        assert tx_on_network.smart_contract_results[0].data == b"@6f6b"

    def test_estimate_transaction_cost(self):
        bob = load_wallets()["bob"]
        tx_computer = TransactionComputer()

        transaction = Transaction(
            sender=Address.new_from_bech32(bob.label),
            receiver=Address.new_from_bech32(bob.label),
            gas_limit=50000,
            chain_id="D",
            data="test transaction".encode()
        )
        transaction.nonce = self.proxy.get_account(Address.new_from_bech32(bob.label)).nonce
        transaction.signature = bob.secret_key.sign(tx_computer.compute_bytes_for_signing(transaction))

        result = self.proxy.estimate_transaction_cost(transaction)

        assert result.gas_limit == 74_000

    def test_send_and_await_for_completed_transaction(self):
        bob = load_wallets()["bob"]
        tx_computer = TransactionComputer()

        transaction = Transaction(
            sender=Address.new_from_bech32(bob.label),
            receiver=Address.new_from_bech32(bob.label),
            gas_limit=50000,
            chain_id="D",
        )
        nonce = self.proxy.get_account(Address.new_from_bech32(bob.label)).nonce

        transaction.nonce = nonce
        transaction.signature = bob.secret_key.sign(tx_computer.compute_bytes_for_signing(transaction))

        hash = self.proxy.send_transaction(transaction)

        tx_on_network = self.proxy.await_transaction_completed(hash)
        assert tx_on_network.status.is_completed

        transaction = Transaction(
            sender=Address.new_from_bech32(bob.label),
            receiver=Address.new_from_bech32("erd1qqqqqqqqqqqqqpgqhdqz9j3zgpl8fg2z0jzx9n605gwxx4djd8ssruw094"),
            gas_limit=5000000,
            chain_id="D",
            data="dummy@05".encode()
        )
        transaction.nonce = nonce + 1
        transaction.signature = bob.secret_key.sign(tx_computer.compute_bytes_for_signing(transaction))

        def condition(tx: TransactionOnNetwork) -> bool:
            return not tx.status.is_successful

        hash = self.proxy.send_transaction(transaction)

        tx_on_network = self.proxy.await_transaction_on_condition(
            transaction_hash=hash,
            condition=condition
        )
        assert not tx_on_network.status.is_successful

    def test_do_get_generic(self):
        query_params = {
            "withTxs": "true"
        }

        result = self.proxy.do_get_generic(f"block/{1}/by-nonce/{5964199}", query_params)
        block = block_from_response(result.to_dictionary())

        miniblocks = block.raw.get("block", {}).get("miniBlocks", [])
        assert len(miniblocks)
        assert len(miniblocks[0].get("transactions", []))

    def test_user_agent(self):
        # using the previoulsy instantiated provider without user agent
        response = requests.get(self.proxy.url + "/network/config", **self.proxy.config.requests_options)
        headers = response.request.headers
        assert headers.get("User-Agent") == "multiversx-sdk-py/proxy/unknown"

        # using the new instantiated provider with user agent
        config = NetworkProviderConfig(client_name="test-client")
        proxy = ProxyNetworkProvider(url='https://devnet-gateway.multiversx.com', config=config)

        response = requests.get(proxy.url + "/network/config", **proxy.config.requests_options)
        headers = response.request.headers
        assert headers.get("User-Agent") == "multiversx-sdk-py/proxy/test-client"
