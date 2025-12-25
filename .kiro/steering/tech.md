# Everything2MD - Tech Stack

## Languages
- **Python 3**: Core conversion engine, GUI, Web backend
- **Bash**: Legacy shell scripts (being phased out)
- **JavaScript/HTML/CSS**: Web frontend

## Key Dependencies
- **FastAPI + Uvicorn**: Web backend API
- **Tkinter**: Desktop GUI
- **pptx2md**: PowerPoint conversion
- **python-pptx, python-docx**: Office document parsing
- **pdfminer.six**: PDF text extraction
- **LibreOffice**: Office format conversion (soffice CLI)
- **Pandoc**: Document format transformation

## Testing
- **pytest**: Python unit/integration tests
- **Bats**: Bash script tests (legacy)
- **pytest-cov**: Coverage reporting

## Build & Packaging
- **PyInstaller**: Windows EXE packaging (`Everything2MD.spec`)
- **Docker**: Container deployment

## Common Commands

```bash
# Run all tests
make test

# Python tests only
pytest test/

# Run with coverage
pytest --cov=src --cov-report=html

# Docker development
docker compose up -d --build
docker compose logs -f

# Package Windows EXE
pyinstaller Everything2MD.spec
```

## Configuration
- Config stored at `~/.config/everything2md/config.json`
- Docker config at `/work/config.json`
- Environment variables in `.env` (API keys)

## Virtual Environment
Always use `.venv` as the virtual environment name:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```
