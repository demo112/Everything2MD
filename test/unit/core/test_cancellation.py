import unittest
import time
import threading
import os
import sys
from unittest.mock import MagicMock, patch

from src.core.engine import ConversionEngine, CancellationContext
from src.core.config import ConfigManager


class TestCancellation(unittest.TestCase):
    def setUp(self):
        self.config = MagicMock(spec=ConfigManager)
        self.config.get.side_effect = lambda k, d=None: d
        self.engine = ConversionEngine(self.config)

    def test_cancellation_context(self):
        ctx = CancellationContext()
        mock_proc = MagicMock()
        mock_proc.pid = 12345

        ctx.set_process(mock_proc)
        self.assertEqual(ctx.process, mock_proc)

        # Mock subprocess.run for taskkill
        with patch("subprocess.run") as mock_run:
            ctx.abort()
            # Should call taskkill on Windows
            if os.name == "nt":
                mock_run.assert_called()
                args = mock_run.call_args[0][0]
                self.assertIn("taskkill", args)
                self.assertIn(str(12345), args)
            else:
                # Non-windows logic (if any)
                pass


if __name__ == "__main__":
    unittest.main()
