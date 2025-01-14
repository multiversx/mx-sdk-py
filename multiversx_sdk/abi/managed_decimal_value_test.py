from decimal import Decimal

from multiversx_sdk.abi.managed_decimal_value import ManagedDecimalValue
from multiversx_sdk.abi.managed_decimal_signed_value import ManagedDecimalSignedValue


class TestManagedDecimalValueTest:

    def test_expected_values(self):
        value = ManagedDecimalValue(1, 2)
        assert not value.is_variable
        assert value.get_precision() == 3
        assert value.get_payload() == Decimal(1)

        value = ManagedDecimalValue("1.234", 3)
        assert value.get_precision() == 4
        assert value.get_payload() == Decimal("1.234")

        value = ManagedDecimalValue("1.3", 2)
        assert value.get_precision() == 3
        assert value.get_payload() == Decimal("1.3")

        value = ManagedDecimalValue(13, 2)
        assert value.get_precision() == 4
        assert value.get_payload() == Decimal(13)

        value = ManagedDecimalValue("2.7", 2)
        assert value.get_precision() == 3
        assert value.get_payload() == Decimal("2.7")

        value = ManagedDecimalValue(value="0.000000000000000001", scale=18)
        assert value.get_precision() == 19
        assert value.get_payload() == Decimal("0.000000000000000001")

    def test_compare_values(self):
        value = ManagedDecimalValue(1, 2)

        assert value != ManagedDecimalValue(2, 2)
        assert value != ManagedDecimalValue(1, 3)
        assert value == ManagedDecimalValue(1, 2)


class TestManagedDecimalSignedValueTest:

    def test_expected_values(self):
        value = ManagedDecimalSignedValue(1, 2)
        assert not value.is_variable
        assert value.get_precision() == 3
        assert value.get_payload() == Decimal(1)

        value = ManagedDecimalSignedValue(-1, 2)
        assert not value.is_variable
        assert value.get_precision() == 4
        assert value.get_payload() == Decimal(-1)

        value = ManagedDecimalSignedValue("1.234", 3)
        assert value.get_precision() == 4
        assert value.get_payload() == Decimal("1.234")

        value = ManagedDecimalSignedValue("1.3", 2)
        assert value.get_precision() == 3
        assert value.get_payload() == Decimal("1.3")

        value = ManagedDecimalSignedValue(13, 2)
        assert value.get_precision() == 4
        assert value.get_payload() == Decimal(13)

        value = ManagedDecimalSignedValue("2.7", 2)
        assert value.get_precision() == 3
        assert value.get_payload() == Decimal("2.7")

        value = ManagedDecimalSignedValue(value="0.000000000000000001", scale=18)
        assert value.get_precision() == 19
        assert value.get_payload() == Decimal("0.000000000000000001")

    def test_compare_values(self):
        value = ManagedDecimalSignedValue(1, 2)

        assert value != ManagedDecimalSignedValue(2, 2)
        assert value != ManagedDecimalSignedValue(1, 3)
        assert value == ManagedDecimalSignedValue(1, 2)
