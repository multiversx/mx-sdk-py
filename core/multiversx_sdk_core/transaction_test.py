from multiversx_sdk_core.address import Address
from multiversx_sdk_core.testutils.wallets import load_wallets
from multiversx_sdk_core.token_payment import TokenPayment
from multiversx_sdk_core.transaction import Transaction
from multiversx_sdk_core.transaction_payload import TransactionPayload


class TestTransaction:
    wallets = load_wallets()
    alice = wallets["alice"]
    carol = wallets["carol"]

    def test_serialize_for_signing(self):
        sender = Address.from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
        receiver = Address.from_bech32("erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx")

        transaction = Transaction(
            nonce=89,
            sender=sender,
            receiver=receiver,
            value=0,
            gas_limit=50000,
            gas_price=1000000000,
            chain_id="D",
            version=1
        )

        assert transaction.serialize_for_signing().decode() == r"""{"nonce":89,"value":"0","receiver":"erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx","sender":"erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th","gasPrice":1000000000,"gasLimit":50000,"chainID":"D","version":1}"""

        transaction = Transaction(
            nonce=90,
            sender=sender,
            receiver=receiver,
            value=TokenPayment.egld_from_amount("1.0"),
            data=TransactionPayload.from_str("hello"),
            gas_limit=70000,
            gas_price=1000000000,
            chain_id="D",
            version=1
        )

        assert transaction.serialize_for_signing().decode() == r"""{"nonce":90,"value":"1000000000000000000","receiver":"erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx","sender":"erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th","gasPrice":1000000000,"gasLimit":70000,"data":"aGVsbG8=","chainID":"D","version":1}"""

    def test_with_usernames(self):
        transaction = Transaction(
            chain_id="T",
            sender=Address.from_bech32(self.carol.label),
            receiver=Address.from_bech32(self.alice.label),
            nonce=204,
            gas_limit=50000,
            sender_username="carol",
            receiver_username="alice",
            value=1000000000000000000
        )
        # needs to match the test from sdk-js-core
        transaction.version = 1

        transaction.signature = self.carol.secret_key.sign(transaction.serialize_for_signing())
        assert transaction.signature.hex() == "5966dd6b98fc5ecbcd203fa38fac7059ba5c17683099071883b0ad6697386769321d851388a99cb8b81aab625aa2d7e13621432dbd8ab334c5891cd7c7755200"

    def test_tx_from_dictionary(self):
        tx_as_dict = {
            "nonce": 7,
            "value": "1000000000000000000",
            "receiver": "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
            "sender": "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
            "senderUsername": "YWxpY2U=",
            "receiverUsername": "Ym9i",
            "gasPrice": 1000000000,
            "gasLimit": 70000,
            "data": "dGVzdCB0eA==",
            "chainID": "D",
            "version": 2,
            "options": 2,
            "signature": "6e6f746176616c69647369676e6174757265",
            "guardian": "erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8",
            "guardianSignature": "6e6f746176616c6964677561726469616e7369676e6174757265"
        }

        transaction = Transaction.from_dictionary(tx_as_dict)

        assert transaction.chainID == "D"
        assert transaction.sender.bech32() == "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"
        assert transaction.receiver.bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
        assert transaction.sender_username == "alice"
        assert transaction.receiver_username == "bob"
        assert str(transaction.data) == "test tx"
        assert transaction.gas_limit == 70000
        assert transaction.gas_price == 1000000000
        assert transaction.nonce == 7
        assert str(transaction.value) == "1000000000000000000"
        assert transaction.version == 2
        assert transaction.options == 2
        assert transaction.signature == b"notavalidsignature"

        if transaction.guardian:
            assert transaction.guardian.bech32() == "erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8"

        assert transaction.guardian_signature == b"notavalidguardiansignature"
