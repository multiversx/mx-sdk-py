from multiversx_sdk.converters.transactions_converter import \
    TransactionsConverter
from multiversx_sdk.core.transaction import Transaction


def test_transaction_converter():
    converter = TransactionsConverter()

    transaction = Transaction(
        nonce=90,
        value=123456789000000000000000000000,
        sender="erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
        receiver="erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
        sender_username="alice",
        receiver_username="bob",
        gas_price=1000000000,
        gas_limit=80000,
        data=b"hello",
        chain_id="localnet"
    )

    tx_as_dict = converter.transaction_to_dictionary(transaction)
    restored_tx = converter.dictionary_to_transaction(tx_as_dict)

    assert transaction == restored_tx


def test_transaction_from_dictionary_with_inner_transaction():
    converter = TransactionsConverter()

    inner_transaction = Transaction(
        nonce=90,
        value=123456789000000000000000000000,
        sender="erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
        receiver="erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx",
        sender_username="alice",
        receiver_username="bob",
        gas_limit=80000,
        data=b"hello",
        chain_id="localnet",
        relayer="erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8"
    )

    relayed_transaction = Transaction(
        nonce=77,
        sender="erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8",
        receiver="erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8",
        gas_limit=180000,
        chain_id="localnet",
        inner_transactions=[inner_transaction]
    )

    tx_as_dict = converter.transaction_to_dictionary(relayed_transaction)
    restored_tx = converter.dictionary_to_transaction(tx_as_dict)

    assert relayed_transaction == restored_tx
