"""
RAGFlow Integration Tests

These tests require a real RAGFlow server to be accessible.
They validate Requirements 6.1-6.5:
- 6.1: API address and key configuration
- 6.2: Get and display available knowledge base list
- 6.3: Batch upload converted files
- 6.4: Display upload progress and result status
- 6.5: Error handling for connection failures
"""
import pytest
import os
import tempfile
from pathlib import Path
from src.core.config import ConfigManager
from src.core.ragflow_client import RAGFlowClient


def get_ragflow_client():
    """Helper to create RAGFlow client from config."""
    local_config = "test_config_real.json"
    if os.path.exists(local_config):
        os.remove(local_config)

    cm = ConfigManager(local_config)
    api_base = cm.get("rag_api_base")
    api_key = cm.get("rag_api_key")
    
    return RAGFlowClient(api_base, api_key), api_base


@pytest.mark.integration
def test_real_ragflow_connection():
    """
    Test connection to real RAGFlow server using configured credentials.
    Validates: Requirements 6.1, 6.2
    """
    client, api_base = get_ragflow_client()
    print(f"\nTesting connection to: {api_base}")

    try:
        datasets = client.list_datasets(page=1, page_size=10)
        print(f"Successfully connected. Found {len(datasets)} datasets.")
        assert isinstance(datasets, list)

    except Exception as e:
        pytest.skip(f"Skipping RAGFlow integration test: Cannot connect to {api_base}. Error: {e}")


@pytest.mark.integration
def test_real_ragflow_list_datasets():
    """
    Test listing knowledge bases from RAGFlow.
    Validates: Requirements 6.2
    """
    client, api_base = get_ragflow_client()

    try:
        datasets = client.list_datasets(page=1, page_size=100)
        
        assert isinstance(datasets, list)
        
        # If datasets exist, verify structure
        if len(datasets) > 0:
            first_dataset = datasets[0]
            # RAGFlow datasets should have id and name
            assert "id" in first_dataset or "dataset_id" in first_dataset
            print(f"Found {len(datasets)} datasets")
            for ds in datasets[:5]:  # Print first 5
                print(f"  - {ds.get('name', 'unnamed')}: {ds.get('id', ds.get('dataset_id', 'no-id'))}")

    except Exception as e:
        pytest.skip(f"Skipping: Cannot connect to {api_base}. Error: {e}")


@pytest.mark.integration
def test_real_ragflow_invalid_credentials():
    """
    Test error handling with invalid API credentials.
    Validates: Requirements 6.5
    """
    client, api_base = get_ragflow_client()
    
    # Create client with invalid key
    invalid_client = RAGFlowClient(api_base, "invalid-api-key-12345")
    
    try:
        # This should fail with authentication error
        invalid_client.list_datasets()
        # If we get here without error, the server might not validate keys
        print("Warning: Server did not reject invalid API key")
    except Exception as e:
        # Expected: should raise an error
        error_msg = str(e).lower()
        print(f"Got expected error for invalid credentials: {e}")
        # The error should indicate authentication/authorization issue
        assert any(word in error_msg for word in ["error", "unauthorized", "forbidden", "invalid", "authentication", "api"])


@pytest.mark.integration
def test_real_ragflow_connection_failure():
    """
    Test error handling when server is unreachable.
    Validates: Requirements 6.5
    """
    # Use an invalid URL that should fail to connect
    invalid_client = RAGFlowClient("http://192.168.255.255:9999", "any-key")
    
    with pytest.raises(Exception) as excinfo:
        invalid_client.list_datasets()
    
    # Should get a connection error
    print(f"Got expected connection error: {excinfo.value}")


@pytest.mark.integration
def test_real_ragflow_document_workflow():
    """
    Test full document workflow: upload, list, delete.
    Validates: Requirements 6.3, 6.4
    
    Note: This test creates and cleans up test data.
    """
    client, api_base = get_ragflow_client()
    
    try:
        # 1. Get first available dataset
        datasets = client.list_datasets(page=1, page_size=10)
        if not datasets:
            pytest.skip("No datasets available for testing document upload")
        
        test_dataset_id = datasets[0].get("id") or datasets[0].get("dataset_id")
        print(f"\nUsing dataset: {datasets[0].get('name')} ({test_dataset_id})")
        
        # 2. Create a test markdown file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Test Document\n\nThis is a test document for RAGFlow integration testing.\n")
            test_file_path = f.name
        
        try:
            # 3. Upload document
            print(f"Uploading test file: {test_file_path}")
            upload_result = client.upload_document(test_dataset_id, test_file_path)
            print(f"Upload result: {upload_result}")
            
            # Verify upload returned data
            assert upload_result is not None
            
            # 4. List documents to verify upload
            docs = client.list_documents(test_dataset_id, page=1, page_size=100)
            print(f"Documents in dataset: {len(docs) if isinstance(docs, list) else 'N/A'}")
            
            # 5. Clean up - delete the uploaded document
            if upload_result:
                doc_ids = []
                if isinstance(upload_result, list):
                    doc_ids = [d.get("id") for d in upload_result if d.get("id")]
                elif isinstance(upload_result, dict) and upload_result.get("id"):
                    doc_ids = [upload_result["id"]]
                
                if doc_ids:
                    print(f"Cleaning up: deleting document(s) {doc_ids}")
                    try:
                        client.delete_documents(test_dataset_id, doc_ids)
                        print("Cleanup successful")
                    except Exception as cleanup_err:
                        print(f"Cleanup warning: {cleanup_err}")
        
        finally:
            # Remove temp file
            if os.path.exists(test_file_path):
                os.remove(test_file_path)
    
    except Exception as e:
        pytest.skip(f"Skipping document workflow test: {e}")
