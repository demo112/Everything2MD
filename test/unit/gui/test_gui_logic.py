import pytest
from unittest.mock import MagicMock, patch, call
import threading
import time
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
def app(mock_root):
    # Import inside fixture to ensure sys.modules is patched
    from src.gui.main import Everything2MDGUI

    # Mock Engine to prevent real initialization
    with patch("src.gui.main.ConversionEngine") as mock_engine_cls:
        with patch("src.gui.main.ConfigManager") as mock_config_cls:
            # Configure ConfigManager to return strings, not Mocks
            mock_config_instance = mock_config_cls.return_value
            mock_config_instance.get.return_value = "INFO"

            app = Everything2MDGUI(mock_root)
            app.engine = mock_engine_cls.return_value
            app.config_manager = mock_config_instance

            # Reset mocks to clear initialization calls
            app.input_path.set.reset_mock()
            app.output_path.set.reset_mock()
            app.file_filters.set.reset_mock()

            return app


def test_gui_initialization(app, mock_root):
    assert app.root == mock_root
    app.root.title.assert_called_with("Everything2MD - 文档转换工具")


def test_browse_input(app):
    with patch(
        "src.gui.main.filedialog.askopenfilename", return_value="C:/test/file.docx"
    ):
        app.browse_input()
        app.input_path.set.assert_called_with("C:/test/file.docx")


def test_browse_input_cancel(app):
    with patch("src.gui.main.filedialog.askopenfilename", return_value=""):
        app.browse_input()
        app.input_path.set.assert_not_called()


def test_browse_input_dir(app):
    with patch("src.gui.main.filedialog.askdirectory", return_value="C:/test/dir"):
        # Mock scan_file_types to avoid thread
        app.scan_file_types = MagicMock()
        app.browse_input_dir()
        app.input_path.set.assert_called_with("C:/test/dir")
        # It triggers scan_file_types via root.after
        # We can't easily test root.after callback execution without mocking root.after


def test_start_conversion_validation_input(app):
    app.input_path.get.return_value = ""
    with patch("src.gui.main.messagebox.showerror") as mock_msg:
        app.start_conversion()
        mock_msg.assert_called_with("错误", "请选择输入路径")


def test_start_conversion_success(app):
    app.input_path.get.return_value = "C:/in.docx"
    app.output_path.get.return_value = "C:/out"
    app.max_parallel_jobs.get.return_value = "4"
    app.file_filters.get.return_value = "docx,pdf"

    # Mock threading.Thread
    with patch("threading.Thread") as mock_thread_cls:
        mock_thread = MagicMock()
        mock_thread_cls.return_value = mock_thread

        app.start_conversion()

        mock_thread.start.assert_called()
        assert app.is_converting is True


def test_run_conversion_thread(app):
    # Test the target function of the thread
    app.input_path.get.return_value = "in"
    app.output_path.get.return_value = "out"

    # Mock engine.run
    app.engine.run = MagicMock()

    app.run_conversion()  # No args

    app.engine.run.assert_called_once()
    # It sets is_converting to False in finally block via root.after
    # We need to manually call on_conversion_finished to verify state change if we want
    app.on_conversion_finished()
    assert app.is_converting is False


def test_scan_file_types(app):
    app.input_path.get.return_value = "C:/test"

    with patch("os.path.isdir", return_value=True):
        with patch("os.walk") as mock_walk:
            mock_walk.return_value = [("root", [], ["f1.docx", "f2.pdf", "f3.unknown"])]

            # Mock refresh_filter_checkboxes
            app.refresh_filter_checkboxes = MagicMock()

            # Mock threading.Thread to run immediately or capture target
            with patch("threading.Thread") as mock_thread_cls:
                app.scan_file_types()

                # Get the target function and run it
                args = mock_thread_cls.call_args
                target = args[1]["target"]
                target()

                # It calls root.after to update UI
                # app.root.after is a Mock.
                # We need to inspect calls to root.after
                # calls: [call(0, lambda...)]
                # It's hard to execute the lambda inside mock call.

                # But we can assume if logic inside target reached end, it's fine.
                # Let's verifying os.walk was called.
                mock_walk.assert_called()


def test_update_filter_string(app):
    # Setup mock vars
    var_docx = MagicMock()
    var_docx.get.return_value = True
    var_pdf = MagicMock()
    var_pdf.get.return_value = False

    app.filter_vars = {"docx": var_docx, "pdf": var_pdf}

    app.update_filter_string()

    app.file_filters.set.assert_called_with("docx")


def test_rag_connect(app):
    app.rag_api_base.get.return_value = "http://api"
    app.rag_api_key.get.return_value = "key"

    with patch("src.gui.main.RAGFlowClient") as mock_rag_cls:
        mock_client = mock_rag_cls.return_value
        mock_client.list_datasets.return_value = [{"id": "1", "name": "kb1"}]

        # refresh_kb_list runs in thread
        with patch("threading.Thread") as mock_thread_cls:
            app.refresh_kb_list()

            args = mock_thread_cls.call_args
            target = args[1]["target"]
            target()

            assert app.ragflow_client is not None
            # app.kb_list is not explicitly set in the snippet I read,
            # it sets values of kb_combo via root.after

            # We can verify RAG client call
            mock_client.list_datasets.assert_called()


def test_window_geometry(app, mock_root):
    """Test that window geometry is set correctly during initialization."""
    mock_root.geometry.assert_called_with("700x600")


def test_start_conversion_validation_output(app):
    """Test that start_conversion validates output path."""
    app.input_path.get.return_value = "C:/in.docx"
    app.output_path.get.return_value = ""
    with patch("src.gui.main.messagebox.showerror") as mock_msg:
        app.start_conversion()
        mock_msg.assert_called_with("错误", "请选择输出路径")


def test_browse_output(app):
    """Test browse output directory functionality."""
    with patch("src.gui.main.filedialog.askdirectory", return_value="C:/output"):
        app.browse_output()
        app.output_path.set.assert_called_with("C:/output")


def test_browse_output_cancel(app):
    """Test browse output cancel does not change path."""
    with patch("src.gui.main.filedialog.askdirectory", return_value=""):
        app.browse_output()
        app.output_path.set.assert_not_called()


def test_cancel_conversion(app):
    """Test cancel conversion functionality."""
    app.is_converting = True
    app.engine.stop = MagicMock()
    
    app.cancel_conversion()
    
    app.engine.stop.assert_called_once()


def test_on_conversion_finished(app):
    """Test conversion finished callback resets state."""
    app.is_converting = True
    
    app.on_conversion_finished()
    
    assert app.is_converting is False


def test_save_config(app):
    """Test save config functionality."""
    app.config_manager.save_config = MagicMock()
    
    with patch("src.gui.main.messagebox.showinfo") as mock_msg:
        app.save_config(show_dialog=True)
        
        app.config_manager.save_config.assert_called_once()
        mock_msg.assert_called_with("成功", "配置已保存")


def test_save_config_error(app):
    """Test save config error handling."""
    app.config_manager.save_config = MagicMock(side_effect=Exception("Save failed"))
    
    with patch("src.gui.main.messagebox.showerror") as mock_msg:
        app.save_config(show_dialog=True)
        
        mock_msg.assert_called()


def test_update_progress(app):
    """Test progress update callback."""
    app._update_progress_ui = MagicMock()
    
    app.update_progress(5, 10)
    
    # update_progress schedules _update_progress_ui via root.after
    app.root.after.assert_called()


def test_update_file_status(app):
    """Test file status update callback."""
    app._update_file_status_ui = MagicMock()
    
    app.update_file_status("test.docx", "success", "Converted")
    
    # update_file_status schedules _update_file_status_ui via root.after
    app.root.after.assert_called()
