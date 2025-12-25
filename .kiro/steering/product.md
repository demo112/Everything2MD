# Everything2MD - Product Overview

Everything2MD is a document conversion tool that transforms various file formats into Markdown.

## Core Purpose
Convert Office documents (Word, Excel, PowerPoint), PDFs, and text files to Markdown format for use in knowledge bases and RAG systems.

## Key Features
- Multi-format support: `.doc`, `.docx`, `.xls`, `.xlsx`, `.ppt`, `.pptx`, `.pdf`, `.txt`, `.emmx`
- Batch processing with parallel execution
- Optional AI-powered image recognition (GPT-4 Vision)
- Optional LLM-based structure cleaning
- RAGFlow integration for knowledge base uploads
- Web UI (Docker) and Desktop GUI (Tkinter)

## Deployment Options
- **Docker (recommended)**: Web interface at `localhost:8000`
- **Desktop EXE**: Standalone Windows executable with GUI
- **Source**: Direct Python/Bash execution

## Critical Requirement
> All features must have full-chain logging capability. Logs alone must be sufficient to reproduce user environment and operation paths.
