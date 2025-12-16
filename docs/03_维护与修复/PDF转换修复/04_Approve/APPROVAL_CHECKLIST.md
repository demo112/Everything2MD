# APPROVAL_CHECKLIST

- [x] **依赖更新**: `requirements.txt` 添加了 `pdfminer.six`。
- [x] **环境安装**: `pip install` 成功。
- [x] **代码逻辑**: `ppt.py` 增加了 `_fallback_pdf_parsing` 方法，并已接入降级链。

## 待验证
- [ ] 模拟一个 PDF 转换，确认是否在无 pandoc/pdftotext 情况下触发 pdfminer。
