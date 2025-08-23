import pytest

from fguess import analyze_number_format


class TestAlignmentAndPadding:
    """Test string alignment and padding detection."""

    @pytest.mark.parametrize("input_str,expected_int,expected_str", [
        ("  34", 'f"{variable:>4d}"', 'f"{variable:>4}"'),
        ("34  ", 'f"{variable:<4d}"', 'f"{variable:<4}"'),
        (" 34 ", 'f"{variable:^4d}"', 'f"{variable:^4}"'),
    ])
    def test_basic_alignment(self, input_str, expected_int, expected_str):
        formats = analyze_number_format(input_str)
        assert ('int', expected_int) in formats
        assert ('str', expected_str) in formats

    @pytest.mark.parametrize("input_str,expected_int,expected_str", [
        ("__34", 'f"{variable:_>4d}"', 'f"{variable:_>4}"'),
        ("34__", 'f"{variable:_<4d}"', 'f"{variable:_<4}"'),
        ("_34_", 'f"{variable:_^4d}"', 'f"{variable:_^4}"'),
        ("**34", 'f"{variable:*>4d}"', 'f"{variable:*>4}"'),
    ])
    def test_custom_fill_alignment(self, input_str, expected_int, expected_str):
        formats = analyze_number_format(input_str)
        assert ('int', expected_int) in formats
        assert ('str', expected_str) in formats

    @pytest.mark.parametrize("input_str,expected_formats", [
        ("0034", [('int', 'f"{variable:04d}"'), ('float', 'f"{variable:04.0f}"')]),
        ("0340.00", [('float', 'f"{variable:07.2f}"')]),
        ("00000123", [('int', 'f"{variable:08d}"')]),
        ("007", [('int', 'f"{variable:03d}"')]),
    ])
    def test_zero_padding(self, input_str, expected_formats):
        formats = analyze_number_format(input_str)
        for expected_format in expected_formats:
            assert expected_format in formats

    @pytest.mark.parametrize("input_str,should_have_center,should_have_literal", [
        ("  4      ", False, True),  # Unequal padding (2 vs 6)
        (" 42  ", False, True),      # Slightly unequal (1 vs 2)
        ("  42   ", False, True),    # Off-by-one (2 vs 3)
        ("    123        ", False, True),  # Large unequal (4 vs 8)
        ("  42  ", True, False),     # Equal padding (2 vs 2)
        (" 42 ", True, False),       # Single equal padding (1 vs 1)
    ])
    def test_padding_edge_cases(self, input_str, should_have_center, should_have_literal):
        """Test that padding is correctly classified as center alignment vs literals."""
        formats = analyze_number_format(input_str)

        has_center = any('^' in f for t, f in formats)
        assert has_center == should_have_center, f"Center alignment detection failed for '{input_str}'"

        if should_have_literal:
            # Check that it's treated as literals (contains the actual padding)
            expected_literal = input_str.replace(input_str.strip(), '{variable}')
            assert any(expected_literal in f for t, f in formats), f"Should treat '{input_str}' as literals"

    def test_very_unequal_padding_right_align(self):
        """Right-only padding should be left alignment."""
        formats = analyze_number_format("42      ")  # 0 left, 6 right
        assert ('int', 'f"{variable:<8d}"') in formats, "Should be left alignment"

    def test_mixed_padding_as_literals(self):
        """Different padding on each side should be treated as literals."""
        formats = analyze_number_format("  34_")
        assert any(' {variable}_' in f for t, f in formats)


class TestNumericFormats:
    """Test detection of various numeric format types."""

    @pytest.mark.parametrize("input_str,expected_format", [
        ("3400.00", 'f"{variable:.2f}"'),
        (" 340.00", 'f"{variable:>7.2f}"'),
        ("3.14159", 'f"{variable:.5f}"'),
        ("1.5", 'f"{variable:.1f}"'),
    ])
    def test_decimal_formats(self, input_str, expected_format):
        formats = analyze_number_format(input_str)
        assert ('float', expected_format) in formats

    @pytest.mark.parametrize("input_str,expected_formats", [
        ("3,400", [('int', 'f"{variable:,}"'), ('float', 'f"{variable:,.0f}"')]),
        ("3,400.00", [('float', 'f"{variable:,.2f}"')]),
        ("1,234,567", [('int', 'f"{variable:,}"')]),
        ("  3,400.00", [('float', 'f"{variable:>10,.2f}"')]),
    ])
    def test_comma_separators(self, input_str, expected_formats):
        formats = analyze_number_format(input_str)
        for expected_format in expected_formats:
            assert expected_format in formats

    def test_comma_with_width(self):
        # When there's a width, 'd' should be kept
        formats = analyze_number_format("     1,234")
        assert any(',' in f and 'd' in f for t, f in formats if t == 'int')

    @pytest.mark.parametrize("input_str,expected_formats", [
        ("3_400", [('int', 'f"{variable:_}"'), ('float', 'f"{variable:_.0f}"')]),
        ("3_400.00", [('float', 'f"{variable:_.2f}"')]),
        ("1_234_567", [('int', 'f"{variable:_}"')]),
        ("1_000_000", [('int', 'f"{variable:_}"'), ('float', 'f"{variable:_.0f}"')]),
        ("  3_400.00", [('float', 'f"{variable:>10_.2f}"')]),
        ("1_234.56", [('float', 'f"{variable:_.2f}"')]),
        ("$1_000_000", [('int', 'f"${variable:_}"'), ('float', 'f"${variable:_.0f}"')]),
        ("1_999.99€", [('float', 'f"{variable:_.2f}€"')]),
    ])
    def test_underscore_separators(self, input_str, expected_formats):
        formats = analyze_number_format(input_str)
        for expected_format in expected_formats:
            assert expected_format in formats

    def test_underscore_with_width(self):
        # When there's a width, 'd' should be kept
        formats = analyze_number_format("     1_234")
        assert any('_' in f and 'd' in f for t, f in formats if t == 'int')

    @pytest.mark.parametrize("input_str,expected_format", [
        ("0x4", 'f"{variable:#x}"'),
        ("0x04", 'f"{variable:#04x}"'),
        ("0xff", 'f"{variable:#x}"'),
        ("0x00ff", 'f"{variable:#06x}"'),
        ("ff", 'f"{variable:x}"'),
        ("FF", 'f"{variable:X}"'),
        ("00ff", 'f"{variable:04x}"'),
    ])
    def test_hex_formats(self, input_str, expected_format):
        formats = analyze_number_format(input_str)
        assert ('int', expected_format) in formats

    @pytest.mark.parametrize("input_str,expected_format", [
        ("34%", 'f"{variable:.0%}"'),
        ("34.0%", 'f"{variable:.1%}"'),
        ("34.56%", 'f"{variable:.2%}"'),
        ("Score: 85%", 'f"Score: {variable:.0%}"'),
        ("+12.5%", 'f"{variable:+.1%}"'),
        ("-5.5%", 'f"{variable:.1%}"'),
    ])
    def test_percentage_formats(self, input_str, expected_format):
        formats = analyze_number_format(input_str)
        assert ('float', expected_format) in formats

    @pytest.mark.parametrize("input_str,expected_format", [
        ("  25%", 'f"{variable:>5.0%}"'),
        ("25%  ", 'f"{variable:<5.0%}"'),
        (" 25% ", 'f"{variable:^5.0%}"'),
        ("  34.5%", 'f"{variable:>7.1%}"'),
        ("34.5%  ", 'f"{variable:<7.1%}"'),
        (" 34.5% ", 'f"{variable:^7.1%}"'),
        ("**25%", 'f"{variable:*>5.0%}"'),
        ("__34.5%", 'f"{variable:_>7.1%}"'),
        ("25%**", 'f"{variable:*<5.0%}"'),
        (" +12.5%", 'f"{variable:>+7.1%}"'),
    ])
    def test_percentage_alignment(self, input_str, expected_format):
        formats = analyze_number_format(input_str)
        assert ('float', expected_format) in formats


class TestLiteralsAndPrefixSuffix:
    """Test detection of literal prefixes and suffixes."""

    def test_currency_prefix(self):
        formats = analyze_number_format("$34.50")
        assert ('float', 'f"${variable:.2f}"') in formats
        assert ('str', 'f"${variable}"') in formats

    def test_currency_suffix(self):
        formats = analyze_number_format("99.99€")
        assert ('float', 'f"{variable:.2f}€"') in formats

    def test_label_with_number(self):
        formats = analyze_number_format("Item #42")
        assert ('int', 'f"Item #{variable:d}"') not in formats
        assert ('str', 'f"Item #{variable}"') in formats

    def test_parentheses(self):
        formats = analyze_number_format("(123)")
        assert ('int', 'f"({variable:d})"') not in formats

    def test_units(self):
        formats = analyze_number_format("5.5km")
        assert ('float', 'f"{variable:.1f}km"') in formats

    def test_complex_suffix(self):
        formats = analyze_number_format("123.45 USD/month")
        assert ('float', 'f"{variable:.2f} USD/month"') in formats

    def test_prefix_and_suffix(self):
        formats = analyze_number_format("Total: $50.00 USD")
        assert ('float', 'f"Total: ${variable:.2f} USD"') in formats

    def test_hex_with_literals(self):
        formats = analyze_number_format("Address: 0x1234")
        assert ('int', 'f"Address: {variable:#x}"') in formats

    def test_hex_with_padding_as_literals(self):
        """Hex numbers with literal padding should be treated as such."""
        formats = analyze_number_format("  0x42")
        assert any('  {variable:#x}' in f for t, f in formats)


class TestSignAndSpecialCases:
    """Test sign handling and special numeric cases."""

    def test_sign_prefix(self):
        formats = analyze_number_format("+42")
        assert ('int', 'f"{variable:+d}"') in formats

    def test_negative_number(self):
        formats = analyze_number_format("-42")
        assert not any(t == 'int' for t, f in formats)

    def test_sign_with_padding(self):
        formats = analyze_number_format(" +42")
        assert any('+' in f for t, f in formats if t == 'int')

    def test_zero_padded_with_sign(self):
        formats = analyze_number_format("+0034")
        assert any('+' in f and '05' in f for t, f in formats)

    def test_underscore_with_left_align(self):
        formats = analyze_number_format("1_000  ")
        assert ('int', 'f"{variable:<7_d}"') in formats

    def test_underscore_with_center_align(self):
        formats = analyze_number_format(" 1_000 ")
        assert ('int', 'f"{variable:^7_d}"') in formats


class TestComplexCombinations:
    """Test complex combinations of formatting features."""

    def test_currency_with_comma(self):
        formats = analyze_number_format("$1,234.56")
        assert ('float', 'f"${variable:,.2f}"') in formats

    def test_currency_with_underscore(self):
        formats = analyze_number_format("$1_234.56")
        assert ('float', 'f"${variable:_.2f}"') in formats

    def test_percentage_with_label(self):
        formats = analyze_number_format("Accuracy: 98.5%")
        assert ('float', 'f"Accuracy: {variable:.1%}"') in formats

    def test_right_aligned_with_comma_and_decimal(self):
        formats = analyze_number_format("  1,234.56")
        assert any(',' in f and '.2f' in f for t, f in formats if t == 'float')

    def test_right_aligned_with_underscore_and_decimal(self):
        formats = analyze_number_format("  1_234.56")
        assert any('_' in f and '.2f' in f for t, f in formats if t == 'float')

    def test_centered_decimal(self):
        formats = analyze_number_format(" 34.5 ")
        assert any('^' in f and '.1f' in f for t, f in formats if t == 'float')

    def test_custom_fill_with_decimal(self):
        formats = analyze_number_format("**34.50")
        assert any('*>' in f and '.2f' in f for t, f in formats if t == 'float')


class TestEdgeCasesAndValidation:
    """Test edge cases and validation logic."""

    def test_single_digit(self):
        formats = analyze_number_format("5")
        assert ('int', 'f"{variable:d}"') not in formats

    def test_number_zero(self):
        formats = analyze_number_format("0")
        assert not any(t == 'int' for t, f in formats)

    def test_very_long_number(self):
        formats = analyze_number_format("123456789")
        assert not any(t == 'int' for t, f in formats)

    def test_plain_string(self):
        formats = analyze_number_format("hello")
        assert not formats, "No format specifications"

    def test_string_with_numbers(self):
        formats = analyze_number_format("test123")
        assert any('test' in f and 'variable' in f for t, f in formats)

    def test_only_padding_characters(self):
        formats = analyze_number_format("___")
        assert not formats, "No format specifications"

    def test_just_decimal_point(self):
        formats = analyze_number_format(".")
        assert not formats, "No format specifications"

    def test_empty_string(self):
        formats = analyze_number_format("")
        assert not formats, "No format specifications"

    def test_trailing_decimal_place(self):
        formats = analyze_number_format("5.")
        assert ('float', 'f"{variable:.0f}"') not in formats

    def test_no_duplicate_formats(self):
        """Ensure no duplicate format specifications are returned."""
        formats = analyze_number_format("1234.56")
        seen = set()
        for type_name, format_spec in formats:
            key = (type_name, format_spec)
            assert key not in seen, f"Duplicate format found: {key}"
            seen.add(key)

    def test_no_string_format_with_percent(self):
        """String format should always be present when there are literals."""
        formats = analyze_number_format("100%")
        assert all(t != 'str' for t, _ in formats), "string format found for 100%"

    def test_string_format_always_present_with_literals(self):
        """String format should always be present when there are literals."""
        test_cases = ["$100", "Item #5", "(42)"]
        for test in test_cases:
            formats = analyze_number_format(test)
            assert any(t == 'str' for t, _ in formats), f"No string format for {test}"


class TestDatetimeFormats:
    """Test datetime format detection and priority."""

    @pytest.mark.parametrize("input_str,expected_format", [
        ("2030-01-24", 'f"{variable:%Y-%m-%d}"'),
        ("01/24/2030", 'f"{variable:%m/%d/%Y}"'),
        ("01/24/30", 'f"{variable:%m/%d/%y}"'),
        ("24 Jan 2030", 'f"{variable:%d %b %Y}"'),
    ])
    def test_basic_date_formats(self, input_str, expected_format):
        formats = analyze_number_format(input_str)
        assert ('datetime', expected_format) in formats
        # Should prioritize datetime over numeric due to datetime structure
        datetime_formats = [f for t, f in formats if t == 'datetime']
        assert len(datetime_formats) > 0

    def test_month_day_year_format_with_comma(self):
        formats = analyze_number_format("Jan 24, 2030")
        # Note: the comma might not be in the specific formats, but similar patterns should be
        datetime_formats = [f for t, f in formats if t == 'datetime']
        assert len(datetime_formats) > 0

    @pytest.mark.parametrize("input_str,expected_format", [
        ("05:45", 'f"{variable:%H:%M}"'),
        ("05:45:13", 'f"{variable:%H:%M:%S}"'),
        ("05:45 AM", 'f"{variable:%I:%M %p}"'),
        ("05:45AM", 'f"{variable:%I:%M%p}"'),
    ])
    def test_time_formats(self, input_str, expected_format):
        formats = analyze_number_format(input_str)
        assert ('datetime', expected_format) in formats

    def test_iso_datetime_format(self):
        formats = analyze_number_format("2030-01-24 05:45")
        datetime_formats = [f for t, f in formats if t == 'datetime']
        assert len(datetime_formats) > 0
        # Should find a format that includes both date and time components
        assert any('Y' in f and 'H' in f for f in datetime_formats)

    def test_iso_datetime_with_seconds(self):
        formats = analyze_number_format("2030-01-24 05:45:13")
        assert any('Y-%m-%d %H:%M:%S' in f for t, f in formats if t == 'datetime')

    def test_full_weekday_datetime(self):
        formats = analyze_number_format("Thursday January 24 2030 05:45:13")
        datetime_formats = [f for t, f in formats if t == 'datetime']
        assert len(datetime_formats) > 0

    def test_date_with_literals(self):
        formats = analyze_number_format("Date: 2030-01-24")
        # Should detect datetime part within literals
        datetime_formats = [f for t, f in formats if t == 'datetime']
        assert len(datetime_formats) > 0
        # Should have format with literal prefix
        assert any('Date:' in f for t, f in formats if t == 'datetime')

    def test_datetime_priority_over_numbers(self):
        """Datetime should be prioritized when structure suggests datetime."""
        formats = analyze_number_format("2030-01-24")
        # Datetime should appear early in results due to datetime structure
        datetime_index = next((i for i, (t, f) in enumerate(formats) if t == 'datetime'), float('inf'))
        numeric_index = next((i for i, (t, f) in enumerate(formats) if t in ('int', 'float')), float('inf'))
        assert datetime_index < numeric_index, "Datetime should be prioritized over numeric for structured dates"

    def test_single_number_datetime_lower_priority(self):
        """Single numeric datetime formats should have lower priority."""
        formats = analyze_number_format("2030")
        # Should have datetime format for year, but it should come after numeric formats
        assert formats == [
            ('float', 'f"{variable:.0f}"'),
            ('datetime', 'f"{variable:%Y}"'),
        ]
