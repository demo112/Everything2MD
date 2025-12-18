import pytest
from unittest.mock import MagicMock, patch, ANY
from pathlib import Path
import tkinter as tk

# Mock tkinter is handled in conftest.py


@pytest.fixture
def mock_root():
    root = MagicMock()
    # Ensure root.tk is also a mock
    root.tk = MagicMock()
    return root


@pytest.fixture
def gui_app(mock_root):
    # Import inside fixture to ensure sys.modules is patched
    from src.gui.main import Everything2MDGUI

    # Mock ConfigManager to avoid file I/O
    with patch("src.gui.main.ConfigManager") as MockConfig:
        MockConfig.return_value.get.return_value = ""
        app = Everything2MDGUI(mock_root)
        # Mock RAGFlowClient
        app.ragflow_client = MagicMock()
        # Mock status bar
        app.status_bar = MagicMock()
        # Mock rag_file_list (Treeview)
        app.rag_file_list = MagicMock()
        # Mock converted_files list
        app.converted_files = [
            {
                "name": "file1.docx",
                "path": "/path/to/file1.docx",
                "status": "Ready",
                "id": "",
            },
            {
                "name": "file2.pdf",
                "path": "/path/to/file2.pdf",
                "status": "Ready",
                "id": "",
            },
        ]
        # Mock KB combo
        app.kb_combo = MagicMock()
        app.kb_map = {"MyKB": "kb_id_123"}

        return app


@patch("os.path.exists", return_value=True)
@patch("os.rename")
@patch("os.remove")
@patch("src.gui.main.calculate_file_hash", return_value="hash123")
@patch("src.gui.main.parse_versioned_filename", side_effect=lambda x: (x, "hash123"))
def test_upload_selected_files_success(mock_parse, mock_hash, mock_remove, mock_rename, mock_exists, gui_app):
    """Test uploading files that are checked [x]"""
    # Setup
    gui_app.kb_combo.get.return_value = "MyKB"

    # Mock treeview items
    # item1: [x], file1.docx
    # item2: [ ], file2.pdf

    children = ["item1", "item2"]
    gui_app.rag_file_list.get_children.return_value = children

    def set_side_effect(item, col, value=None):
        if value is not None:
            return  # Setting value
        # Getting value
        if item == "item1" and col == "select":
            return "☑"
        if item == "item2" and col == "select":
            return "☐"
        return ""

    gui_app.rag_file_list.set.side_effect = set_side_effect

    def item_side_effect(item):
        if item == "item1":
            return {"values": ["☑", "file1.docx", "Ready", "Not Uploaded"]}
        if item == "item2":
            return {"values": ["☐", "file2.pdf", "Ready", "Not Uploaded"]}
        return {}

    gui_app.rag_file_list.item.side_effect = item_side_effect

    # Mock upload response with a doc ID
    gui_app.ragflow_client.upload_document.return_value = {"id": "doc_id_123"}

    # Mock list_documents to return empty list (no duplicates)
    gui_app.ragflow_client.list_documents.return_value = []

    # Run
    # Since upload runs in a thread, we need to ensure the thread target is called or mocked.
    # The method uses threading.Thread(target=_bg_upload).start()
    # We can mock threading.Thread to run immediately.

    with patch("threading.Thread") as MockThread:
        gui_app.upload_selected_files()

        # Verify thread was started
        assert MockThread.called

        # Get the target function
        target = MockThread.call_args[1]["target"]

        # Execute target synchronously
        target()

        # Verify upload_document was called for file1 but not file2
        # Note: file path might be changed due to renaming (vHash appended)
        # file1.docx -> file1_vhash123.docx
        # So we check if upload_document was called with ANY path that ends with .docx
        gui_app.ragflow_client.upload_document.assert_called_once()
        args = gui_app.ragflow_client.upload_document.call_args
        # args[0] are positional args: (dataset_id, file_path)
        assert args[0][0] == "kb_id_123"
        assert "file1_vhash123.docx" in args[0][1] or "file1.docx" in args[0][1]

        # Verify run_parsing was called
        gui_app.ragflow_client.run_parsing.assert_called_once_with(
            "kb_id_123", ["doc_id_123"]
        )


def test_upload_no_selection(gui_app):
    """Test warning when no files are selected"""
    # Setup
    children = ["item1", "item2"]
    gui_app.rag_file_list.get_children.return_value = children

    # All unchecked
    gui_app.rag_file_list.set.return_value = "[ ]"

    with patch("src.gui.main.messagebox.showinfo") as mock_msg:
        gui_app.upload_selected_files()
        mock_msg.assert_called_with("提示", "请先在列表中勾选要上传的文件")
        # Ensure thread not started
        with patch("threading.Thread") as MockThread:
            assert not MockThread.called


def test_upload_no_kb_selected(gui_app):
    """Test error when no KB is selected"""
    # Setup
    children = ["item1"]
    gui_app.rag_file_list.get_children.return_value = children
    gui_app.rag_file_list.set.return_value = "☑"  # Selected

    gui_app.kb_combo.get.return_value = ""  # No KB

    with patch("src.gui.main.messagebox.showerror") as mock_err:
        gui_app.upload_selected_files()
        mock_err.assert_called_with("错误", "请选择目标知识库")


@patch("os.path.exists", return_value=True)
@patch("src.gui.main.calculate_file_hash", return_value="hash123")
@patch("src.gui.main.parse_versioned_filename", side_effect=lambda x: (x, "hash123"))
def test_upload_duplicates_check(mock_parse, mock_hash, mock_exists, gui_app):
    """Test duplicate detection"""
    gui_app.kb_combo.get.return_value = "MyKB"

    # Mock treeview
    gui_app.rag_file_list.get_children.return_value = ["item1"]
    
    # ... mock set/item ...
    def set_side_effect(item, col, value=None):
        if value is not None: return
        if col == "select": return "☑"
        return ""
    gui_app.rag_file_list.set.side_effect = set_side_effect
    
    gui_app.rag_file_list.item.return_value = {"values": ["☑", "file1.docx", "Ready", "Not Uploaded"]}

    # Mock list_documents to return existing doc
    # Existing doc has name "file1_vhash123.docx" (based on how upload_document names it?)
    # Wait, the code checks if doc_name in existing_names
    # The code generates doc_name = f"{filename}_v{file_hash}{ext}"
    
    gui_app.ragflow_client.list_documents.return_value = [
        {"name": "file1_vhash123.docx", "id": "existing_id"}
    ]

    with patch("threading.Thread") as mock_thread:
        # Mock thread to just return a mock
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance
        
        gui_app.upload_selected_files()
        
        # Verify thread started
        mock_thread_instance.start.assert_called_once()
        
        # Get target and run it
        args = mock_thread.call_args[1] if mock_thread.call_args else mock_thread.call_args_list[0][1]
        target = args['target']
        target()
        
        # Should NOT call upload_document
        gui_app.ragflow_client.upload_document.assert_not_called()
