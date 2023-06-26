from typing import Any, Dict

from multiversx_sdk_core import Address

from multiversx_sdk_network_providers.proxy_network_provider import (
    ContractQuery,
    ProxyNetworkProvider,
)


class TestProxy:
    proxy = ProxyNetworkProvider("https://devnet-gateway.multiversx.com")

    def test_get_network_config(self):
        result = self.proxy.get_network_config()

        assert result.chain_id == "D"
        assert result.gas_per_data_byte == 1500
        assert result.round_duration == 6000
        assert result.rounds_per_epoch == 1200
        assert result.min_gas_limit == 50000
        assert result.min_gas_price == 1_000_000_000
        assert result.min_transaction_version == 1
        assert result.top_up_factor == 0.5
        assert result.num_shards_without_meta == 3

    def test_get_network_status(self):
        result = self.proxy.get_network_status()

        assert result.nonce >= 3436532
        assert result.current_round >= 3472246
        assert result.epoch_number >= 2863
        assert result.round_at_epoch_start >= 3471351
        assert result.rounds_passed_in_current_epcoch > 0
        assert result.nonces_passed_in_current_epoch > 0
        assert result.highest_final_nonce >= 3436531
        assert result.nonce_at_epoch_start >= 3435637
        assert result.rounds_per_epoch == 1200

    def test_get_network_gas_configs(self):
        result = self.proxy.get_network_gas_configs()
        built_in_cost = result["gasConfigs"]["builtInCost"]
        meta_system_sc_cost = result["gasConfigs"]["metaSystemSCCost"]

        assert built_in_cost["ESDTTransfer"] == 200000
        assert meta_system_sc_cost["Stake"] == 5000000

    def test_get_account(self):
        address = Address.from_bech32(
            "erd1testnlersh4z0wsv8kjx39me4rmnvjkwu8dsaea7ukdvvc9z396qykv7z7"
        )
        result = self.proxy.get_account(address)

        assert (
            result.address.bech32()
            == "erd1testnlersh4z0wsv8kjx39me4rmnvjkwu8dsaea7ukdvvc9z396qykv7z7"
        )
        assert result.username == ""

    def test_get_fungible_token_of_account(self):
        address = Address.from_bech32(
            "erd1testnlersh4z0wsv8kjx39me4rmnvjkwu8dsaea7ukdvvc9z396qykv7z7"
        )
        result = self.proxy.get_fungible_token_of_account(address, "ABC-10df96")

        assert result.identifier == "ABC-10df96"
        assert result.balance == 50

    def test_get_nonfungible_token_of_account(self):
        address = Address.from_bech32(
            "erd1testnlersh4z0wsv8kjx39me4rmnvjkwu8dsaea7ukdvvc9z396qykv7z7"
        )
        result = self.proxy.get_nonfungible_token_of_account(
            address, "ASDASD-510041", 2
        )

        assert result.balance == 1
        assert result.nonce == 2
        assert result.collection == "ASDASD-510041"
        assert result.identifier == "ASDASD-510041-02"
        assert result.type == ""
        assert result.royalties == 75

    def test_get_transaction_status(self):
        result = self.proxy.get_transaction_status(
            "3f6f03c00ff95e02719dc045e9108ce88bc31a4106396164dcac0efa66229f52"
        )

        assert result.status == "success"

    def test_query_contract(self):
        query = ContractQuery(
            Address.from_bech32(
                "erd1qqqqqqqqqqqqqpgquykqja5c4v33zdmnwglj3jphqwrelzdn396qlc9g33"
            ),
            "getSum",
            0,
            [],
        )
        result = self.proxy.query_contract(query)

        assert len(result.return_data) == 1

    def test_get_definition_of_fungible_token(self):
        result = self.proxy.get_definition_of_fungible_token("ABC-10df96")

        assert result.identifier == "ABC-10df96"
        assert (
            result.owner.bech32()
            == "erd1testnlersh4z0wsv8kjx39me4rmnvjkwu8dsaea7ukdvvc9z396qykv7z7"
        )
        assert result.can_upgrade
        assert not result.can_freeze
        assert result.decimals == 1
        assert result.supply == 5

    def test_get_definition_of_token_collection(self):
        result = self.proxy.get_definition_of_token_collection("ASDASD-510041")

        assert result.collection == "ASDASD-510041"
        assert (
            result.owner.bech32()
            == "erd1testnlersh4z0wsv8kjx39me4rmnvjkwu8dsaea7ukdvvc9z396qykv7z7"
        )
        assert result.type == "NonFungibleESDT"
        assert result.decimals == 0
        assert result.can_freeze
        assert not result.can_pause

    def test_get_transaction(self):
        result = self.proxy.get_transaction(
            "2e6bd2671dbb57f1f1013c89f044359c2465f1514e0ea718583900e43c1931fe"
        )

        assert result.nonce == 829
        assert result.block_nonce == 3777937
        assert result.epoch == 3153
        assert (
            result.hash
            == "2e6bd2671dbb57f1f1013c89f044359c2465f1514e0ea718583900e43c1931fe"
        )
        assert result.is_completed == True
        assert (
            result.sender.bech32()
            == "erd1testnlersh4z0wsv8kjx39me4rmnvjkwu8dsaea7ukdvvc9z396qykv7z7"
        )
        assert result.contract_results.items == []

    def test_get_transaction_with_events(self):
        transaction = self.proxy.get_transaction("c451566a6168e38d2980fcb83d4ea154f78d53f7abf3264dd51c2c7c585671aa")
        assert transaction.logs
        assert transaction.logs.events
        assert len(transaction.logs.events) == 2
        assert len(transaction.logs.events[0].topics) == 4
        assert transaction.logs.events[0].topics[0].hex() == "5745474c442d643763366262"
        assert transaction.logs.events[0].topics[1].hex() == ""
        assert transaction.logs.events[0].topics[2].hex() == "0de0b6b3a7640000"
        assert transaction.logs.events[0].topics[3].hex() == "00000000000000000500e01285f90311fb5925a9623a1dc62eee41fa8c869a0d"

    def test_get_sc_invoking_tx(self):
        result = self.proxy.get_transaction(
            "cd2da63a51fd422c8b69a1b5ebcb9edbbf0eb9750c3fe8e199d39ed5d82000e9"
        )

        assert result.is_completed == True
        assert len(result.contract_results.items) > 0
        assert (
            result.data
            == "issue@54455354@54455354@03e8@00@63616e4d696e74@74727565@63616e4275726e@74727565@63616e4368616e67654f776e6572@74727565@63616e55706772616465@74727565"
        )
        assert sum([r.is_refund for r in result.contract_results.items]) == 1

    def test_get_hyperblock(self):
        result_by_nonce = self.proxy.get_hyperblock(4199287)
        result_by_hash = self.proxy.get_hyperblock(
            "41d75def48fcf965cbadee144bc13382adc486737e9237ba1896db83658661ef"
        )

        assert result_by_nonce.get("hash") == result_by_hash.get("hash")
        assert result_by_nonce.get("nonce") == result_by_hash.get("nonce")
        assert result_by_nonce.get("round") == result_by_hash.get("round")
        assert result_by_nonce.get("epoch") == result_by_hash.get("epoch")
        assert result_by_nonce.get("numTxs") == result_by_hash.get("numTxs")
        assert result_by_nonce.get("timestamp") == result_by_hash.get("timestamp")

    def test_send_transaction(self):
        transaction = DummyTransaction(
            {
                "nonce": 42,
                "value": "1",
                "receiver": "erd1testnlersh4z0wsv8kjx39me4rmnvjkwu8dsaea7ukdvvc9z396qykv7z7",
                "sender": "erd15x2panzqvfxul2lvstfrmdcl5t4frnsylfrhng8uunwdssxw4y9succ9sq",
                "gasPrice": 1000000000,
                "gasLimit": 50000,
                "chainID": "D",
                "version": 1,
                "signature": "c8eb539e486db7d703d8c70cab3b7679113f77c4685d8fcc94db027ceacc6b8605115034355386dffd7aa12e63dbefa03251a2f1b1d971f52250187298d12900",
            }
        )

        expected_hash = (
            "6e2fa63ea02937f00d7549f3e4eb9af241e4ac13027aa65a5300816163626c01"
        )

        assert self.proxy.send_transaction(transaction) == expected_hash

    def test_send_transactions(self):
        first_tx = DummyTransaction(
            {
                "nonce": 42,
                "value": "1",
                "receiver": "erd1testnlersh4z0wsv8kjx39me4rmnvjkwu8dsaea7ukdvvc9z396qykv7z7",
                "sender": "erd15x2panzqvfxul2lvstfrmdcl5t4frnsylfrhng8uunwdssxw4y9succ9sq",
                "gasPrice": 1000000000,
                "gasLimit": 50000,
                "chainID": "D",
                "version": 1,
                "signature": "c8eb539e486db7d703d8c70cab3b7679113f77c4685d8fcc94db027ceacc6b8605115034355386dffd7aa12e63dbefa03251a2f1b1d971f52250187298d12900",
            }
        )

        second_tx = DummyTransaction(
            {
                "nonce": 43,
                "value": "1",
                "receiver": "erd1testnlersh4z0wsv8kjx39me4rmnvjkwu8dsaea7ukdvvc9z396qykv7z7",
                "sender": "erd15x2panzqvfxul2lvstfrmdcl5t4frnsylfrhng8uunwdssxw4y9succ9sq",
                "gasPrice": 1000000000,
                "gasLimit": 50000,
                "chainID": "D",
                "version": 1,
                "signature": "9c4c22d0ae1b5a10c39583a5ab9020b00b27aa69d4ac8ab4922620dbf0df4036ed890f9946d38a9d0c85d6ac485c0d9b2eac0005e752f249fd0ad863b0471d02",
            }
        )

        third_tx = DummyTransaction({"nonce": 44})

        transactions = [first_tx, second_tx, third_tx]

        expected_hashes = [
            "6e2fa63ea02937f00d7549f3e4eb9af241e4ac13027aa65a5300816163626c01",
            "37d7e84313a5baea2a61c6ab10bb29b52bc54f7ac9e3918a9faeb1e08f42081c",
        ]

        assert self.proxy.send_transactions(transactions) == (
            2,
            {"0": f"{expected_hashes[0]}", "1": f"{expected_hashes[1]}"},
        )


class DummyTransaction:
    def __init__(self, transaction: Dict[str, Any]) -> None:
        self.transaction = transaction

    def to_dictionary(self) -> Dict[str, Any]:
        return self.transaction
