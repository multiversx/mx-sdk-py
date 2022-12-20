
from erdpy_core.address import Address
from erdpy_core.interfaces import IAddress, ITransactionValue
from erdpy_core.token_payment import TokenPayment
from erdpy_core.transaction_builders.esdt_builders import (
    ESDTIssueBuilder, ESDTNFTTransferBuilder, ESDTTransferBuilder,
    MultiESDTNFTTransferBuilder)


class DummyConfig:
    def __init__(self) -> None:
        self.chain_id = "D"
        self.min_gas_price = 1000000000
        self.min_gas_limit = 50000
        self.gas_limit_per_byte = 1500

        self.gas_limit_esdt_transfer = 200000
        self.additional_gas_for_esdt_transfer = 100000

        self.gas_limit_esdt_nft_transfer = 200000
        self.additional_gas_for_esdt_nft_transfer = 800000

        self.gas_limit_esdt_issue = 60000000
        self.issue_cost: ITransactionValue = 50000000000000000
        self.esdt_contract_address: IAddress = Address.from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u")


def test_esdt_issue_builder():
    issuer = Address.from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")

    builder = ESDTIssueBuilder(
        config=DummyConfig(),
        issuer=issuer,
        token_name="FOO",
        token_ticker="FOO",
        initial_supply=1000000000000,
        num_decimals=8,
        can_freeze=True,
        can_mint=True,
        can_upgrade=True
    )

    payload = builder.build_payload()
    tx = builder.build_transaction()

    assert payload.data == b"issue@464f4f@464f4f@e8d4a51000@08@63616e467265657a65@74727565@63616e4d696e74@74727565@63616e55706772616465@74727565"
    assert tx.chainID == "D"
    assert tx.sender == issuer
    assert tx.receiver.bech32() == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"
    assert tx.gas_limit == 50000 + payload.length() * 1500 + 60000000
    assert tx.data.encoded() == payload.encoded()


def test_esdt_transfer_builder():
    alice = Address.from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
    bob = Address.from_bech32("erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx")
    payment = TokenPayment.fungible_from_amount("COUNTER-8b028f", "100.00", 2)

    builder = ESDTTransferBuilder(
        config=DummyConfig(),
        sender=alice,
        receiver=bob,
        payment=payment
    )

    payload = builder.build_payload()
    tx = builder.build_transaction()
    assert payload.data == b"ESDTTransfer@434f554e5445522d386230323866@2710"
    assert tx.chainID == "D"
    assert tx.sender == alice
    assert tx.receiver == bob
    assert tx.gas_limit == 50000 + payload.length() * 1500 + 100000 + 200000
    assert tx.data.encoded() == payload.encoded()


def test_esdt_nft_transfer_builder():
    alice = Address.from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
    bob = Address.from_bech32("erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx")
    payment = TokenPayment.non_fungible("ERDPY-38f249", 1)

    builder = ESDTNFTTransferBuilder(
        config=DummyConfig(),
        sender=alice,
        destination=bob,
        payment=payment
    )

    payload = builder.build_payload()
    tx = builder.build_transaction()
    assert payload.data == b"ESDTNFTTransfer@45524450592d333866323439@01@01@8049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f8"
    assert tx.chainID == "D"
    assert tx.sender == alice
    assert tx.receiver == alice
    assert tx.gas_limit == 50000 + payload.length() * 1500 + 200000 + 800000
    assert tx.data.encoded() == payload.encoded()


def test_multi_esdt_nft_transfer_builder():
    alice = Address.from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
    bob = Address.from_bech32("erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx")

    payment_one = TokenPayment.non_fungible("ERDPY-38f249", 1)
    payment_two = TokenPayment.fungible_from_amount("BAR-c80d29", "10.00", 18)

    builder = MultiESDTNFTTransferBuilder(
        config=DummyConfig(),
        sender=alice,
        destination=bob,
        payments=[payment_one, payment_two]
    )

    payload = builder.build_payload()
    tx = builder.build_transaction()
    assert payload.data == b"MultiESDTNFTTransfer@8049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f8@02@45524450592d333866323439@01@01@4241522d633830643239@@8ac7230489e80000"
    assert tx.chainID == "D"
    assert tx.sender == alice
    assert tx.receiver == alice
    assert tx.gas_limit == 50000 + payload.length() * 1500 + 2 * (200000 + 800000)
    assert tx.data.encoded() == payload.encoded()
