import pytest
from unittest.mock import Mock, patch
from src.core.ragflow_client import RAGFlowClient

@pytest.fixture
def client():
    return RAGFlowClient("http://mock-api", "mock-key")

def test_delete_documents(client):
    with patch("httpx.Client") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.__enter__.return_value = mock_instance
        
        mock_resp = Mock()
        mock_resp.json.return_value = {"code": 0, "data": None}
        mock_resp.raise_for_status.return_value = None
        mock_instance.request.return_value = mock_resp
        
        client.delete_documents("kb1", ["doc1", "doc2"])
        
        mock_instance.request.assert_called_with(
            "DELETE",
            "http://mock-api/api/v1/datasets/kb1/documents",
            headers={"Authorization": "Bearer mock-key"},
            json={"ids": ["doc1", "doc2"]}
        )

def test_delete_documents_error(client):
    with patch("httpx.Client") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.__enter__.return_value = mock_instance
        
        mock_instance.request.side_effect = Exception("API Error")
        
        with pytest.raises(Exception):
            client.delete_documents("kb1", ["doc1"])
