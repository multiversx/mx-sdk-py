import pytest

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.network_providers.proxy_network_provider import (
    ContractQuery, ProxyNetworkProvider)


@pytest.mark.networkInteraction
class TestProxy:
    proxy = ProxyNetworkProvider("https://devnet-gateway.multiversx.com")

    def test_get_network_config(self):
        result = self.proxy.get_network_config()

        assert result.chain_id == "D"
        assert result.gas_per_data_byte == 1500
        assert result.round_duration == 6000
        assert result.rounds_per_epoch == 2400
        assert result.min_gas_limit == 50000
        assert result.min_gas_price == 1_000_000_000
        assert result.min_transaction_version == 1
        assert result.top_up_factor == 0.5
        assert result.num_shards_without_meta == 3

    def test_get_network_status(self):
        result = self.proxy.get_network_status()

        assert result.nonce > 0
        assert result.current_round > 0
        assert result.epoch_number > 0
        assert result.round_at_epoch_start > 0
        assert result.rounds_passed_in_current_epcoch > 0
        assert result.nonces_passed_in_current_epoch > 0
        assert result.highest_final_nonce > 0
        assert result.nonce_at_epoch_start > 0
        assert result.rounds_per_epoch == 2400

    def test_get_network_gas_configs(self):
        result = self.proxy.get_network_gas_configs()
        built_in_cost = result["gasConfigs"]["builtInCost"]
        meta_system_sc_cost = result["gasConfigs"]["metaSystemSCCost"]

        assert built_in_cost["ESDTTransfer"] == 200000
        assert meta_system_sc_cost["Stake"] == 5000000

    def test_get_account(self):
        address = Address.new_from_bech32(
            "erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl"
        )
        result = self.proxy.get_account(address)

        assert result.address.to_bech32() == "erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl"
        assert result.username == ""

    def test_get_fungible_token_of_account(self):
        address = Address.new_from_bech32(
            "erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl"
        )
        result = self.proxy.get_fungible_token_of_account(address, "TEST-ff155e")

        assert result.identifier == "TEST-ff155e"
        assert result.balance == 99999999999980000

    def test_get_nonfungible_token_of_account(self):
        address = Address.new_from_bech32(
            "erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl"
        )
        result = self.proxy.get_nonfungible_token_of_account(
            address, "NFTEST-ec88b8", 1
        )

        assert result.balance == 1
        assert result.nonce == 1
        assert result.collection == "NFTEST-ec88b8"
        assert result.identifier == "NFTEST-ec88b8-01"
        assert result.type == ""
        assert result.royalties == 25

    def test_get_transaction_status(self):
        result = self.proxy.get_transaction_status(
            "9d47c4b4669cbcaa26f5dec79902dd20e55a0aa5f4b92454a74e7dbd0183ad6c"
        )
        assert result.status == "success"

    def test_query_contract(self):
        query = ContractQuery(
            Address.new_from_bech32(
                "erd1qqqqqqqqqqqqqpgqqy34h7he2ya6qcagqre7ur7cc65vt0mxrc8qnudkr4"
            ),
            "getSum",
            0,
            [],
        )
        result = self.proxy.query_contract(query)
        assert len(result.return_data) == 1

    def test_get_definition_of_fungible_token(self):
        result = self.proxy.get_definition_of_fungible_token("TEST-ff155e")

        assert result.identifier == "TEST-ff155e"
        assert result.owner.to_bech32() == "erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl"
        assert result.can_upgrade
        assert not result.can_freeze
        assert result.decimals == 6
        assert result.supply == 100000000000

    def test_get_definition_of_token_collection(self):
        result = self.proxy.get_definition_of_token_collection("NFTEST-ec88b8")

        assert result.collection == "NFTEST-ec88b8"
        assert result.owner.to_bech32() == "erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl"
        assert result.type == "NonFungibleESDT"
        assert result.decimals == 0
        assert not result.can_freeze
        assert not result.can_pause

    def test_get_transaction(self):
        result = self.proxy.get_transaction(
            "9d47c4b4669cbcaa26f5dec79902dd20e55a0aa5f4b92454a74e7dbd0183ad6c"
        )

        assert result.nonce == 0
        assert result.block_nonce == 835600
        assert result.epoch == 348
        assert result.hash == "9d47c4b4669cbcaa26f5dec79902dd20e55a0aa5f4b92454a74e7dbd0183ad6c"
        assert result.is_completed is None
        assert result.sender.to_bech32() == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert result.contract_results.items == []

    def test_get_transaction_with_events(self):
        transaction = self.proxy.get_transaction("6fe05e4ca01d42c96ae5182978a77fe49f26bcc14aac95ad4f19618173f86ddb")
        assert transaction.logs
        assert transaction.logs.events
        assert len(transaction.logs.events) == 2
        assert len(transaction.logs.events[0].topics) == 8
        assert transaction.logs.events[0].topics[0].hex() == "544553542d666631353565"
        assert transaction.logs.events[0].topics[1].hex() == ""
        assert transaction.logs.events[0].topics[2].hex() == "63616e4368616e67654f776e6572"

    def test_get_sc_invoking_tx(self):
        result = self.proxy.get_transaction(
            "6fe05e4ca01d42c96ae5182978a77fe49f26bcc14aac95ad4f19618173f86ddb", True
        )

        assert result.is_completed is True
        assert len(result.contract_results.items) > 0
        assert result.data == "issue@54455354546f6b656e@54455354@016345785d8a0000@06@63616e4368616e67654f776e6572@74727565@63616e55706772616465@74727565@63616e4164645370656369616c526f6c6573@74727565"
        assert sum([r.is_refund for r in result.contract_results.items]) == 1

    def test_get_hyperblock(self):
        result_by_nonce = self.proxy.get_hyperblock(835683)
        result_by_hash = self.proxy.get_hyperblock(
            "55ef33845c94111c09233d3882f17023a18f6bb86a1b7e7a5ba0c5b5030e1957"
        )

        assert result_by_nonce.get("hash") == result_by_hash.get("hash")
        assert result_by_nonce.get("nonce") == result_by_hash.get("nonce")
        assert result_by_nonce.get("round") == result_by_hash.get("round")
        assert result_by_nonce.get("epoch") == result_by_hash.get("epoch")
        assert result_by_nonce.get("numTxs") == result_by_hash.get("numTxs")
        assert result_by_nonce.get("timestamp") == result_by_hash.get("timestamp")

    def test_send_transaction(self):
        transaction = Transaction(
            sender="erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl",
            receiver="erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl",
            gas_limit=50000,
            chain_id="D",
            value=5000000000000000000,
            nonce=100,
            gas_price=1000000000,
            version=2,
            signature=bytes.fromhex("faf50b8368cb2c20597dad671a14aa76d4c65937d6e522c64946f16ad6a250262463e444596fa7ee2af1273f6ad0329d43af48d1ae5f3b295bc8f48fdba41a05")
        )
        expected_hash = ("fc914860c1d137ed8baa602e561381f97c7bad80d150c5bf90760d3cfd3a4cea")
        assert self.proxy.send_transaction(transaction) == expected_hash

    def test_send_transaction_with_data(self):
        transaction = Transaction(
            sender="erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl",
            receiver="erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl",
            gas_limit=70000,
            chain_id="D",
            nonce=105,
            gas_price=1000000000,
            version=2,
            data=b"foo",
            signature=bytes.fromhex("7a8bd08351bac6b1113545f5a896cb0b63806abd93d639bc4d16bfbc82c7b514f68ed7b36c743f4c3d2d1e1d3cb356824041d51dfe587a149f6fc9ab0dd9c408")
        )
        expected_hash = ("4dc7d4e18c0cf9ca7f17677ef0ac3d1363528e892996b518bee909bb17cf7929")
        assert self.proxy.send_transaction(transaction) == expected_hash

    def test_send_transactions(self):
        first_tx = Transaction(
            sender="erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl",
            receiver="erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl",
            gas_limit=50000,
            chain_id="D",
            nonce=103,
            gas_price=1000000000,
            version=2,
            signature=bytes.fromhex("498d5abb9f8eb69cc75f24320e8929dadbfa855ffac220d5e92175a83be68e0437801af3a1411e3d839738230097a1c38da5c8c4df3f345defc5d40300675900")
        )

        second_tx = Transaction(
            sender="erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl",
            receiver="erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl",
            gas_limit=50000,
            chain_id="D",
            nonce=104,
            gas_price=1000000000,
            version=2,
            signature=bytes.fromhex("341a2f3b738fbd20692e3bbd1cb36cb5f4ce9c0a9acc0cf4322269c0fcf34fd6bb59cd94062a9a4730e47f41b1ef3e29b69c6ab2a2a4dca9c9a7724681bc1708")
        )

        invalid_tx = Transaction(
            sender="erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl",
            receiver="erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl",
            gas_limit=50000,
            chain_id="D",
            nonce=77
        )

        transactions = [first_tx, second_tx, invalid_tx]

        expected_hashes = [
            "61b4f2561fc57bfb8b8971ed23cd64259b664bc0404ea7a0449def8ceef24b08",
            "30274b60b5635f981fa89ccfe726a34ca7121caa5d34123021c77a5c64cc9163",
        ]

        num_txs, hashes = self.proxy.send_transactions(transactions)
        assert num_txs == 2
        assert hashes == {"0": f"{expected_hashes[0]}", "1": f"{expected_hashes[1]}"}
