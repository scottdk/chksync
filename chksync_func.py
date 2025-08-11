#!/usr/bin/env python3
"""A tool to compare two folders and show differences in size and file count."""

import argparse
import os
import sys
import csv
import io
import pandas as pd
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from tabulate import tabulate


class DebugUtils:
    """Utility class for debug printing."""
    
    @staticmethod
    def debug_print(message, vars_to_show=None):
        """Helper function to print debug messages with function name, line number, and optionally caller variables."""
        frame = sys._getframe(2)  # Get caller's caller frame (skip this static method)
        line_num = frame.f_lineno
        func_name = frame.f_code.co_name

        # Optionally show caller variables
        var_info = ""
        if vars_to_show:
            caller_locals = frame.f_locals
            var_values = []
            for var_name in vars_to_show:
                if var_name in caller_locals:
                    var_values.append(f"{var_name}={caller_locals[var_name]}")
                else:
                    var_values.append(f"{var_name}=<not found>")
            var_info = f" [{', '.join(var_values)}]"

        print(f"({func_name:<25}:{line_num:>3}){var_info} {message}")

    @staticmethod
    def debug_with_counters(message):
        """Debug print that automatically shows common counter variables."""
        frame = sys._getframe(2)  # Get caller's caller frame
        caller_locals = frame.f_locals

        # Look for common counter variables
        counters = ['folder', 'entry', 'fp', 'processed_parent_items', 'num_sized_files_total',
                    'num_sized_files_this_folder', 'counted_files_total', 'counted_files_this_folder',
                    'processed_files', 'total_file_size_so_far', 'filecount_this_item', 'size_this_item',
                    'size_this_file', 'total_size_this_folder']
        found_counters = []
        for var in counters:
            if var in caller_locals:
                found_counters.append(f"{var.upper():<27} == {caller_locals[var]}")
        sep = "\n" + " " * 33 + "- "
        counter_info = f"{sep}{sep.join(found_counters)}" if found_counters else ""

        line_num = frame.f_lineno
        func_name = frame.f_code.co_name
        print(f"({func_name:<25}:{line_num:>3}) {message}{counter_info}")


class FolderScanner:
    """Handles scanning folders and collecting file/size information."""
    
    def __init__(self, verbose_level=0):
        self.verbose_level = verbose_level
    
    def scan_folder(self, folder):
        """Get first level entries from a folder with size and file count."""
        if self.verbose_level >= 2:
            DebugUtils.debug_with_counters("START: scanning a parent level item")
        
        entries = {}
        # Use os.scandir() for better performance on large directories
        # It returns DirEntry objects that cache stat information
        processed_parent_items = 0
        num_sized_files_total = 0
        counted_files_total = 0
        total_file_size_so_far = 0

        with os.scandir(folder) as dir_entries:
            for entry in dir_entries:
                processed_parent_items += 1

                try:
                    if entry.is_file(follow_symlinks=False):
                        # Use cached stat info from DirEntry
                        num_sized_files_total += 1
                        # For files, we can directly get size and count
                        # filecount is always 1 for a single file
                        size_this_item = entry.stat().st_size
                        filecount_this_item = 1
                        counted_files_total += 1
                        if self.verbose_level >= 2:
                            DebugUtils.debug_with_counters("(Found file, skip scans) Scanning")
                    elif entry.is_dir(follow_symlinks=False):
                        # For directories, we still need to calculate size and count
                        path = entry.path
                        size_this_item, num_sized_files_total = self._get_dir_size(
                            path, parent_folder=folder, 
                            num_sized_files_total=num_sized_files_total
                        )

                        # For directories, we still need to calculate size and count
                        filecount_this_item, counted_files_total = self._get_file_count(
                            path, parent_folder=folder, 
                            counted_files_total=counted_files_total
                        )
                        if self.verbose_level >= 2:
                            DebugUtils.debug_with_counters("(Found directory, run scans) Scanning")
                    else:
                        continue

                    entries[entry.name] = (size_this_item, filecount_this_item)
                    total_file_size_so_far = (
                        total_file_size_so_far + size_this_item 
                        if size_this_item else total_file_size_so_far
                    )

                except (OSError, PermissionError) as e:
                    if self.verbose_level >= 2:
                        DebugUtils.debug_with_counters(f"Warning: Cannot access ENTRY=={entry.name}: {e}")
                    continue

                # Show progress every 100 entries
                if self.verbose_level >= 1 and (
                    counted_files_total % 100 == 0 
                    or counted_files_total == filecount_this_item 
                    or filecount_this_item > 100
                ):
                    if self.verbose_level >= 2:
                        DebugUtils.debug_with_counters("processed 100 entries")
                    print(
                        f"\rProcessing {folder:<30}, "
                        f"Total items: {counted_files_total:>10,} "
                        f"Total size: {total_file_size_so_far:>10,}", 
                        end="", flush=True
                    )

        if self.verbose_level >= 2:
            DebugUtils.debug_with_counters("FINISH: scanning a parent level item")
        
        if self.verbose_level >= 1:
            # Show final progress line before clearing
            print(
                f"\rCompleted {folder:<30}, "
                f"Total items: {counted_files_total:>10,} "
                f"Total size: {total_file_size_so_far:>10,}"
            )
            # Clear the progress line by overwriting it with spaces and carriage return
            print(f"\r{' ' * 120}", end="", flush=True)
            print("\r", end="", flush=True)
        
        return entries

    def _get_dir_size(self, folder, parent_folder=None, num_sized_files_total=0):
        """Calculate directory size recursively."""
        if self.verbose_level >= 2:
            DebugUtils.debug_with_counters("START: sizing")
        
        num_sized_files_this_folder = 0
        size_this_file = 0
        total_size_this_folder = 0
        
        for root, dirs, files in os.walk(folder):
            for f in files:
                fp = os.path.join(root, f)
                try:
                    num_sized_files_total += 1
                    num_sized_files_this_folder += 1
                    # Show progress every 100 entries
                    if self.verbose_level >= 2 and (
                        num_sized_files_total % 100 == 0 
                        or num_sized_files_total == 1 
                        or total_size_this_folder >= 100
                    ):
                        DebugUtils.debug_with_counters("Processed 100 entries")
                    
                    size_this_file = os.path.getsize(fp)
                    total_size_this_folder += size_this_file
                except Exception:
                    pass
                
                # Show progress every 100 entries
                if self.verbose_level >= 1 and (
                    num_sized_files_total % 100 == 0 
                    or num_sized_files_this_folder > 100
                ):
                    if self.verbose_level >= 2:
                        DebugUtils.debug_with_counters("processed 100 entries")
                    print(
                        f"\rProcessing {folder:<30}, "
                        f"Total items: {num_sized_files_total:>10,}, "
                        f"Total size: {num_sized_files_total:>10,}", 
                        end="", flush=True
                    )

        return total_size_this_folder, num_sized_files_total

    def _get_file_count(self, folder, parent_folder=None, counted_files_total=0):
        """Count files in directory recursively."""
        if self.verbose_level >= 2:
            DebugUtils.debug_with_counters("START: counting")

        total_count_this_folder = 0
        for _, _, files in os.walk(folder):
            total_count_this_folder += len(files)
            counted_files_total += len(files)
            # Show progress every 100 entries
            if self.verbose_level >= 2 and (
                counted_files_total % 100 == 0 
                or counted_files_total == 1 
                or total_count_this_folder >= 100
            ):
                DebugUtils.debug_with_counters("Processed 100 entries")
        
        if self.verbose_level >= 2:
            DebugUtils.debug_with_counters("FINISH: counting")

        return total_count_this_folder, counted_files_total


class ComparisonData:
    """Handles building and managing comparison data."""
    
    def __init__(self, entries1, entries2, only_diffs=False):
        self.entries1 = entries1
        self.entries2 = entries2
        self.only_diffs = only_diffs
        self.data = []
        
    def build_data(self):
        """Build the comparison data from the two folder entries."""
        all_names = sorted(set(self.entries1.keys()) | set(self.entries2.keys()))

        # Prepare data for DataFrame
        self.data = []
        total_size1 = 0
        total_size2 = 0
        total_fc1 = 0
        total_fc2 = 0
        size_diff_count = 0
        file_diff_count = 0
        diff_count = 0

        for name in all_names:
            size1, fc1 = self.entries1.get(name, (0, 0))
            size2, fc2 = self.entries2.get(name, (0, 0))
            sizediff = '*' if size1 != size2 else ''
            filediff = '*' if fc1 != fc2 else ''
            diff = '**' if fc1 != fc2 or size1 != size2 else ''

            # Only add row if not filtering or if there are differences
            if not self.only_diffs or diff:
                self.data.append({
                    'Name': name,
                    'Size1': size1,  # Keep as number for proper formatting
                    'Size2': size2,  # Keep as number for proper formatting
                    'SD': sizediff,
                    'Filecount1': fc1,  # Keep as number for proper formatting
                    'Filecount2': fc2,  # Keep as number for proper formatting
                    'CD': filediff,
                    'DIFF': diff
                })

            total_size1 += size1
            total_size2 += size2
            total_fc1 += fc1
            total_fc2 += fc2

            if size1 != size2:
                size_diff_count += 1
            if fc1 != fc2:
                file_diff_count += 1
            if size1 != size2 or fc1 != fc2:
                diff_count += 1

        # Add separator row before totals - like header separator
        separator_row = {
            'Name': "───────────────",
            'Size1': "───────────",
            'Size2': "───────────", 
            'SD': "──────",
            'Filecount1': "────────────────",
            'Filecount2': "────────────────",
            'CD': "──────",
            'DIFF': "────────"
        }
        self.data.append(separator_row)

        # Add totals row to the data
        totals_row = {
            'Name': "TOTAL",
            'Size1': total_size1,
            'Size2': total_size2,
            'SD': size_diff_count,
            'Filecount1': total_fc1,
            'Filecount2': total_fc2,
            'CD': file_diff_count,
            'DIFF': diff_count
        }

        self.data.append(totals_row)
        return self.data

def parse_arguments():
    """Parse command line arguments and return the parsed args."""
    parser = argparse.ArgumentParser(
        description='Compare two folders and show differences in size and file count',
        prog='chksync'
    )

    # Add folder arguments - can be used either positionally or with flags
    parser.add_argument('folder1', nargs='?', help='First folder to compare')
    parser.add_argument('folder2', nargs='?', help='Second folder to compare')
    parser.add_argument('-f1', '--folder1', dest='folder1_flag', 
                       help='First folder to compare (alternative to positional)')
    parser.add_argument('-f2', '--folder2', dest='folder2_flag', 
                       help='Second folder to compare (alternative to positional)')

    # Add other options  
    parser.add_argument('-r', '--rich', action='store_true', default=False,
                       help='Force rich formatting (overrides auto-detection)')
    parser.add_argument('-p', '--plain', action='store_true', default=False,
                       help='Force plain text output (overrides rich auto-detection)')
    parser.add_argument('-c', '--csv', action='store_true', default=False,
                       help='Output in CSV format')
    parser.add_argument('-v', '--verbose', action='count', default=0,
                       help='Increase verbosity: -v for progress, -vv for debug output')
    parser.add_argument('--only-diffs', action='store_true', 
                       help='Show only entries with differences')

    return parser.parse_args()

def validate_and_get_folders(args, parser):
    """Validate arguments and return the two folders to compare."""
    # Determine folder1 and folder2 - prefer flags over positional
    folder1 = args.folder1_flag if args.folder1_flag else args.folder1
    folder2 = args.folder2_flag if args.folder2_flag else args.folder2

    # Validate that we have both folders
    if not folder1 or not folder2:
        parser.error('Two folders must be specified either positionally or using -f1/-f2 flags')

    # Validate folders exist
    if not os.path.exists(folder1):
        parser.error(f'Folder1 does not exist: {folder1}')
    if not os.path.exists(folder2):
        parser.error(f'Folder2 does not exist: {folder2}')

    return folder1, folder2

def should_use_rich_output(args):
    """Determine whether to use rich output formatting."""
    # Check for CSV output first - it overrides everything
    if args.csv:
        return False
        
    # Check for explicit plain flag first - it overrides everything
    if args.plain:
        return False

    # Check for explicit rich flag
    if args.rich:
        return True

    # Auto-detect: use rich if output is going to a terminal
    return sys.stdout.isatty()

def build_comparison_data(entries1, entries2, only_diffs):
    """Build the comparison data from the two folder entries."""
    all_names = sorted(set(entries1.keys()) | set(entries2.keys()))

    # Prepare data for DataFrame
    data = []
    total_size1 = 0
    total_size2 = 0
    total_fc1 = 0
    total_fc2 = 0
    size_diff_count = 0
    file_diff_count = 0
    diff_count = 0

    for name in all_names:
        size1, fc1 = entries1.get(name, (0, 0))
        size2, fc2 = entries2.get(name, (0, 0))
        sizediff = '*' if size1 != size2 else ''
        filediff = '*' if fc1 != fc2 else ''
        diff = '**' if fc1 != fc2 or size1 != size2 else ''

        # Only add row if not filtering or if there are differences
        if not only_diffs or diff:
            data.append({
                'Name': name,
                'Size1': size1,  # Keep as number for proper formatting
                'Size2': size2,  # Keep as number for proper formatting
                'SD': sizediff,
                'Filecount1': fc1,  # Keep as number for proper formatting
                'Filecount2': fc2,  # Keep as number for proper formatting
                'CD': filediff,
                'DIFF': diff
            })

        total_size1 += size1
        total_size2 += size2
        total_fc1 += fc1
        total_fc2 += fc2

        if size1 != size2:
            size_diff_count += 1
        if fc1 != fc2:
            file_diff_count += 1
        if size1 != size2 or fc1 != fc2:
            diff_count += 1

    # Add separator row before totals - like header separator
    separator_row = {
        'Name': "───────────────",
        'Size1': "───────────",
        'Size2': "───────────", 
        'SD': "──────",
        'Filecount1': "────────────────",
        'Filecount2': "────────────────",
        'CD': "──────",
        'DIFF': "────────"
    }
    data.append(separator_row)

    # Add totals row to the data
    totals_row = {
        'Name': "TOTAL",
        'Size1': total_size1,
        'Size2': total_size2,
        'SD': size_diff_count,
        'Filecount1': total_fc1,
        'Filecount2': total_fc2,
        'CD': file_diff_count,
        'DIFF': diff_count
    }

    data.append(totals_row)
    return data

def format_markdown_table(data, use_rich=False):
    """Format the data as a properly aligned markdown table."""
    # Create DataFrame with main data and totals
    df = pd.DataFrame(data)

    # Format numbers with commas and handle TOTAL row styling
    df_formatted = df.copy()
    for col in ['Size1', 'Size2', 'Filecount1', 'Filecount2']:
        # For both rich and plain output, just format with commas (no bold)
        # Don't format separator row (contains dashes)
        df_formatted[col] = df[col].apply(
            lambda x: f"{x:,}" if isinstance(x, (int, float)) else str(x)
        )

    # Format SD, CD, and DIFF columns - add commas only for TOTAL row
    for col in ['SD', 'CD', 'DIFF']:
        df_formatted[col] = df.apply(
            lambda row: f"{row[col]:,}" 
            if row['Name'] == 'TOTAL' and isinstance(row[col], (int, float)) 
            else str(row[col]), 
            axis=1
        )

    # Create the table with markdown format - right align numeric columns
    markdown_output = tabulate(
        df_formatted, headers='keys', tablefmt='github', showindex=False,
        colalign=('left', 'right', 'right', 'right', 'right', 'right', 'right', 'right')
    )

    # Manually modify the markdown to ensure right alignment
    lines = markdown_output.split('\n')
    if len(lines) >= 2:
        # Replace the separator line to force right alignment for numeric columns
        separator_line = lines[1]
        # Modify separator: left, right, right, right, right, right, right, right
        separator_parts = separator_line.split('|')
        if len(separator_parts) >= 9:  # Including empty parts at start/end
            for i in range(2, 9):  # Columns 2-8 should be right-aligned
                separator_parts[i] = separator_parts[i].replace('-', '').rjust(
                    len(separator_parts[i]), '-'
                )
            lines[1] = '|'.join(separator_parts)
        markdown_output = '\n'.join(lines)

    return markdown_output

def format_csv_output(data):
    """Format the data as CSV output."""
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Name', 'Size1', 'Size2', 'SD', 'Filecount1', 'Filecount2', 'CD', 'DIFF'])
    
    # Write data rows, excluding separator row
    for entry in data:
        # Skip separator row (contains unicode dashes)
        if isinstance(entry['Size1'], str) and entry['Size1'].startswith('─'):
            continue
            
        # Format numbers for CSV - no commas, just raw numbers
        size1 = entry['Size1'] if isinstance(entry['Size1'], (int, float)) else entry['Size1']
        size2 = entry['Size2'] if isinstance(entry['Size2'], (int, float)) else entry['Size2']
        filecount1 = entry['Filecount1'] if isinstance(entry['Filecount1'], (int, float)) else entry['Filecount1']
        filecount2 = entry['Filecount2'] if isinstance(entry['Filecount2'], (int, float)) else entry['Filecount2']
        
        # Format SD, CD, DIFF columns
        sd = entry['SD'] if isinstance(entry['SD'], (int, float)) else entry['SD']
        cd = entry['CD'] if isinstance(entry['CD'], (int, float)) else entry['CD']
        diff = entry['DIFF'] if isinstance(entry['DIFF'], (int, float)) else entry['DIFF']
        
        writer.writerow([
            entry['Name'],
            size1,
            size2,
            sd,
            filecount1,
            filecount2,
            cd,
            diff
        ])
    
    return output.getvalue().strip()

def output_results(data, folder1, folder2, use_rich, csv_output=False, verbose_level=0):
    """Output results in rich format, plain markdown, or CSV."""
    if csv_output:
        if verbose_level >= 1:
            debug_print("Using CSV output")
        csv_output_text = format_csv_output(data)
        print(csv_output_text)
    elif use_rich:
        if verbose_level >= 1:
            debug_print("Using rich console output")
        console = Console()

        # Create markdown content with folder information
        markdown_content = f"""# Folder Comparison Report

**Folder 1:** `{folder1}`  
**Folder 2:** `{folder2}`
"""

        # Create a table for rich output
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan", no_wrap=True, justify="left")
        table.add_column("Size1", style="green", justify="right")
        table.add_column("Size2", style="green", justify="right")
        table.add_column("SD", justify="right")
        table.add_column("Filecount1", style="yellow", justify="right")
        table.add_column("Filecount2", style="yellow", justify="right")
        table.add_column("CD", justify="right")
        table.add_column("DIFF", style="red", justify="right")

        for entry in data:
            # Skip the separator row in rich output (we handle it manually)
            if isinstance(entry['Size1'], str) and entry['Size1'].startswith('─'):
                continue
                
            # Rich formatting with proper alignment and commas - all values must be strings
            size1_formatted = f"{entry['Size1']:,}" if entry['Size1'] != 'N/A' else 'N/A'
            size2_formatted = f"{entry['Size2']:,}" if entry['Size2'] != 'N/A' else 'N/A'
            filecount1_formatted = f"{entry['Filecount1']:,}" if entry['Filecount1'] != 'N/A' else 'N/A'
            filecount2_formatted = f"{entry['Filecount2']:,}" if entry['Filecount2'] != 'N/A' else 'N/A'

            # Format SD, CD, DIFF with commas only for TOTAL row
            sd_formatted = (f"{entry['SD']:,}" if entry['Name'] == 'TOTAL' 
                          and isinstance(entry['SD'], (int, float)) else str(entry['SD']))
            cd_formatted = (f"{entry['CD']:,}" if entry['Name'] == 'TOTAL' 
                          and isinstance(entry['CD'], (int, float)) else str(entry['CD']))
            diff_formatted = (f"{entry['DIFF']:,}" if entry['Name'] == 'TOTAL' 
                            and isinstance(entry['DIFF'], (int, float)) else str(entry['DIFF']))

            # Add separator line before TOTAL row
            if entry['Name'] == 'TOTAL':
                table.add_row(
                    "───────────────",  # Name column
                    "───────────",      # Size1 column
                    "───────────",      # Size2 column
                    "──────",           # SD column
                    "────────────────", # Filecount1 column
                    "────────────────", # Filecount2 column
                    "──────",           # CD column
                    "────────"          # DIFF column
                )
                table.add_row(
                    f"[bold]{entry['Name']}[/bold]",
                    f"[bold]{size1_formatted}[/bold]",
                    f"[bold]{size2_formatted}[/bold]",
                    f"[bold]{sd_formatted}[/bold]",
                    f"[bold]{filecount1_formatted}[/bold]",
                    f"[bold]{filecount2_formatted}[/bold]",
                    f"[bold]{cd_formatted}[/bold]",
                    f"[bold]{diff_formatted}[/bold]"
                )
            else:
                table.add_row(
                    str(entry['Name']),
                    size1_formatted,
                    size2_formatted,
                    sd_formatted,
                    filecount1_formatted,
                    filecount2_formatted,
                    cd_formatted,
                    diff_formatted
                )

        print("\n")
        # Render the markdown header
        md = Markdown(markdown_content)
        console.print(md)
        console.print(table)
    else:
        if verbose_level >= 1:
            debug_print("Using plain markdown output")
        # Plain markdown output - just the table with borders
        markdown_table = format_markdown_table(data, use_rich=False)
        
        # Extract the separator line from the table to use as border, but replace | with │
        lines = markdown_table.split('\n')
        separator_line = lines[1] if len(lines) > 1 else "│" + "─" * 118 + "│"
        
        # Create top border with corners ┌ ┐ and T-junctions ┬
        top_border = separator_line.replace('|', '┬')
        top_border = top_border.replace('-', '─')
        # Replace first and last ┬ with corners
        if top_border.startswith('┬'):
            top_border = '┌' + top_border[1:]
        if top_border.endswith('┬'):
            top_border = top_border[:-1] + '┐'
        
        # Create bottom border with corners └ ┘ and T-junctions ┴
        bottom_border = separator_line.replace('|', '┴')
        bottom_border = bottom_border.replace('-', '─')
        # Replace first and last ┴ with corners
        if bottom_border.startswith('┴'):
            bottom_border = '└' + bottom_border[1:]
        if bottom_border.endswith('┴'):
            bottom_border = bottom_border[:-1] + '┘'
        
        # Also replace | with appropriate T-junctions in the header separator line within the table
        # and replace - with unicode dashes for consistency
        if len(lines) > 1:
            header_separator = lines[1].replace('-', '─')
            # Split by | to handle each position
            parts = header_separator.split('|')
            if len(parts) > 2:
                # First position gets ├, last position gets ┤, middle positions get ┼
                new_parts = []
                for i, part in enumerate(parts):
                    if i == 0:
                        new_parts.append(part)  # Keep empty start
                    elif i == 1:
                        new_parts.append(part)  # Keep first part as is
                    elif i == len(parts) - 1:
                        new_parts.append(part)  # Keep empty end
                    else:
                        new_parts.append(part)  # Keep content as is
                # Now join with appropriate connectors
                result = new_parts[0] + '├'
                for i in range(1, len(new_parts) - 2):
                    result += new_parts[i] + '┼'
                result += new_parts[-2] + '┤' + new_parts[-1]
                lines[1] = result
            else:
                lines[1] = header_separator.replace('|', '┼')
            markdown_table = '\n'.join(lines)
        
        # Replace all | with │ in the table content for vertical lines
        markdown_table = markdown_table.replace('|', '│')
        
        print(top_border)
        print(markdown_table)
        print(bottom_border)

def main():
    """Main function to run the folder comparison tool."""
    args = parse_arguments()
    parser = argparse.ArgumentParser(prog='chksync')  # Create parser for error reporting

    folder1, folder2 = validate_and_get_folders(args, parser)

    only_diffs = args.only_diffs
    verbose_level = args.verbose
    csv_output = args.csv
    use_rich = should_use_rich_output(args)

    entries1 = get_first_level_entries(folder1, verbose_level=verbose_level)
    entries2 = get_first_level_entries(folder2, verbose_level=verbose_level)

    data = build_comparison_data(entries1, entries2, only_diffs)

    output_results(data, folder1, folder2, use_rich, csv_output, verbose_level)


if __name__ == "__main__":
    main()