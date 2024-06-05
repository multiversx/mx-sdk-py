import base64

import pytest

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.network_providers.api_network_provider import \
    ApiNetworkProvider
from multiversx_sdk.network_providers.errors import GenericError
from multiversx_sdk.network_providers.interface import IPagination
from multiversx_sdk.network_providers.proxy_network_provider import \
    ContractQuery


class Pagination(IPagination):
    def __init__(self, start: int, size: int) -> None:
        self.start = start
        self.size = size

    def get_start(self) -> int:
        return self.start

    def get_size(self) -> int:
        return self.size


@pytest.mark.networkInteraction
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
        assert result.rounds_per_epoch == 2400
        assert result.refresh_rate == 6000
        assert result.epoch
        assert result.rounds_passed
        assert result.transactions
        assert result.accounts

    def test_get_network_gas_configs(self):
        result = self.api.get_network_gas_configs()
        built_in_cost = result["gasConfigs"]["builtInCost"]
        meta_system_sc_cost = result["gasConfigs"]["metaSystemSCCost"]

        assert built_in_cost["ESDTTransfer"] == 200000
        assert meta_system_sc_cost["Stake"] == 5000000

    def test_get_account(self):
        address = Address.new_from_bech32('erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl')
        result = self.api.get_account(address)

        assert result.address.to_bech32() == address.to_bech32()
        assert result.username == ''
        assert len(result.code_hash) == 0
        assert len(base64.b64decode(result.root_hash)) == 32

        address = Address.new_from_bech32('erd1qqqqqqqqqqqqqpgqws44xjx2t056nn79fn29q0rjwfrd3m43396ql35kxy')
        result = self.api.get_account(address)

        assert result.address.to_bech32() == address.to_bech32()
        assert result.username == ''
        assert len(base64.b64decode(result.code_hash)) == 32
        assert len(base64.b64decode(result.root_hash)) == 32

    def test_get_generic_with_bad_address(self):
        with pytest.raises(GenericError, match='a bech32 address is expected'):
            url = 'accounts/erd1bad'
            self.api.do_get_generic(url)

    def test_get_fungible_token_of_account(self):
        address = Address.new_from_bech32('erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl')
        result = self.api.get_fungible_token_of_account(address, "TEST-ff155e")
        assert result.identifier == "TEST-ff155e"

    def test_get_nonfungible_token_of_account(self):
        address = Address.new_from_bech32('erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl')
        result = self.api.get_nonfungible_token_of_account(address, "NFTEST-ec88b8", 1)

        assert result.balance == 0
        assert result.nonce == 1
        assert result.collection == "NFTEST-ec88b8"
        assert result.identifier == "NFTEST-ec88b8-01"
        assert result.type == 'NonFungibleESDT'
        assert result.royalties == 25

    def test_get_meta_esdt(self):
        adr = Address.new_from_bech32('erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl')
        result = self.api.get_nonfungible_token_of_account(adr, 'METATEST-ebeb7e', 1)

        assert result.balance != 0
        assert result.nonce == 1
        assert result.identifier == 'METATEST-ebeb7e-01'
        assert result.decimals == 6

    def test_get_transaction(self):
        result = self.api.get_transaction('9d47c4b4669cbcaa26f5dec79902dd20e55a0aa5f4b92454a74e7dbd0183ad6c')

        assert result.hash == '9d47c4b4669cbcaa26f5dec79902dd20e55a0aa5f4b92454a74e7dbd0183ad6c'
        assert result.nonce == 0
        assert result.is_completed
        assert result.sender.to_bech32() == 'erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2'
        assert result.receiver.to_bech32() == 'erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl'
        assert result.value == '5000000000000000000'
        assert str(result.status) == "success"

    def test_get_account_transactions(self):
        address = Address.new_from_bech32('erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl')
        pagination = Pagination(0, 2)

        result = self.api.get_account_transactions(address, pagination)

        assert len(result) == 2

    def test_get_trasactions(self):
        hashes = ["9d47c4b4669cbcaa26f5dec79902dd20e55a0aa5f4b92454a74e7dbd0183ad6c", "6fe05e4ca01d42c96ae5182978a77fe49f26bcc14aac95ad4f19618173f86ddb"]
        result = self.api.get_bunch_of_transactions(hashes)

        assert len(result) == 2
        assert result[0].status.is_successful()
        assert result[1].status.is_successful()

    def test_get_transaction_with_events(self):
        transaction = self.api.get_transaction("6fe05e4ca01d42c96ae5182978a77fe49f26bcc14aac95ad4f19618173f86ddb")
        assert transaction.logs
        assert transaction.logs.events
        assert len(transaction.logs.events) == 2
        assert len(transaction.logs.events[0].topics) == 8
        assert transaction.logs.events[0].topics[0].hex() == "544553542d666631353565"
        assert transaction.logs.events[0].topics[1].hex() == ""
        assert transaction.logs.events[0].topics[2].hex() == "63616e4368616e67654f776e6572"

    def test_get_transactions_in_mempool_for_account(self):
        address = Address.new_from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        result = self.api.get_transactions_in_mempool_for_account(address)
        assert len(result) == 0

    def test_get_sc_invoking_tx(self):
        result = self.api.get_transaction('6fe05e4ca01d42c96ae5182978a77fe49f26bcc14aac95ad4f19618173f86ddb')

        assert result.is_completed is True
        assert len(result.contract_results.items) > 0
        assert result.data == 'issue@54455354546f6b656e@54455354@016345785d8a0000@06@63616e4368616e67654f776e6572@74727565@63616e55706772616465@74727565@63616e4164645370656369616c526f6c6573@74727565'

    def test_get_transaction_status(self):
        result = self.api.get_transaction_status('6fe05e4ca01d42c96ae5182978a77fe49f26bcc14aac95ad4f19618173f86ddb')
        assert result.status == 'success'

    def test_query_contract(self):
        query = ContractQuery(Address.new_from_bech32('erd1qqqqqqqqqqqqqpgqqy34h7he2ya6qcagqre7ur7cc65vt0mxrc8qnudkr4'),
                              'getSum', 0, [])
        result = self.api.query_contract(query)
        assert len(result.return_data) == 1

    def test_get_definition_of_fungible_token(self):
        result = self.api.get_definition_of_fungible_token('TEST-ff155e')

        assert result.identifier == 'TEST-ff155e'
        assert result.owner.to_bech32() == 'erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl'
        assert result.can_upgrade
        assert not result.can_freeze
        assert result.decimals == 6
        assert result.supply == 100000000000

    def test_get_definition_of_token_collection(self):
        result = self.api.get_definition_of_token_collection('NFTEST-ec88b8')

        assert result.collection == 'NFTEST-ec88b8'
        assert result.owner.to_bech32() == 'erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl'
        assert result.type == 'NonFungibleESDT'
        assert result.decimals == 0
        assert not result.can_freeze
        assert not result.can_pause

    def test_get_non_fungible_token(self):
        result = self.api.get_non_fungible_token('NFTEST-ec88b8', 1)

        assert result.type == 'NonFungibleESDT'
        assert result.nonce == 1
        assert result.identifier == 'NFTEST-ec88b8-01'
        assert result.collection == 'NFTEST-ec88b8'
        assert result.creator.to_bech32() == 'erd1487vz5m4zpxjyqw4flwa3xhnkzg4yrr3mkzf5sf0zgt94hjprc8qazcccl'
        assert result.balance == 0
        assert result.royalties == 25
        assert result.timestamp == 1699019354

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
        expected_hash = (
            "fc914860c1d137ed8baa602e561381f97c7bad80d150c5bf90760d3cfd3a4cea"
        )

        assert self.api.send_transaction(transaction) == expected_hash
