import unittest
import zipfile
import json
import shutil
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).resolve().parent.parent / 'src'))

from core.converters.emmx import EmmxConverter

class TestEmmxConverter(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path('tests/temp_emmx_test')
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.converter = EmmxConverter()

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def create_mock_emmx(self, filename, content):
        path = self.test_dir / filename
        with zipfile.ZipFile(path, 'w') as z:
            z.writestr('doc/document.json', json.dumps(content))
        return path

    def test_convert_standard_structure(self):
        # 模拟 MindMaster 结构
        data = {
            "models": {
                "map": {
                    "text": "Root Node",
                    "children": [
                        {
                            "text": "Child 1",
                            "children": [
                                {"text": "Grandchild 1.1"}
                            ]
                        },
                        {
                            "text": "Child 2"
                        }
                    ]
                }
            }
        }
        input_path = self.create_mock_emmx('test_standard.emmx', data)
        output_path = self.test_dir / 'test_standard.md'
        
        self.converter.convert(input_path, output_path)
        
        self.assertTrue(output_path.exists())
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        print(f"\nMarkdown Output:\n{content}")
        
        self.assertIn("# MindMap", content)
        self.assertIn("- Root Node", content)
        self.assertIn("  - Child 1", content)
        self.assertIn("    - Grandchild 1.1", content)
        self.assertIn("  - Child 2", content)

    def test_convert_flat_structure(self):
        # 模拟另一种可能得结构
        data = {
            "root": {
                "text": "Root",
                "topics": [
                    {"text": "Topic 1"}
                ]
            }
        }
        input_path = self.create_mock_emmx('test_flat.emmx', data)
        output_path = self.test_dir / 'test_flat.md'
        
        self.converter.convert(input_path, output_path)
        
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        self.assertIn("- Root", content)
        self.assertIn("  - Topic 1", content)

if __name__ == '__main__':
    unittest.main()
