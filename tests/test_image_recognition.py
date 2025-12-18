import pytest
import asyncio
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from core.image_recognition import ImageRecognizer
from core.config import ConfigManager


@pytest.fixture
def mock_config():
    config = MagicMock(spec=ConfigManager)
    config.get.side_effect = lambda key, default=None: {
        "img_rec_enabled": True,
        "img_rec_api_base": "https://api.openai.com/v1",
        "img_rec_api_key": "sk-test",
        "img_rec_model": "gpt-4-vision-preview",
        "img_rec_concurrency": 2,
    }.get(key, default)
    return config


@pytest.mark.asyncio
async def test_process_markdown(tmp_path, mock_config):
    # Setup
    md_file = tmp_path / "test.md"
    img_dir = tmp_path / "media"
    img_dir.mkdir()
    img_file = img_dir / "image1.png"
    img_file.write_bytes(b"fake_image_content")

    md_content = """
# Test Document

Here is an image:
![Test Image](media/image1.png)

End of document.
"""
    md_file.write_text(md_content, encoding="utf-8")

    recognizer = ImageRecognizer(mock_config)

    # Mock httpx.AsyncClient
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "This is a test description."}}]
    }

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("httpx.AsyncClient", return_value=mock_client):
        # Run
        await recognizer._process_markdown_async(md_file)

    # Verify
    new_content = md_file.read_text(encoding="utf-8")
    expected_snippet = "> **图解**:\n> This is a test description."

    assert expected_snippet in new_content
    assert "![Test Image](media/image1.png)" in new_content


@pytest.mark.asyncio
async def test_process_markdown_disabled(tmp_path):
    # Setup
    config = MagicMock(spec=ConfigManager)
    config.get.side_effect = lambda key, default=None: {"img_rec_enabled": False}.get(
        key, default
    )

    md_file = tmp_path / "test.md"
    md_content = "![Img](img.png)"
    md_file.write_text(md_content, encoding="utf-8")

    recognizer = ImageRecognizer(config)

    with patch("httpx.AsyncClient") as mock_client:
        await recognizer._process_markdown_async(md_file)
        mock_client.assert_not_called()

    assert md_file.read_text(encoding="utf-8") == md_content


@pytest.mark.asyncio
async def test_process_markdown_with_encoded_path(tmp_path, mock_config):
    # Setup
    md_file = tmp_path / "test_encoded.md"
    img_dir = tmp_path / "media"
    img_dir.mkdir()
    
    # Create image with Chinese name
    img_name = "中文图片.png"
    img_file = img_dir / img_name
    img_file.write_bytes(b"fake_image_content")
    
    # URL encoded path: media/%E4%B8%AD%E6%96%87%E5%9B%BE%E7%89%87.png
    encoded_path = "media/%E4%B8%AD%E6%96%87%E5%9B%BE%E7%89%87.png"
    
    md_content = f"""
# Test Encoded Path

![Chinese Image]({encoded_path})
"""
    md_file.write_text(md_content, encoding="utf-8")
    
    recognizer = ImageRecognizer(mock_config)
    
    # Mock httpx.AsyncClient
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Description for Chinese image."}}]
    }
    
    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    
    with patch("httpx.AsyncClient", return_value=mock_client):
        # Run
        await recognizer._process_markdown_async(md_file)
        
    # Verify
    new_content = md_file.read_text(encoding="utf-8")
    expected_snippet = "> **图解**:\n> Description for Chinese image."
    
    assert expected_snippet in new_content
    # Original link should be preserved
    assert f"![Chinese Image]({encoded_path})" in new_content


if __name__ == "__main__":
    pytest.main([__file__])
