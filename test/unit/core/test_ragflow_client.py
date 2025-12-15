import pytest
from unittest.mock import Mock, patch
from src.core.ragflow_client import RAGFlowClient

@pytest.fixture
def client():
    return RAGFlowClient("http://mock-api", "mock-key")

def test_list_datasets(client):
    with patch("httpx.Client") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.__enter__.return_value = mock_instance
        
        mock_resp = Mock()
        mock_resp.json.return_value = {"code": 0, "data": [{"id": "1", "name": "test"}]}
        mock_instance.get.return_value = mock_resp
        
        data = client.list_datasets()
        assert len(data) == 1
        assert data[0]["name"] == "test"
        
        mock_instance.get.assert_called_once()

def test_upload_document(client, tmp_path):
    # Create dummy file
    f = tmp_path / "test.md"
    f.write_text("content")
    
    with patch("httpx.Client") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.__enter__.return_value = mock_instance
        
        mock_resp = Mock()
        mock_resp.json.return_value = {"code": 0, "data": {"id": "doc1"}}
        mock_instance.post.return_value = mock_resp
        
        res = client.upload_document("kb1", str(f))
        assert res["id"] == "doc1"

def test_upload_missing_file(client):
    with pytest.raises(FileNotFoundError):
        client.upload_document("kb1", "nonexistent.md")

def test_api_error(client):
    with patch("httpx.Client") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.__enter__.return_value = mock_instance
        
        mock_resp = Mock()
        mock_resp.json.return_value = {"code": 1, "message": "fail"}
        mock_resp.raise_for_status = Mock()
        mock_instance.get.return_value = mock_resp
        
        with pytest.raises(Exception, match="API Error.*fail"):
            client.list_datasets()

def test_api_error_includes_url(client):
    """Test that API errors include the URL for debugging"""
    with patch("httpx.Client") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.__enter__.return_value = mock_instance
        
        mock_resp = Mock()
        mock_resp.json.return_value = {"code": 1, "message": "something wrong"}
        mock_resp.raise_for_status = Mock()
        mock_instance.get.return_value = mock_resp
        
        # We expect the URL to be in the error message
        with pytest.raises(Exception) as excinfo:
            client.list_datasets()
        
        error_msg = str(excinfo.value)
        assert "API Error" in error_msg
        assert "something wrong" in error_msg
        assert "http://mock-api/api/v1/datasets" in error_msg
