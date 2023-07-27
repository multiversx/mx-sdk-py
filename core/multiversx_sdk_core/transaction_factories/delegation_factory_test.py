from multiversx_sdk_wallet import ValidatorSecretKey, ValidatorSigner

from multiversx_sdk_core.address import Address
from multiversx_sdk_core.constants import DELEGATION_MANAGER_SC_ADDRESS
from multiversx_sdk_core.interfaces import IValidatorPublicKey
from multiversx_sdk_core.messages import ArbitraryMessage
from multiversx_sdk_core.transaction_factories.delegation_factory import \
    DelegationFactory
from multiversx_sdk_core.transaction_factories.transaction_factory_config import \
    TransactionFactoryConfig


class MockValidatorPublicKey(IValidatorPublicKey):
    def __init__(self, buffer: bytes) -> None:
        self.buffer = buffer

    def hex(self) -> str:
        return self.buffer.hex()


class TestDelegationFactory:
    config = TransactionFactoryConfig("D")
    factory = DelegationFactory(config)

    def test_create_new_delegation_contract(self):
        transaction = self.factory.create_transaction_intent_for_new_delegation_contract(
            sender=Address.from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"),
            total_delegation_cap=5000000000000000000000,
            service_fee=10,
            value=1250000000000000000000
        )

        assert transaction.sender == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver == DELEGATION_MANAGER_SC_ADDRESS
        assert transaction.data
        assert transaction.data.decode() == "createNewDelegationContract@010f0cf064dd59200000@0a"
        assert transaction.gas_limit == 60176500
        assert transaction.value == "1250000000000000000000"

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

        transaction = self.factory.create_transaction_intent_for_adding_nodes(
            sender=sender,
            delegation_contract=delegation_contract,
            public_keys=public_keys,
            signed_messages=signed_messages
        )

        assert transaction.sender == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.data
        assert transaction.data.decode() == "addNodes@e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208@81109fa1c8d3dc7b6c2d6e65206cc0bc1a83c9b2d1eb91a601d66ad32def430827d5eb52917bd2b0d04ce195738db216"
        assert transaction.value == "0"

    def test_remove_nodes(self):
        sender = Address.from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        mock_validator_key = MockValidatorPublicKey("notavalidblskeyhexencoded".encode())
        public_keys = [mock_validator_key]

        transaction = self.factory.create_transaction_intent_for_removing_nodes(
            sender=sender,
            delegation_contract=delegation_contract,
            public_keys=public_keys
        )

        assert transaction.sender == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.data
        assert transaction.data.decode() == "removeNodes@6e6f746176616c6964626c736b6579686578656e636f646564"
        assert transaction.value == "0"

    def test_stake_nodes(self):
        sender = Address.from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        mock_validator_key = MockValidatorPublicKey("notavalidblskeyhexencoded".encode())
        public_keys = [mock_validator_key]

        transaction = self.factory.create_transaction_intent_for_staking_nodes(
            sender=sender,
            delegation_contract=delegation_contract,
            public_keys=public_keys
        )

        assert transaction.sender == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.data
        assert transaction.data.decode() == "stakeNodes@6e6f746176616c6964626c736b6579686578656e636f646564"
        assert transaction.value == "0"

    def test_unbond_nodes(self):
        sender = Address.from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        mock_validator_key = MockValidatorPublicKey("notavalidblskeyhexencoded".encode())
        public_keys = [mock_validator_key]

        transaction = self.factory.create_transaction_intent_for_unbonding_nodes(
            sender=sender,
            delegation_contract=delegation_contract,
            public_keys=public_keys
        )

        assert transaction.sender == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.data
        assert transaction.data.decode() == "unBondNodes@6e6f746176616c6964626c736b6579686578656e636f646564"
        assert transaction.value == "0"

    def test_unstake_nodes(self):
        sender = Address.from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        mock_validator_key = MockValidatorPublicKey("notavalidblskeyhexencoded".encode())
        public_keys = [mock_validator_key]

        transaction = self.factory.create_transaction_intent_for_unstaking_nodes(
            sender=sender,
            delegation_contract=delegation_contract,
            public_keys=public_keys
        )

        assert transaction.sender == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.data
        assert transaction.data.decode() == "unStakeNodes@6e6f746176616c6964626c736b6579686578656e636f646564"
        assert transaction.value == "0"

    def test_unjail_nodes(self):
        sender = Address.from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        mock_validator_key = MockValidatorPublicKey("notavalidblskeyhexencoded".encode())
        public_keys = [mock_validator_key]

        transaction = self.factory.create_transaction_intent_for_unjailing_nodes(
            sender=sender,
            delegation_contract=delegation_contract,
            public_keys=public_keys
        )

        assert transaction.sender == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.data
        assert transaction.data.decode() == "unJailNodes@6e6f746176616c6964626c736b6579686578656e636f646564"
        assert transaction.value == "0"

    def test_change_service_fee(self):
        sender = Address.from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        transaction = self.factory.create_transaction_intent_for_changing_service_fee(
            sender=sender,
            delegation_contract=delegation_contract,
            service_fee=10
        )

        assert transaction.sender == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.data
        assert transaction.data.decode() == "changeServiceFee@0a"
        assert transaction.value == "0"

    def test_modify_delegation_cap(self):
        sender = Address.from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        transaction = self.factory.create_transaction_intent_for_modifying_delegation_cap(
            sender=sender,
            delegation_contract=delegation_contract,
            delegation_cap=5000000000000000000000
        )

        assert transaction.sender == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.data
        assert transaction.data.decode() == "modifyTotalDelegationCap@010f0cf064dd59200000"
        assert transaction.value == "0"

    def test_set_automatic_activation(self):
        sender = Address.from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        transaction = self.factory.create_transaction_intent_for_setting_automatic_activation(
            sender=sender,
            delegation_contract=delegation_contract
        )

        assert transaction.sender == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.data
        assert transaction.data.decode() == "setAutomaticActivation@74727565"
        assert transaction.value == "0"

    def test_unset_automatic_activation(self):
        sender = Address.from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        transaction = self.factory.create_transaction_intent_for_unsetting_automatic_activation(
            sender=sender,
            delegation_contract=delegation_contract
        )

        assert transaction.sender == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.data
        assert transaction.data.decode() == "setAutomaticActivation@66616c7365"
        assert transaction.value == "0"

    def test_set_cap_check_redelegate_rewards(self):
        sender = Address.from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        transaction = self.factory.create_transaction_intent_for_setting_cap_check_on_redelegate_rewards(
            sender=sender,
            delegation_contract=delegation_contract
        )

        assert transaction.sender == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.data
        assert transaction.data.decode() == "setCheckCapOnReDelegateRewards@74727565"
        assert transaction.value == "0"

    def test_unset_cap_check_redelegate_rewards(self):
        sender = Address.from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        transaction = self.factory.create_transaction_intent_for_unsetting_cap_check_on_redelegate_rewards(
            sender=sender,
            delegation_contract=delegation_contract
        )

        assert transaction.sender == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.data
        assert transaction.data.decode() == "setCheckCapOnReDelegateRewards@66616c7365"
        assert transaction.value == "0"

    def test_set_metadata(self):
        sender = Address.from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        transaction = self.factory.create_transaction_intent_for_setting_metadata(
            sender=sender,
            delegation_contract=delegation_contract,
            name="name",
            website="website",
            identifier="identifier"
        )

        assert transaction.sender == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.data
        assert transaction.data.decode() == "setMetaData@6e616d65@77656273697465@6964656e746966696572"
        assert transaction.value == "0"
