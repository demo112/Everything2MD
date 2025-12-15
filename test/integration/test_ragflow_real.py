import pytest
import os
from src.core.config import ConfigManager
from src.core.ragflow_client import RAGFlowClient

@pytest.mark.integration
def test_real_ragflow_connection():
    """
    Test connection to real RAGFlow server using configured credentials.
    This test requires the RAGFlow server to be accessible.
    """
    # 1. Load Config
    # Use a local temporary config file to ensure we load the latest defaults from code
    # (which contain the user's real credentials)
    local_config = "test_config_real.json"
    if os.path.exists(local_config):
        os.remove(local_config)
        
    cm = ConfigManager(local_config)
    
    api_base = cm.get("rag_api_base")
    api_key = cm.get("rag_api_key")
    
    print(f"\nTesting connection to: {api_base}")
    
    if not api_base or "localhost" in api_base or "127.0.0.1" in api_base:
        # If it's still localhost default, we might skip or warn, but here we expect the specific IP
        pass

    client = RAGFlowClient(api_base, api_key)
    
    try:
        # 2. Call API
        datasets = client.list_datasets(page=1, page_size=10)
        
        # 3. Verify
        print(f"Successfully connected. Found {len(datasets)} datasets.")
        assert isinstance(datasets, list)
        
    except Exception as e:
        pytest.fail(f"Failed to connect to RAGFlow at {api_base}: {str(e)}")
