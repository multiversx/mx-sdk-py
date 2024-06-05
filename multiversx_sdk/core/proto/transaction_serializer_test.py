from multiversx_sdk.core.proto.transaction_serializer import ProtoSerializer
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transaction_computer import TransactionComputer
from multiversx_sdk.testutils.wallets import load_wallets


class TestProtoSerializer:
    wallets = load_wallets()
    alice = wallets["alice"]
    bob = wallets["bob"]
    carol = wallets["carol"]
    proto_serializer = ProtoSerializer()
    transaction_computer = TransactionComputer()

    def test_serialize_tx_no_data_no_value(self):
        transaction = Transaction(
            sender=self.alice.label,
            receiver=self.bob.label,
            gas_limit=50000,
            chain_id="local-testnet",
            nonce=89,
            value=0,
        )
        transaction.signature = self.alice.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        serialized_transaction = self.proto_serializer.serialize_transaction(transaction)
        assert serialized_transaction.hex() == "0859120200001a208049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f82a200139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1388094ebdc0340d08603520d6c6f63616c2d746573746e6574580262403f08a1dd64fbb627d10b048e0b45b1390f29bb0e457762a2ccb710b029f299022a67a4b8e45cf62f4314afec2e56b5574c71e38df96cc41fae757b7ee5062503"

    def test_serialize_tx_with_data_no_value(self):
        transaction = Transaction(
            sender=self.alice.label,
            receiver=self.bob.label,
            gas_limit=80000,
            chain_id="local-testnet",
            data=b"hello",
            nonce=90
        )
        transaction.signature = self.alice.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        serialized_transaction = self.proto_serializer.serialize_transaction(transaction)
        assert serialized_transaction.hex() == "085a120200001a208049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f82a200139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1388094ebdc034080f1044a0568656c6c6f520d6c6f63616c2d746573746e657458026240f9e8c1caf7f36b99e7e76ee1118bf71b55cde11a2356e2b3adf15f4ad711d2e1982469cbba7eb0afbf74e8a8f78e549b9410cd86eeaa88fcba62611ac9f6e30e"

    def test_serialize_tx_with_data_and_value(self):
        transaction = Transaction(
            sender=self.alice.label,
            receiver=self.bob.label,
            gas_limit=100000,
            chain_id="local-testnet",
            nonce=92,
            data=b"for the spaceship",
            value=123456789000000000000000000000
        )
        transaction.signature = self.alice.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        serialized_transaction = self.proto_serializer.serialize_transaction(transaction)
        assert serialized_transaction.hex() == "085c120e00018ee90ff6181f3761632000001a208049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f82a200139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1388094ebdc0340a08d064a11666f722074686520737061636573686970520d6c6f63616c2d746573746e65745802624001f05aa8cb0614e12a94ab9dcbde5e78370a4e05d23ef25a1fb9d5fcf1cb3b1f33b919cd8dafb1704efb18fa233a8aa0d3344fb6ee9b613a7d7a403786ffbd0a"

    def test_serialize_tx_with_nonce_zero(self):
        transaction = Transaction(
            sender=self.alice.label,
            receiver=self.bob.label,
            chain_id="local-testnet",
            gas_limit=80000,
            nonce=0,
            value=0,
            data=b"hello",
            version=1
        )
        transaction.signature = self.alice.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        serialized_transaction = self.proto_serializer.serialize_transaction(transaction)
        assert serialized_transaction.hex() == "120200001a208049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f82a200139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1388094ebdc034080f1044a0568656c6c6f520d6c6f63616c2d746573746e657458016240dfa3e9f2fdec60dcb353bac3b3435b4a2ff251e7e98eaf8620f46c731fc70c8ba5615fd4e208b05e75fe0f7dc44b7a99567e29f94fcd91efac7e67b182cd2a04"

    def test_serialized_tx_with_usernames(self):
        transaction = Transaction(
            sender=self.carol.label,
            receiver=self.alice.label,
            gas_limit=50000,
            chain_id="T",
            nonce=204,
            value=1000000000000000000,
            sender_username="carol",
            receiver_username="alice"
        )
        transaction.signature = self.carol.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        serialized_transaction = self.proto_serializer.serialize_transaction(transaction)
        assert serialized_transaction.hex() == "08cc011209000de0b6b3a76400001a200139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e12205616c6963652a20b2a11555ce521e4944e09ab17549d85b487dcd26c84b5017a39e31a3670889ba32056361726f6c388094ebdc0340d086035201545802624051e6cd78fb3ab4b53ff7ad6864df27cb4a56d70603332869d47a5cf6ea977c30e696103e41e8dddf2582996ad335229fdf4acb726564dbc1a0bc9e705b511f06"

    def test_serialized_tx_with_inner_txs(self):
        inner_transaction = Transaction(
            sender=self.carol.label,
            receiver=self.alice.label,
            gas_limit=50000,
            chain_id="T",
            nonce=204,
            value=1000000000000000000,
            sender_username="carol",
            receiver_username="alice"
        )
        inner_transaction.signature = self.carol.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(inner_transaction))

        relayed_transaction = Transaction(
            sender=self.carol.label,
            receiver=self.alice.label,
            gas_limit=50000,
            chain_id="T",
            nonce=204,
            value=1000000000000000000,
            sender_username="carol",
            receiver_username="alice",
            relayer=self.carol.label,
            inner_transactions=[inner_transaction]
        )

        relayed_transaction.signature = self.carol.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(
            relayed_transaction))
        serialized_transaction = self.proto_serializer.serialize_transaction(relayed_transaction)
        assert serialized_transaction.hex() == "08cc011209000de0b6b3a76400001a200139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e12205616c6963652a20b2a11555ce521e4944e09ab17549d85b487dcd26c84b5017a39e31a3670889ba32056361726f6c388094ebdc0340d0860352015458026240901a6a974d6ab36546e7881c6e0364ec4c61a891aa70e5eb60f818d6c92a39cfa0beac6fab73f503853cfe8fe6149b4be207ddb93788f8450d75a07fa8759d06820120b2a11555ce521e4944e09ab17549d85b487dcd26c84b5017a39e31a3670889ba8a01b10108cc011209000de0b6b3a76400001a200139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e12205616c6963652a20b2a11555ce521e4944e09ab17549d85b487dcd26c84b5017a39e31a3670889ba32056361726f6c388094ebdc0340d086035201545802624051e6cd78fb3ab4b53ff7ad6864df27cb4a56d70603332869d47a5cf6ea977c30e696103e41e8dddf2582996ad335229fdf4acb726564dbc1a0bc9e705b511f06"
