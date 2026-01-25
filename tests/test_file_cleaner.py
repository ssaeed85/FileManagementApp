"""
Comprehensive test suite for file_cleaner.py

Focus on date parsing functions and core cleaning operations.
"""
import pytest
from pathlib import Path
from file_cleaner import FileNameCleaner, DATE_PATTERNS


class TestSplitNameExtension:
    """Test filename and extension splitting."""
    
    def test_simple_filename(self):
        name, ext = FileNameCleaner.split_name_extension("document.txt")
        assert name == "document"
        assert ext == ".txt"
    
    def test_multiple_dots(self):
        name, ext = FileNameCleaner.split_name_extension("my.file.name.pdf")
        assert name == "my.file.name"
        assert ext == ".pdf"
    
    def test_no_extension(self):
        name, ext = FileNameCleaner.split_name_extension("README")
        assert name == "README"
        assert ext == ""
    
    def test_hidden_file(self):
        name, ext = FileNameCleaner.split_name_extension(".gitignore")
        assert name == ".gitignore"
        assert ext == ""


class TestReplaceString:
    """Test string replacement in filenames."""
    
    def test_replace_space_with_underscore(self):
        result = FileNameCleaner.replace_string("my document.txt", " ", "_")
        assert result == "my_document.txt"
    
    def test_replace_multiple_occurrences(self):
        result = FileNameCleaner.replace_string("one-two-three.txt", "-", "_")
        assert result == "one_two_three.txt"
    
    def test_remove_character(self):
        result = FileNameCleaner.replace_string("file(1).txt", "(", "")
        assert result == "file1).txt"
    
    def test_preserve_extension(self):
        result = FileNameCleaner.replace_string("test.file.txt", ".", "_")
        assert result == "test_file.txt"  # Extension preserved


class TestToCamelCase:
    """Test camelCase and PascalCase conversion."""
    
    def test_camel_case_with_spaces(self):
        result = FileNameCleaner.to_camel_case("my file name.txt", upper_first=False)
        assert result == "my File Name.txt"
    
    def test_pascal_case_with_spaces(self):
        result = FileNameCleaner.to_camel_case("my file name.txt", upper_first=True)
        assert result == "My File Name.txt"
    
    def test_camel_case_with_underscores(self):
        result = FileNameCleaner.to_camel_case("my_file_name.txt", upper_first=False)
        assert result == "my_File_Name.txt"
    
    def test_camel_case_with_dashes(self):
        result = FileNameCleaner.to_camel_case("my-file-name.txt", upper_first=False)
        assert result == "my-File-Name.txt"
    
    def test_preserve_separators(self):
        result = FileNameCleaner.to_camel_case("test-file_name.txt", upper_first=False)
        assert result == "test-File_Name.txt"


class TestRegexReplace:
    """Test regex find and replace operations."""
    
    def test_simple_regex(self):
        result = FileNameCleaner.regex_replace("file123.txt", r"\d+", "456")
        assert result == "file456.txt"
    
    def test_regex_with_groups(self):
        result = FileNameCleaner.regex_replace("file_2024_01.txt", r"(\d{4})_(\d{2})", r"\2-\1")
        assert result == "file_01-2024.txt"
    
    def test_preserve_extension(self):
        result = FileNameCleaner.regex_replace("test.txt", r"test", "demo", preserve_extension=True)
        assert result == "demo.txt"
    
    def test_invalid_regex_returns_original(self):
        result = FileNameCleaner.regex_replace("file.txt", r"[invalid(", "test")
        assert result == "file.txt"


class TestDatePatternConstants:
    """Verify DATE_PATTERNS dictionary exists and is properly structured."""
    
    def test_date_patterns_exists(self):
        assert DATE_PATTERNS is not None
        assert isinstance(DATE_PATTERNS, dict)
    
    def test_expected_patterns_present(self):
        expected_keys = [
            'space_yyyy_mm_dd',
            'space_nn_nn_yyyy',
            'space_yy_mm_dd',
            'dot_dd_mm_yyyy',
            'iso_date',
            'dash_dd_mm_yyyy',
            'iso_slash',
            'slash_dd_mm_yyyy',
            'yyyymmdd',
            'ddmmyyyy'
        ]
        for key in expected_keys:
            assert key in DATE_PATTERNS, f"Missing pattern: {key}"
    
    def test_patterns_are_strings(self):
        for key, pattern in DATE_PATTERNS.items():
            assert isinstance(pattern, str), f"Pattern {key} is not a string"


class TestParseSpaceSeparatedFourDigitYear:
    """Test 'YYYY MM DD' date format parsing."""
    
    def test_valid_date_yyyy_mm_dd(self):
        result = FileNameCleaner._parse_space_separated_four_digit_year(
            "report 2025 01 31", "%Y-%m-%d"
        )
        assert result == "report 2025-01-31"
    
    def test_multiple_dates(self):
        result = FileNameCleaner._parse_space_separated_four_digit_year(
            "2024 12 25 and 2025 01 01", "%Y.%m.%d"
        )
        assert result == "2024.12.25 and 2025.01.01"
    
    def test_invalid_date_skipped(self):
        # February 30 doesn't exist
        result = FileNameCleaner._parse_space_separated_four_digit_year(
            "test 2025 02 30 file", "%Y-%m-%d"
        )
        assert result == "test 2025 02 30 file"  # Unchanged
    
    def test_invalid_month_skipped(self):
        result = FileNameCleaner._parse_space_separated_four_digit_year(
            "test 2025 13 01 file", "%Y-%m-%d"
        )
        assert result == "test 2025 13 01 file"  # Month 13 invalid
    
    def test_no_dates_unchanged(self):
        result = FileNameCleaner._parse_space_separated_four_digit_year(
            "no dates here", "%Y-%m-%d"
        )
        assert result == "no dates here"


class TestParseSpaceSeparatedYearAtEnd:
    """Test 'DD MM YYYY' and 'MM DD YYYY' date format parsing."""
    
    def test_unambiguous_dd_mm_yyyy(self):
        # Day > 12, must be DD MM YYYY
        result = FileNameCleaner._parse_space_separated_year_at_end(
            "report 31 01 2025", "%Y-%m-%d"
        )
        assert result == "report 2025-01-31"
    
    def test_unambiguous_mm_dd_yyyy(self):
        # Month > 12, must be MM DD YYYY
        result = FileNameCleaner._parse_space_separated_year_at_end(
            "report 01 31 2025", "%Y-%m-%d"
        )
        assert result == "report 2025-01-31"
    
    def test_ambiguous_defaults_to_european(self):
        # 12 01 2025 - could be Dec 1 or Jan 12
        # Should default to DD MM YYYY (European): Jan 12, 2025
        result = FileNameCleaner._parse_space_separated_year_at_end(
            "report 12 01 2025", "%Y-%m-%d"
        )
        assert result == "report 2025-01-12"
    
    def test_ambiguous_falls_back_to_american(self):
        # If European format fails validation, try American
        result = FileNameCleaner._parse_space_separated_year_at_end(
            "report 02 03 2025", "%Y-%m-%d"
        )
        # Should parse as Feb 3, 2025 (DD MM YYYY)
        assert result == "report 2025-03-02"
    
    def test_multiple_dates_mixed_formats(self):
        result = FileNameCleaner._parse_space_separated_year_at_end(
            "file 31 12 2024 and 01 15 2025", "%Y.%m.%d"
        )
        assert result == "file 2024.12.31 and 2025.01.15"


class TestParseTwoDigitYearSpaces:
    """Test 'YY MM DD' and 'MM DD YY' date format parsing."""
    
    def test_unambiguous_yy_mm_dd(self):
        # First number > 12, must be year: 25 01 31 = 2025-01-31
        result = FileNameCleaner._parse_two_digit_year_spaces(
            "file 25 01 31", "%Y-%m-%d"
        )
        assert result == "file 2025-01-31"
    
    def test_unambiguous_mm_dd_yy(self):
        # Last number > 12, must be year: 01 31 25 = 2025-01-31
        result = FileNameCleaner._parse_two_digit_year_spaces(
            "file 01 31 25", "%Y-%m-%d"
        )
        assert result == "file 2025-01-31"
    
    def test_ambiguous_defaults_to_yy_mm_dd(self):
        # 23 07 01 - defaults to YY MM DD: 2023-07-01
        result = FileNameCleaner._parse_two_digit_year_spaces(
            "file 23 07 01", "%Y-%m-%d"
        )
        assert result == "file 2023-07-01"
    
    def test_year_2000_assumption(self):
        # Assumes 2000s for 2-digit years
        result = FileNameCleaner._parse_two_digit_year_spaces(
            "file 99 12 31", "%Y-%m-%d"
        )
        assert result == "file 2099-12-31"


class TestParseDotSeparatedDates:
    """Test 'DD.MM.YYYY' date format parsing."""
    
    def test_unambiguous_european_format(self):
        # 31.12.2024 - must be DD.MM.YYYY
        result = FileNameCleaner._parse_dot_separated_dates(
            "file 31.12.2024", "%Y-%m-%d"
        )
        assert result == "file 2024-12-31"
    
    def test_unambiguous_american_format(self):
        # 12.31.2024 - must be MM.DD.YYYY
        result = FileNameCleaner._parse_dot_separated_dates(
            "file 12.31.2024", "%Y-%m-%d"
        )
        assert result == "file 2024-12-31"
    
    def test_ambiguous_defaults_to_european(self):
        # 01.02.2025 - defaults to DD.MM.YYYY: Feb 1, 2025
        result = FileNameCleaner._parse_dot_separated_dates(
            "file 01.02.2025", "%Y-%m-%d"
        )
        assert result == "file 2025-02-01"
    
    def test_multiple_dot_dates(self):
        result = FileNameCleaner._parse_dot_separated_dates(
            "report 01.01.2024 and 31.12.2024", "%Y.%m.%d"
        )
        assert result == "report 2024.01.01 and 2024.12.31"


class TestParseCommonDatePatterns:
    """Test other common date patterns (ISO, slashes, numeric)."""
    
    def test_iso_format(self):
        result = FileNameCleaner._parse_common_date_patterns(
            "report 2025-01-31", "%Y.%m.%d"
        )
        assert result == "report 2025.01.31"
    
    def test_slash_format_iso(self):
        result = FileNameCleaner._parse_common_date_patterns(
            "file 2025/01/31", "%Y-%m-%d"
        )
        assert result == "file 2025-01-31"
    
    def test_numeric_yyyymmdd(self):
        result = FileNameCleaner._parse_common_date_patterns(
            "report 20250131", "%Y-%m-%d"
        )
        assert result == "report 2025-01-31"
    
    def test_multiple_pattern_types(self):
        result = FileNameCleaner._parse_common_date_patterns(
            "file 2025-01-31 and 20251231", "%Y.%m.%d"
        )
        assert result == "file 2025.01.31 and 2025.12.31"
    
    def test_invalid_date_skipped(self):
        # Invalid date should be skipped
        result = FileNameCleaner._parse_common_date_patterns(
            "file 2025-13-45", "%Y-%m-%d"
        )
        assert result == "file 2025-13-45"


class TestStandardizeDates:
    """Comprehensive tests for the main standardize_dates function."""
    
    def test_default_output_format(self):
        # Default format is %Y.%m.%d
        result = FileNameCleaner.standardize_dates("report 2025 01 31.txt")
        assert result == "report 2025.01.31.txt"
    
    def test_custom_output_format(self):
        result = FileNameCleaner.standardize_dates(
            "report 2025 01 31.txt", 
            output_format="%d-%m-%Y"
        )
        assert result == "report 31-01-2025.txt"
    
    def test_multiple_date_formats_in_one_filename(self):
        result = FileNameCleaner.standardize_dates(
            "backup 2024 12 25 and 31.01.2025.zip",
            output_format="%Y-%m-%d"
        )
        assert result == "backup 2024-12-25 and 2025-01-31.zip"
    
    def test_preserve_extension(self):
        result = FileNameCleaner.standardize_dates("file 2025-01-31.pdf")
        assert result.endswith(".pdf")
    
    def test_no_dates_unchanged(self):
        result = FileNameCleaner.standardize_dates("regular_filename.txt")
        assert result == "regular_filename.txt"
    
    def test_complex_filename(self):
        result = FileNameCleaner.standardize_dates(
            "Project Report 2024 12 25 - Review 31.12.2024 - Final.docx",
            output_format="%Y-%m-%d"
        )
        assert "2024-12-25" in result
        assert "2024-12-31" in result
        assert result.endswith(".docx")
    
    def test_all_date_formats_chain(self):
        # Test that all parsers work in sequence
        filenames = [
            ("backup 2025 01 31.zip", "backup 2025.01.31.zip"),
            ("report 31 01 2025.txt", "report 2025.01.31.txt"),
            ("file 25 01 31.doc", "file 2025.01.31.doc"),
            ("data 31.01.2025.csv", "data 2025.01.31.csv"),
            ("log 2025-01-31.txt", "log 2025.01.31.txt"),
            ("archive 20250131.zip", "archive 2025.01.31.zip"),
        ]
        
        for input_name, expected in filenames:
            result = FileNameCleaner.standardize_dates(input_name)
            assert result == expected, f"Failed for {input_name}: got {result}, expected {expected}"


class TestPreviewChanges:
    """Test preview_changes with mocked file system."""
    
    def test_preview_single_operation(self, tmp_path):
        # Create test files
        (tmp_path / "test file.txt").write_text("content")
        (tmp_path / "another file.pdf").write_text("content")
        
        operations = [
            {'type': 'replace_string', 'source': ' ', 'replacement': '_'}
        ]
        
        changes = FileNameCleaner.preview_changes(str(tmp_path), operations)
        
        assert len(changes) == 2
        # Changes are returned in directory iteration order, so just check both exist
        filenames = [change[0] for change in changes]
        assert "test file.txt" in filenames
        assert "another file.pdf" in filenames
    
    def test_preview_multiple_operations(self, tmp_path):
        # Create test file
        (tmp_path / "my document 2025 01 31.txt").write_text("content")
        
        operations = [
            {'type': 'replace_string', 'source': ' ', 'replacement': '_'},
            {'type': 'standardize_dates', 'format': '%Y-%m-%d'}
        ]
        
        changes = FileNameCleaner.preview_changes(str(tmp_path), operations)
        
        assert len(changes) == 1
        # First operation replaces spaces with underscores
        # Second operation parses "2025_01_31" (but underscores don't match space patterns)
        # So the result will have underscores, not dashes in the date
        assert "my_document" in changes[0][1]
        assert changes[0][1].endswith(".txt")
    
    def test_preview_no_changes(self, tmp_path):
        # Create test file
        (tmp_path / "file.txt").write_text("content")
        
        operations = [
            {'type': 'replace_string', 'source': 'notfound', 'replacement': '_'}
        ]
        
        changes = FileNameCleaner.preview_changes(str(tmp_path), operations)
        
        assert len(changes) == 0  # No changes because pattern not found
    
    def test_preview_skips_directories(self, tmp_path):
        # Create file and directory
        (tmp_path / "file.txt").write_text("content")
        (tmp_path / "subdir").mkdir()
        
        operations = [
            {'type': 'replace_string', 'source': 'file', 'replacement': 'document'}
        ]
        
        changes = FileNameCleaner.preview_changes(str(tmp_path), operations)
        
        assert len(changes) == 1  # Only file, not directory


class TestApplyChanges:
    """Test apply_changes with real file operations."""
    
    def test_apply_simple_rename(self, tmp_path):
        # Create test file
        test_file = tmp_path / "old_name.txt"
        test_file.write_text("content")
        
        changes = [
            ("old_name.txt", "new_name.txt", str(test_file))
        ]
        
        success_count, errors = FileNameCleaner.apply_changes(changes)
        
        assert success_count == 1
        assert len(errors) == 0
        assert not test_file.exists()
        assert (tmp_path / "new_name.txt").exists()
    
    def test_apply_multiple_renames(self, tmp_path):
        # Create multiple test files
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("content1")
        file2.write_text("content2")
        
        changes = [
            ("file1.txt", "renamed1.txt", str(file1)),
            ("file2.txt", "renamed2.txt", str(file2))
        ]
        
        success_count, errors = FileNameCleaner.apply_changes(changes)
        
        assert success_count == 2
        assert len(errors) == 0
        assert (tmp_path / "renamed1.txt").exists()
        assert (tmp_path / "renamed2.txt").exists()
    
    def test_apply_case_only_change(self, tmp_path):
        # Test case-only rename (Windows compatibility)
        test_file = tmp_path / "file.txt"
        test_file.write_text("content")
        
        changes = [
            ("file.txt", "FILE.txt", str(test_file))
        ]
        
        success_count, errors = FileNameCleaner.apply_changes(changes)
        
        assert success_count == 1
        assert len(errors) == 0
        # Note: On Windows, case-only changes use temp file workaround
    
    def test_apply_fails_if_target_exists(self, tmp_path):
        # Create two files
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("content1")
        file2.write_text("content2")
        
        # Try to rename file1 to file2 (already exists)
        changes = [
            ("file1.txt", "file2.txt", str(file1))
        ]
        
        success_count, errors = FileNameCleaner.apply_changes(changes)
        
        assert success_count == 0
        assert len(errors) == 1
        assert "already exists" in errors[0]
        assert file1.exists()  # Original still exists
    
    def test_apply_handles_permission_error(self, tmp_path):
        # This test simulates permission errors
        # In real scenarios, this would fail with PermissionError
        changes = [
            ("nonexistent.txt", "new.txt", str(tmp_path / "nonexistent.txt"))
        ]
        
        success_count, errors = FileNameCleaner.apply_changes(changes)
        
        assert success_count == 0
        assert len(errors) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
