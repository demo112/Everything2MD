import pytest
from unittest.mock import Mock, patch, mock_open
from src.core.ragflow_client import RAGFlowClient
import httpx
import json


@pytest.fixture
def rag_client():
    return RAGFlowClient("http://api.example.com", "fake-api-key")


@pytest.fixture
def mock_httpx_client():
    with patch("httpx.Client") as mock:
        yield mock


def test_list_datasets_success(rag_client, mock_httpx_client):
    mock_response = Mock()
    mock_response.json.return_value = {
        "code": 0,
        "data": [{"id": "1", "name": "test_ds"}],
    }
    mock_response.raise_for_status.return_value = None

    # Configure context manager
    mock_httpx_client.return_value.__enter__.return_value.get.return_value = (
        mock_response
    )

    result = rag_client.list_datasets()
    assert result == [{"id": "1", "name": "test_ds"}]

    # Verify call
    mock_httpx_client.return_value.__enter__.return_value.get.assert_called_with(
        "http://api.example.com/api/v1/datasets",
        headers={"Authorization": "Bearer fake-api-key"},
        params={"page": 1, "page_size": 100},
    )


def test_list_datasets_api_error(rag_client, mock_httpx_client):
    mock_response = Mock()
    mock_response.json.return_value = {"code": 1, "message": "Something went wrong"}
    mock_response.raise_for_status.return_value = None
    mock_httpx_client.return_value.__enter__.return_value.get.return_value = (
        mock_response
    )

    with pytest.raises(Exception, match="API Error.*Something went wrong"):
        rag_client.list_datasets()


def test_create_dataset_success(rag_client, mock_httpx_client):
    mock_response = Mock()
    mock_response.json.return_value = {
        "code": 0,
        "data": {"id": "new_id", "name": "new_ds"},
    }
    mock_response.raise_for_status.return_value = None
    mock_httpx_client.return_value.__enter__.return_value.post.return_value = (
        mock_response
    )

    result = rag_client.create_dataset("new_ds")
    assert result["id"] == "new_id"

    mock_httpx_client.return_value.__enter__.return_value.post.assert_called()


def test_upload_document_success(rag_client, mock_httpx_client):
    mock_response = Mock()
    mock_response.json.return_value = {"code": 0, "data": {"id": "doc_id"}}
    mock_response.raise_for_status.return_value = None
    mock_httpx_client.return_value.__enter__.return_value.post.return_value = (
        mock_response
    )

    with patch("builtins.open", mock_open(read_data=b"file content")) as m_open:
        with patch("pathlib.Path.exists", return_value=True):
            with patch(
                "pathlib.Path.name", "test.txt"
            ):  # This mock might be tricky on Path object properties
                # Instead of mocking Path property directly which is hard, let's just rely on Path object behavior
                # But we need exists() to be true.

                # Let's just create a dummy file for test or use mock properly
                # Using patch("pathlib.Path.exists") works for the instance check

                result = rag_client.upload_document("ds_id", "/path/to/test.txt")
                assert result["id"] == "doc_id"

                # Verify post called with files
                args, kwargs = (
                    mock_httpx_client.return_value.__enter__.return_value.post.call_args
                )
                assert "files" in kwargs
                assert "file" in kwargs["files"]


def test_upload_document_file_not_found(rag_client):
    with patch("pathlib.Path.exists", return_value=False):
        with pytest.raises(FileNotFoundError):
            rag_client.upload_document("ds_id", "/nonexistent/file.txt")
