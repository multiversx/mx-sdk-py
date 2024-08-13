from typing import List

import pytest

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.errors import InvalidInnerTransactionError
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transaction_computer import TransactionComputer
from multiversx_sdk.core.transactions_factories.relayed_transactions_factory import \
    RelayedTransactionsFactory
from multiversx_sdk.core.transactions_factories.transactions_factory_config import \
    TransactionsFactoryConfig
from multiversx_sdk.testutils.wallets import load_wallets


class TestRelayedTransactionsFactory:
    config = TransactionsFactoryConfig("T")
    factory = RelayedTransactionsFactory(config)
    transaction_computer = TransactionComputer()
    wallets = load_wallets()

    def test_create_relayed_v1_with_invalid_inner_tx(self):
        alice = self.wallets["alice"]

        inner_transaction = Transaction(
            sender=alice.label,
            receiver="erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u",
            gas_limit=10000000,
            data="getContractConfig".encode(),
            chain_id=self.config.chain_id
        )

        with pytest.raises(InvalidInnerTransactionError, match="The inner transaction is not signed"):
            self.factory.create_relayed_v1_transaction(
                inner_transaction=inner_transaction,
                relayer_address=Address.from_bech32(self.wallets["bob"].label)
            )

        inner_transaction.gas_limit = 0
        inner_transaction.signature = b"invalidsignature"

        with pytest.raises(InvalidInnerTransactionError, match="The gas limit is not set for the inner transaction"):
            self.factory.create_relayed_v1_transaction(
                inner_transaction=inner_transaction,
                relayer_address=Address.from_bech32(self.wallets["bob"].label)
            )

    def test_create_relayed_v1_transaction(self):
        alice = self.wallets["alice"]
        bob = self.wallets["bob"]

        inner_transaction = Transaction(
            sender=bob.label,
            receiver="erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u",
            gas_limit=60000000,
            chain_id=self.config.chain_id,
            data=b"getContractConfig",
            nonce=198
        )

        inner_tx_bytes = self.transaction_computer.compute_bytes_for_signing(inner_transaction)
        inner_transaction.signature = bob.secret_key.sign(inner_tx_bytes)

        relayed_transaction = self.factory.create_relayed_v1_transaction(
            inner_transaction=inner_transaction,
            relayer_address=Address.from_bech32(alice.label)
        )
        relayed_transaction.nonce = 2627

        relayed_tx_bytes = self.transaction_computer.compute_bytes_for_signing(relayed_transaction)
        relayed_transaction.signature = alice.secret_key.sign(relayed_tx_bytes)

        assert relayed_transaction.data.decode() == "relayedTx@7b226e6f6e6365223a3139382c2273656e646572223a2267456e574f65576d6d413063306a6b71764d354241707a61644b46574e534f69417643575163776d4750673d222c227265636569766572223a22414141414141414141414141415141414141414141414141414141414141414141414141414141432f2f383d222c2276616c7565223a302c226761735072696365223a313030303030303030302c226761734c696d6974223a36303030303030302c2264617461223a225a3256305132397564484a68593352446232356d6157633d222c227369676e6174757265223a2272525455544858677a4273496e4f6e454b6b7869642b354e66524d486e33534948314673746f577352434c434b3258514c41614f4e704449346531476173624c5150616130566f364144516d4f2b52446b6f364a43413d3d222c22636861696e4944223a2256413d3d222c2276657273696f6e223a327d"
        assert relayed_transaction.signature.hex() == "128e7cdc14c2b9beee2f3ff7a7fa5d1f5ef31a654a0c92e223c90ab28265fa277d306f23a06536248cf9573e828017004fb639617fade4d68a37524aafca710d"

    def test_create_relayed_v1_transaction_with_usernames(self):
        alice = self.wallets["alice"]
        carol = self.wallets["carol"]
        frank = self.wallets["frank"]

        inner_transaction = Transaction(
            sender=carol.label,
            receiver=alice.label,
            gas_limit=50000,
            chain_id=self.config.chain_id,
            nonce=208,
            sender_username="carol",
            receiver_username="alice",
            value=1000000000000000000
        )

        inner_tx_bytes = self.transaction_computer.compute_bytes_for_signing(inner_transaction)
        inner_transaction.signature = carol.secret_key.sign(inner_tx_bytes)

        relayed_transaction = self.factory.create_relayed_v1_transaction(
            inner_transaction=inner_transaction,
            relayer_address=Address.from_bech32(frank.label)
        )
        relayed_transaction.nonce = 715

        relayed_tx_bytes = self.transaction_computer.compute_bytes_for_signing(relayed_transaction)
        relayed_transaction.signature = frank.secret_key.sign(relayed_tx_bytes)

        assert relayed_transaction.data.decode() == "relayedTx@7b226e6f6e6365223a3230382c2273656e646572223a227371455656633553486b6c45344a717864556e59573068397a536249533141586f3534786f32634969626f3d222c227265636569766572223a2241546c484c76396f686e63616d433877673970645168386b77704742356a6949496f3349484b594e6165453d222c2276616c7565223a313030303030303030303030303030303030302c226761735072696365223a313030303030303030302c226761734c696d6974223a35303030302c2264617461223a22222c227369676e6174757265223a226a33427a6469554144325963517473576c65707663664a6f75657a48573063316b735a424a4d6339573167435450512b6870636759457858326f6f367a4b5654347464314b4b6f79783841526a346e336474576c44413d3d222c22636861696e4944223a2256413d3d222c2276657273696f6e223a322c22736e64557365724e616d65223a22593246796232773d222c22726376557365724e616d65223a22595778705932553d227d"
        assert relayed_transaction.signature.hex() == "3787d640e5a579e7977a4a1bcdd435ad11855632fa4a414a06fbf8355692d1a58d76ef0adbdd6ccd6bd3c329f36bd53c180d4873ec1a6c558e659aeb9ab92d00"

    def test_compute_relayed_v1_with_guarded_inner_tx(self):
        alice = self.wallets["alice"]
        bob = self.wallets["bob"]
        grace = self.wallets["grace"]

        inner_transaction = Transaction(
            sender=bob.label,
            receiver="erd1qqqqqqqqqqqqqpgq54tsxmej537z9leghvp69hfu4f8gg5eu396q83gnnz",
            gas_limit=60000000,
            chain_id=self.config.chain_id,
            data=b"getContractConfig",
            nonce=198,
            version=2,
            options=2,
            guardian=grace.label
        )

        inner_tx_bytes = self.transaction_computer.compute_bytes_for_signing(inner_transaction)
        inner_transaction.signature = bob.secret_key.sign(inner_tx_bytes)
        inner_transaction.guardian_signature = grace.secret_key.sign(inner_tx_bytes)

        relayed_transaction = self.factory.create_relayed_v1_transaction(
            inner_transaction=inner_transaction,
            relayer_address=Address.from_bech32(alice.label)
        )
        relayed_transaction.nonce = 2627

        relayed_tx_bytes = self.transaction_computer.compute_bytes_for_signing(relayed_transaction)
        relayed_transaction.signature = alice.secret_key.sign(relayed_tx_bytes)

        assert relayed_transaction.data.decode() == "relayedTx@7b226e6f6e6365223a3139382c2273656e646572223a2267456e574f65576d6d413063306a6b71764d354241707a61644b46574e534f69417643575163776d4750673d222c227265636569766572223a22414141414141414141414146414b565841323879704877692f79693741364c64504b704f68464d386958513d222c2276616c7565223a302c226761735072696365223a313030303030303030302c226761734c696d6974223a36303030303030302c2264617461223a225a3256305132397564484a68593352446232356d6157633d222c227369676e6174757265223a224b4b78324f33383655725135416b4f465258307578327933446a384853334b373038487174344668377161557669424550716c45614e746e6158706a6f2f333651476d4a456934784435457a6c6f4f677a634d4442773d3d222c22636861696e4944223a2256413d3d222c2276657273696f6e223a322c226f7074696f6e73223a322c22677561726469616e223a22486f714c61306e655733766843716f56696c70715372744c5673774939535337586d7a563868477450684d3d222c22677561726469616e5369676e6174757265223a222b5431526f4833625a792f54423177342b6a365155477258645637457577553073753948646551626453515269463953757a686d634b705463526d58595252366c534c6652394931624d7134674730436538363741513d3d227d"
        assert relayed_transaction.signature.hex() == "39cff9d5100e290fbc7361cb6e2402261caf864257b4116f150e0c61e7869155dff8361fa5449431eb7a8ed847c01ba9b3b5ebafe5fac1a3d40c64829d827e00"

    def test_guarded_relayed_v1_with_guarded_inner_tx(self):
        alice = self.wallets["alice"]
        bob = self.wallets["bob"]
        grace = self.wallets["grace"]
        frank = self.wallets["frank"]

        inner_transaction = Transaction(
            sender=bob.label,
            receiver="erd1qqqqqqqqqqqqqpgq54tsxmej537z9leghvp69hfu4f8gg5eu396q83gnnz",
            gas_limit=60000000,
            chain_id=self.config.chain_id,
            data=b"addNumber",
            nonce=198,
            version=2,
            options=2,
            guardian=grace.label
        )

        inner_tx_bytes = self.transaction_computer.compute_bytes_for_signing(inner_transaction)
        inner_transaction.signature = bob.secret_key.sign(inner_tx_bytes)
        inner_transaction.guardian_signature = grace.secret_key.sign(inner_tx_bytes)

        relayed_transaction = self.factory.create_relayed_v1_transaction(
            inner_transaction=inner_transaction,
            relayer_address=Address.from_bech32(alice.label)
        )
        relayed_transaction.options = 2
        relayed_transaction.nonce = 2627
        relayed_transaction.guardian = frank.label

        relayed_tx_bytes = self.transaction_computer.compute_bytes_for_signing(relayed_transaction)
        relayed_transaction.signature = alice.secret_key.sign(relayed_tx_bytes)
        relayed_transaction.guardian_signature = frank.secret_key.sign(relayed_tx_bytes)

        assert relayed_transaction.data.decode() == "relayedTx@7b226e6f6e6365223a3139382c2273656e646572223a2267456e574f65576d6d413063306a6b71764d354241707a61644b46574e534f69417643575163776d4750673d222c227265636569766572223a22414141414141414141414146414b565841323879704877692f79693741364c64504b704f68464d386958513d222c2276616c7565223a302c226761735072696365223a313030303030303030302c226761734c696d6974223a36303030303030302c2264617461223a225957526b546e5674596d5679222c227369676e6174757265223a223469724d4b4a656d724d375174344e7635487633544c44683775654779487045564c4371674a3677652f7a662b746a4933354975573452633458543451533433475333356158386c6a533834324a38426854645043673d3d222c22636861696e4944223a2256413d3d222c2276657273696f6e223a322c226f7074696f6e73223a322c22677561726469616e223a22486f714c61306e655733766843716f56696c70715372744c5673774939535337586d7a563868477450684d3d222c22677561726469616e5369676e6174757265223a2270424754394e674a78307539624c56796b654d78786a454865374269696c37764932324a46676f32787a6e2f496e3032463769546563356b44395045324f747065386c475335412b532f4a36417762576834446744673d3d227d"
        assert relayed_transaction.signature.hex() == "8ede1bbeed96b102344dffeac12c2592c62b7313cdeb132e8c8bf11d2b1d3bb8189d257a6dbcc99e222393d9b9ec77656c349dae97a32e68bdebd636066bf706"

    def test_create_relayed_v2_with_invalid_inner_tx(self):
        alice = self.wallets["alice"]
        bob = self.wallets["bob"]
        carol = self.wallets["carol"]

        inner_transaction = Transaction(
            sender=alice.label,
            receiver=bob.label,
            gas_limit=50000,
            chain_id=self.config.chain_id
        )

        with pytest.raises(InvalidInnerTransactionError, match="The gas limit should not be set for the inner transaction"):
            self.factory.create_relayed_v2_transaction(
                inner_transaction=inner_transaction,
                inner_transaction_gas_limit=50000,
                relayer_address=Address.from_bech32(carol.label)
            )

        inner_transaction.gas_limit = 0
        with pytest.raises(InvalidInnerTransactionError, match="The inner transaction is not signed"):
            self.factory.create_relayed_v2_transaction(
                inner_transaction=inner_transaction,
                inner_transaction_gas_limit=50000,
                relayer_address=Address.from_bech32(carol.label)
            )

    def test_compute_relayed_v2_transaction(self):
        alice = self.wallets["alice"]
        bob = self.wallets["bob"]

        inner_transaction = Transaction(
            sender=bob.label,
            receiver="erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u",
            gas_limit=0,
            chain_id=self.config.chain_id,
            data=b"getContractConfig",
            nonce=15,
            version=2,
            options=0
        )

        serialized_inner_transaction = self.transaction_computer.compute_bytes_for_signing(inner_transaction)
        inner_transaction.signature = bob.secret_key.sign(serialized_inner_transaction)

        relayed_transaction = self.factory.create_relayed_v2_transaction(
            inner_transaction=inner_transaction,
            inner_transaction_gas_limit=60_000_000,
            relayer_address=Address.from_bech32(alice.label)
        )
        relayed_transaction.nonce = 37

        serialized_relayed_transaction = self.transaction_computer.compute_bytes_for_signing(relayed_transaction)
        relayed_transaction.signature = alice.secret_key.sign(serialized_relayed_transaction)

        assert relayed_transaction.version == 2
        assert relayed_transaction.options == 0
        assert relayed_transaction.gas_limit == 60414500
        assert relayed_transaction.data.decode() == "relayedTxV2@000000000000000000010000000000000000000000000000000000000002ffff@0f@676574436f6e7472616374436f6e666967@fc3ed87a51ee659f937c1a1ed11c1ae677e99629fae9cc289461f033e6514d1a8cfad1144ae9c1b70f28554d196bd6ba1604240c1c1dc19c959e96c1c3b62d0c"

    def test_compute_relayed_v3_transaction(self):
        alice = self.wallets["alice"]
        bob = self.wallets["bob"]

        inner_transaction = Transaction(
            sender=bob.label,
            receiver=bob.label,
            gas_limit=50000,
            chain_id="T",
            nonce=0,
            version=2,
            relayer=alice.label
        )

        inner_transactions = [inner_transaction]
        serialized_inner_transaction = self.transaction_computer.compute_bytes_for_signing(inner_transaction)
        inner_transaction.signature = bob.secret_key.sign(serialized_inner_transaction)

        relayed_transaction = self.factory.create_relayed_v3_transaction(
            relayer_address=Address.from_bech32(alice.label),
            inner_transactions=inner_transactions
        )
        serialized_relayed_transaction = self.transaction_computer.compute_bytes_for_signing(relayed_transaction)
        relayed_transaction.signature = alice.secret_key.sign(serialized_relayed_transaction)
        assert relayed_transaction.signature.hex() == "88b9bce6fe62a641fca593f95c12ad09032a44b34c9e5cf16d070f0563b1695bf9d452a9df52bce3373fd5e10ed96c3d65cd189f5873e3a3184a89f4980c9e0c"
        assert relayed_transaction.gas_limit == 100000

    def test_create_relayed_v3_with_invalid_inner_tx(self):
        alice = self.wallets["alice"]
        bob = self.wallets["bob"]

        inner_transaction = Transaction(
            sender=bob.label,
            receiver="erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
            gas_limit=2500,
            chain_id="local-testnet",
            nonce=0,
            version=2,
            relayer="erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"
        )

        serialized_inner_transaction = self.transaction_computer.compute_bytes_for_signing(inner_transaction)
        inner_transaction.signature = bob.secret_key.sign(serialized_inner_transaction)

        inner_transactions = [inner_transaction]

        """
        In the inner tx, the relayer address is acutally bob's. The creation should fail
        """
        with pytest.raises(InvalidInnerTransactionError) as err:
            self.factory.create_relayed_v3_transaction(
                relayer_address=Address.from_bech32(alice.label),
                inner_transactions=inner_transactions
            )
        assert str(err.value) == "The inner transaction has an incorrect relayer address"

        inner_transaction.signature = b""
        with pytest.raises(InvalidInnerTransactionError) as err:
            self.factory.create_relayed_v3_transaction(
                relayer_address=Address.from_bech32(alice.label),
                inner_transactions=inner_transactions
            )
        assert str(err.value) == "The inner transaction is not signed"

        inner_transactions: List[Transaction] = []
        with pytest.raises(InvalidInnerTransactionError) as err:
            self.factory.create_relayed_v3_transaction(
                relayer_address=Address.from_bech32(alice.label),
                inner_transactions=inner_transactions
            )
        assert str(err.value) == "The are no inner transactions"
