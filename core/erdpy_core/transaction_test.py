
from erdpy_core.address import Address
from erdpy_core.token_payment import TokenPayment
from erdpy_core.transaction import Transaction
from erdpy_core.transaction_payload import TransactionPayload


def test_serialize_for_signing():
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
