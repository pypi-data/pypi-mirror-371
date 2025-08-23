import pytest

from fguess import get_test_value


class TestGetTestValue:
    """Test the get_test_value function."""

    # ===== String Type Tests =====
    @pytest.mark.parametrize("input_str,expected", [
        ("123", "123"),
        ("$123", "123"),
        ("123km", "123"),
        ("  123  ", "123"),
        ("hello", "hello"),
    ])
    def test_get_test_value_str(self, input_str, expected):
        assert get_test_value(input_str, "str") == expected

    # ===== Integer Type Tests =====
    @pytest.mark.parametrize("input_str,expected", [
        ("123", 123),
        ("-123", -123),
        ("$123", 123),
        ("1,234", 1234),
        ("1_234", 1234),
        ("1_000_000", 1000000),
        ("$1_234", 1234),
        ("0xff", 255),
        ("ff", 255),
        ("FF", 255),
        ("0034", 34),
    ])
    def test_get_test_value_int(self, input_str, expected):
        assert get_test_value(input_str, "int") == expected

    def test_get_test_value_int_padded(self):
        assert get_test_value("  123  ", "int") == 123

    def test_get_test_value_int_invalid(self):
        assert get_test_value("not_a_number", "int") == 0

    # ===== Float Type Tests =====
    def test_get_test_value_float_simple(self):
        assert get_test_value("123.45", "float") == 123.45

    def test_get_test_value_float_negative(self):
        assert get_test_value("-123.45", "float") == -123.45

    def test_get_test_value_float_percentage(self):
        assert get_test_value("34.5%", "float") == 0.345

    def test_get_test_value_float_integer(self):
        assert get_test_value("123", "float") == 123.0

    def test_get_test_value_float_comma(self):
        assert get_test_value("1,234.56", "float") == 1234.56

    def test_get_test_value_float_underscore(self):
        assert get_test_value("1_234.56", "float") == 1234.56

    def test_get_test_value_float_large_underscore(self):
        assert get_test_value("1_000_000.99", "float") == 1000000.99

    def test_get_test_value_float_underscore_with_prefix(self):
        assert get_test_value("$1_234.56", "float") == 1234.56

    def test_get_test_value_float_zero_padded(self):
        assert get_test_value("00123.45", "float") == 123.45

    def test_get_test_value_float_with_prefix(self):
        assert get_test_value("$99.99", "float") == 99.99

    def test_get_test_value_float_padded(self):
        assert get_test_value("  123.45  ", "float") == 123.45

    def test_get_test_value_float_invalid(self):
        assert get_test_value("not_a_number", "float") == 0.0

    # ===== Edge Cases for get_test_value =====
    def test_get_test_value_empty_string(self):
        assert get_test_value("", "str") == ""
        assert get_test_value("", "int") == 0
        assert get_test_value("", "float") == 0.0

    def test_get_test_value_just_sign(self):
        assert get_test_value("+", "int") == 0
        assert get_test_value("-", "float") == 0.0

    def test_get_test_value_zero(self):
        assert get_test_value("0", "int") == 0
        assert get_test_value("0", "float") == 0.0
        assert get_test_value("0", "str") == "0"

    def test_get_test_value_underscore_only(self):
        assert get_test_value("_", "int") == 0
        assert get_test_value("_", "float") == 0.0
        assert get_test_value("_", "str") == "_"


class TestGetTestValueDatetime:
    """Test get_test_value function for datetime types."""

    def test_get_test_value_datetime_iso_date(self):
        from datetime import datetime
        result = get_test_value("2030-01-24", "datetime")
        assert isinstance(result, datetime)
        assert result.year == 2030
        assert result.month == 1
        assert result.day == 24

    def test_get_test_value_datetime_us_date(self):
        from datetime import datetime
        result = get_test_value("01/24/2030", "datetime")
        assert isinstance(result, datetime)
        assert result.year == 2030
        assert result.month == 1
        assert result.day == 24

    def test_get_test_value_datetime_time(self):
        from datetime import datetime
        result = get_test_value("05:45", "datetime")
        assert isinstance(result, datetime)
        assert result.hour == 5
        assert result.minute == 45

    def test_get_test_value_datetime_full(self):
        from datetime import datetime
        result = get_test_value("2030-01-24 05:45:13", "datetime")
        assert isinstance(result, datetime)
        assert result.year == 2030
        assert result.month == 1
        assert result.day == 24
        assert result.hour == 5
        assert result.minute == 45
        assert result.second == 13

    def test_get_test_value_datetime_month_name(self):
        from datetime import datetime
        result = get_test_value("Jan 24 2030", "datetime")
        assert isinstance(result, datetime)
        assert result.year == 2030
        assert result.month == 1
        assert result.day == 24

    def test_get_test_value_datetime_weekday(self):
        from datetime import datetime
        result = get_test_value("Thursday", "datetime")
        assert isinstance(result, datetime)
        # Should return some valid datetime

    def test_get_test_value_datetime_invalid(self):
        from datetime import datetime
        result = get_test_value("not-a-date", "datetime")
        assert isinstance(result, datetime)
        # Should return default datetime when parsing fails
        assert result.year == 2030  # Default from the implementation

    def test_get_test_value_datetime_with_literals(self):
        from datetime import datetime
        result = get_test_value("Date: 2030-01-24", "datetime")
        assert isinstance(result, datetime)
        assert result.year == 2030
        assert result.month == 1
        assert result.day == 24
