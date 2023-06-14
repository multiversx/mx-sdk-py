from multiversx_sdk_core.address import Address
from multiversx_sdk_core.constants import DELEGATION_MANAGER_SC_ADDRESS
from multiversx_sdk_core.transaction_builders.delegation_factory import (
    DelegationFactory, ICreateNewDelegationContractArgs,
    MetaChainSystemSCsCost)


class Config:
    def __init__(self) -> None:
        self.chain_id = "D"
        self.min_gas_price = 1000000000
        self.min_gas_limit = 50000
        self.gas_limit_per_byte = 1500


class NewDelegationContractArgs(ICreateNewDelegationContractArgs):
    def __init__(self) -> None:
        self.sender = Address.from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        self.receiver = Address.from_bech32(DELEGATION_MANAGER_SC_ADDRESS)
        self.transaction_nonce = 777
        self.value = 1250000000000000000000
        self.total_delegation_cap = 5000000000000000000000
        self.service_fee = 10
        self.data = None
        self.gas_limit = None
        self.gas_price = None


class TestDelagationFactory:
    config = Config()
    args = NewDelegationContractArgs()
    factory = DelegationFactory(config)

    def test_compute_data_field(self):
        data = self.factory._prepare_data_for_create_new_delegation_contract(self.args)
        assert str(data) == "createNewDelegationContract@010f0cf064dd59200000@0a"

    def test_compute_gas_limit(self):
        data = self.factory._prepare_data_for_create_new_delegation_contract(self.args)
        gas_limit = self.factory._estimate_system_sc_call(data.length(), MetaChainSystemSCsCost.DELEGATION_MANAGER_OPS, 2)
        assert gas_limit == 100126500

    def test_create_new_delegation_contract(self):
        transaction = self.factory.create_new_delegation_contract(self.args)

        assert transaction.sender.bech32() == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver.bech32() == DELEGATION_MANAGER_SC_ADDRESS
        assert transaction.chainID == "D"
        assert transaction.nonce == 777
        assert transaction.signature == b""
