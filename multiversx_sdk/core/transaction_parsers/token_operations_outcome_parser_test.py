from multiversx_sdk.core import Address
from multiversx_sdk.core.codec import encode_unsigned_number
from multiversx_sdk.core.transaction_parsers.token_operations_outcome_parser import \
    TokenOperationsOutcomeParser
from multiversx_sdk.core.transaction_parsers.transaction_on_network_wrapper import (
    ContractResultsWrapper, TransactionEventTopicWrapper,
    TransactionEventWrapper, TransactionLogsWrapper,
    TransactionOnNetworkWrapper)
from multiversx_sdk.core.transactions_factories.transactions_factory_config import \
    TransactionsFactoryConfig

frank = Address.new_from_bech32("erd1kdl46yctawygtwg2k462307dmz2v55c605737dp3zkxh04sct7asqylhyv")
grace = Address.new_from_bech32("erd1r69gk66fmedhhcg24g2c5kn2f2a5k4kvpr6jfw67dn2lyydd8cfswy6ede")
parser = TokenOperationsOutcomeParser(TransactionsFactoryConfig("D"))


def test_parse_issue_fungible():
    transaction = TransactionOnNetworkWrapper(
        ContractResultsWrapper([]),
        TransactionLogsWrapper([
            TransactionEventWrapper(
                address=frank,
                identifier="issue",
                topics=[TransactionEventTopicWrapper("FOOBAR".encode())],
                data=""
            )
        ])
    )

    outcome = parser.parse_issue_fungible(transaction)
    assert outcome.token_identifier == "FOOBAR"


def test_parse_set_special_role():
    transaction = TransactionOnNetworkWrapper(
        ContractResultsWrapper([]),
        TransactionLogsWrapper([
            TransactionEventWrapper(
                address=grace,
                identifier="ESDTSetRole",
                topics=[
                    TransactionEventTopicWrapper("FOOBAR".encode()),
                    TransactionEventTopicWrapper("".encode()),
                    TransactionEventTopicWrapper("".encode()),
                    TransactionEventTopicWrapper("ESDTRoleLocalMint".encode()),
                    TransactionEventTopicWrapper("ESDTRoleLocalBurn".encode())
                ],
                data=""
            )
        ])
    )

    outcome = parser.parse_set_special_role(transaction)
    assert outcome.token_identifier == "FOOBAR"
    assert outcome.roles == ["ESDTRoleLocalMint", "ESDTRoleLocalBurn"]
    assert outcome.user_address == grace.to_bech32()


def test_parse_local_mint():
    transaction = TransactionOnNetworkWrapper(
        ContractResultsWrapper([]),
        TransactionLogsWrapper([
            TransactionEventWrapper(
                address=grace,
                identifier="ESDTLocalMint",
                topics=[
                    TransactionEventTopicWrapper("FOOBAR".encode()),
                    TransactionEventTopicWrapper("".encode()),
                    TransactionEventTopicWrapper(encode_unsigned_number(200))
                ],
                data=""
            )
        ])
    )

    outcome = parser.parse_local_mint(transaction)
    assert outcome.token_identifier == "FOOBAR"
    assert outcome.nonce == 0
    assert outcome.minted_supply == 200
    assert outcome.user_address == grace.to_bech32()


def test_parse_nft_create():
    transaction = TransactionOnNetworkWrapper(
        ContractResultsWrapper([]),
        TransactionLogsWrapper([
            TransactionEventWrapper(
                address=grace,
                identifier="ESDTNFTCreate",
                topics=[
                    TransactionEventTopicWrapper("FOOBAR".encode()),
                    TransactionEventTopicWrapper(encode_unsigned_number(42)),
                    TransactionEventTopicWrapper(encode_unsigned_number(1))
                ],
                data=""
            )
        ])
    )

    outcome = parser.parse_nft_create(transaction)
    assert outcome.token_identifier == "FOOBAR"
    assert outcome.nonce == 42
    assert outcome.initial_quantity == 1
