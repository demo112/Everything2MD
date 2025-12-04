#!/bin/bash

# Environment Loader Module
# Loads tools from the project's 'tools' directory into PATH

# Get script directory if not already set
if [[ -z "$SCRIPT_DIR" ]]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
else
    # SCRIPT_DIR is src/modules/../.. -> project root
    # Wait, in main.sh SCRIPT_DIR is src/
    # So we want project root
    PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
fi

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TOOLS_DIR="$PROJECT_ROOT/tools"

# Add Pandoc to PATH
if [[ -d "$TOOLS_DIR/pandoc" ]]; then
    export PATH="$TOOLS_DIR/pandoc:$PATH"
    log_info "已加载内置 Pandoc: $TOOLS_DIR/pandoc"
fi

# Add Poppler to PATH (pdftotext)
# Poppler structure is usually Library/bin or bin depending on version
if [[ -d "$TOOLS_DIR/poppler/Library/bin" ]]; then
    export PATH="$TOOLS_DIR/poppler/Library/bin:$PATH"
    log_info "已加载内置 Poppler: $TOOLS_DIR/poppler/Library/bin"
elif [[ -d "$TOOLS_DIR/poppler/bin" ]]; then
    export PATH="$TOOLS_DIR/poppler/bin:$PATH"
    log_info "已加载内置 Poppler: $TOOLS_DIR/poppler/bin"
fi

# Add LibreOffice Portable if exists
if [[ -d "$TOOLS_DIR/LibreOfficePortable" ]]; then
    # Usually LibreOfficePortable/App/libreoffice/program or similar
    if [[ -d "$TOOLS_DIR/LibreOfficePortable/App/libreoffice/program" ]]; then
         export PATH="$TOOLS_DIR/LibreOfficePortable/App/libreoffice/program:$PATH"
         log_info "已加载内置 LibreOffice: $TOOLS_DIR/LibreOfficePortable"
    fi
fi
