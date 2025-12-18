import pytest
import os
from src.core.utils import calculate_file_hash

def test_calculate_file_hash(tmp_path):
    # Create a test file
    test_file = tmp_path / "test_hash.txt"
    content = b"Hello World"
    test_file.write_bytes(content)
    
    # Calculate hash
    # MD5 of "Hello World" is b10a8db164e0754105b7a99be72e3fe5
    h = calculate_file_hash(str(test_file), length=8)
    assert h == "b10a8db1"
    
    # Test different length
    h_full = calculate_file_hash(str(test_file), length=32)
    assert h_full == "b10a8db164e0754105b7a99be72e3fe5"

def test_calculate_file_hash_missing(tmp_path):
    # Missing file
    h = calculate_file_hash(str(tmp_path / "nonexistent"), length=8)
    assert h == ""
