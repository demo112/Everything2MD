import sys
import os
from pathlib import Path
import tempfile
import pytest
from hypothesis import given, strategies as st, settings

from src.core.utils import split_large_file


class TestSplitter:
    def test_no_split_small_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "small.md"
            content = "This is a small file."
            p.write_text(content, encoding="utf-8")

            # Threshold 1MB
            result = split_large_file(p, 1)
            assert len(result) == 1
            assert result[0] == p
            assert p.exists()
            assert p.read_text(encoding="utf-8") == content

    def test_split_large_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "large.md"
            # Create content
            # Each line 100 'a' + \n = 101 bytes
            line = "a" * 100 + "\n"
            lines = [line] * 20  # 2020 bytes total
            p.write_text("".join(lines), encoding="utf-8")

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
            assert not p.exists()  # Original deleted

            # Verify content
            full_content = ""
            for part in result:
                full_content += part.read_text(encoding="utf-8")

            assert full_content == "".join(lines)

            # Verify naming
            assert result[0].name == "large_part1.md"
            assert result[1].name == "large_part2.md"
            assert result[2].name == "large_part3.md"

    def test_disabled(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "test.md"
            p.write_text("content", encoding="utf-8")
            result = split_large_file(p, 0)
            assert len(result) == 1
            assert result[0] == p


# =============================================================================
# Property-Based Tests for Large File Splitting
# =============================================================================


# Strategy for generating markdown-like content with multiple lines
markdown_line_strategy = st.text(
    alphabet=st.characters(
        whitelist_categories=('L', 'N', 'P', 'S', 'Zs'),
        whitelist_characters=' \t-_#*[]()>',
        blacklist_characters='\x00\r'
    ),
    min_size=0,
    max_size=200
)

markdown_content_strategy = st.lists(
    markdown_line_strategy,
    min_size=1,
    max_size=100
).map(lambda lines: '\n'.join(lines) + '\n')


@given(
    content=markdown_content_strategy,
    max_size_kb=st.integers(min_value=1, max_value=10)
)
@settings(max_examples=100)
def test_property_split_content_integrity(content, max_size_kb):
    """
    Property 7: 大文件分割完整性 (Large File Split Integrity)
    
    *For any* file content and size threshold, splitting and then concatenating
    all parts should produce content equivalent to the original.
    
    **Validates: Requirements 9.1-9.3**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "test_file.md"
        file_path.write_text(content, encoding="utf-8")
        
        # Convert KB to MB for the function (use small values for testing)
        max_size_mb = max_size_kb / 1024.0
        
        # Perform split
        result_paths = split_large_file(file_path, max_size_mb)
        
        # Concatenate all parts
        combined_content = ""
        for part_path in result_paths:
            assert part_path.exists(), f"Part file {part_path} should exist"
            combined_content += part_path.read_text(encoding="utf-8")
        
        # Verify content integrity
        assert combined_content == content, "Combined content should equal original"


@given(
    content=markdown_content_strategy
)
@settings(max_examples=100)
def test_property_no_split_when_under_threshold(content):
    """
    Property 7: Files under threshold should not be split
    
    *For any* file content, if the file size is under the threshold,
    the function should return the original file path unchanged.
    
    **Validates: Requirements 9.1**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "small_file.md"
        file_path.write_text(content, encoding="utf-8")
        
        # Use a large threshold (100 MB) to ensure no split
        result_paths = split_large_file(file_path, 100)
        
        # Should return single path (original)
        assert len(result_paths) == 1
        assert result_paths[0] == file_path
        assert file_path.exists()
        assert file_path.read_text(encoding="utf-8") == content


@given(
    num_lines=st.integers(min_value=10, max_value=50),
    line_length=st.integers(min_value=50, max_value=200)
)
@settings(max_examples=100)
def test_property_split_parts_naming(num_lines, line_length):
    """
    Property 7: Split parts should have correct sequential naming
    
    *For any* file that gets split, the resulting parts should be named
    with sequential _partN suffixes.
    
    **Validates: Requirements 9.3**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "document.md"
        
        # Create content that will definitely be split
        line = "x" * line_length + "\n"
        content = line * num_lines
        file_path.write_text(content, encoding="utf-8")
        
        # Use very small threshold to force splitting
        # 0.0001 MB = ~100 bytes
        result_paths = split_large_file(file_path, 0.0001)
        
        if len(result_paths) > 1:
            # Verify sequential naming
            for i, part_path in enumerate(result_paths, start=1):
                expected_name = f"document_part{i}.md"
                assert part_path.name == expected_name, \
                    f"Part {i} should be named {expected_name}, got {part_path.name}"
            
            # Original file should be deleted
            assert not file_path.exists(), "Original file should be deleted after split"


@given(
    num_lines=st.integers(min_value=20, max_value=100),
    line_length=st.integers(min_value=100, max_value=300)
)
@settings(max_examples=100)
def test_property_split_parts_size_constraint(num_lines, line_length):
    """
    Property 7: Each split part should respect size constraints
    
    *For any* file that gets split, each resulting part (except possibly the last)
    should be close to but not exceed the target size.
    
    **Validates: Requirements 9.1, 9.2**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "large_doc.md"
        
        # Create content
        line = "a" * line_length + "\n"
        content = line * num_lines
        file_path.write_text(content, encoding="utf-8")
        
        # Use small threshold to force splitting
        max_size_mb = 0.001  # ~1KB
        threshold_bytes = max_size_mb * 1024 * 1024
        
        result_paths = split_large_file(file_path, max_size_mb)
        
        if len(result_paths) > 1:
            # All parts except the last should be reasonably sized
            for i, part_path in enumerate(result_paths[:-1]):
                part_size = part_path.stat().st_size
                # Part should not exceed threshold (with some tolerance for line boundaries)
                assert part_size <= threshold_bytes * 1.5, \
                    f"Part {i+1} size {part_size} exceeds threshold {threshold_bytes}"
