import pytest
from typing import Any, Dict

from multiversx_sdk_core import Address
from multiversx_sdk_network_providers.api_network_provider import ApiNetworkProvider
from multiversx_sdk_network_providers.errors import GenericError
from multiversx_sdk_network_providers.proxy_network_provider import ContractQuery
from multiversx_sdk_network_providers.interface import IPagination


class Pagination(IPagination):
    def __init__(self, start: int, size: int) -> None:
        self.start = start
        self.size = size

    def get_start(self) -> int:
        return self.start

    def get_size(self) -> int:
        return self.size


class TestApi:
    api = ApiNetworkProvider('https://devnet-api.multiversx.com')

    def test_get_network_stake_statistic(self):
        result = self.api.get_network_stake_statistics()

        assert result.total_validators > 0
        assert result.active_validators > 0
        assert result.total_staked > 0

    def test_get_general_statistics(self):
        result = self.api.get_network_general_statistics()

        assert result.shards == 3
        assert result.rounds_per_epoch == 1200
        assert result.refresh_rate == 6000
        assert result.epoch >= 2864
        assert result.rounds_passed >= 0
        assert result.transactions >= 4330650
        assert result.accounts >= 92270

    def test_get_network_gas_configs(self):
        result = self.api.get_network_gas_configs()
        built_in_cost = result["gasConfigs"]["builtInCost"]
        meta_system_sc_cost = result["gasConfigs"]["metaSystemSCCost"]

        assert built_in_cost["ESDTTransfer"] == 200000
        assert meta_system_sc_cost["Stake"] == 5000000

    def test_get_account(self):
        address = Address.from_bech32('erd1testnlersh4z0wsv8kjx39me4rmnvjkwu8dsaea7ukdvvc9z396qykv7z7')
        result = self.api.get_account(address)

        assert result.address.bech32() == 'erd1testnlersh4z0wsv8kjx39me4rmnvjkwu8dsaea7ukdvvc9z396qykv7z7'
        assert result.username == ''

    def test_get_generic_with_bad_address(self):
        with pytest.raises(GenericError, match='a bech32 address is expected'):
            url = 'accounts/erd1bad'
            self.api.do_get_generic(url)

    def test_get_fungible_token_of_account(self):
        address = Address.from_bech32('erd1testnlersh4z0wsv8kjx39me4rmnvjkwu8dsaea7ukdvvc9z396qykv7z7')
        result = self.api.get_fungible_token_of_account(address, 'ABC-10df96')

        assert result.identifier == 'ABC-10df96'

    def test_get_nonfungible_token_of_account(self):
        address = Address.from_bech32('erd1testnlersh4z0wsv8kjx39me4rmnvjkwu8dsaea7ukdvvc9z396qykv7z7')
        result = self.api.get_nonfungible_token_of_account(address, 'ASDASD-510041', 2)

        assert result.balance == 0
        assert result.nonce == 2
        assert result.collection == 'ASDASD-510041'
        assert result.identifier == 'ASDASD-510041-02'
        assert result.type == 'NonFungibleESDT'
        assert result.royalties == 75

    def test_get_meta_esdt(self):
        adr = Address.from_bech32('erd1dk5urklhptgjp69k684wzapjxdp40fu0a3jn39rtcc78wxhewkyscp53au')
        result = self.api.get_nonfungible_token_of_account(adr, 'EGLDRIDEF-9cf6f6', 4)

        assert result.balance != 0
        assert result.nonce == 4
        assert result.identifier == 'EGLDRIDEF-9cf6f6-04'
        assert result.decimals == 18

    def test_get_transaction(self):
        result = self.api.get_transaction('2cb813be9d5e5040abb2522da75fa5c8d94f72caa510ff51d7525659f398298b')

        assert result.hash == '2cb813be9d5e5040abb2522da75fa5c8d94f72caa510ff51d7525659f398298b'
        assert result.nonce == 828
        assert result.is_completed
        assert result.sender.bech32() == 'erd1testnlersh4z0wsv8kjx39me4rmnvjkwu8dsaea7ukdvvc9z396qykv7z7'
        assert result.receiver.bech32() == 'erd1c8tnzykaj7lhrd5cy6jap533afr4dqu7uqcdm6qv4wuwly9lcsqqm9ll4f'
        assert result.value == '10000000000000000000'

    def test_get_account_transactions(self):
        address = Address.from_bech32('erd1testnlersh4z0wsv8kjx39me4rmnvjkwu8dsaea7ukdvvc9z396qykv7z7')
        pagination = Pagination(0, 2)

        result = self.api.get_account_transactions(address, pagination)

        assert len(result) == 2

    def test_get_trasactions(self):
        hashes = ["19de07b20873c6b9c77d3666eab532329f16f55a62b9fc961e52e4e0d57835d6", "8e43a0fb73bb97d1cacbca7de6d90ffacd9b7e10773f4ba37c6b8adbad6461dc"]
        result = self.api.get_bunch_of_transactions(hashes)

        assert len(result) == 2
        assert result[0].status.is_failed()
        assert result[1].status.is_successful()

    def test_get_transaction_with_events(self):
        transaction = self.api.get_transaction("c451566a6168e38d2980fcb83d4ea154f78d53f7abf3264dd51c2c7c585671aa")
        assert transaction.logs
        assert transaction.logs.events
        assert len(transaction.logs.events) == 2
        assert len(transaction.logs.events[0].topics) == 4
        assert transaction.logs.events[0].topics[0].hex() == "5745474c442d643763366262"
        assert transaction.logs.events[0].topics[1].hex() == ""
        assert transaction.logs.events[0].topics[2].hex() == "0de0b6b3a7640000"
        assert transaction.logs.events[0].topics[3].hex() == "00000000000000000500e01285f90311fb5925a9623a1dc62eee41fa8c869a0d"

    def test_get_transactions_in_mempool_for_account(self):
        address = Address.from_bech32("erd1testnlersh4z0wsv8kjx39me4rmnvjkwu8dsaea7ukdvvc9z396qykv7z7")
        result = self.api.get_transactions_in_mempool_for_account(address)

        assert len(result) == 0

    def test_get_sc_invoking_tx(self):
        result = self.api.get_transaction('cd2da63a51fd422c8b69a1b5ebcb9edbbf0eb9750c3fe8e199d39ed5d82000e9')

        assert result.is_completed == True
        assert len(result.contract_results.items) > 0
        assert result.data == 'issue@54455354@54455354@03e8@00@63616e4d696e74@74727565@63616e4275726e@74727565@63616e4368616e67654f776e6572@74727565@63616e55706772616465@74727565'

    def test_get_transaction_status(self):
        result = self.api.get_transaction_status('2cb813be9d5e5040abb2522da75fa5c8d94f72caa510ff51d7525659f398298b')

        assert result.status == 'success'

    def test_query_contract(self):
        query = ContractQuery(Address.from_bech32('erd1qqqqqqqqqqqqqpgquykqja5c4v33zdmnwglj3jphqwrelzdn396qlc9g33'),
                              'getSum', 0, [])
        result = self.api.query_contract(query)

        assert len(result.return_data) == 1

    def test_get_definition_of_fungible_token(self):
        result = self.api.get_definition_of_fungible_token('ABC-10df96')

        assert result.identifier == 'ABC-10df96'
        assert result.owner.bech32() == 'erd1testnlersh4z0wsv8kjx39me4rmnvjkwu8dsaea7ukdvvc9z396qykv7z7'
        assert result.can_upgrade
        assert not result.can_freeze
        assert result.decimals == 1
        assert result.supply == 5

    def test_get_definition_of_token_collection(self):
        result = self.api.get_definition_of_token_collection('ASDASD-510041')

        assert result.collection == 'ASDASD-510041'
        assert result.owner.bech32() == 'erd1testnlersh4z0wsv8kjx39me4rmnvjkwu8dsaea7ukdvvc9z396qykv7z7'
        assert result.type == 'NonFungibleESDT'
        assert result.decimals == 0
        assert result.can_freeze
        assert not result.can_pause

    def test_get_non_fungible_token(self):
        result = self.api.get_non_fungible_token('ASDASD-510041', 2)

        assert result.type == 'NonFungibleESDT'
        assert result.nonce == 2
        assert result.identifier == 'ASDASD-510041-02'
        assert result.collection == 'ASDASD-510041'
        assert result.creator.bech32() == 'erd1testnlersh4z0wsv8kjx39me4rmnvjkwu8dsaea7ukdvvc9z396qykv7z7'
        assert result.balance == 0
        assert result.royalties != 0
        assert result.timestamp != 0

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

        assert self.api.send_transaction(transaction) == expected_hash


class DummyTransaction:
    def __init__(self, transaction: Dict[str, Any]) -> None:
        self.transaction = transaction

    def to_dictionary(self) -> Dict[str, Any]:
        return self.transaction
