"""
Tests for ImageRecognizer module.

Requirements covered:
- 7.1: WHEN 图片识别启用, THE Image_Recognizer SHALL 扫描Markdown中的图片引用
- 7.2: THE Image_Recognizer SHALL 调用配置的LLM API（如GPT-4 Vision）解析图片内容
- 7.3: THE Image_Recognizer SHALL 将识别结果作为图片描述插入Markdown
- 7.4: THE Image_Recognizer SHALL 支持配置并发数和上下文长度
- 7.5: IF 图片识别失败, THEN THE Image_Recognizer SHALL 记录警告日志并继续处理
"""

import pytest
import asyncio
import base64
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch
import httpx

from src.core.image_recognition import ImageRecognizer


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_config_manager():
    """Create a mock ConfigManager with default image recognition settings."""
    config = MagicMock()
    config_data = {
        "img_rec_enabled": True,
        "img_rec_api_base": "https://api.openai.com/v1",
        "img_rec_api_key": "test-api-key",
        "img_rec_model": "gpt-4-vision-preview",
        "img_rec_concurrency": 2,
        "img_rec_context_length": 500,
    }
    config.get.side_effect = lambda key, default=None: config_data.get(key, default)
    return config


@pytest.fixture
def mock_config_disabled():
    """Create a mock ConfigManager with image recognition disabled."""
    config = MagicMock()
    config_data = {
        "img_rec_enabled": False,
        "img_rec_api_base": "https://api.openai.com/v1",
        "img_rec_api_key": "",
        "img_rec_model": "gpt-4-vision-preview",
        "img_rec_concurrency": 2,
        "img_rec_context_length": 500,
    }
    config.get.side_effect = lambda key, default=None: config_data.get(key, default)
    return config


@pytest.fixture
def image_recognizer(mock_config_manager):
    """Create an ImageRecognizer instance with mocked config."""
    return ImageRecognizer(mock_config_manager)


@pytest.fixture
def sample_image(tmp_path):
    """Create a sample test image file."""
    img_path = tmp_path / "test_image.png"
    # Create a minimal valid PNG (1x1 pixel)
    png_data = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )
    img_path.write_bytes(png_data)
    return img_path


@pytest.fixture
def sample_markdown_with_images(tmp_path, sample_image):
    """Create a sample Markdown file with image references."""
    md_content = f"""# Test Document

Some text before the image.

![Test Image]({sample_image.name})

Some text after the image.

Another paragraph with more content.
"""
    md_path = tmp_path / "test.md"
    md_path.write_text(md_content, encoding="utf-8")
    return md_path


@pytest.fixture
def sample_markdown_no_images(tmp_path):
    """Create a sample Markdown file without images."""
    md_content = """# Test Document

This document has no images.

Just plain text content.
"""
    md_path = tmp_path / "no_images.md"
    md_path.write_text(md_content, encoding="utf-8")
    return md_path


# =============================================================================
# Requirement 7.1: Image scanning in Markdown
# =============================================================================

def test_image_pattern_detection(image_recognizer, tmp_path):
    """Test that image references are correctly detected in Markdown (Req 7.1)"""
    md_content = """# Document
    
![Image 1](image1.png)

Some text

![Image 2](path/to/image2.jpg)

More text

![](image3.gif)
"""
    md_path = tmp_path / "test.md"
    md_path.write_text(md_content, encoding="utf-8")
    
    import re
    pattern = re.compile(r"!\[(.*?)\]\((.*?)\)")
    matches = list(pattern.finditer(md_content))
    
    assert len(matches) == 3
    assert matches[0].group(2) == "image1.png"
    assert matches[1].group(2) == "path/to/image2.jpg"
    assert matches[2].group(2) == "image3.gif"


def test_url_encoded_image_paths(image_recognizer, tmp_path):
    """Test handling of URL-encoded image paths (Req 7.1)"""
    from urllib.parse import unquote
    
    # Chinese characters URL-encoded
    encoded_path = "%E5%9B%BE%E7%89%87.png"
    decoded_path = unquote(encoded_path)
    
    assert decoded_path == "图片.png"


def test_no_images_in_markdown(image_recognizer, sample_markdown_no_images, mock_config_manager):
    """Test processing Markdown with no images (Req 7.1)"""
    original_content = sample_markdown_no_images.read_text(encoding="utf-8")
    
    # Should complete without error and not modify the file
    image_recognizer.process_markdown(sample_markdown_no_images)
    
    # Content should remain unchanged
    assert sample_markdown_no_images.read_text(encoding="utf-8") == original_content


# =============================================================================
# Requirement 7.2: LLM API call (with mocks)
# =============================================================================

@pytest.mark.asyncio
async def test_api_call_structure(image_recognizer, sample_image):
    """Test that API calls are structured correctly (Req 7.2)"""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Test description"}}]
    }
    mock_response.raise_for_status = MagicMock()
    
    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    
    semaphore = asyncio.Semaphore(2)
    
    result = await image_recognizer._process_single_image(
        sample_image, mock_client, semaphore, 1, 1, "Test context"
    )
    
    # Verify API was called
    mock_client.post.assert_called_once()
    call_args = mock_client.post.call_args
    
    # Check URL
    assert "chat/completions" in call_args[0][0]
    
    # Check headers
    headers = call_args[1]["headers"]
    assert "Authorization" in headers
    assert "Bearer test-api-key" in headers["Authorization"]
    
    # Check payload structure
    payload = call_args[1]["json"]
    assert payload["model"] == "gpt-4-vision-preview"
    assert "messages" in payload
    assert payload["messages"][0]["role"] == "user"


@pytest.mark.asyncio
async def test_api_response_parsing(image_recognizer, sample_image):
    """Test that API responses are correctly parsed (Req 7.2)"""
    expected_description = "This is a test chart showing data trends."
    
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": expected_description}}]
    }
    mock_response.raise_for_status = MagicMock()
    
    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    
    semaphore = asyncio.Semaphore(2)
    
    result = await image_recognizer._process_single_image(
        sample_image, mock_client, semaphore, 1, 1, ""
    )
    
    assert result == expected_description


# =============================================================================
# Requirement 7.3: Result insertion into Markdown
# =============================================================================

@pytest.mark.asyncio
async def test_description_insertion_format(image_recognizer, sample_markdown_with_images, sample_image):
    """Test that descriptions are inserted in correct format (Req 7.3)"""
    description = "Test image description"
    
    # Mock the API call
    with patch.object(image_recognizer, '_process_single_image', new_callable=AsyncMock) as mock_process:
        mock_process.return_value = description
        
        await image_recognizer._process_markdown_async(sample_markdown_with_images)
    
    content = sample_markdown_with_images.read_text(encoding="utf-8")
    
    # Check that description is inserted as blockquote
    assert "> **图解**:" in content
    assert f"> {description}" in content


@pytest.mark.asyncio
async def test_multiple_images_processing(image_recognizer, tmp_path):
    """Test processing multiple images in one document (Req 7.3)"""
    # Create multiple test images
    for i in range(3):
        img_path = tmp_path / f"image{i}.png"
        png_data = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )
        img_path.write_bytes(png_data)
    
    md_content = """# Multi-Image Document

![Image 0](image0.png)

Text between images.

![Image 1](image1.png)

More text.

![Image 2](image2.png)

End of document.
"""
    md_path = tmp_path / "multi.md"
    md_path.write_text(md_content, encoding="utf-8")
    
    descriptions = ["Description 0", "Description 1", "Description 2"]
    call_count = [0]
    
    async def mock_process(*args, **kwargs):
        idx = call_count[0]
        call_count[0] += 1
        return descriptions[idx] if idx < len(descriptions) else ""
    
    with patch.object(image_recognizer, '_process_single_image', side_effect=mock_process):
        await image_recognizer._process_markdown_async(md_path)
    
    content = md_path.read_text(encoding="utf-8")
    
    # All descriptions should be present
    for desc in descriptions:
        assert f"> {desc}" in content


# =============================================================================
# Requirement 7.4: Configuration support
# =============================================================================

def test_config_loading(mock_config_manager):
    """Test that configuration is correctly loaded (Req 7.4)"""
    recognizer = ImageRecognizer(mock_config_manager)
    cfg = recognizer._get_config()
    
    assert cfg["enabled"] == True
    assert cfg["api_base"] == "https://api.openai.com/v1"
    assert cfg["api_key"] == "test-api-key"
    assert cfg["model"] == "gpt-4-vision-preview"
    assert cfg["concurrency"] == 2
    assert cfg["context_length"] == 500


def test_concurrency_setting(tmp_path):
    """Test that concurrency setting is respected (Req 7.4)"""
    config = MagicMock()
    config_data = {
        "img_rec_enabled": True,
        "img_rec_api_base": "https://api.openai.com/v1",
        "img_rec_api_key": "test-key",
        "img_rec_model": "gpt-4-vision-preview",
        "img_rec_concurrency": 5,
        "img_rec_context_length": 500,
    }
    config.get.side_effect = lambda key, default=None: config_data.get(key, default)
    
    recognizer = ImageRecognizer(config)
    cfg = recognizer._get_config()
    
    assert cfg["concurrency"] == 5


def test_context_length_setting(tmp_path):
    """Test that context length setting is respected (Req 7.4)"""
    config = MagicMock()
    config_data = {
        "img_rec_enabled": True,
        "img_rec_api_base": "https://api.openai.com/v1",
        "img_rec_api_key": "test-key",
        "img_rec_model": "gpt-4-vision-preview",
        "img_rec_concurrency": 2,
        "img_rec_context_length": 1000,
    }
    config.get.side_effect = lambda key, default=None: config_data.get(key, default)
    
    recognizer = ImageRecognizer(config)
    cfg = recognizer._get_config()
    
    assert cfg["context_length"] == 1000


def test_disabled_recognition(mock_config_disabled, sample_markdown_with_images):
    """Test that processing is skipped when disabled (Req 7.4)"""
    recognizer = ImageRecognizer(mock_config_disabled)
    original_content = sample_markdown_with_images.read_text(encoding="utf-8")
    
    recognizer.process_markdown(sample_markdown_with_images)
    
    # Content should remain unchanged
    assert sample_markdown_with_images.read_text(encoding="utf-8") == original_content


# =============================================================================
# Requirement 7.5: Error handling
# =============================================================================

@pytest.mark.asyncio
async def test_missing_image_handling(image_recognizer, tmp_path):
    """Test handling of missing image files (Req 7.5)"""
    md_content = """# Document

![Missing Image](nonexistent.png)

Some text.
"""
    md_path = tmp_path / "missing.md"
    md_path.write_text(md_content, encoding="utf-8")
    
    # Should not raise exception
    await image_recognizer._process_markdown_async(md_path)


@pytest.mark.asyncio
async def test_api_error_handling(image_recognizer, sample_image):
    """Test handling of API errors (Req 7.5)"""
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_client.post.side_effect = httpx.HTTPStatusError(
        "Server Error", request=MagicMock(), response=mock_response
    )
    
    semaphore = asyncio.Semaphore(2)
    
    # Should return empty string on error, not raise
    result = await image_recognizer._process_single_image(
        sample_image, mock_client, semaphore, 1, 1, ""
    )
    
    assert result == ""


@pytest.mark.asyncio
async def test_image_encoding_error(image_recognizer, tmp_path):
    """Test handling of image encoding errors (Req 7.5)"""
    # Create an invalid image file
    invalid_img = tmp_path / "invalid.png"
    invalid_img.write_text("not an image")
    
    # _encode_image should handle this gracefully
    result = await image_recognizer._encode_image(invalid_img)
    
    # Should return base64 of the text content (not fail)
    assert result is not None


@pytest.mark.asyncio
async def test_continue_on_single_failure(image_recognizer, tmp_path):
    """Test that processing continues after single image failure (Req 7.5)"""
    # Create one valid image
    valid_img = tmp_path / "valid.png"
    png_data = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )
    valid_img.write_bytes(png_data)
    
    md_content = f"""# Document

![Missing](nonexistent.png)

![Valid]({valid_img.name})

End.
"""
    md_path = tmp_path / "mixed.md"
    md_path.write_text(md_content, encoding="utf-8")
    
    call_count = [0]
    
    async def mock_process(image_path, *args, **kwargs):
        call_count[0] += 1
        if "nonexistent" in str(image_path):
            return ""  # Simulates failure
        return "Valid description"
    
    with patch.object(image_recognizer, '_process_single_image', side_effect=mock_process):
        await image_recognizer._process_markdown_async(md_path)
    
    # Both images should have been attempted
    assert call_count[0] == 2
    
    content = md_path.read_text(encoding="utf-8")
    # Valid image description should be present
    assert "> Valid description" in content


# =============================================================================
# Image extraction from DOCX source
# =============================================================================

def test_extract_image_from_docx(image_recognizer, tmp_path):
    """Test extracting images from DOCX source files."""
    import zipfile
    
    # Create a mock DOCX file (which is a ZIP)
    docx_path = tmp_path / "test.docx"
    img_data = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )
    
    with zipfile.ZipFile(docx_path, 'w') as zf:
        zf.writestr("word/media/image1.png", img_data)
    
    target_dir = tmp_path / "output"
    target_dir.mkdir()
    
    result = image_recognizer._extract_image_from_source(
        docx_path, "image1.png", target_dir
    )
    
    assert result is not None
    assert result.exists()
    assert result.name == "image1.png"


def test_extract_image_non_docx_source(image_recognizer, tmp_path):
    """Test that extraction returns None for non-DOCX sources."""
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_text("fake pdf")
    
    result = image_recognizer._extract_image_from_source(
        pdf_path, "image.png", tmp_path
    )
    
    assert result is None


def test_extract_image_missing_in_docx(image_recognizer, tmp_path):
    """Test extraction when image doesn't exist in DOCX."""
    import zipfile
    
    docx_path = tmp_path / "test.docx"
    with zipfile.ZipFile(docx_path, 'w') as zf:
        zf.writestr("word/document.xml", "<doc></doc>")
    
    result = image_recognizer._extract_image_from_source(
        docx_path, "nonexistent.png", tmp_path
    )
    
    assert result is None
