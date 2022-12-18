
from decimal import Decimal

from erdpy_core.token_payment import TokenPayment


def test_with_egld():
    assert str(TokenPayment.egld_from_amount(Decimal("1"))) == "1000000000000000000"
    assert str(TokenPayment.egld_from_amount(Decimal("10"))) == "10000000000000000000"
    assert str(TokenPayment.egld_from_amount(Decimal("100"))) == "100000000000000000000"
    assert str(TokenPayment.egld_from_amount(Decimal("1000"))) == "1000000000000000000000"
    assert str(TokenPayment.egld_from_amount(Decimal("0.1"))) == "100000000000000000"
    assert str(TokenPayment.egld_from_amount(Decimal("0.123456789"))) == "123456789000000000"
    assert str(TokenPayment.egld_from_amount(Decimal("0.123456789123456789"))) == "123456789123456789"
    assert str(TokenPayment.egld_from_amount(Decimal("0.123456789123456789777"))) == "123456789123456789"
    assert str(TokenPayment.egld_from_amount(Decimal("0.123456789123456789777777888888"))) == "123456789123456789"

    assert TokenPayment.egld_from_amount(Decimal("0.1")).to_amount_string() == "0.100000000000000000"
    assert TokenPayment.egld_from_amount(Decimal("1")).to_amount_string() == "1.000000000000000000"
    assert TokenPayment.egld_from_amount(Decimal("10")).to_amount_string() == "10.000000000000000000"
    assert TokenPayment.egld_from_amount(Decimal("100.00")).to_amount_string() == "100.000000000000000000"
    assert TokenPayment.egld_from_amount(Decimal("1000")).to_amount_string() == "1000.000000000000000000"
    assert TokenPayment.egld_from_amount(Decimal("1000")).to_amount_string(normalize=True) == "1000"
    assert TokenPayment.egld_from_amount(Decimal("0.123456789")).to_amount_string() == "0.123456789000000000"
    assert TokenPayment.egld_from_amount(Decimal("0.123456789")).to_amount_string(normalize=True) == "0.123456789"
    assert TokenPayment.egld_from_amount(Decimal("0.123456789123456789777777888888")).to_amount_string() == "0.123456789123456789"

    assert str(TokenPayment.egld_from_integer(0)) == "0"
    assert TokenPayment.egld_from_integer(0).to_amount_string() == "0.000000000000000000"

    assert str(TokenPayment.egld_from_integer(1)) == "1"
    assert TokenPayment.egld_from_integer(1).to_amount_string() == "0.000000000000000001"

    assert str(TokenPayment.egld_from_integer(123456789123456789)) == "123456789123456789"
    assert TokenPayment.egld_from_integer(123456789123456789).to_amount_string() == "0.123456789123456789"


def test_with_fungible_esdt():
    identifier = "USDC-c76f1f"
    num_decimals = 6

    assert str(TokenPayment.fungible_from_amount(identifier, Decimal("1"), num_decimals)) == "1000000"
    assert str(TokenPayment.fungible_from_amount(identifier, Decimal("0.1"), num_decimals)) == "100000"
    assert str(TokenPayment.fungible_from_amount(identifier, Decimal("0.123456789"), num_decimals)) == "123456"
    assert str(TokenPayment.fungible_from_integer(identifier, 1000000, num_decimals)) == "1000000"
    assert TokenPayment.fungible_from_integer(identifier, 1000000, num_decimals).to_amount_string() == "1.000000"


def test_with_meta_esdt():
    identifier = "MEXFARML-28d646"
    num_decimals = 18
    nonce = 12345678

    payment = TokenPayment.meta_esdt_from_amount(identifier, nonce, Decimal("0.1"), num_decimals)
    assert str(payment) == "100000000000000000"
    assert payment.to_amount_string() == "0.100000000000000000"
    assert payment.token_identifier == identifier
    assert payment.token_nonce == nonce


def test_with_nft():
    identifier = "ERDPY-38f249"
    nonce = 1

    payment = TokenPayment.non_fungible(identifier, nonce)
    assert str(payment) == "1"
    assert payment.to_amount_string() == "1"
    assert payment.token_identifier == identifier
    assert payment.token_nonce == nonce
