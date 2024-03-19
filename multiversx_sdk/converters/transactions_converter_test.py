from multiversx_sdk.converters.transactions_converter import \
    TransactionsConverter
from multiversx_sdk.core.transaction import Transaction


class TransactionMatcher:
    def __init__(self, transaction: Transaction) -> None:
        self.expected = transaction

    def __eq__(self, actual: object) -> bool:
        if isinstance(actual, Transaction):
            return self.expected.chain_id == actual.chain_id and \
                self.expected.sender == actual.sender and \
                self.expected.receiver == actual.receiver and \
                self.expected.gas_limit == actual.gas_limit and \
                self.expected.data == actual.data and \
                self.expected.nonce == actual.nonce and \
                self.expected.value == actual.value and \
                self.expected.gas_price == actual.gas_price and \
                self.expected.sender_username == actual.sender_username and \
                self.expected.receiver_username == actual.receiver_username and \
                self.expected.version == actual.version and \
                self.expected.options == actual.options and \
                self.expected.guardian == actual.guardian and \
                self.expected.signature == actual.signature and \
                self.expected.guardian_signature == actual.guardian_signature
        return False


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

    assert TransactionMatcher(transaction) == restored_tx
