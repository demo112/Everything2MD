import sys
import os
from pathlib import Path
import tempfile
import pytest

from src.core.utils import split_large_file

class TestSplitter:
    def test_no_split_small_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "small.md"
            content = "This is a small file."
            p.write_text(content, encoding='utf-8')
            
            # Threshold 1MB
            result = split_large_file(p, 1)
            assert len(result) == 1
            assert result[0] == p
            assert p.exists()
            assert p.read_text(encoding='utf-8') == content

    def test_split_large_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "large.md"
            # Create content
            # Each line 100 'a' + \n = 101 bytes
            line = "a" * 100 + "\n"
            lines = [line] * 20 # 2020 bytes total
            p.write_text("".join(lines), encoding='utf-8')
            
            # Threshold = 0.001 MB = 1024 bytes (approx 1024 bytes)
            # Target = 1024 * 0.9 = 921 bytes
            # 921 / 101 ~= 9.1 lines
            # So part 1 should have 9 lines.
            # If 9 lines: 909 bytes < 921. 10th line adds 101 -> 1010 > 921.
            # Logic: "if current_size + line_bytes > target_bytes and current_size > 0:"
            # So when reading 10th line: 909 + 101 = 1010 > 921.
            # Triggers split. Close part 1. Start part 2. Write 10th line to part 2.
            # So Part 1 has 9 lines.
            # Part 2 starts.
            # Total 20 lines. 20 - 9 = 11 left.
            # Part 2 will take next 9 lines.
            # Part 3 will take remaining 2 lines.
            # Total 3 parts.
            
            result = split_large_file(p, 0.001)
            
            assert len(result) == 3
            assert not p.exists() # Original deleted
            
            # Verify content
            full_content = ""
            for part in result:
                full_content += part.read_text(encoding='utf-8')
                
            assert full_content == "".join(lines)
            
            # Verify naming
            assert result[0].name == "large_part1.md"
            assert result[1].name == "large_part2.md"
            assert result[2].name == "large_part3.md"

    def test_disabled(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "test.md"
            p.write_text("content", encoding='utf-8')
            result = split_large_file(p, 0)
            assert len(result) == 1
            assert result[0] == p
