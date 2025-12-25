# Everything2MD - Project Structure

```
Everything2MD/
├── src/
│   ├── core/                 # Python core logic
│   │   ├── config.py         # Configuration management
│   │   ├── engine.py         # Main conversion engine
│   │   ├── converters/       # Format-specific converters
│   │   │   ├── office.py     # Word/Excel conversion
│   │   │   ├── ppt.py        # PowerPoint conversion
│   │   │   └── emmx.py       # EMMX format conversion
│   │   ├── image_recognition.py  # AI image parsing
│   │   ├── structure_cleaner.py  # LLM structure cleaning
│   │   ├── ragflow_client.py     # RAGFlow API client
│   │   └── utils.py          # Shared utilities
│   ├── gui/
│   │   └── main.py           # Tkinter desktop GUI
│   └── modules/              # [Legacy] Bash modules
│
├── web/
│   ├── backend/
│   │   └── main.py           # FastAPI backend
│   └── frontend/
│       ├── index.html
│       ├── script.js
│       └── style.css
│
├── test/
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   ├── ui/                   # UI automation tests
│   └── fixtures/             # Test files
│
├── docs/                     # 6A workflow documentation
│   ├── 01_核心系统/          # Core system docs
│   ├── 02_功能模块/          # Feature module docs
│   ├── 03_维护与修复/        # Maintenance/fix docs
│   └── 04_*/                 # Other categories
│
├── tools/                    # Bundled tools (pandoc, poppler)
├── scripts/                  # Build/utility scripts
├── archive/                  # Deprecated/backup files
├── logs/                     # Runtime logs
├── data/                     # Input/output directories
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── Makefile
├── pytest.ini
└── Everything2MD.spec        # PyInstaller config
```

## Key Patterns
- **Converters**: Each format has a dedicated converter in `src/core/converters/`
- **Config**: Centralized via `ConfigManager` class with nested JSON structure
- **Logging**: All operations must log to `logs/everything2md.log`
- **Tests**: Mirror source structure under `test/` with `test_` prefix

## Documentation (6A Workflow)
Each feature/fix follows the 6A process with docs in `docs/[category]/[feature]/`:
- `01_Align/` - Requirements alignment
- `02_Architect/` - Design documents
- `03_Atomize/` - Task breakdown
- `04_Approve/` - Approval checklist
- `05_Automate/` - Implementation acceptance
- `06_Assess/` - Final assessment
