from multiversx_sdk_wallet import ValidatorSecretKey, ValidatorSigner

from multiversx_sdk_core.address import Address
from multiversx_sdk_core.constants import DELEGATION_MANAGER_SC_ADDRESS
from multiversx_sdk_core.messages import ArbitraryMessage
from multiversx_sdk_core.transaction_builders.delegation_factory import (
    DelegationFactory, IAddNodesArgs, ICreateNewDelegationContractArgs,
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


class AddNodesArgs(IAddNodesArgs):
    def __init__(self) -> None:
        self.sender = Address.from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        self.delegation_contract = Address.from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        validator_secret_key = ValidatorSecretKey.from_string("7cff99bd671502db7d15bc8abc0c9a804fb925406fbdd50f1e4c17a4cd774247")
        validator_signer = ValidatorSigner(validator_secret_key)

        message = ArbitraryMessage(bytes.fromhex(self.delegation_contract.hex()))
        signed_message = validator_signer.sign(message)
        public_key = validator_secret_key.generate_public_key()

        self.public_keys = [public_key]
        self.signed_messages = [signed_message]

        self.transaction_nonce = 777
        self.data = None
        self.gas_limit = None
        self.gas_price = None
        self.value = None


class TestDelagationFactory:
    config = Config()
    factory = DelegationFactory(config)

    def test_compute_data_field_for_new_delegation_contract(self):
        data = self.factory._prepare_data_for_create_new_delegation_contract(NewDelegationContractArgs())
        assert str(data) == "createNewDelegationContract@010f0cf064dd59200000@0a"

    def test_compute_gas_limit_for_new_delegation_contract(self):
        data = self.factory._prepare_data_for_create_new_delegation_contract(NewDelegationContractArgs())
        gas_limit = self.factory._estimate_system_sc_call(data.length(), MetaChainSystemSCsCost.DELEGATION_MANAGER_OPS, 2)
        assert gas_limit == 100126500

    def test_create_new_delegation_contract(self):
        transaction = self.factory.create_new_delegation_contract(NewDelegationContractArgs())

        assert transaction.sender.bech32() == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver.bech32() == DELEGATION_MANAGER_SC_ADDRESS
        assert transaction.chainID == "D"
        assert transaction.nonce == 777
        assert transaction.signature == b""
        assert str(transaction.data) == "createNewDelegationContract@010f0cf064dd59200000@0a"

    def test_compute_data_field_for_add_nodes(self):
        data = self.factory._prepare_data_for_add_nodes(AddNodesArgs())
        assert str(data) == "addNodes@e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208@81109fa1c8d3dc7b6c2d6e65206cc0bc1a83c9b2d1eb91a601d66ad32def430827d5eb52917bd2b0d04ce195738db216"

    def test_add_nodes(self):
        transaction = self.factory.add_nodes(AddNodesArgs())

        assert transaction.sender.bech32() == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver.bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.chainID == "D"
        assert transaction.nonce == 777
        assert transaction.signature == b""
        assert str(transaction.data) == "addNodes@e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208@81109fa1c8d3dc7b6c2d6e65206cc0bc1a83c9b2d1eb91a601d66ad32def430827d5eb52917bd2b0d04ce195738db216"
