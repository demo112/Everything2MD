# DESIGN_PPTX_Conversion_Fix

## 1. 模块设计

### 1.1 PptConverter (`src/core/converters/ppt.py`)

#### `_convert_pptx` 方法改进
```python
def _convert_pptx(self, input_path, output_path, context=None):
    # ... import logic ...
    
    # FIX 1: Ensure paths are strings
    str_input_path = str(input_path)
    str_output_path = str(output_path)
    str_img_dir = str(output_path.parent / "img")
    
    # ... existing config setup ...
    config = ConversionConfig(
        pptx_path=str_input_path,  # Use string
        output_path=str_output_path, # Use string
        image_dir=str_img_dir,       # Use string
        # ... other args ...
    )
    
    try:
        pptx_convert(config)
    except Exception as e:
        # ... logging ...
        # FIX 2: Use absolute path for fallback command
        executable = self._get_pptx2md_executable()
        cmd = [executable, str_input_path, "-o", str_output_path, "-i", str_img_dir]
        self._run_subprocess(cmd, ...)
```

#### `_get_pptx2md_executable` 辅助方法
```python
def _get_pptx2md_executable(self):
    # 1. Try finding in current python environment's Scripts (Windows) or bin (Linux)
    import sys
    import os
    
    if os.name == 'nt':
        candidate = Path(sys.prefix) / "Scripts" / "pptx2md.exe"
    else:
        candidate = Path(sys.prefix) / "bin" / "pptx2md"
        
    if candidate.exists():
        return str(candidate)
        
    # 2. Fallback to PATH lookup
    import shutil
    path_exe = shutil.which("pptx2md")
    if path_exe:
        return path_exe
        
    return "pptx2md" # Last resort
```

## 2. 验证设计
- **Unit Test**: Mock `pptx2md` 库，验证传入参数类型。
- **Integration Test**: 创建一个最小化的 PPTX 文件，运行实际转换。

## 3. 数据流向
无变化。
