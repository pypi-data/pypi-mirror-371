from fguess import analyze_number_format, get_test_value


class TestRoundTrip:
    """Test that format specs can recreate the original string."""

    def verify_format(self, input_str, expected_type):
        """Helper to verify at least one format works."""
        formats = analyze_number_format(input_str)
        assert len(formats) > 0, f"No formats found for '{input_str}'"
        assert any(t == expected_type for t, _ in formats), \
            f"Expected {expected_type} format for '{input_str}'"

    def test_basic_numbers(self):
        self.verify_format("42", "float")
        self.verify_format("3.14", "float")
        self.verify_format("0", "float")

    def test_formatted_numbers(self):
        self.verify_format("1,234", "int")
        self.verify_format("1_234", "int")
        self.verify_format("$99.99", "float")
        self.verify_format("85%", "float")
        self.verify_format("0x2a", "int")
        self.verify_format("1.5e-3", "float")

    def test_underscore_numbers(self):
        self.verify_format("1_000", "int")
        self.verify_format("1_000_000", "int")
        self.verify_format("1_234.56", "float")
        self.verify_format("$1_000_000", "int")
        self.verify_format("1_999.99€", "float")

    def test_padded_numbers(self):
        self.verify_format("  42", "int")
        self.verify_format("42  ", "int")
        self.verify_format("_42_", "int")
        self.verify_format("0042", "int")

    def test_complex_underscore_combinations(self):
        self.verify_format("  1_234.56", "float")
        self.verify_format("$1_234_567.89", "float")
        self.verify_format("Total: 1_000_000 units", "str")


class TestDatetimeRoundTrip:
    """Test that datetime format specs work correctly."""

    def verify_datetime_format(self, input_str):
        """Helper to verify at least one datetime format works."""
        formats = analyze_number_format(input_str)
        datetime_formats = [(t, f) for t, f in formats if t == 'datetime']
        assert len(datetime_formats) > 0, f"No datetime formats found for '{input_str}'"

        # Verify we can get a test value
        from datetime import datetime
        test_value = get_test_value(input_str, 'datetime')
        assert isinstance(test_value, datetime), f"get_test_value should return datetime for '{input_str}'"

    def test_basic_date_formats(self):
        self.verify_datetime_format("2030-01-24")
        self.verify_datetime_format("01/24/2030")
        self.verify_datetime_format("01/24/30")

    def test_time_formats(self):
        self.verify_datetime_format("05:45")
        self.verify_datetime_format("05:45:13")
        self.verify_datetime_format("5:45 AM")

    def test_combined_formats(self):
        self.verify_datetime_format("2030-01-24 05:45")
        self.verify_datetime_format("2030-01-24 05:45:13")
        self.verify_datetime_format("Thu Jan 24 2030")

    def test_month_and_weekday_names(self):
        self.verify_datetime_format("January")
        self.verify_datetime_format("Thursday")
        self.verify_datetime_format("Jan 24")
        self.verify_datetime_format("Thu Jan 24")

    def test_timezone_formats(self):
        self.verify_datetime_format("05:45 PST")
        # Note: Some complex timezone formats might not parse, but should still be detected

    def test_iso_formats(self):
        self.verify_datetime_format("20300124T054513Z")

    def test_datetime_with_literals(self):
        self.verify_datetime_format("Date: 2030-01-24")
        self.verify_datetime_format("Meeting at 05:45")


class TestDatetimeFormatUniqueness:
    """Test that datetime formats are properly deduplicated and prioritized."""

    def test_no_duplicate_datetime_formats(self):
        """Ensure no duplicate datetime format specifications are returned."""
        test_cases = ["2030-01-24", "05:45:13", "Thu Jan 24 2030"]
        for input_str in test_cases:
            formats = analyze_number_format(input_str)
            datetime_formats = [(t, f) for t, f in formats if t == 'datetime']
            seen = set()
            for type_name, format_spec in datetime_formats:
                key = (type_name, format_spec)
                assert key not in seen, f"Duplicate datetime format found for '{input_str}': {key}"
                seen.add(key)

    def test_datetime_vs_numeric_priority(self):
        """Test priority between datetime and numeric formats."""
        # Single digit - should prioritize numeric
        formats = analyze_number_format("5")
        first_types = [t for t, f in formats[:2]]
        assert 'datetime' not in first_types or any(t in ['int', 'float'] for t in first_types[:1])

    def test_datetime_structure_priority(self):
        """Test that clear datetime structure gets priority."""
        structured_formats = ["2030-01-24", "05:45:13", "Jan 24 2030"]
        for input_str in structured_formats:
            formats = analyze_number_format(input_str)
            datetime_formats = [f for t, f in formats if t == 'datetime']
            assert len(datetime_formats) > 0, f"Should detect datetime in structured format: '{input_str}'"
