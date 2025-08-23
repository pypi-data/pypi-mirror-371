# utils.py

"""
This module contains various utility functions for the project.
Includes cross-platform console clearing and file/folder creation utilities.
"""

from pathlib import Path
import os
from typing import Dict, List



def clear_console() -> None:
    """
    Clears the console in a cross-platform way (Windows and Unix).
    """
    os.system('cls' if os.name == 'nt' else 'clear')



def create_structure(base_path: str, structure: Dict[str, List[str]]) -> None:
    """
    Creates folders and files according to the given structure.

    :param base_path: Base path where everything is created.
    :param structure: Dictionary with folder names and list of files.
                      Example: {"folder1": ["a.txt", "b.py"], "folder2": []}
    """
    base_path = Path(base_path)
    base_path.mkdir(parents=True, exist_ok=True)

    for folder, files in structure.items():
        folder_path = base_path / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        for file in files:
            file_path = folder_path / file
            file_path.touch(exist_ok=True)  # Create the file if it does not exist
            # Optionally: write default content
            file_path.write_text(f"# Generated file: {file}", encoding="utf-8")

# Unit test placeholder
def _test_utils():
    """Basic test for utils functions (expand with pytest for real tests)."""
    import tempfile
    temp_dir = tempfile.mkdtemp()
    try:
        create_structure(temp_dir, {"foo": ["bar.txt"]})
        assert (Path(temp_dir) / "foo" / "bar.txt").exists()
    finally:
        import shutil
        shutil.rmtree(temp_dir)

