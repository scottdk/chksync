# chksync

A powerful Python command-line tool to compare two folders and show differences in size and file count. Features multiple output formats including Rich console output, plain text with Unicode box drawing, and CSV for data analysis.

When mygrating my NAS to a new Operating system, I wanted a faster way to verify a backup of tens of terabytes on a USB drive, under the assumption that if each root folder was the same size and contained the same number of files, then they can be considered equal. 

## Features

- 🔍 **Comprehensive Comparison** - Compares files and directories by size and file count
- 🎨 **Multiple Output Formats** - Rich console, plain text with Unicode borders, and CSV
- 📊 **Detailed Statistics** - Shows totals, differences, and counts with proper formatting
- ⚡ **High Performance** - Efficiently handles large directories with progress reporting
- 🎯 **Flexible Filtering** - Option to show only differences
- 📱 **Smart Auto-detection** - Automatically chooses best output format for terminal vs pipes
- 🧪 **Test Suite** - Includes comprehensive test file generator for development and validation

## Installation

### Prerequisites
- Python 3.6+
- Required packages: `rich`, `pandas`, `tabulate`

### Install Dependencies
```bash
pip install rich pandas tabulate
```

### Download
```bash
git clone https://github.com/scottdk/chksync.git
cd chksync
```

## Test File Generation

For testing and development purposes, the repository includes a `create_test_files.py` script that generates comprehensive test data.

### Running the Test File Generator

```bash
python create_test_files.py
```

This script creates a complete test directory structure with:

#### Basic Test Folders
- **`test/test_folder1/`** and **`test/test_folder2/`** - Realistic folder comparison scenarios
- Common files (same content), unique files, and files with different sizes
- Subdirectories with nested file structures
- Symbolic links (with fallback for unsupported systems)

#### Performance Test Folders  
- **`test/test_large_folder1/`** and **`test/test_large_folder2/`** - Large-scale testing
- 350+ files each with various numbering patterns
- Content variations between folders for comprehensive comparison testing
- Different file size patterns to test sorting and performance

#### Mixed Content Testing
- **`test/mixed_content/`** - Edge case testing scenarios
- Empty files, single lines, multi-line content
- Unicode characters and special content
- Whitespace handling and long lines
- Various file sizes from 0 bytes to 1KB+

### Generated Test Structure
```
test/
├── test_folder1/
│   ├── common.txt                    # Same content in both folders
│   ├── file1.txt                     # Different content/size
│   ├── unique1.txt                   # Only exists in folder1  
│   ├── takeout.zip -> ../dummy.zip   # Symbolic link
│   └── subdir1/
│       ├── sub_file.txt
│       └── sub_file1.txt
├── test_folder2/
│   ├── common.txt                    # Same as folder1
│   ├── file1.txt                     # Different from folder1
│   ├── unique2.txt                   # Only exists in folder2
│   ├── takeout.zip -> ../dummy.zip   # Symbolic link
│   └── subdir1/
│       ├── sub_file.txt
│       ├── sub_file1.txt
│       └── sub_file2.txt             # Extra file in folder2
├── test_large_folder1/               # 350+ files for performance testing
├── test_large_folder2/               # 350+ files with differences
├── mixed_content/                    # Various content types
└── dummy.zip                         # Target for symbolic links
```

### Test Scenarios

The generated test data provides scenarios for:
- **Basic functionality**: File size differences, unique files, common files
- **Directory structure**: Subdirectories with varying file counts  
- **Performance testing**: Large datasets with hundreds of files
- **Edge cases**: Empty files, Unicode content, long lines, whitespace
- **Symbolic links**: Link handling and fallback behavior
- **Sorting validation**: Mixed numbering patterns (1, 10, 100, 1000, etc.)

### Example Test Commands

After running `create_test_files.py`, test chksync with:

```bash
# Basic functionality test
python chksync.py test/test_folder1 test/test_folder2 --rich

# Performance test with large datasets  
python chksync.py test/test_large_folder1 test/test_large_folder2 --csv --only-diffs

# Mixed content testing
python chksync.py test/test_folder1 test/mixed_content --plain

# Verbose progress on large folders
python chksync.py test/test_large_folder1 test/test_large_folder2 --verbose
```

**Note**: Test files are automatically excluded from git tracking via `.gitignore`. The script can be run multiple times safely - it will recreate the entire test structure each time.

## Usage

### Basic Syntax
```bash
python chksync.py <folder1> <folder2> [OPTIONS]
```

### Alternative Syntax with Flags
```bash
python chksync.py -f1 <folder1> -f2 <folder2> [OPTIONS]
```

## Command Line Options

| Option | Long Form | Description |
|--------|-----------|-------------|
| `-r` | `--rich` | Force rich formatting (overrides auto-detection) |
| `-p` | `--plain` | Force plain text output (overrides rich auto-detection) |
| `-c` | `--csv` | Output in CSV format |
| `-v` | `--verbose` | Increase verbosity: `-v` for progress, `-vv` for debug output |
| `--only-diffs` | | Show only entries with differences |
| `-f1` | `--folder1` | First folder to compare (alternative to positional) |
| `-f2` | `--folder2` | Second folder to compare (alternative to positional) |

## Output Formats

### Rich Console Output (Default for Terminals)

Rich output provides colorized, professionally formatted tables with:
- Color-coded columns (cyan for names, green for sizes, yellow for file counts, red for differences)
- Proper number formatting with commas
- Markdown header with folder paths
- Footer row with totals

**Example:**
```bash
python chksync.py test/folder1 test/folder2 --rich
```

**Sample Output:**
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                                                                            Folder Comparison Report                                                                             ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Folder 1: test/folder1                                                                                                                                                        
Folder 2: test/folder2                                                                                                                                                        
┏━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━┳━━━━━━┓
┃ Name        ┃ Size1 ┃ Size2 ┃ SD ┃ Filecount1 ┃ Filecount2 ┃ CD ┃ DIFF ┃
┡━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━╇━━━━━━┩
│ file1.txt   │    85 │   111 │  * │          1 │          1 │    │   ** │
│ file2.txt   │   120 │     0 │  * │          1 │          0 │  * │   ** │
│ subdir1     │   453 │   867 │  * │          5 │          8 │  * │   ** │
├─────────────┼───────┼───────┼────┼────────────┼────────────┼────┼──────┤
│ TOTAL       │   658 │   978 │  3 │          7 │          9 │  2 │    3 │
└─────────────┴───────┴───────┴────┴────────────┴────────────┴────┴──────┘
```

### Plain Text Output with Unicode Borders

Plain output uses Unicode box drawing characters for professional appearance:
- Clean table layout with proper borders
- Right-aligned numeric columns
- Enhanced separator for totals row
- Works great for terminals that don't support Rich

**Example:**
```bash
python chksync.py test/folder1 test/folder2 --plain
```

**Sample Output:**
```
┌─────────────┬─────────┬─────────┬──────┬──────────────┬──────────────┬──────┬────────┐
│ Name        │   Size1 │   Size2 │   SD │   Filecount1 │   Filecount2 │   CD │   DIFF │
├─────────────┼─────────┼─────────┼──────┼──────────────┼──────────────┼──────┼────────┤
│ file1.txt   │      85 │     111 │    * │            1 │            1 │      │     ** │
│ file2.txt   │     120 │       0 │    * │            1 │            0 │    * │     ** │
│ subdir1     │     453 │     867 │    * │            5 │            8 │    * │     ** │
╞═════════════╪═════════╪═════════╪══════╪══════════════╪══════════════╪══════╪════════╡
│ TOTAL       │     658 │     978 │    3 │            7 │            9 │    2 │      3 │
└─────────────┴─────────┴─────────┴──────┴──────────────┴──────────────┴──────┴────────┘
```

### CSV Output

CSV format is perfect for data analysis, spreadsheets, and further processing:
- Machine-readable format
- Raw numbers without formatting
- Easy to import into Excel, databases, or analysis tools
- Great for piping to other commands

**Example:**
```bash
python chksync.py test/folder1 test/folder2 --csv
```

**Sample Output:**
```csv
Name,Size1,Size2,SD,Filecount1,Filecount2,CD,DIFF
file1.txt,85,111,*,1,1,,**
file2.txt,120,0,*,1,0,*,**
subdir1,453,867,*,5,8,*,**
TOTAL,658,978,3,7,9,2,3
```

## Column Meanings

| Column | Description |
|--------|-------------|
| **Name** | File or directory name |
| **Size1** | Size in bytes in first folder |
| **Size2** | Size in bytes in second folder |
| **SD** | Size Difference indicator (`*` if sizes differ) |
| **Filecount1** | Number of files in first folder |
| **Filecount2** | Number of files in second folder |
| **CD** | Count Difference indicator (`*` if file counts differ) |
| **DIFF** | Overall difference indicator (`**` if any difference exists) |

## Advanced Usage Examples

### Show Only Differences
```bash
python chksync.py folder1 folder2 --only-diffs
```

### Verbose Output with Progress
```bash
python chksync.py folder1 folder2 --verbose
```

### Debug Mode
```bash
python chksync.py folder1 folder2 -vv
```

### Large Dataset Analysis with Filtering
```bash
# Show just header and first 10 entries
python chksync.py large_folder1 large_folder2 --csv | head -11

# Show only the totals line
python chksync.py large_folder1 large_folder2 --csv | tail -1

# Count total files processed
python chksync.py large_folder1 large_folder2 --csv | wc -l

# Show top 3 and bottom 5 rows with separator
python chksync.py large_folder1 large_folder2 --csv | { head -4; echo "..."; tail -5; }
```

### Integration with Other Tools
```bash
# Save results to file
python chksync.py folder1 folder2 --csv > comparison_results.csv

# Find only files with differences
python chksync.py folder1 folder2 --csv | grep "\\*\\*"

# Sort by size difference
python chksync.py folder1 folder2 --csv | sort -t, -k2 -n
```

## Performance

chksync efficiently handles large directories:
- Uses `os.scandir()` for optimal performance
- Progress reporting for long-running operations
- Processes 10,000+ files without issues
- Memory-efficient recursive directory scanning

## Error Handling

- **Missing folders**: Clear error messages for non-existent directories
- **Permission errors**: Graceful handling of inaccessible files/directories
- **Invalid arguments**: Comprehensive argument validation
- **Large datasets**: Automatic progress reporting and memory management

## Auto-Detection Logic

chksync automatically chooses the best output format:
- **CSV flag (`--csv`)**: Always uses CSV format
- **Plain flag (`--plain`)**: Forces plain text output
- **Rich flag (`--rich`)**: Forces rich console output
- **Auto-detection**: Uses rich format for terminals, plain for pipes/redirects

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is open source. Feel free to use, modify, and distribute.

## Requirements

- Python 3.6+
- rich
- pandas  
- tabulate

## Author

Created by Scott DK

---

**Note**: This tool is designed for comparing file structures and sizes. It does not compare file contents - only metadata like size and file counts.