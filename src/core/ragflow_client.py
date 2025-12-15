import httpx
import json
from pathlib import Path
from .utils import log_info, log_error

class RAGFlowClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {api_key}"
        }

    def _handle_response(self, response, url=None):
        try:
            response.raise_for_status()
            data = response.json()
            # RAGFlow API response structure usually: { "code": 0, "message": "success", "data": ... }
            if data.get('code', -1) != 0:
                raise Exception(f"API Error (URL: {url}): {data.get('message', 'Unknown error')}")
            return data.get('data')
        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP Error {e.response.status_code} for {url}: {e.response.text}")
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON response from {url}: {response.text[:200]}")
        except Exception as e:
            # Avoid wrapping if it's already one of our exceptions
            if str(e).startswith("API Error") or str(e).startswith("HTTP Error") or str(e).startswith("Invalid JSON"):
                raise
            raise Exception(f"Request Error for {url}: {str(e)}")

    def list_datasets(self, page=1, page_size=100):
        """List knowledge bases (datasets)"""
        url = f"{self.base_url}/api/v1/datasets"
        params = {"page": page, "page_size": page_size}
        try:
            with httpx.Client(timeout=10.0) as client:
                log_info(f"RAGFlow API Request: GET {url}")
                resp = client.get(url, headers=self.headers, params=params)
                return self._handle_response(resp, url)
        except Exception as e:
            log_error(f"Failed to list datasets: {e}")
            raise

    def create_dataset(self, name: str, template_id: str = None):
        """Create a new dataset. If template_id is provided, copy config from it."""
        url = f"{self.base_url}/api/v1/datasets"
        payload = {"name": name}
        
        try:
            with httpx.Client(timeout=10.0) as client:
                # 1. Create Dataset
                log_info(f"RAGFlow API Request: POST {url}")
                resp = client.post(url, headers=self.headers, json=payload)
                new_dataset = self._handle_response(resp, url)
                
                # 2. Apply Template (Optional)
                if template_id:
                    # TODO: Fetch template config and update new dataset
                    # For now, we just log this limitation or implement if API allows
                    log_info(f"Template application not yet fully implemented. Created empty dataset: {name}")
                
                return new_dataset
        except Exception as e:
            log_error(f"Failed to create dataset: {e}")
            raise

    def upload_document(self, dataset_id: str, file_path: str):
        """Upload a document to a dataset"""
        # Correct endpoint per RAGFlow API docs: /api/v1/datasets/{dataset_id}/documents
        url = f"{self.base_url}/api/v1/datasets/{dataset_id}/documents"
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # For this endpoint, dataset_id is in URL, not body data usually.
        # But let's check docs again. Docs say: 
        # POST /api/v1/datasets/{dataset_id}/documents
        # form 'file=@...'
        
        try:
            with open(path, 'rb') as f:
                files = {'file': (path.name, f)}
                # Remove Content-Type header to let httpx set boundary for multipart
                headers = self.headers.copy()
                
                with httpx.Client(timeout=30.0) as client:
                    log_info(f"RAGFlow API Request: POST {url}")
                    resp = client.post(url, headers=headers, files=files)
                    return self._handle_response(resp, url)
        except Exception as e:
            log_error(f"Failed to upload document: {e}")
            raise

    def list_documents(self, dataset_id: str, page=1, page_size=100, keywords=None):
        """List documents in a dataset"""
        url = f"{self.base_url}/api/v1/datasets/{dataset_id}/documents"
        params = {"page": page, "page_size": page_size}
        if keywords:
            params["keywords"] = keywords
            
        try:
            with httpx.Client(timeout=10.0) as client:
                log_info(f"RAGFlow API Request: GET {url}")
                resp = client.get(url, headers=self.headers, params=params)
                return self._handle_response(resp, url)
        except Exception as e:
            log_error(f"Failed to list documents: {e}")
            raise

    def run_parsing(self, dataset_id: str, doc_ids: list):
        """Start parsing for uploaded documents"""
        # Based on GitHub issue #9614 and other findings:
        # The correct endpoint to start parsing (chunking) for documents is:
        # POST /api/v1/datasets/{dataset_id}/chunks
        # Payload: {"document_ids": ["id1", "id2"]}
        
        url = f"{self.base_url}/api/v1/datasets/{dataset_id}/chunks"
        
        payload = {
            "document_ids": doc_ids
        }
        
        try:
            with httpx.Client(timeout=10.0) as client:
                log_info(f"RAGFlow API Request: POST {url}")
                resp = client.post(url, headers=self.headers, json=payload)
                return self._handle_response(resp, url)
        except Exception as e:
            log_error(f"Failed to start parsing: {e}")
            raise
