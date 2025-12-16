# TASK_PDF转换修复

## 任务清单

- [ ] **Task 1: 添加依赖**
    - 文件: `requirements.txt`
    - 内容: 添加 `pdfminer.six`。
    - 验证: `pip install` 成功。

- [ ] **Task 2: 实现 PDF 解析逻辑**
    - 文件: `src/core/converters/ppt.py`
    - 内容: 
        - 导入 `pdfminer.high_level.extract_text`。
        - 实现 `_convert_ppt` 中的三级降级逻辑。
    - 验证: 单元测试覆盖。

- [ ] **Task 3: 更新 Spec 文件**
    - 文件: `Everything2MD.spec`
    - 内容: 确认是否需要配置 (通常不需要，但为了保险可以加 `pdfminer` 到 hiddenimports)。
    - 验证: 构建 EXE 验证。

- [ ] **Task 4: 验证测试**
    - 操作: 使用一个 PDF 文件，强制跳过 pandoc/pdftotext，检查输出。
