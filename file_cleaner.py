"""
Core file name cleaning functions.
"""
import re
from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime
from dateutil import parser as date_parser

# Date pattern dictionary - organized by format type
DATE_PATTERNS = {
    'space_yyyy_mm_dd': r'\b(\d{4}) (\d{2}) (\d{2})\b',      # 2025 01 31
    'space_nn_nn_yyyy': r'\b(\d{2}) (\d{2}) (\d{4})\b',      # 31 01 2025 or 01 31 2025
    'space_yy_mm_dd': r'\b(\d{2}) (\d{2}) (\d{2})\b',        # 25 01 31 or 01 31 25
    'dot_dd_mm_yyyy': r'\b(\d{2})\.(\d{2})\.(\d{4})\b',      # 31.01.2025 or 01.31.2025
    'iso_date': r'\d{4}-\d{2}-\d{2}',                        # 2025-01-31
    'dash_dd_mm_yyyy': r'\d{2}-\d{2}-\d{4}',                 # 31-01-2025
    'iso_slash': r'\d{4}/\d{2}/\d{2}',                       # 2025/01/31
    'slash_dd_mm_yyyy': r'\d{2}/\d{2}/\d{4}',                # 31/01/2025
    'yyyymmdd': r'\d{8}',                                    # 20250131
    'ddmmyyyy': r'\d{2}\d{2}\d{4}',                          # 31012025
}

class FileNameCleaner:
    """Handles various file name cleaning operations."""
    
    @staticmethod
    def split_name_extension(filename: str) -> Tuple[str, str]:
        """Split filename into name and extension."""
        path = Path(filename)
        return path.stem, path.suffix
    
    @staticmethod
    def replace_string(filename: str, source_string: str, replacement: str = "_") -> str:
        """
        Replace a specific string in filename, preserving the extension.
        
        Args:
            filename: The original filename
            source_string: String to replace (can be single char or substring)
            replacement: String to replace with (empty string to remove)
        
        Returns:
            Cleaned filename
        """
        name, ext = FileNameCleaner.split_name_extension(filename)
        cleaned_name = name.replace(source_string, replacement)
        return f"{cleaned_name}{ext}"
    
    @staticmethod
    def to_camel_case(filename: str, upper_first: bool = False) -> str:
        """
        Convert filename to camelCase or PascalCase, only changing character case.
        
        Args:
            filename: The original filename
            upper_first: If True, use PascalCase instead of camelCase
        
        Returns:
            Camel cased filename (preserves all characters, only changes case)
        """
        name, ext = FileNameCleaner.split_name_extension(filename)
        
        if not name:
            return filename
        
        result = []
        capitalize_next = upper_first  # For PascalCase, capitalize the first letter
        
        for i, char in enumerate(name):
            if char in '_-. ':
                # Keep the separator character as-is
                result.append(char)
                capitalize_next = True  # Next letter should be capitalized
            elif capitalize_next and char.isalpha():
                result.append(char.upper())
                capitalize_next = False
            else:
                result.append(char.lower())
        
        camel_name = ''.join(result)
        return f"{camel_name}{ext}"
    
    @staticmethod
    def regex_replace(filename: str, pattern: str, replacement: str, preserve_extension: bool = True) -> str:
        """
        Apply regex find and replace to filename.
        
        Args:
            filename: The original filename
            pattern: Regex pattern to find
            replacement: Replacement string (can use \\1, \\2 for groups)
                        Special case conversions: \\U\\1 (uppercase), \\L\\1 (lowercase), \\T\\1 (title case)
            preserve_extension: If True, only apply regex to name part
        
        Returns:
            Modified filename
        """
        try:
            # Check if replacement contains case conversion sequences
            has_case_conversion = bool(re.search(r'\\[ULT]\\\d+', replacement))
            
            if has_case_conversion:
                # Parse replacement string for case conversion sequences
                def replace_func(match):
                    result = replacement
                    # Replace backreferences with actual captured groups
                    for i in range(len(match.groups()) + 1):
                        group_text = match.group(i) if i < len(match.groups()) + 1 else ''
                        # Handle case conversions
                        result = re.sub(rf'\\U\\{i}', group_text.upper() if group_text else '', result)
                        result = re.sub(rf'\\L\\{i}', group_text.lower() if group_text else '', result)
                        result = re.sub(rf'\\T\\{i}', group_text.title() if group_text else '', result)
                        # Handle regular backreferences
                        result = re.sub(rf'(?<!\\[ULT])\\{i}', group_text if group_text else '', result)
                    return result
                
                if preserve_extension:
                    name, ext = FileNameCleaner.split_name_extension(filename)
                    cleaned_name = re.sub(pattern, replace_func, name)
                    return f"{cleaned_name}{ext}"
                else:
                    return re.sub(pattern, replace_func, filename)
            else:
                # Standard regex replacement without case conversion
                if preserve_extension:
                    name, ext = FileNameCleaner.split_name_extension(filename)
                    cleaned_name = re.sub(pattern, replacement, name)
                    return f"{cleaned_name}{ext}"
                else:
                    return re.sub(pattern, replacement, filename)
        except re.error as e:
            # Return original filename if regex is invalid
            return filename
        except Exception as e:
            # Return original filename for any other errors
            return filename
    
    @staticmethod
    def _parse_space_separated_four_digit_year(text: str, output_format: str) -> str:
        """
        Handle 'YYYY MM DD' format with spaces (4-digit year at start).
        
        Args:
            text: Text to parse
            output_format: Desired date format (strftime format)
        
        Returns:
            Text with standardized dates
        """
        matches = list(re.finditer(DATE_PATTERNS['space_yyyy_mm_dd'], text))
        result = text
        
        for match in reversed(matches):  # Reverse to maintain positions
            year_str, month_str, day_str = match.groups()
            try:
                year = int(year_str)
                month = int(month_str)
                day = int(day_str)
                
                # Validate date
                parsed_date = datetime(year, month, day)
                formatted_date = parsed_date.strftime(output_format)
                result = result[:match.start()] + formatted_date + result[match.end():]
            except (ValueError, TypeError):
                continue
        
        return result
    
    @staticmethod
    def _parse_space_separated_year_at_end(text: str, output_format: str) -> str:
        """
        Handle 'NN NN YYYY' format with spaces (4-digit year at end).
        Smart detection for DD MM YYYY vs MM DD YYYY.
        
        Args:
            text: Text to parse
            output_format: Desired date format (strftime format)
        
        Returns:
            Text with standardized dates
        """
        matches = list(re.finditer(DATE_PATTERNS['space_nn_nn_yyyy'], text))
        result = text
        
        for match in reversed(matches):
            n1, n2, year_str = match.groups()
            try:
                num1 = int(n1)
                num2 = int(n2)
                year = int(year_str)
                
                parsed_date = None
                
                # If first number > 12, it must be DD MM YYYY (day first)
                if num1 > 12:
                    parsed_date = datetime(year, num2, num1)
                # If second number > 12, it must be MM DD YYYY (day second)
                elif num2 > 12:
                    parsed_date = datetime(year, num1, num2)
                else:
                    # Ambiguous - try DD MM YYYY first (European standard), then MM DD YYYY
                    try:
                        parsed_date = datetime(year, num2, num1)
                    except ValueError:
                        parsed_date = datetime(year, num1, num2)
                
                if parsed_date:
                    formatted_date = parsed_date.strftime(output_format)
                    result = result[:match.start()] + formatted_date + result[match.end():]
            except (ValueError, TypeError):
                continue
        
        return result
    
    @staticmethod
    def _parse_two_digit_year_spaces(text: str, output_format: str) -> str:
        """
        Handle 'NN NN NN' format with spaces.
        Smart detection for YY MM DD vs MM DD YY.
        
        Args:
            text: Text to parse
            output_format: Desired date format (strftime format)
        
        Returns:
            Text with standardized dates
        """
        matches = list(re.finditer(DATE_PATTERNS['space_yy_mm_dd'], text))
        result = text
        
        for match in reversed(matches):
            n1, n2, n3 = match.groups()
            try:
                num1 = int(n1)
                num2 = int(n2)
                num3 = int(n3)
                
                parsed_date = None
                
                # If first number > 12, it must be YY MM DD (year, not month)
                if num1 > 12:
                    full_year = 2000 + num1
                    parsed_date = datetime(full_year, num2, num3)
                # If last number > 12, it must be MM DD YY (year at end)
                elif num3 > 12:
                    full_year = 2000 + num3
                    parsed_date = datetime(full_year, num1, num2)
                else:
                    # Ambiguous - try YY MM DD first, then MM DD YY
                    try:
                        full_year = 2000 + num1
                        parsed_date = datetime(full_year, num2, num3)
                    except ValueError:
                        full_year = 2000 + num3
                        parsed_date = datetime(full_year, num1, num2)
                
                if parsed_date:
                    formatted_date = parsed_date.strftime(output_format)
                    result = result[:match.start()] + formatted_date + result[match.end():]
            except (ValueError, TypeError):
                continue
        
        return result
    
    @staticmethod
    def _parse_dot_separated_dates(text: str, output_format: str) -> str:
        """
        Handle DD.MM.YYYY with dots (4-digit year at end).
        Smart detection for DD.MM.YYYY vs MM.DD.YYYY.
        
        Args:
            text: Text to parse
            output_format: Desired date format (strftime format)
        
        Returns:
            Text with standardized dates
        """
        matches = list(re.finditer(DATE_PATTERNS['dot_dd_mm_yyyy'], text))
        result = text
        
        for match in reversed(matches):
            n1, n2, year_str = match.groups()
            try:
                num1 = int(n1)
                num2 = int(n2)
                year = int(year_str)
                
                parsed_date = None
                
                # If first number > 12, it must be DD.MM.YYYY (day first)
                if num1 > 12:
                    parsed_date = datetime(year, num2, num1)
                # If second number > 12, it must be MM.DD.YYYY (day second)
                elif num2 > 12:
                    parsed_date = datetime(year, num1, num2)
                else:
                    # Ambiguous - try DD.MM.YYYY first (European standard), then MM.DD.YYYY
                    try:
                        parsed_date = datetime(year, num2, num1)
                    except ValueError:
                        parsed_date = datetime(year, num1, num2)
                
                if parsed_date:
                    formatted_date = parsed_date.strftime(output_format)
                    result = result[:match.start()] + formatted_date + result[match.end():]
            except (ValueError, TypeError):
                continue
        
        return result
    
    @staticmethod
    def _parse_common_date_patterns(text: str, output_format: str) -> str:
        """
        Handle other common date patterns (ISO dates, slashes, numeric formats).
        
        Args:
            text: Text to parse
            output_format: Desired date format (strftime format)
        
        Returns:
            Text with standardized dates
        """
        # Use patterns that weren't handled by specific parsers
        common_pattern_keys = ['iso_date', 'dash_dd_mm_yyyy', 'iso_slash', 
                               'slash_dd_mm_yyyy', 'yyyymmdd', 'ddmmyyyy']
        
        result = text
        
        for pattern_key in common_pattern_keys:
            pattern = DATE_PATTERNS[pattern_key]
            matches = re.finditer(pattern, result)
            for match in reversed(list(matches)):
                date_str = match.group()
                try:
                    # Try to parse the date
                    parsed_date = date_parser.parse(date_str, fuzzy=False)
                    formatted_date = parsed_date.strftime(output_format)
                    result = result[:match.start()] + formatted_date + result[match.end():]
                except (ValueError, date_parser.ParserError):
                    continue
        
        return result
    
    @staticmethod
    def standardize_dates(filename: str, output_format: str = "%Y.%m.%d") -> str:
        """
        Find and standardize date formats in filename.
        
        Args:
            filename: The original filename
            output_format: Desired date format (strftime format)
        
        Returns:
            Filename with standardized dates
        """
        name, ext = FileNameCleaner.split_name_extension(filename)
        
        # Apply each parser in sequence
        result = FileNameCleaner._parse_space_separated_four_digit_year(name, output_format)
        result = FileNameCleaner._parse_space_separated_year_at_end(result, output_format)
        result = FileNameCleaner._parse_two_digit_year_spaces(result, output_format)
        result = FileNameCleaner._parse_dot_separated_dates(result, output_format)
        result = FileNameCleaner._parse_common_date_patterns(result, output_format)
        
        return f"{result}{ext}"
    
    @staticmethod
    def preview_changes(directory: str, operations: List[dict]) -> List[Tuple[str, str, str]]:
        """
        Preview file name changes for all files in a directory.
        
        Args:
            directory: Path to directory containing files
            operations: List of operations to apply (each dict has 'type' and parameters)
        
        Returns:
            List of tuples: (original_name, new_name, full_path)
        """
        dir_path = Path(directory)
        if not dir_path.exists():
            return []
        
        changes = []
        for file_path in dir_path.iterdir():
            # Skip directories
            if file_path.is_dir():
                continue
            
            filename = file_path.name
            new_name = filename
            
            # Apply each operation in sequence
            for op in operations:
                op_type = op.get('type')
                
                if op_type == 'replace_string':
                    new_name = FileNameCleaner.replace_string(
                        new_name,
                        op.get('source', '.'),
                        op.get('replacement', '_')
                    )
                
                elif op_type == 'camel_case':
                    new_name = FileNameCleaner.to_camel_case(
                        new_name,
                        op.get('upper_first', False)
                    )
                
                elif op_type == 'regex':
                    new_name = FileNameCleaner.regex_replace(
                        new_name,
                        op.get('pattern', ''),
                        op.get('replacement', ''),
                        op.get('preserve_extension', True)
                    )
                
                elif op_type == 'standardize_dates':
                    new_name = FileNameCleaner.standardize_dates(
                        new_name,
                        op.get('format', '%Y.%m.%d')
                    )
            
            # Only include if the name actually changed
            if new_name != filename:
                changes.append((filename, new_name, str(file_path)))
        
        return changes
    
    @staticmethod
    def apply_changes(changes: List[Tuple[str, str, str]]) -> Tuple[int, List[str]]:
        """
        Apply the file name changes.
        
        Args:
            changes: List of tuples from preview_changes
        
        Returns:
            Tuple of (success_count, list of error messages)
        """
        success_count = 0
        errors = []
        
        for original, new_name, file_path_str in changes:
            try:
                file_path = Path(file_path_str)
                new_path = file_path.parent / new_name
                
                # Check if this is a case-only change (Windows is case-insensitive)
                is_case_only_change = original.lower() == new_name.lower() and original != new_name
                
                if is_case_only_change:
                    # Two-step rename for case-only changes on Windows
                    # Step 1: Rename to a temporary name
                    import uuid
                    temp_name = f"_temp_{uuid.uuid4().hex[:8]}_{new_name}"
                    temp_path = file_path.parent / temp_name
                    file_path.rename(temp_path)
                    # Step 2: Rename to final name
                    temp_path.rename(new_path)
                else:
                    # Check if target already exists
                    if new_path.exists():
                        errors.append(f"Cannot rename '{original}': '{new_name}' already exists")
                        continue
                    
                    file_path.rename(new_path)
                
                success_count += 1
            except Exception as e:
                errors.append(f"Error renaming '{original}': {str(e)}")
        
        return success_count, errors
