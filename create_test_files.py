#!/usr/bin/env python3
"""
Script to create test files and directories for the chksync project.
This recreates the test structure that was removed from git tracking.
"""

import os
import zipfile
from pathlib import Path


def create_test_structure():
    """Create the complete test directory structure with sample files."""
    base_dir = Path("test")
    
    # Create base test directory
    base_dir.mkdir(exist_ok=True)
    print(f"Created directory: {base_dir}")
    
    # Test folder 1
    test_folder1 = base_dir / "test_folder1"
    test_folder1.mkdir(exist_ok=True)
    print(f"Created directory: {test_folder1}")
    
    # Create files in test_folder1
    files_folder1 = {
        "common.txt": "This is a common file in folder 1\nShared content\nLine 3",
        "file1.txt": "Content of file1 in test_folder1\nUnique to folder 1",
        "unique1.txt": "This file only exists in test_folder1\nSpecial content for testing",
    }
    
    for filename, content in files_folder1.items():
        file_path = test_folder1 / filename
        file_path.write_text(content)
        print(f"Created file: {file_path}")
    
    # Create subdir1 in test_folder1
    subdir1_path = test_folder1 / "subdir1"
    subdir1_path.mkdir(exist_ok=True)
    print(f"Created directory: {subdir1_path}")
    
    subdir1_files = {
        "sub_file.txt": "Subdirectory file content\nNested file in folder1/subdir1",
        "sub_file1.txt": "Another subdirectory file\nOnly in folder1",
    }
    
    for filename, content in subdir1_files.items():
        file_path = subdir1_path / filename
        file_path.write_text(content)
        print(f"Created file: {file_path}")
    
    # Test folder 2
    test_folder2 = base_dir / "test_folder2"
    test_folder2.mkdir(exist_ok=True)
    print(f"Created directory: {test_folder2}")
    
    # Create files in test_folder2
    files_folder2 = {
        "common.txt": "This is a common file in folder 2\nShared content\nLine 3",  # Same as folder1
        "file1.txt": "Content of file1 in test_folder2\nDifferent from folder 1",
        "unique2.txt": "This file only exists in test_folder2\nSpecial content for testing folder 2",
    }
    
    for filename, content in files_folder2.items():
        file_path = test_folder2 / filename
        file_path.write_text(content)
        print(f"Created file: {file_path}")
    
    # Create subdir1 in test_folder2
    subdir2_path = test_folder2 / "subdir1"
    subdir2_path.mkdir(exist_ok=True)
    print(f"Created directory: {subdir2_path}")
    
    subdir2_files = {
        "sub_file.txt": "Subdirectory file content\nNested file in folder2/subdir1",  # Same as folder1
        "sub_file1.txt": "Another subdirectory file\nOnly in folder2, different content",
        "sub_file2.txt": "Extra file in folder2 subdir\nUnique to test_folder2/subdir1",
    }
    
    for filename, content in subdir2_files.items():
        file_path = subdir2_path / filename
        file_path.write_text(content)
        print(f"Created file: {file_path}")
    
    # Create symbolic links for takeout.zip (pointing to a dummy file)
    dummy_zip_content = b"PK\x03\x04\x14\x00\x00\x00\x08\x00"  # Minimal zip header
    dummy_zip_path = base_dir / "dummy.zip"
    dummy_zip_path.write_bytes(dummy_zip_content)
    
    # Create symbolic links
    takeout1_link = test_folder1 / "takeout.zip"
    takeout2_link = test_folder2 / "takeout.zip"
    
    try:
        takeout1_link.symlink_to("../dummy.zip")
        print(f"Created symlink: {takeout1_link} -> ../dummy.zip")
    except (OSError, NotImplementedError):
        # Fallback: copy the file instead of creating symlink
        takeout1_link.write_bytes(dummy_zip_content)
        print(f"Created file (symlink fallback): {takeout1_link}")
    
    try:
        takeout2_link.symlink_to("../dummy.zip")
        print(f"Created symlink: {takeout2_link} -> ../dummy.zip")
    except (OSError, NotImplementedError):
        # Fallback: copy the file instead of creating symlink
        takeout2_link.write_bytes(dummy_zip_content)
        print(f"Created file (symlink fallback): {takeout2_link}")


def create_large_test_folders():
    """Create large test folders with many files for performance testing."""
    base_dir = Path("test")
    
    # Create test_large_folder1 and test_large_folder2
    for folder_num in [1, 2]:
        folder_name = f"test_large_folder{folder_num}"
        large_folder = base_dir / folder_name
        large_folder.mkdir(exist_ok=True)
        print(f"Created directory: {large_folder}")
        
        # Create numbered files
        file_numbers = list(range(1, 251))  # 250 files
        
        # Add some files with different numbering patterns for testing sorting
        additional_numbers = [10, 100, 1000, 10000] + list(range(1001, 1100))
        file_numbers.extend(additional_numbers)
        
        for i in file_numbers:
            filename = f"file_{i}.txt"
            content = f"Content of file {i} in {folder_name}\n"
            content += f"File number: {i}\n"
            content += f"Folder: {folder_name}\n"
            
            # Add some variation between folders
            if folder_num == 2 and i <= 150:
                content += "Modified content for folder 2\n"
            
            file_path = large_folder / filename
            file_path.write_text(content)
            
            # Print progress every 50 files
            if i % 50 == 0:
                print(f"Created {i} files in {folder_name}")
        
        print(f"Completed {folder_name} with {len(file_numbers)} files")


def create_mixed_content_files():
    """Create files with different types of content for testing."""
    base_dir = Path("test")
    
    # Create a mixed content folder
    mixed_folder = base_dir / "mixed_content"
    mixed_folder.mkdir(exist_ok=True)
    print(f"Created directory: {mixed_folder}")
    
    # Various file types and contents
    mixed_files = {
        "empty_file.txt": "",
        "single_line.txt": "Single line file",
        "multi_line.txt": "Line 1\nLine 2\nLine 3\nLine 4",
        "unicode_content.txt": "Unicode: αβγδε ñáéíóú 中文 🚀",
        "numbers.txt": "\n".join(str(i) for i in range(1, 101)),
        "whitespace.txt": "   \n\t\n   spaces and tabs   \n",
        "long_line.txt": "A" * 1000,
    }
    
    for filename, content in mixed_files.items():
        file_path = mixed_folder / filename
        file_path.write_text(content, encoding='utf-8')
        print(f"Created file: {file_path}")


def main():
    """Main function to create all test files and directories."""
    print("Creating test file structure for chksync...")
    print("=" * 50)
    
    try:
        # Create basic test structure
        create_test_structure()
        print("\n" + "=" * 50)
        
        # Create large test folders
        print("Creating large test folders...")
        create_large_test_folders()
        print("\n" + "=" * 50)
        
        # Create mixed content files
        print("Creating mixed content files...")
        create_mixed_content_files()
        print("\n" + "=" * 50)
        
        print("✅ Test file structure created successfully!")
        print("\nTest directory structure:")
        print("test/")
        print("├── test_folder1/")
        print("│   ├── common.txt")
        print("│   ├── file1.txt")
        print("│   ├── unique1.txt")
        print("│   ├── takeout.zip -> ../dummy.zip")
        print("│   └── subdir1/")
        print("│       ├── sub_file.txt")
        print("│       └── sub_file1.txt")
        print("├── test_folder2/")
        print("│   ├── common.txt")
        print("│   ├── file1.txt")
        print("│   ├── unique2.txt")
        print("│   ├── takeout.zip -> ../dummy.zip")
        print("│   └── subdir1/")
        print("│       ├── sub_file.txt")
        print("│       ├── sub_file1.txt")
        print("│       └── sub_file2.txt")
        print("├── test_large_folder1/ (250+ files)")
        print("├── test_large_folder2/ (250+ files)")
        print("├── mixed_content/")
        print("└── dummy.zip")
        
        print(f"\nYou can now test chksync with:")
        print("python chksync.py test/test_folder1 test/test_folder2")
        print("python chksync.py test/test_large_folder1 test/test_large_folder2")
        
    except Exception as e:
        print(f"❌ Error creating test files: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
