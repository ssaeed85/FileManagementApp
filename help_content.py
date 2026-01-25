"""
Help content and UI text for the File Management Application.

This module centralizes all help text, tooltips, and informational content
to make maintenance and updates easier.
"""

# Duplicate Finder Help Content
DUPLICATE_FINDER_HOW_TO = """
**Getting Started:**

1. **Select Two Directories**
   - Use the sidebar directory explorer to browse your filesystem
   - Click "📂 Select from Sidebar" to set Folder 1
   - Navigate to a different location and click the button again to set Folder 2
   - Each folder path is displayed in the respective column

2. **Configure Scanning Options**
   - **Include Subdirectories**: Check to scan folders recursively
   - Toggle separately for each directory based on your needs
   - Useful when searching through nested folder structures

3. **Explore Files**
   - Click "🔍 Explore Files" to scan both directories
   - The app counts files in each location
   - Wait for the scan to complete (progress shown)

4. **Adjust Matching Settings**
   - **Name Similarity Threshold (default 0.7)**: How similar filenames must be
     - Lower = more matches, but more false positives
     - Higher = fewer matches, but more accurate
   - **Use Smart Matching (TF-IDF)**: Recommended for better results

5. **Find Duplicates**
   - Click "🔍 Find Duplicates" to compare files
   - Results show potential matches with confidence scores
   - Click any file path to open it in your default application

6. **Review Results**
   - Each match shows filename, path, size, name match %, size match %, and confidence
   - Sort by confidence (highest first) to find best matches
   - Use the information to decide which files to keep or remove

**💡 Pro Tips:**
- Files must have the **same extension** to be considered duplicates
- Start with default threshold (0.7) and adjust if needed
- Click file paths to quickly open and compare actual content
- Size similarity is informational only - not used as a filter
"""

DUPLICATE_FINDER_HOW_IT_WORKS = """
**How It Works:**

The duplicate finder uses intelligent fuzzy matching to identify potential duplicates across two directories:

**🔤 Name Similarity (TF-IDF)**
- Uses **Term Frequency-Inverse Document Frequency** for smarter matching
- Tokenizes filenames into words (e.g., "project report 2024" → ["project", "report", "2024"])
- Great for files with common words like "document", "report", "backup"
- Less weight given to common terms, more weight to unique identifiers

**📏 Size Similarity (Informational)**
- Compares file sizes as additional context
- Calculated as: `smaller_size / larger_size`
- Perfect match = 1.0, different sizes = lower score
- **Not used as a filter** - shown for reference only

**🎯 Confidence Score**
- Weighted combination: **60% name similarity + 40% size similarity**
- Higher confidence = more likely to be a duplicate
- Results sorted by confidence (highest first)

**⚙️ Name Threshold Explained:**
- **Name Threshold (default 0.7)**: Minimum name similarity to consider (0-1 scale)
- Lower threshold = more matches but more false positives
- Higher threshold = fewer matches but more accurate

**💡 Pro Tips:**
- Start with default thresholds and adjust based on results
- Files must have the **same extension** to match
- Enable subdirectories for deep scanning
- Click file paths in results to open them directly
- Use preview before making any deletion decisions
"""

# File Cleaner Help Content
FILE_CLEANER_HOW_TO = """
**Getting Started:**

1. **Select a Directory**
   - Use the sidebar directory explorer to navigate to your target folder
   - The current path is displayed, and you can click folder names to navigate

2. **Choose Your Operations**
   - Check the boxes for operations you want to apply:
     - **Replace strings**: Replace specific characters or words (e.g., spaces → underscores)
     - **Convert to camelCase/PascalCase**: Developer-friendly naming conventions
     - **Regex find & replace**: Advanced pattern matching with capture groups
     - **Standardize date formats**: Auto-detect and convert dates to YYYY.MM.DD

3. **Configure Settings**
   - Each operation has specific settings that appear when enabled
   - Add multiple replacements if needed
   - Use case-sensitive or case-insensitive matching

4. **Preview Changes**
   - Click "Preview Changes" to see exactly what will happen
   - Review the before/after table carefully
   - No files are modified during preview

5. **Apply Changes**
   - Once satisfied with the preview, click "Apply Changes"
   - Files are renamed immediately (be careful!)
   - Click file paths to open them in your default application

**💡 Pro Tips:**
- Always preview before applying changes
- Chain multiple operations together for complex transformations
- Use regex for advanced renaming patterns (see examples below)
- Date standardization works with 10+ input formats automatically
"""

FILE_CLEANER_DATE_FORMATS = """
**The app automatically detects and converts dates in the following formats:**

**Space-separated:**
- `2025 01 31` → `2025.01.31` (YYYY MM DD)
- `31 01 2025` → `2025.01.31` (DD MM YYYY)
- `25 01 31` → `2025.01.31` (YY MM DD)

**Dot-separated:**
- `31.01.2025` → `2025.01.31`
- `01.31.2025` → `2025.01.31`

**ISO and slash formats:**
- `2025-01-31` → `2025.01.31`
- `2025/01/31` → `2025.01.31`
- `31-01-2025` → `2025.01.31`
- `31/01/2025` → `2025.01.31`

**Numeric (no separators):**
- `20250131` → `2025.01.31`
- `31012025` → `2025.01.31`

**Smart Detection:** For ambiguous dates like `12 01 2025`, the app defaults to 
European format (DD MM YYYY) unless logically impossible, then tries American format (MM DD YYYY).

💡 **Tip:** Select your desired output format when you enable "Standardize date formats" below.
"""
