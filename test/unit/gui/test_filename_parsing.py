import pytest
import re

def _parse_versioned_filename(filename: str):
    """
    Parse filename to extract basename and hash.
    Pattern: {basename}_v{hash}.{ext}
    Returns: (basename, hash) or (filename, "")
    """
    # Regex for _v{8 hex chars}.ext
    match = re.search(r"^(.*)_v([a-f0-9]{8})\.(\w+)$", filename)
    if match:
        return match.group(1) + "." + match.group(3), match.group(2)
    return filename, ""

def test_parse_normal_file():
    res = _parse_versioned_filename("foo.md")
    assert res == ("foo.md", "")

def test_parse_versioned_file():
    res = _parse_versioned_filename("foo_v12345678.md")
    assert res == ("foo.md", "12345678")

def test_parse_complex_name():
    res = _parse_versioned_filename("my_report_final_vabcdef01.pdf")
    assert res == ("my_report_final.pdf", "abcdef01")

def test_parse_invalid_hash_length():
    # 7 chars - invalid
    res = _parse_versioned_filename("foo_v1234567.md")
    assert res == ("foo_v1234567.md", "")
    
    # 9 chars - invalid
    res = _parse_versioned_filename("foo_v123456789.md")
    assert res == ("foo_v123456789.md", "")

def test_parse_non_hex():
    res = _parse_versioned_filename("foo_vgghijkl.md")
    assert res == ("foo_vgghijkl.md", "")
