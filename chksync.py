#!/usr/bin/env python3

import os
import sys
import pandas as pd
from tabulate import tabulate
from rich.console import Console
from rich.markdown import Markdown

def debug_print(message, vars_to_show=None):
    """Helper function to print debug messages with function name, line number, and optionally caller variables"""
    frame = sys._getframe(1)  # Get caller's frame
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

def debug_with_counters(message):
    """Debug print that automatically shows common counter variables"""
    frame = sys._getframe(1)
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

def get_first_level_entries(folder):
  # debug_with_counters("START:  scanning a parent level item")
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
          # debug_with_counters("(Found file, skip scans) Scanning")
        elif entry.is_dir(follow_symlinks=False):
          # For directories, we still need to calculate size and count
          path = entry.path
          size_this_item, num_sized_files_total = get_dir_size(path, parent_folder=folder, num_sized_files_total=num_sized_files_total)
          # For directories, we still need to calculate size and count
          # filecount is the number of files in the directory
          # processed_files is updated by get_file_count
          # This will scan the directory and return the size and file count
          filecount_this_item, counted_files_total = get_file_count(path, parent_folder=folder, counted_files_total=counted_files_total)
          # debug_with_counters("(Found directory, run scans ) Scanning")
        else:
          continue

        entries[entry.name] = (size_this_item, filecount_this_item)
        total_file_size_so_far = total_file_size_so_far + size_this_item if size_this_item else total_file_size_so_far
        

      except (OSError, PermissionError) as e:
        debug_with_counters(f"Warning: Cannot access ENTRY=={entry.name}: {e}")
        continue

      # Show progress every 100 entries
      if counted_files_total % 100 == 0 or counted_files_total == filecount_this_item or filecount_this_item > 100:
        # debug_with_counters("processed 100 entries") #, end="", flush=True)
        print(f"\rProcessing {folder:<30}, Total items: {counted_files_total:>10,} Total size: {total_file_size_so_far:>10,}", end="", flush=True)
        # print(f"\rProcessing {folder}: {i}/{total_items} entries - {name}", end="", flush=True)

  # debug_with_counters("FINISH: scanning a parent level item")
  # print(f"========================================================================================")
  print(f"\rProcessing {folder:<30}, Total items: {counted_files_total:>10,} Total size: {total_file_size_so_far:>10,}") #, end="", flush=True)
  return entries

def get_dir_size(folder, parent_folder=None, num_sized_files_total=0):
  # debug_with_counters("START:  sizing")
  num_sized_files_this_folder = 0
  # Debug breakpoint for takeout.zip
  if os.path.basename(folder) == "takeout.zip":
    pass  # Set breakpoint here
  size_this_file = 0
  total_size_this_folder = 0
  for root, dirs, files in os.walk(folder):
    for f in files:
      fp = os.path.join(root, f)
      try:
        num_sized_files_total += 1
        num_sized_files_this_folder += 1
        # Show progress every 100 entries
        # if num_sized_files_total % 100 == 0 or num_sized_files_total == 1 or total_size_this_folder >= 100 or True:
          # debug_with_counters("Processed 100 entries")
        size_this_file = os.path.getsize(fp)
        total_size_this_folder += size_this_file
      except Exception:
        pass
          # Show progress every 100 entries
      if num_sized_files_total % 100 == 0 or num_sized_files_this_folder > 100: #num_sized_files_total == num_sized_files_this_folder or num_sized_files_this_folder > 100:
        # debug_with_counters("processed 100 entries") #, end="", flush=True)
        print(f"\rProcessing {folder:<30}, Total items: {num_sized_files_total:>10,}, Total size: {num_sized_files_total:>10,}", end="", flush=True)
        # print(f"\rProcessing {folder}: {i}/{total_items} entries - {name}", end="", flush=True)
    # debug_with_counters("FINISH: sizing")
  # print(f"Total size of {folder}: {total_size_this_folder} bytes")
  # print(f"Total size of {folder}: {total_size_this_folder / (1024 * 1024):.2f} MB")
  # print(f"Total size of {folder}: {total_size_this_folder / (1024 * 1024 * 1024):.2f} GB")
  # print(f"Total size of {folder}: {total_size_this_folder / (1024 * 1024 * 1024):.2f} TB")
  return total_size_this_folder, num_sized_files_total

def get_file_count(folder, parent_folder=None, counted_files_total=0):
  # Debug breakpoint for takeout.zip
  # debug_with_counters("START:  counting")
  if os.path.basename(folder) == "takeout.zip":
    pass  # Set breakpoint here

  total_count_this_folder = 0
  for _, _, files in os.walk(folder):
    total_count_this_folder += len(files)
    counted_files_total += len(files)
    # Show progress every 100 entries
    # if counted_files_total % 100 == 0 or counted_files_total == 1 or total_count_this_folder >= 100 or True:
      # debug_with_counters("Processed 100 entries")
  # debug_with_counters("FINISH:  counting")
  # print(f"Total file count in {folder}: {total_count_this_folder}")
  # print(f"Total file count in {folder}: {total_count_this_folder:,}") 
  return total_count_this_folder, counted_files_total

def main():
  if len(sys.argv) < 3 or len(sys.argv) > 4:
    print(f"Usage: {sys.argv[0]} Folder1 Folder2 [only-diffs]")
    sys.exit(1)
  
  folder1, folder2 = sys.argv[1], sys.argv[2]
  only_diffs = len(sys.argv) == 4 and sys.argv[3].lower() == "only-diffs"
  entries1 = get_first_level_entries(folder1)
  entries2 = get_first_level_entries(folder2)
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
    # Debug breakpoint for takeout.zip
    if name == "takeout.zip":
      pass  # Set breakpoint here

    size1, fc1 = entries1.get(name, (0, 0))
    size2, fc2 = entries2.get(name, (0, 0))
    sizediff = '*' if size1 != size2 else ''
    filediff = '*' if fc1 != fc2 else ''
    diff = '**' if fc1 != fc2 or size1 != size2 else ''

    # Only add row if not filtering or if there are differences
    if not only_diffs or diff:
      data.append({
          'Name': name,
          'Size1': f"{size1:,}",
          'Size2': f"{size2:,}",
          'SD': sizediff,
          'Filecount1': f"{fc1:,}",
          'Filecount2': f"{fc2:,}",
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
  
  # Create DataFrame with main data
  df = pd.DataFrame(data)
  
  # Add totals row to the DataFrame
  totals_row = {
      'Name': f"**TOTAL**",
      'Size1': f"**{total_size1:,}**",
      'Size2': f"**{total_size2:,}**",
      'SD': f"**{str(size_diff_count)}**",
      'Filecount1': f"**{total_fc1:,}**",
      'Filecount2': f"**{total_fc2:,}**",
      'CD': f"**{str(file_diff_count)}**",
      'DIFF': f"**{str(diff_count)}**"
  }
  
  # Combine main data and totals into single DataFrame
  df_with_totals = pd.concat([df, pd.DataFrame([totals_row])], ignore_index=True)
  
  # Print the complete table with markdown format - right align numeric columns
  markdown_output = tabulate(df_with_totals, headers='keys', tablefmt='github', showindex=False, 
                           colalign=('left', 'right', 'right', 'center', 'right', 'right', 'center', 'center'))
  
  # Manually modify the markdown to ensure right alignment
  lines = markdown_output.split('\n')
  if len(lines) >= 2:
    # Replace the separator line to force right alignment for numeric columns
    header_line = lines[0]
    separator_line = lines[1]
    # Modify separator: left, right, right, center, right, right, center, center
    separator_parts = separator_line.split('|')
    if len(separator_parts) >= 9:  # Including empty parts at start/end
      separator_parts[2] = separator_parts[2].replace('-', '').rjust(len(separator_parts[2]), '-') + ':'  # Size1 right
      separator_parts[3] = separator_parts[3].replace('-', '').rjust(len(separator_parts[3]), '-') + ':'  # Size2 right  
      separator_parts[4] = ':' + separator_parts[4].replace('-', '').center(len(separator_parts[4])-2, '-') + ':'  # SD center
      separator_parts[5] = separator_parts[5].replace('-', '').rjust(len(separator_parts[5]), '-') + ':'  # Filecount1 right
      separator_parts[6] = separator_parts[6].replace('-', '').rjust(len(separator_parts[6]), '-') + ':'  # Filecount2 right
      separator_parts[7] = ':' + separator_parts[7].replace('-', '').center(len(separator_parts[7])-2, '-') + ':'  # CD center
      separator_parts[8] = ':' + separator_parts[8].replace('-', '').center(len(separator_parts[8])-2, '-') + ':'  # DIFF center
      lines[1] = '|'.join(separator_parts)
    markdown_output = '\n'.join(lines)
  
  # print(markdown_output)
  pass

  # Print with enhanced formatting using rich markdown rendering
  console = Console()
  
  # Create markdown content
  markdown_content = f"""# Folder Comparison Report

{markdown_output}
"""
  print("\n")
  # Render the markdown
  md = Markdown(markdown_content)
  console.print(md)
  
  # # Save markdown outputs to files
  # with open('markdown_output.txt', 'w') as f:
  #   f.write(markdown_output)
  
  # with open('markdown_output_with_separator.txt', 'w') as f:
  #   f.write(markdown_output_with_separator)
  
  # with open('markdown_content.md', 'w') as f:
  #   f.write(markdown_content)

  # print(f"\nFiles saved:")
  # print(f"- markdown_output.txt")
  # print(f"- markdown_output_with_separator.txt") 
  # print(f"- markdown_content.md")

if __name__ == "__main__":
  main()