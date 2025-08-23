# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

`fguess` is a Python library and CLI tool that reverse-engineers Python f-string format specifications from formatted output examples. It analyzes formatted strings and suggests the most likely format specifications that would produce that output. The package depends on `strptime-cli` for datetime format detection.

## Commands

### Testing
- `hatch test` - Run all tests
- `hatch test --cover` - Run tests with coverage
- `hatch run cov-html` - Generate HTML coverage report
- `hatch test tests/test_specific.py` - Run specific test file
- `hatch test tests/test_specific.py::TestClass::test_method` - Run specific test

### Code Quality
- `hatch run lint:check` - Check code formatting and linting with ruff
- `hatch run lint:fmt` - Format code with ruff

### Build and Package
- `hatch build` - Build the package
- `hatch version` - Show current version (defined in fguess.py)

## Architecture

### Core Components

**Main Module (`fguess.py`)**
- Single-file implementation containing all functionality
- Core function: `analyze_number_format(s)` - takes a formatted string and returns list of (type, format_spec) tuples
- Two main detection paths:
  1. **Numeric format detection** - handles integers, floats, hex, percentages, with various padding/alignment
  2. **Datetime format detection** - delegates to `strptime-cli` package for robust datetime format detection

**Format Detection Pipeline**
1. **Datetime detection** - uses `strptime.detect_format()` from the `strptime-cli` package to detect datetime formats
2. **Literal splitting** - separates numeric content from prefix/suffix literals
3. **Padding analysis** - detects alignment and fill characters
4. **Number parsing** - determines numeric type and formatting options
5. **Priority ordering** - ranks results by likelihood (datetime with structure > numeric > string > single numeric datetime)

**Key Data Structures**
- `FormatSpec` dataclass - represents all components of a format specification
- `NumberParts` dataclass - holds prefix, numeric part, and suffix after literal splitting
- Extensive regex patterns for different number formats (hex, percentage, thousands separators, etc.)
- Datetime detection is handled by the external `strptime-cli` dependency

### Testing Structure

Tests are organized by functionality:
- `test_analyze_number_format.py` - main function testing with various input formats
- `test_get_test_value.py` - test value generation for validation
- `test_roundrip.py` - round-trip testing (format detection → application → verification)

### Format Priority Logic

The tool prioritizes format suggestions based on:
1. Multi-part datetime formats (when string has datetime structure like spaces, colons, dashes)
2. Numeric formats (int/float with various formatting options)
3. String formats
4. Single numeric datetime formats (lowest priority, e.g., just "%d" or "%Y")

### Entry Points

- CLI: `python fguess.py "formatted_string"` or interactive mode
- Module: `from fguess import analyze_number_format`
- Package script: `strptime` (defined in pyproject.toml, maps to strptime:main)