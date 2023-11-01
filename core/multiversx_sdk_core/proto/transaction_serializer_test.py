from multiversx_sdk_core.proto.transaction_serializer import ProtoSerializer
from multiversx_sdk_core.testutils.wallets import load_wallets
from multiversx_sdk_core.transaction import Transaction


class TestProtoSerializer:
    wallets = load_wallets()
    alice = wallets["alice"]
    bob = wallets["bob"]
    carol = wallets["carol"]
    proto_serializer = ProtoSerializer()

    def test_serialize_tx_no_data_no_value(self):
        transaction = Transaction(
            sender=self.alice.label,
            receiver=self.bob.label,
            gas_limit=50000,
            chain_id="local-testnet",
            nonce=89,
            amount=0,
        )
        # we do this to match the test in mx-sdk-js-core
        transaction.version = 1

        transaction.signature = bytes.fromhex("b56769014f2bdc5cf9fc4a05356807d71fcf8775c819b0f1b0964625b679c918ffa64862313bfef86f99b38cb84fcdb16fa33ad6eb565276616723405cd8f109")
        serialized_transaction = self.proto_serializer.serialize_transaction(transaction)

        assert serialized_transaction.hex() == "0859120200001a208049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f82a200139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1388094ebdc0340d08603520d6c6f63616c2d746573746e657458016240b56769014f2bdc5cf9fc4a05356807d71fcf8775c819b0f1b0964625b679c918ffa64862313bfef86f99b38cb84fcdb16fa33ad6eb565276616723405cd8f109"

    def test_serialize_tx_with_data_no_value(self):
        transaction = Transaction(
            sender=self.alice.label,
            receiver=self.bob.label,
            gas_limit=80000,
            chain_id="local-testnet",
            data=b"hello",
            nonce=90
        )
        # we do this to match the test in mx-sdk-js-core
        transaction.version = 1

        transaction.signature = bytes.fromhex("e47fd437fc17ac9a69f7bf5f85bafa9e7628d851c4f69bd9fedc7e36029708b2e6d168d5cd652ea78beedd06d4440974ca46c403b14071a1a148d4188f6f2c0d")
        serialized_transaction = self.proto_serializer.serialize_transaction(transaction)

        assert serialized_transaction.hex() == "085a120200001a208049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f82a200139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1388094ebdc034080f1044a0568656c6c6f520d6c6f63616c2d746573746e657458016240e47fd437fc17ac9a69f7bf5f85bafa9e7628d851c4f69bd9fedc7e36029708b2e6d168d5cd652ea78beedd06d4440974ca46c403b14071a1a148d4188f6f2c0d"

    def test_serialize_tx_with_data_and_value(self):
        transaction = Transaction(
            sender=self.alice.label,
            receiver=self.bob.label,
            gas_limit=100000,
            chain_id="local-testnet",
            nonce=92,
            data=b"for the spaceship",
            amount=123456789000000000000000000000
        )
        # we do this to match the test in mx-sdk-js-core
        transaction.version = 1

        transaction.signature = bytes.fromhex("39938d15812708475dfc8125b5d41dbcea0b2e3e7aabbbfceb6ce4f070de3033676a218b73facd88b1432d7d4accab89c6130b3abe5cc7bbbb5146e61d355b03")
        serialized_transaction = self.proto_serializer.serialize_transaction(transaction)

        assert serialized_transaction.hex() == "085c120e00018ee90ff6181f3761632000001a208049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f82a200139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1388094ebdc0340a08d064a11666f722074686520737061636573686970520d6c6f63616c2d746573746e65745801624039938d15812708475dfc8125b5d41dbcea0b2e3e7aabbbfceb6ce4f070de3033676a218b73facd88b1432d7d4accab89c6130b3abe5cc7bbbb5146e61d355b03"

    def test_serialize_tx_with_nonce_zero(self):
        transaction = Transaction(
            sender=self.alice.label,
            receiver=self.bob.label,
            chain_id="local-testnet",
            gas_limit=80000,
            nonce=0,
            amount=0,
            data=b"hello",
            version=1
        )

        transaction.signature = bytes.fromhex("dfa3e9f2fdec60dcb353bac3b3435b4a2ff251e7e98eaf8620f46c731fc70c8ba5615fd4e208b05e75fe0f7dc44b7a99567e29f94fcd91efac7e67b182cd2a04")
        serialized_transaction = self.proto_serializer.serialize_transaction(transaction)

        assert serialized_transaction.hex() == "120200001a208049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f82a200139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1388094ebdc034080f1044a0568656c6c6f520d6c6f63616c2d746573746e657458016240dfa3e9f2fdec60dcb353bac3b3435b4a2ff251e7e98eaf8620f46c731fc70c8ba5615fd4e208b05e75fe0f7dc44b7a99567e29f94fcd91efac7e67b182cd2a04"

    def test_serialized_tx_with_usernames(self):
        transaction = Transaction(
            sender=self.carol.label,
            receiver=self.alice.label,
            gas_limit=50000,
            chain_id="T",
            nonce=204,
            amount=1000000000000000000,
            sender_username="carol",
            receiver_username="alice"
        )
        # we do this to match the test in mx-sdk-js-core
        transaction.version = 1

        transaction.signature = bytes.fromhex("5966dd6b98fc5ecbcd203fa38fac7059ba5c17683099071883b0ad6697386769321d851388a99cb8b81aab625aa2d7e13621432dbd8ab334c5891cd7c7755200")
        serialized_transaction = self.proto_serializer.serialize_transaction(transaction)

        assert serialized_transaction.hex() == "08cc011209000de0b6b3a76400001a200139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e12205616c6963652a20b2a11555ce521e4944e09ab17549d85b487dcd26c84b5017a39e31a3670889ba32056361726f6c388094ebdc0340d08603520154580162405966dd6b98fc5ecbcd203fa38fac7059ba5c17683099071883b0ad6697386769321d851388a99cb8b81aab625aa2d7e13621432dbd8ab334c5891cd7c7755200"
