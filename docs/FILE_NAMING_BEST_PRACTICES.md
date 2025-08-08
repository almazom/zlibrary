# File Naming Best Practices for EPUB Downloads

## Overview
The EPUB download pipeline automatically applies best practices to ensure files are download-friendly, URL-safe, and compatible across all platforms.

## Best Practices Applied

### 1. **Replace Spaces with Underscores**
- **Why**: Spaces break URLs, cause issues in downloads, and require escaping in shells
- **Example**: 
  - ❌ `Data and Goliath The Hidden Battles.epub`
  - ✅ `Data_and_Goliath_The_Hidden_Battles.epub`

### 2. **Transliterate Non-ASCII Characters**
- **Why**: Prevents encoding issues, ensures compatibility across systems
- **Example**:
  - ❌ `Преступление и наказание.epub`
  - ✅ `Prestuplenie_i_nakazanie.epub`

### 3. **Remove Special Characters**
- **Why**: Special characters can break shells, URLs, and filesystem operations
- **Allowed**: Only alphanumeric, underscore (_), and dash (-)
- **Example**:
  - ❌ `Book: The $ecret! (2024).epub`
  - ✅ `Book_The_Secret_2024.epub`

### 4. **Avoid Multiple Dots**
- **Why**: Can create hidden files on Unix systems, causes confusion
- **Example**:
  - ❌ `book.v2.final.epub`
  - ✅ `book_v2_final.epub`

### 5. **Length Limitation**
- **Why**: Filesystem compatibility (255 char limit on most systems)
- **Practice**: Limit to 100 characters for safety
- **Example**:
  - ❌ 200+ character filename
  - ✅ Truncated to 100 chars max

## Implementation

The renaming happens automatically in two places:

1. **During Download** - Immediate application of best practices
2. **Post-processing** - EPUBDiagnostics validates and renames if needed

## Examples of Transformed Filenames

| Original | Transformed | Reason |
|----------|------------|--------|
| `Data and Goliath.epub` | `Data_and_Goliath.epub` | Spaces → underscores |
| `Взломать всё.epub` | `Vzlomat_vsyo.epub` | Cyrillic → Latin |
| `Book: Part 1 (2024).epub` | `Book_Part_1_2024.epub` | Special chars removed |
| `my.book.v2.epub` | `my_book_v2.epub` | Multiple dots removed |

## Benefits

1. **URL-Safe**: Can be shared in links without encoding
2. **Shell-Safe**: No need for quotes in terminal commands
3. **Cross-Platform**: Works on Linux, Windows, macOS
4. **Download-Friendly**: No issues with browsers or download managers
5. **API-Ready**: Perfect for web services and APIs

## Usage

The pipeline automatically applies these rules. No manual intervention needed:

```bash
# Downloads with automatic best-practice naming
./scripts/epub_search.sh --download "Book Title With Spaces"
# Result: Book_Title_With_Spaces.epub
```

## Code Location

- **Renaming Logic**: `src/pipeline/epub_diagnostics.py`
- **Download Script**: `scripts/epub_search.sh`
- **Validation**: `src/pipeline/cognitive_validator.py`

## Testing

```bash
# Test renaming of existing files
./scripts/rename_cyrillic_files.sh downloads/

# Test new download
./scripts/epub_search.sh --download "Test Book Name"
```

## Summary

Following these best practices ensures:
- ✅ No broken downloads
- ✅ No URL encoding issues  
- ✅ No shell escaping needed
- ✅ Cross-platform compatibility
- ✅ Clean, professional filenames