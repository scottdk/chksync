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
        """Print debug messages with function name, line number, and optional caller variables."""
        frame = sys._getframe(2)
        line_num = frame.f_lineno
        func_name = frame.f_code.co_name

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
        frame = sys._getframe(2)
        caller_locals = frame.f_locals

        counters = [
            'folder', 'entry', 'fp', 'processed_parent_items', 'num_sized_files_total',
            'num_sized_files_this_folder', 'counted_files_total', 'counted_files_this_folder',
            'processed_files', 'total_file_size_so_far', 'filecount_this_item',
            'size_this_item', 'size_this_file', 'total_size_this_folder'
        ]
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
        processed_parent_items = 0
        num_sized_files_total = 0
        counted_files_total = 0
        total_file_size_so_far = 0

        with os.scandir(folder) as dir_entries:
            for entry in dir_entries:
                processed_parent_items += 1

                try:
                    if entry.is_file(follow_symlinks=False):
                        num_sized_files_total += 1
                        size_this_item = entry.stat().st_size
                        filecount_this_item = 1
                        counted_files_total += 1
                        if self.verbose_level >= 2:
                            DebugUtils.debug_with_counters("(Found file, skip scans) Scanning")
                    elif entry.is_dir(follow_symlinks=False):
                        path = entry.path
                        size_this_item, num_sized_files_total = self._get_dir_size(
                            path, parent_folder=folder, 
                            num_sized_files_total=num_sized_files_total
                        )

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
            print(
                f"\rCompleted {folder:<30}, "
                f"Total items: {counted_files_total:>10,} "
                f"Total size: {total_file_size_so_far:>10,}"
            )
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

            if not self.only_diffs or diff:
                self.data.append({
                    'Name': name,
                    'Size1': size1,
                    'Size2': size2,
                    'SD': sizediff,
                    'Filecount1': fc1,
                    'Filecount2': fc2,
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


class OutputFormatter:
    """Base class for output formatters."""
    
    def __init__(self, verbose_level=0):
        self.verbose_level = verbose_level
    
    def format_output(self, data, folder1, folder2):
        """Format and output the comparison data."""
        raise NotImplementedError("Subclasses must implement format_output")


class RichFormatter(OutputFormatter):
    """Rich console output formatter with colors and styling."""
    
    def format_output(self, data, folder1, folder2):
        """Format and output using Rich console."""
        if self.verbose_level >= 1:
            DebugUtils.debug_print("Using rich console output")
        
        console = Console()

        markdown_content = f"""# Folder Comparison Report

**Folder 1:** `{folder1}`  
**Folder 2:** `{folder2}`
"""

        totals = data[-1] if data else None

        table = Table(
            show_header=True, show_footer=True, 
            header_style="bold", footer_style="bold"
        )
        
        # Add columns with footer values
        table.add_column(
            "Name", style="cyan", header_style="cyan", footer_style="cyan", 
            no_wrap=True, justify="left",
            footer=totals['Name'] if totals else None
        )
        
        # Format footer values for numeric columns
        for col_name, col_data, style in [
            ("Size1", "Size1", "green"), ("Size2", "Size2", "green"), ("SD", "SD", "green"),
            ("Filecount1", "Filecount1", "yellow"), ("Filecount2", "Filecount2", "yellow"),
            ("CD", "CD", "yellow"), ("DIFF", "DIFF", "red")
        ]:
            footer_val = None
            if totals and isinstance(totals[col_data], (int, float)):
                footer_val = f"{totals[col_data]:,}"
            
            table.add_column(
                col_name, style=style, header_style=style, footer_style=style,
                justify="right", footer=footer_val
            )

        for entry in data:
            if entry['Name'] != 'TOTAL':
                size1_formatted = f"{entry['Size1']:,}" if entry['Size1'] != 'N/A' else 'N/A'
                size2_formatted = f"{entry['Size2']:,}" if entry['Size2'] != 'N/A' else 'N/A'
                filecount1_formatted = f"{entry['Filecount1']:,}" if entry['Filecount1'] != 'N/A' else 'N/A'
                filecount2_formatted = f"{entry['Filecount2']:,}" if entry['Filecount2'] != 'N/A' else 'N/A'

                sd_formatted = (f"{entry['SD']:,}" if entry['Name'] == 'TOTAL' 
                              and isinstance(entry['SD'], (int, float)) else str(entry['SD']))
                cd_formatted = (f"{entry['CD']:,}" if entry['Name'] == 'TOTAL' 
                              and isinstance(entry['CD'], (int, float)) else str(entry['CD']))
                diff_formatted = (f"{entry['DIFF']:,}" if entry['Name'] == 'TOTAL' 
                                and isinstance(entry['DIFF'], (int, float)) else str(entry['DIFF']))

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
        md = Markdown(markdown_content)
        console.print(md)
        console.print(table)


class PlainFormatter(OutputFormatter):
    """Plain text formatter with Unicode box drawing characters."""
    
    def format_output(self, data, folder1, folder2):
        """Format and output using plain markdown with Unicode borders."""
        if self.verbose_level >= 1:
            DebugUtils.debug_print("Using plain markdown output")
        
        markdown_table = self._format_markdown_table(data)
        
        lines = markdown_table.split('\n')
        separator_line = lines[1] if len(lines) > 1 else "│" + "─" * 118 + "│"
        
        top_border = separator_line.replace('|', '┬')
        top_border = top_border.replace('-', '─')

        if top_border.startswith('┬'):
            top_border = '┌' + top_border[1:]
        if top_border.endswith('┬'):
            top_border = top_border[:-1] + '┐'
        
        bottom_border = separator_line.replace('|', '┴')
        bottom_border = bottom_border.replace('-', '─')
        
        if bottom_border.startswith('┴'):
            bottom_border = '└' + bottom_border[1:]
        if bottom_border.endswith('┴'):
            bottom_border = bottom_border[:-1] + '┘'
        
        if len(lines) > 1:
            header_separator = lines[1].replace('-', '─')
            parts = header_separator.split('|')
            if len(parts) > 2:
                new_parts = []
                for i, part in enumerate(parts):
                    if i == 0:
                        new_parts.append(part)
                    elif i == 1:
                        new_parts.append(part)
                    elif i == len(parts) - 1:
                        new_parts.append(part)
                    else:
                        new_parts.append(part)
                result = new_parts[0] + '├'
                for i in range(1, len(new_parts) - 2):
                    result += new_parts[i] + '┼'
                result += new_parts[-2] + '┤' + new_parts[-1]
                new_header_separator = result
            else:
                new_header_separator = header_separator.replace('|', '┼')

            totals_separator = new_header_separator
            for old, new in [['─', '═'], ['┼', '╪'], ['├', '╞'], ['┤', '╡'], 
                           ['┬', '╤'], ['┴', '╧']]:
                totals_separator = totals_separator.replace(old, new)

            lines[1] = new_header_separator
            lines.insert(len(lines)-1, totals_separator)
            markdown_table = '\n'.join(lines)
        
        markdown_table = markdown_table.replace('|', '│')
        
        print(top_border)
        print(markdown_table)
        print(bottom_border)

    def _format_markdown_table(self, data):
        """Format the data as a properly aligned markdown table."""
        
        df = pd.DataFrame(data)

        df_formatted = df.copy()
        for col in ['Size1', 'Size2', 'Filecount1', 'Filecount2']:
            df_formatted[col] = df[col].apply(
                lambda x: f"{x:,}" if isinstance(x, (int, float)) else str(x)
            )

        for col in ['SD', 'CD', 'DIFF']:
            df_formatted[col] = df.apply(
                lambda row: f"{row[col]:,}" 
                if row['Name'] == 'TOTAL' and isinstance(row[col], (int, float)) 
                else str(row[col]), 
                axis=1
            )

        markdown_output = tabulate(
            df_formatted, headers='keys', tablefmt='github', showindex=False,
            colalign=('left', 'right', 'right', 'right', 'right', 'right', 'right', 'right')
        )

        lines = markdown_output.split('\n')
        if len(lines) >= 2:
            separator_line = lines[1]
            separator_parts = separator_line.split('|')
            if len(separator_parts) >= 9:
                for i in range(2, 9):
                    separator_parts[i] = separator_parts[i].replace('-', '').rjust(
                        len(separator_parts[i]), '-'
                    )
                lines[1] = '|'.join(separator_parts)
            markdown_output = '\n'.join(lines)

        return markdown_output


class CsvFormatter(OutputFormatter):
    """CSV output formatter for machine-readable data."""
    
    def format_output(self, data, folder1, folder2):
        """Format and output as CSV."""
        if self.verbose_level >= 1:
            DebugUtils.debug_print("Using CSV output")
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow(['Name', 'Size1', 'Size2', 'SD', 'Filecount1', 'Filecount2', 'CD', 'DIFF'])
        
        for entry in data:
            writer.writerow([
                entry['Name'],
                entry['Size1'],
                entry['Size2'],
                entry['SD'],
                entry['Filecount1'],
                entry['Filecount2'],
                entry['CD'],
                entry['DIFF']
            ])
        
        csv_output = output.getvalue().strip()
        print(csv_output)


class FolderComparator:
    """Main class that orchestrates the folder comparison process."""
    
    def __init__(self, folder1, folder2, args):
        self.folder1 = folder1
        self.folder2 = folder2
        self.args = args
        self.scanner = FolderScanner(verbose_level=args.verbose)
        
    def compare(self):
        """Run the complete folder comparison."""
        entries1 = self.scanner.scan_folder(self.folder1)
        entries2 = self.scanner.scan_folder(self.folder2)
        
        comparison_data = ComparisonData(entries1, entries2, self.args.only_diffs)
        data = comparison_data.build_data()
        
        formatter = self._create_formatter()
        formatter.format_output(data, self.folder1, self.folder2)
    
    def _create_formatter(self):
        """Create the appropriate output formatter based on arguments."""
        if self.args.csv:
            return CsvFormatter(self.args.verbose)
        elif self._should_use_rich_output():
            return RichFormatter(self.args.verbose)
        else:
            return PlainFormatter(self.args.verbose)
    
    def _should_use_rich_output(self):
        """Determine whether to use rich output formatting."""
        if self.args.csv:
            return False
            
        if self.args.plain:
            return False

        if self.args.rich:
            return True

        return sys.stdout.isatty()


def parse_arguments():
    """Parse command line arguments and return the parsed args."""
    parser = argparse.ArgumentParser(
        description='Compare two folders and show differences in size and file count',
        prog='chksync'
    )

    parser.add_argument('folder1', nargs='?', help='First folder to compare')
    parser.add_argument('folder2', nargs='?', help='Second folder to compare')
    parser.add_argument('-f1', '--folder1', dest='folder1_flag', 
                       help='First folder to compare (alternative to positional)')
    parser.add_argument('-f2', '--folder2', dest='folder2_flag', 
                       help='Second folder to compare (alternative to positional)')

    parser.add_argument('-r', '--rich', action='store_true', default=False,
                       help='Force rich formatting (overrides auto-detection)')
    parser.add_argument('-p', '--plain', action='store_true', default=False,
                       help='Force plain text output (overrides rich auto-detection)')
    parser.add_argument('-c', '--csv', action='store_true', default=False,
                       help='Output in CSV format')
    parser.add_argument('-v', '--verbose', action='count', default=0,
                       help='Increase verbosity: -v for progress, -vv for debug output')
    parser.add_argument('-d', '--only-diffs', action='store_true', 
                       help='Show only entries with differences')

    return parser.parse_args()

def validate_and_get_folders(args, parser):
    """Validate arguments and return the two folders to compare."""
    folder1 = args.folder1_flag if args.folder1_flag else args.folder1
    folder2 = args.folder2_flag if args.folder2_flag else args.folder2

    if not folder1 or not folder2:
        parser.error('Two folders must be specified either positionally or using -f1/-f2 flags')

    if not os.path.exists(folder1):
        parser.error(f'Folder1 does not exist: {folder1}')
    if not os.path.exists(folder2):
        parser.error(f'Folder2 does not exist: {folder2}')

    return folder1, folder2

def main():
    """Main function to run the folder comparison tool."""
    args = parse_arguments()
    parser = argparse.ArgumentParser(prog='chksync')

    folder1, folder2 = validate_and_get_folders(args, parser)

    comparator = FolderComparator(folder1, folder2, args)
    comparator.compare()


if __name__ == "__main__":
    main()