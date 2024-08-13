from multiversx_sdk.core.address import Address
from multiversx_sdk.core.constants import DELEGATION_MANAGER_SC_ADDRESS
from multiversx_sdk.core.transactions_factories.delegation_transactions_factory import \
    DelegationTransactionsFactory
from multiversx_sdk.core.transactions_factories.transactions_factory_config import \
    TransactionsFactoryConfig
from multiversx_sdk.wallet import ValidatorSecretKey, ValidatorSigner


class TestDelegationTransactionsFactory:
    config = TransactionsFactoryConfig("D")
    factory = DelegationTransactionsFactory(config)

    def test_create_transaction_for_new_delegation_contract(self):
        transaction = self.factory.create_transaction_for_new_delegation_contract(
            sender=Address.new_from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"),
            total_delegation_cap=5000000000000000000000,
            service_fee=10,
            amount=1250000000000000000000
        )

        assert transaction.sender == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver == DELEGATION_MANAGER_SC_ADDRESS
        assert transaction.data
        assert transaction.data.decode() == "createNewDelegationContract@010f0cf064dd59200000@0a"
        assert transaction.gas_limit == 60126500
        assert transaction.value == 1250000000000000000000

    def test_create_transaction_for_adding_nodes(self):
        sender = Address.new_from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        validator_secret_key = ValidatorSecretKey.from_string("7cff99bd671502db7d15bc8abc0c9a804fb925406fbdd50f1e4c17a4cd774247")
        validator_signer = ValidatorSigner(validator_secret_key)

        signed_message = validator_signer.sign(bytes.fromhex(delegation_contract.to_hex()))
        public_key = validator_secret_key.generate_public_key()

        public_keys = [public_key]
        signed_messages = [signed_message]

        transaction = self.factory.create_transaction_for_adding_nodes(
            sender=sender,
            delegation_contract=delegation_contract,
            public_keys=public_keys,
            signed_messages=signed_messages
        )

        assert transaction.sender == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.data
        assert transaction.data.decode() == "addNodes@e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208@81109fa1c8d3dc7b6c2d6e65206cc0bc1a83c9b2d1eb91a601d66ad32def430827d5eb52917bd2b0d04ce195738db216"
        assert transaction.value == 0

    def test_create_transaction_for_removing_nodes(self):
        sender = Address.new_from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        public_keys = ["notavalidblskeyhexencoded".encode()]

        transaction = self.factory.create_transaction_for_removing_nodes(
            sender=sender,
            delegation_contract=delegation_contract,
            public_keys=public_keys
        )

        assert transaction.sender == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.data
        assert transaction.data.decode() == "removeNodes@6e6f746176616c6964626c736b6579686578656e636f646564"
        assert transaction.value == 0

    def test_create_transaction_for_staking_nodes(self):
        sender = Address.new_from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        public_keys = ["notavalidblskeyhexencoded".encode()]

        transaction = self.factory.create_transaction_for_staking_nodes(
            sender=sender,
            delegation_contract=delegation_contract,
            public_keys=public_keys
        )

        assert transaction.sender == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.data
        assert transaction.data.decode() == "stakeNodes@6e6f746176616c6964626c736b6579686578656e636f646564"
        assert transaction.value == 0

    def test_create_transaction_for_unbonding_nodes(self):
        sender = Address.new_from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        public_keys = ["notavalidblskeyhexencoded".encode()]

        transaction = self.factory.create_transaction_for_unbonding_nodes(
            sender=sender,
            delegation_contract=delegation_contract,
            public_keys=public_keys
        )

        assert transaction.sender == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.data
        assert transaction.data.decode() == "unBondNodes@6e6f746176616c6964626c736b6579686578656e636f646564"
        assert transaction.value == 0

    def test_create_transaction_for_unstaking_nodes(self):
        sender = Address.new_from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        public_keys = ["notavalidblskeyhexencoded".encode()]

        transaction = self.factory.create_transaction_for_unstaking_nodes(
            sender=sender,
            delegation_contract=delegation_contract,
            public_keys=public_keys
        )

        assert transaction.sender == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.data
        assert transaction.data.decode() == "unStakeNodes@6e6f746176616c6964626c736b6579686578656e636f646564"
        assert transaction.value == 0

    def test_create_transaction_for_unjailing_nodes(self):
        sender = Address.new_from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        public_keys = ["notavalidblskeyhexencoded".encode()]

        transaction = self.factory.create_transaction_for_unjailing_nodes(
            sender=sender,
            delegation_contract=delegation_contract,
            public_keys=public_keys,
            amount=25000000000000000000  # 2.5 egld
        )

        assert transaction.sender == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.data
        assert transaction.data.decode() == "unJailNodes@6e6f746176616c6964626c736b6579686578656e636f646564"
        assert transaction.value == 25000000000000000000

    def test_create_transaction_for_changing_service_fee(self):
        sender = Address.new_from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        transaction = self.factory.create_transaction_for_changing_service_fee(
            sender=sender,
            delegation_contract=delegation_contract,
            service_fee=10
        )

        assert transaction.sender == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.data
        assert transaction.data.decode() == "changeServiceFee@0a"
        assert transaction.value == 0

    def test_create_transaction_for_modifying_delegation_cap(self):
        sender = Address.new_from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        transaction = self.factory.create_transaction_for_modifying_delegation_cap(
            sender=sender,
            delegation_contract=delegation_contract,
            delegation_cap=5000000000000000000000
        )

        assert transaction.sender == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.data
        assert transaction.data.decode() == "modifyTotalDelegationCap@010f0cf064dd59200000"
        assert transaction.value == 0

    def test_create_transaction_for_setting_automatic_activation(self):
        sender = Address.new_from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        transaction = self.factory.create_transaction_for_setting_automatic_activation(
            sender=sender,
            delegation_contract=delegation_contract
        )

        assert transaction.sender == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.data
        assert transaction.data.decode() == "setAutomaticActivation@74727565"
        assert transaction.value == 0

    def test_create_transaction_for_unsetting_automatic_activation(self):
        sender = Address.new_from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        transaction = self.factory.create_transaction_for_unsetting_automatic_activation(
            sender=sender,
            delegation_contract=delegation_contract
        )

        assert transaction.sender == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.data
        assert transaction.data.decode() == "setAutomaticActivation@66616c7365"
        assert transaction.value == 0

    def test_create_transaction_for_setting_cap_check_on_redelegate_rewards(self):
        sender = Address.new_from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        transaction = self.factory.create_transaction_for_setting_cap_check_on_redelegate_rewards(
            sender=sender,
            delegation_contract=delegation_contract
        )

        assert transaction.sender == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.data
        assert transaction.data.decode() == "setCheckCapOnReDelegateRewards@74727565"
        assert transaction.value == 0

    def test_create_transaction_for_unsetting_cap_check_on_redelegate_rewards(self):
        sender = Address.new_from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        transaction = self.factory.create_transaction_for_unsetting_cap_check_on_redelegate_rewards(
            sender=sender,
            delegation_contract=delegation_contract
        )

        assert transaction.sender == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.data
        assert transaction.data.decode() == "setCheckCapOnReDelegateRewards@66616c7365"
        assert transaction.value == 0

    def test_create_transaction_for_setting_metadata(self):
        sender = Address.new_from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        transaction = self.factory.create_transaction_for_setting_metadata(
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
        assert transaction.value == 0

    def test_create_transaction_for_delegating(self):
        sender = Address.new_from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        transaction = self.factory.create_transaction_for_delegating(
            sender=sender,
            delegation_contract=delegation_contract,
            amount=1000000000000000000
        )

        assert transaction.sender == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.data
        assert transaction.data.decode() == "delegate"
        assert transaction.value == 1000000000000000000
        assert transaction.gas_limit == 12000000

    def test_create_transaction_for_claiming_rewards(self):
        sender = Address.new_from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        transaction = self.factory.create_transaction_for_claiming_rewards(
            sender=sender,
            delegation_contract=delegation_contract
        )

        assert transaction.sender == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.data
        assert transaction.data.decode() == "claimRewards"
        assert transaction.value == 0
        assert transaction.gas_limit == 6000000

    def test_create_transaction_for_redelegating_rewards(self):
        sender = Address.new_from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        transaction = self.factory.create_transaction_for_redelegating_rewards(
            sender=sender,
            delegation_contract=delegation_contract
        )

        assert transaction.sender == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.data
        assert transaction.data.decode() == "reDelegateRewards"
        assert transaction.value == 0
        assert transaction.gas_limit == 12000000

    def test_create_transaction_for_undelegating(self):
        sender = Address.new_from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        transaction = self.factory.create_transaction_for_undelegating(
            sender=sender,
            delegation_contract=delegation_contract,
            amount=1000000000000000000
        )

        assert transaction.sender == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.data
        assert transaction.data.decode() == "unDelegate@0de0b6b3a7640000"
        assert transaction.value == 0
        assert transaction.gas_limit == 12000000

    def test_create_transaction_for_withdrawing(self):
        sender = Address.new_from_bech32("erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2")
        delegation_contract = Address.new_from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc")

        transaction = self.factory.create_transaction_for_withdrawing(
            sender=sender,
            delegation_contract=delegation_contract
        )

        assert transaction.sender == "erd18s6a06ktr2v6fgxv4ffhauxvptssnaqlds45qgsrucemlwc8rawq553rt2"
        assert transaction.receiver == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtllllls002zgc"
        assert transaction.data
        assert transaction.data.decode() == "withdraw"
        assert transaction.value == 0
        assert transaction.gas_limit == 12000000
