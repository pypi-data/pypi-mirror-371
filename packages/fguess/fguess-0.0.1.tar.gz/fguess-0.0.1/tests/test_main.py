import sys
from unittest.mock import patch

from fguess import main


class TestMainFunction:
    """Test the main CLI function."""

    def test_main_with_command_line_argument_with_results(self, capsys):
        """Test main function with command line argument that has results."""
        with patch.object(sys, 'argv', ['fguess.py', '42']):
            main()

        captured = capsys.readouterr()
        assert "Input: '42'" in captured.out
        assert "-" * 40 in captured.out
        assert "→" in captured.out  # Should have format results
        assert "variable =" in captured.out  # Should show test values

    def test_main_with_command_line_argument_no_results(self, capsys):
        """Test main function with command line argument that has no results."""
        with patch.object(sys, 'argv', ['fguess.py', 'hello']):
            main()

        captured = capsys.readouterr()
        assert "Input: 'hello'" in captured.out
        assert "-" * 40 in captured.out
        assert "No format specifications found" in captured.out

    @patch('builtins.input', return_value='123.45')
    def test_main_interactive_mode_with_results(self, mock_input, capsys):
        """Test main function in interactive mode with results."""
        with patch.object(sys, 'argv', ['fguess.py']):
            main()

        captured = capsys.readouterr()
        assert "Enter a formatted string (or 'quit' to exit):" in captured.out
        assert "Input: '123.45'" in captured.out
        assert "-" * 40 in captured.out
        assert "→" in captured.out  # Should have format results

    @patch('builtins.input', return_value='quit')
    def test_main_interactive_mode_quit(self, mock_input, capsys):
        """Test main function in interactive mode with quit command."""
        with patch.object(sys, 'argv', ['fguess.py']):
            main()

        captured = capsys.readouterr()
        assert "Enter a formatted string (or 'quit' to exit):" in captured.out
        # Should not have any other output after quit
        assert "Input:" not in captured.out
        assert "→" not in captured.out

    @patch('builtins.input', return_value='QUIT')  # Test case-insensitive
    def test_main_interactive_mode_quit_case_insensitive(self, mock_input, capsys):
        """Test that quit command is case-insensitive."""
        with patch.object(sys, 'argv', ['fguess.py']):
            main()

        captured = capsys.readouterr()
        assert "Enter a formatted string (or 'quit' to exit):" in captured.out
        assert "Input:" not in captured.out

    @patch('builtins.input', return_value='nonexistent')
    def test_main_interactive_mode_no_results(self, mock_input, capsys):
        """Test main function in interactive mode with no format results."""
        with patch.object(sys, 'argv', ['fguess.py']):
            main()

        captured = capsys.readouterr()
        assert "Enter a formatted string (or 'quit' to exit):" in captured.out
        assert "Input: 'nonexistent'" in captured.out
        assert "No format specifications found" in captured.out

    def test_main_duplicate_formats_deduplication(self, capsys):
        """Test that duplicate formats are properly deduplicated in output."""
        # Use an input that might generate duplicate formats in the internal logic
        with patch.object(sys, 'argv', ['fguess.py', '42']):
            main()

        captured = capsys.readouterr()
        # Count how many times a specific format appears
        lines = captured.out.split('\n')
        format_lines = [line for line in lines if '→' in line]

        # Should not have duplicate format lines (deduplication should work)
        assert len(format_lines) == len(set(format_lines))

    def test_main_output_formatting(self, capsys):
        """Test the specific formatting of the main function output."""
        with patch.object(sys, 'argv', ['fguess.py', '$123.45']):
            main()

        captured = capsys.readouterr()
        lines = captured.out.split('\n')

        # Check that we have the expected structure
        input_line = next((line for line in lines if line.startswith("Input:")), None)
        assert input_line == "Input: '$123.45'"

        separator_line = next((line for line in lines if line == "-" * 40), None)
        assert separator_line is not None

        # Should have format result lines with proper spacing
        format_lines = [line for line in lines if '→' in line]
        assert len(format_lines) > 0

        for format_line in format_lines:
            # Check format: "type     → format_spec"
            parts = format_line.split('→')
            assert len(parts) == 2
            type_part = parts[0].strip()
            assert type_part in ['str', 'int', 'float', 'datetime']

    def test_main_test_value_generation(self, capsys):
        """Test that test values are generated and displayed correctly."""
        with patch.object(sys, 'argv', ['fguess.py', '0x42']):
            main()

        captured = capsys.readouterr()

        # Should have lines with test values
        example_lines = [line for line in captured.out.split('\n') if 'e.g., variable =' in line]
        assert len(example_lines) > 0

        # Should show the actual test value
        assert any('66' in line for line in example_lines)  # 0x42 = 66

    def test_main_empty_input(self, capsys):
        """Test main function with empty input."""
        with patch.object(sys, 'argv', ['fguess.py', '']):
            main()

        captured = capsys.readouterr()
        assert "Input: ''" in captured.out
        assert "No format specifications found" in captured.out

    @patch('builtins.input', return_value='')
    def test_main_interactive_empty_input(self, mock_input, capsys):
        """Test main function in interactive mode with empty input."""
        with patch.object(sys, 'argv', ['fguess.py']):
            main()

        captured = capsys.readouterr()
        assert "Enter a formatted string (or 'quit' to exit):" in captured.out
        assert "Input: ''" in captured.out
        assert "No format specifications found" in captured.out

    def test_main_datetime_format_display(self, capsys):
        """Test that datetime formats are displayed correctly."""
        with patch.object(sys, 'argv', ['fguess.py', '2030-01-24']):
            main()

        captured = capsys.readouterr()

        # Should have datetime format
        assert 'datetime' in captured.out
        assert '%Y-%m-%d' in captured.out
        # Should show datetime test value
        assert 'datetime.datetime' in captured.out or '2030' in captured.out

    def test_main_multiple_format_types(self, capsys):
        """Test display when multiple format types are available."""
        with patch.object(sys, 'argv', ['fguess.py', '  42  ']):  # Should have int and str formats
            main()

        captured = capsys.readouterr()

        # Should have multiple format types
        format_lines = [line for line in captured.out.split('\n') if '→' in line]
        format_types = set()

        for line in format_lines:
            type_part = line.split('→')[0].strip()
            format_types.add(type_part)

        # Should have at least int and str formats
        assert len(format_types) >= 2
        assert 'int' in format_types or 'str' in format_types

    def test_main_special_characters_in_input(self, capsys):
        """Test main function with special characters that need proper display."""
        special_input = "Price: $1,234.56€"
        with patch.object(sys, 'argv', ['fguess.py', special_input]):
            main()

        captured = capsys.readouterr()

        # Input should be displayed correctly with special characters
        assert f"Input: '{special_input}'" in captured.out

        # Should handle Unicode characters properly
        assert '€' in captured.out
