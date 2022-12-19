from erdpy_core import Address

from erdpy_network.proxy_network_provider import (ContractQuery,
                                                  ProxyNetworkProvider)


class TestProxy:
    proxy = ProxyNetworkProvider('https://devnet-gateway.elrond.com')

    def test_get_network_config(self):
        result = self.proxy.get_network_config()

        assert result.chain_id == 'D'
        assert result.gas_per_data_byte == 1500
        assert result.round_duration == 6000
        assert result.rounds_per_epoch == 1200
        assert result.min_gas_limit == 50000
        assert result.min_gas_price == 1_000_000_000
        assert result.min_transaction_version == 1
        assert result.top_up_factor == 0.5

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

    def test_get_account(self):
        address = Address.from_bech32('erd1testnlersh4z0wsv8kjx39me4rmnvjkwu8dsaea7ukdvvc9z396qykv7z7')
        result = self.proxy.get_account(address)

        assert result.address.bech32() == 'erd1testnlersh4z0wsv8kjx39me4rmnvjkwu8dsaea7ukdvvc9z396qykv7z7'
        assert result.username == ''

    def test_get_fungible_token_of_account(self):
        address = Address.from_bech32('erd1testnlersh4z0wsv8kjx39me4rmnvjkwu8dsaea7ukdvvc9z396qykv7z7')
        result = self.proxy.get_fungible_token_of_account(address, 'ABC-10df96')

        assert result.identifier == 'ABC-10df96'
        assert result.balance == 50

    def test_get_nonfungible_token_of_account(self):
        address = Address.from_bech32('erd1testnlersh4z0wsv8kjx39me4rmnvjkwu8dsaea7ukdvvc9z396qykv7z7')
        result = self.proxy.get_nonfungible_token_of_account(address, 'ASDASD-510041', 2)

        assert result.balance == 1
        assert result.nonce == 2
        assert result.collection == 'ASDASD-510041'
        assert result.identifier == 'ASDASD-510041-02'
        assert result.type == ''
        assert result.royalties == 75

    def test_get_transaction_status(self):
        result = self.proxy.get_transaction_status('2cb813be9d5e5040abb2522da75fa5c8d94f72caa510ff51d7525659f398298b')

        assert result.status == 'success'

    def test_query_contract(self):
        query = ContractQuery(Address.from_bech32('erd1qqqqqqqqqqqqqpgquykqja5c4v33zdmnwglj3jphqwrelzdn396qlc9g33'),
                              'getSum', 0, [])
        result = self.proxy.query_contract(query)

        assert len(result.return_data) == 1

    def test_get_definition_of_fungible_token(self):
        result = self.proxy.get_definition_of_fungible_token('ABC-10df96')

        assert result.identifier == 'ABC-10df96'
        assert result.owner.bech32() == 'erd1testnlersh4z0wsv8kjx39me4rmnvjkwu8dsaea7ukdvvc9z396qykv7z7'
        assert result.can_upgrade
        assert not result.can_freeze
        assert result.decimals == 1
        assert result.supply == 5

    def test_get_definition_of_token_collection(self):
        result = self.proxy.get_definition_of_token_collection('ASDASD-510041')

        assert result.collection == 'ASDASD-510041'
        assert result.owner.bech32() == 'erd1testnlersh4z0wsv8kjx39me4rmnvjkwu8dsaea7ukdvvc9z396qykv7z7'
        assert result.type == 'NonFungibleESDT'
        assert result.decimals == 0
        assert result.can_freeze
        assert not result.can_pause

    def test_get_transaction(self):
        result = self.proxy.get_transaction('2cb813be9d5e5040abb2522da75fa5c8d94f72caa510ff51d7525659f398298b')

        assert result.nonce == 828
        assert result.block_nonce == 3047400
        assert result.epoch == 2540
        assert result.hash == '2cb813be9d5e5040abb2522da75fa5c8d94f72caa510ff51d7525659f398298b'
        assert result.is_completed == True
        assert result.sender.bech32() == 'erd1testnlersh4z0wsv8kjx39me4rmnvjkwu8dsaea7ukdvvc9z396qykv7z7'
        assert result.contract_results.items == []

    def test_get_sc_invoking_tx(self):
        result = self.proxy.get_transaction('cd2da63a51fd422c8b69a1b5ebcb9edbbf0eb9750c3fe8e199d39ed5d82000e9')

        assert result.is_completed == True
        assert len(result.contract_results.items) > 0
        assert result.data == 'issue@54455354@54455354@03e8@00@63616e4d696e74@74727565@63616e4275726e@74727565@63616e4368616e67654f776e6572@74727565@63616e55706772616465@74727565'
