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