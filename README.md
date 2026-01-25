# 📁 File Management Application

> *Because life's too short for files named "Copy of Document (2) final FINAL_v3.docx"*

⚠️ **Windows Only** - This application uses Windows-specific features (`os.startfile`) for opening files and directories. Compatible with Windows 7 and later.

A local Streamlit application that brings order to the chaos of your filesystem. Clean up messy file names, hunt down duplicates across directories, and standardize date formats with surgical precision—all with a user-friendly GUI and a preview-before-you-commit philosophy.

---

## ✨ Features

### 🧹 **File Name Cleaning**
Transform your chaotic file names into beautifully standardized masterpieces.

- **Character Replacement** - Replace spaces, special characters, or any substring with your chosen replacement (e.g., `my document.txt` → `my_document.txt`)
- **camelCase & PascalCase Conversion** - Convert filenames to developer-friendly formats while preserving separators
- **Regex Find & Replace** - Unleash the power of regular expressions with capture groups for complex transformations. Common use cases:
   - **Case conversion**: `(\w+)` → `\U\1` (uppercase), `\L\1` (lowercase), `\T\1` (title case)
   - **Prefixing/Suffixing**: `^` → `PREFIX_` (add to start), `$` → `_SUFFIX` (add to end)
   - **Remove special characters**: `[._#!]` → ` ` (replace with space) or `` (remove entirely)
   - **Extract and reorder**: `(\d{4})-(\w+)` → `\2_\1` (swap year and name)
   - **Number padding**: `(\d+)` → custom logic for `001`, `002`, etc.
   - **Remove parentheses content**: `\s*\([^)]*\)` → `` (removes "(1)", "(copy)", etc.)
   - **Collapse multiple spaces**: `\s+` → `_` (normalize whitespace)
 
- **Date Standardization** - Automatically detect and standardize dates in multiple formats to **`YYYY.MM.DD`** (customizable):
  
  **Supported Input Formats:**
  - Space-separated (4-digit year): `2025 01 31` → `2025.01.31`
  - Space-separated (year at end): `31 01 2025` or `01 31 2025` → `2025.01.31`
  - Space-separated (2-digit year): `25 01 31` or `01 31 25` → `2025.01.31`
  - Dot-separated: `31.01.2025` or `01.31.2025` → `2025.01.31`
  - ISO date formats: `2025-01-31` → `2025.01.31`
  - Slash formats: `2025/01/31` or `31/01/2025` → `2025.01.31`
  - Numeric (no separators): `20250131` → `2025.01.31`
  
  **Smart Detection:** For ambiguous dates (e.g., `12 01 2025`), defaults to European format (DD MM YYYY) unless logically impossible, then falls back to American format (MM DD YYYY)
  
  💡 *An interactive help panel in the app provides quick reference to all supported formats*
- **Preview Mode** - See exactly what will change before committing
- **Batch Operations** - Chain multiple operations together for complex transformations

### 🔍 **Duplicate File Finder**
Find potential duplicates across two directories using intelligent fuzzy matching.

- **TF-IDF Similarity** - Uses Term Frequency-Inverse Document Frequency for smarter filename matching (great for files with common words)
- **Size Comparison** - Compares file sizes as additional informational context (not used as a filter)
- **Configurable Name Threshold** - Adjust name similarity threshold to fine-tune results
- **Recursive Scanning** - Optional subdirectory scanning for deep searches
- **Confidence Scoring** - Each match gets a confidence score based on weighted similarity
- **Interactive Results** - Click to open files directly from the results table

### 🗂️ **Directory Explorer**
Navigate your filesystem with ease using an intuitive sidebar browser with history tracking.

---

## 🚀 Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd FileManagementApp
   ```

2. **Create and activate a virtual environment** *(optional but recommended)*
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser** to `http://localhost:8501`

---

## 📖 Usage

### File Name Cleaning
1. Navigate to the **"Clean File Names"** tab
2. Use the directory explorer to select a folder
3. Choose your cleanup operations:
   - Replace characters (e.g., replace spaces with underscores)
   - Convert to camelCase or PascalCase
   - Apply regex patterns
   - Standardize date formats (converts to `YYYY.MM.DD` by default; supports 10+ input formats)
     - Click the **"ℹ️ Supported Date Formats"** expander in the app for quick reference
4. **Preview** your changes in the table
5. Click **"Apply Changes"** when satisfied

### Duplicate Finding
1. Navigate to the **"Find Duplicates"** tab
2. Select **Directory 1** and **Directory 2**
3. Choose whether to include subdirectories for each
4. Adjust similarity thresholds (optional)
5. Click **"🔍 Explore Files"** to scan
6. Review potential duplicates with confidence scores
7. Click file paths to open them directly

---

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests with verbose output
pytest tests/ -v

# Run with coverage report
pytest --cov=. --cov-report=term-missing

# Run only file_cleaner tests
pytest tests/test_file_cleaner.py -v

# Generate HTML coverage report
pytest --cov=. --cov-report=html
```

Current test coverage: **84%** for `file_cleaner.py` with **59 passing tests**

---

## 🏗️ Architecture

### Code Quality Features
- ✅ **Type hints** throughout for better IDE support
- ✅ **pathlib.Path** for cross-platform file operations
- ✅ **Constants at module level** - no magic numbers
- ✅ **Comprehensive docstrings** for all functions
- ✅ **Refactored date parsing** with dedicated helper functions
- ✅ **DRY principle** - minimal code duplication

### Design Patterns
- Static methods for stateless operations
- Dictionary-based pattern management
- Separation of concerns (preview vs. apply)
- Configurable thresholds via constants

---

## 📋 Requirements

- **Windows 7 or later** (uses `os.startfile` for opening files)
- Python 3.8+
- streamlit >= 1.30.0
- python-dateutil >= 2.8.2
- pytest >= 7.4.0 *(for testing)*
- pytest-cov >= 4.1.0 *(for coverage)*

---

## 🗂️ Project Structure

```
FileManagementApp/
│
├── app.py                      # Main Streamlit application
├── file_cleaner.py             # File name cleaning operations
├── duplicate_finder.py         # Duplicate detection with fuzzy matching
├── help_content.py             # Centralized help text and UI content
│
├── tests/                      # Test suite
│   ├── __init__.py
│   └── test_file_cleaner.py    # Comprehensive tests (59 tests, 84% coverage)
│
├── requirements.txt            # Python dependencies
├── pyproject.toml              # pytest configuration
├── README.md                   # This file
│
├── __pycache__/                # Python bytecode cache
└── htmlcov/                    # Coverage reports (generated)
```

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Add new file cleaning operations
- Improve duplicate detection algorithms
- Expand test coverage
- Fix bugs or improve documentation

---

## 📝 License

This project is open source and available under the MIT License.

---

**Made with ☕ and a healthy dose of "I should probably organize my Downloads folder"**
