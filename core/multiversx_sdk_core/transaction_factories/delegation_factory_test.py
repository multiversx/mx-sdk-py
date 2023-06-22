from multiversx_sdk_wallet import ValidatorSecretKey, ValidatorSigner

from multiversx_sdk_core.address import Address
from multiversx_sdk_core.constants import DELEGATION_MANAGER_SC_ADDRESS
from multiversx_sdk_core.messages import ArbitraryMessage
from multiversx_sdk_core.transaction_factories.delegation_factory import \
    DelegationFactory
from multiversx_sdk_core.transaction_factories.transaction_factory_config import \
    TransactionFactoryConfig


class TestDelegationFactory:
    config = TransactionFactoryConfig("D")
    factory = DelegationFactory(config)

    def test_create_new_delegation_contract(self):
        transaction = self.factory.create_new_delegation_contract(
            sender=Address.from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"),
            receiver=Address.from_bech32(DELEGATION_MANAGER_SC_ADDRESS),
            transaction_nonce=777,
            value=1250000000000000000000,
            total_delegation_cap=5000000000000000000000,
            service_fee=10,
            gas_limit=None,
            gas_price=None,
        )

        assert transaction.sender.bech32() == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver.bech32() == DELEGATION_MANAGER_SC_ADDRESS
        assert transaction.chainID == "D"
        assert transaction.nonce == 777
        assert transaction.signature == b""
        assert str(transaction.data) == "createNewDelegationContract@010f0cf064dd59200000@0a"
        assert transaction.gas_limit == 60126500

    def test_add_nodes(self):
        sender = Address.from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        validator_secret_key = ValidatorSecretKey.from_string("7cff99bd671502db7d15bc8abc0c9a804fb925406fbdd50f1e4c17a4cd774247")
        validator_signer = ValidatorSigner(validator_secret_key)

        message = ArbitraryMessage(bytes.fromhex(delegation_contract.hex()))
        signed_message = validator_signer.sign(message)
        public_key = validator_secret_key.generate_public_key()

        public_keys = [public_key]
        signed_messages = [signed_message]

        transaction_nonce = 777
        gas_limit = None
        gas_price = None
        value = None

        transaction = self.factory.add_nodes(
            sender=sender,
            delegation_contract=delegation_contract,
            public_keys=public_keys,
            signed_messages=signed_messages,
            value=value,
            transaction_nonce=transaction_nonce,
            gas_price=gas_price,
            gas_limit=gas_limit
        )

        assert transaction.sender.bech32() == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver.bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.chainID == "D"
        assert transaction.nonce == 777
        assert transaction.signature == b""
        assert str(transaction.data) == "addNodes@e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208@81109fa1c8d3dc7b6c2d6e65206cc0bc1a83c9b2d1eb91a601d66ad32def430827d5eb52917bd2b0d04ce195738db216"

    def test_remove_nodes(self):
        sender = Address.from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        public_keys = ["notavalidblskeyhexencoded"]

        transaction_nonce = 777
        gas_limit = None
        gas_price = None
        value = None

        transaction = self.factory.remove_nodes(
            sender=sender,
            delegation_contract=delegation_contract,
            bls_keys=public_keys,
            value=value,
            transaction_nonce=transaction_nonce,
            gas_price=gas_price,
            gas_limit=gas_limit
        )

        assert transaction.sender.bech32() == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver.bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.chainID == "D"
        assert transaction.nonce == 777
        assert transaction.signature == b""
        assert str(transaction.data) == "removeNodes@notavalidblskeyhexencoded"

    def test_stake_nodes(self):
        sender = Address.from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        public_keys = ["notavalidblskeyhexencoded"]

        transaction_nonce = 777
        gas_limit = None
        gas_price = None
        value = None

        transaction = self.factory.stake_nodes(
            sender=sender,
            delegation_contract=delegation_contract,
            bls_keys=public_keys,
            value=value,
            transaction_nonce=transaction_nonce,
            gas_price=gas_price,
            gas_limit=gas_limit
        )

        assert transaction.sender.bech32() == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver.bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.chainID == "D"
        assert transaction.nonce == 777
        assert transaction.signature == b""
        assert str(transaction.data) == "stakeNodes@notavalidblskeyhexencoded"

    def test_unbond_nodes(self):
        sender = Address.from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        public_keys = ["notavalidblskeyhexencoded"]

        transaction_nonce = 777
        gas_limit = None
        gas_price = None
        value = None

        transaction = self.factory.unbond_nodes(
            sender=sender,
            delegation_contract=delegation_contract,
            bls_keys=public_keys,
            value=value,
            transaction_nonce=transaction_nonce,
            gas_price=gas_price,
            gas_limit=gas_limit
        )

        assert transaction.sender.bech32() == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver.bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.chainID == "D"
        assert transaction.nonce == 777
        assert transaction.signature == b""
        assert str(transaction.data) == "unBondNodes@notavalidblskeyhexencoded"

    def test_unstake_nodes(self):
        sender = Address.from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        public_keys = ["notavalidblskeyhexencoded"]

        transaction_nonce = 777
        gas_limit = None
        gas_price = None
        value = None

        transaction = self.factory.unstake_nodes(
            sender=sender,
            delegation_contract=delegation_contract,
            bls_keys=public_keys,
            value=value,
            transaction_nonce=transaction_nonce,
            gas_price=gas_price,
            gas_limit=gas_limit
        )

        assert transaction.sender.bech32() == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver.bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.chainID == "D"
        assert transaction.nonce == 777
        assert transaction.signature == b""
        assert str(transaction.data) == "unStakeNodes@notavalidblskeyhexencoded"

    def test_unjail_nodes(self):
        sender = Address.from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        public_keys = ["notavalidblskeyhexencoded"]

        transaction_nonce = 777
        gas_limit = None
        gas_price = None
        value = None

        transaction = self.factory.unjail_nodes(
            sender=sender,
            delegation_contract=delegation_contract,
            bls_keys=public_keys,
            value=value,
            transaction_nonce=transaction_nonce,
            gas_price=gas_price,
            gas_limit=gas_limit
        )

        assert transaction.sender.bech32() == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver.bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.chainID == "D"
        assert transaction.nonce == 777
        assert transaction.signature == b""
        assert str(transaction.data) == "unJailNodes@notavalidblskeyhexencoded"

    def test_change_service_fee(self):
        sender = Address.from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        transaction_nonce = 777
        gas_limit = None
        gas_price = None
        value = None

        transaction = self.factory.change_service_fee(
            sender=sender,
            delegation_contract=delegation_contract,
            service_fee=10,
            value=value,
            transaction_nonce=transaction_nonce,
            gas_price=gas_price,
            gas_limit=gas_limit
        )

        assert transaction.sender.bech32() == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver.bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.chainID == "D"
        assert transaction.nonce == 777
        assert transaction.signature == b""
        assert str(transaction.data) == "changeServiceFee@0a"

    def test_modify_delegation_cap(self):
        sender = Address.from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        transaction_nonce = 777
        gas_limit = None
        gas_price = None
        value = None

        transaction = self.factory.modify_delegation_cap(
            sender=sender,
            delegation_contract=delegation_contract,
            delegation_cap=5000000000000000000000,
            value=value,
            transaction_nonce=transaction_nonce,
            gas_price=gas_price,
            gas_limit=gas_limit
        )

        assert transaction.sender.bech32() == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver.bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.chainID == "D"
        assert transaction.nonce == 777
        assert transaction.signature == b""
        assert str(transaction.data) == "modifyTotalDelegationCap@010f0cf064dd59200000"

    def test_set_automatic_activation(self):
        sender = Address.from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        transaction_nonce = 777
        gas_limit = None
        gas_price = None
        value = None

        transaction = self.factory.set_automatic_activation(
            sender=sender,
            delegation_contract=delegation_contract,
            value=value,
            transaction_nonce=transaction_nonce,
            gas_price=gas_price,
            gas_limit=gas_limit
        )

        assert transaction.sender.bech32() == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver.bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.chainID == "D"
        assert transaction.nonce == 777
        assert transaction.signature == b""
        assert str(transaction.data) == "setAutomaticActivation@74727565"

    def test_unset_automatic_activation(self):
        sender = Address.from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        transaction_nonce = 777
        gas_limit = None
        gas_price = None
        value = None

        transaction = self.factory.unset_automatic_activation(
            sender=sender,
            delegation_contract=delegation_contract,
            value=value,
            transaction_nonce=transaction_nonce,
            gas_price=gas_price,
            gas_limit=gas_limit
        )

        assert transaction.sender.bech32() == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver.bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.chainID == "D"
        assert transaction.nonce == 777
        assert transaction.signature == b""
        assert str(transaction.data) == "setAutomaticActivation@66616c7365"

    def test_set_redelegate_cap(self):
        sender = Address.from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        transaction_nonce = 777
        gas_limit = None
        gas_price = None
        value = None

        transaction = self.factory.set_redelegate_cap(
            sender=sender,
            delegation_contract=delegation_contract,
            value=value,
            transaction_nonce=transaction_nonce,
            gas_price=gas_price,
            gas_limit=gas_limit
        )

        assert transaction.sender.bech32() == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver.bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.chainID == "D"
        assert transaction.nonce == 777
        assert transaction.signature == b""
        assert str(transaction.data) == "setCheckCapOnReDelegateRewards@74727565"

    def test_unset_redelegate_cap(self):
        sender = Address.from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        transaction_nonce = 777
        gas_limit = None
        gas_price = None
        value = None

        transaction = self.factory.unset_redelegate_cap(
            sender=sender,
            delegation_contract=delegation_contract,
            value=value,
            transaction_nonce=transaction_nonce,
            gas_price=gas_price,
            gas_limit=gas_limit
        )

        assert transaction.sender.bech32() == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver.bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.chainID == "D"
        assert transaction.nonce == 777
        assert transaction.signature == b""
        assert str(transaction.data) == "setCheckCapOnReDelegateRewards@66616c7365"

    def test_set_metadata(self):
        sender = Address.from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        transaction_nonce = 777
        gas_limit = None
        gas_price = None
        value = None

        transaction = self.factory.set_metadata(
            sender=sender,
            delegation_contract=delegation_contract,
            name="name",
            website="website",
            identifier="identifier",
            value=value,
            transaction_nonce=transaction_nonce,
            gas_price=gas_price,
            gas_limit=gas_limit
        )

        assert transaction.sender.bech32() == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver.bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.chainID == "D"
        assert transaction.nonce == 777
        assert transaction.signature == b""
        assert str(transaction.data) == "setMetaData@6e616d65@77656273697465@6964656e746966696572"
