from decimal import Decimal

from multiversx_sdk.abi.managed_decimal_value import ManagedDecimalValue


class TestManagedDecimalValueTest:

    def test_expected_values(self):
        value = ManagedDecimalValue(1, 2)

        assert not value.is_variable
        assert value.get_precision() == 3
        assert value.to_string() == "1.00"
        assert value.get_payload() == Decimal(1)

        value = ManagedDecimalValue("1.234", 3)
        assert value.get_precision() == 4
        assert value.to_string() == "1.234"
        assert value.get_payload() == Decimal("1.234")

        value = ManagedDecimalValue("1.3", 2)
        assert value.get_precision() == 3
        assert value.to_string() == "1.30"
        assert value.get_payload() == Decimal("1.3")

        value = ManagedDecimalValue(13, 2)
        assert value.get_precision() == 4
        assert value.to_string() == "13.00"
        assert value.get_payload() == Decimal(13)

        value = ManagedDecimalValue("2.7", 2)
        assert value.get_precision() == 3
        assert value.to_string() == "2.70"
        assert value.get_payload() == Decimal("2.7")

    def test_compare_values(self):
        value = ManagedDecimalValue(1, 2)

        assert value != ManagedDecimalValue(2, 2)
        assert value != ManagedDecimalValue(1, 3)
        assert value == ManagedDecimalValue(1, 2)
