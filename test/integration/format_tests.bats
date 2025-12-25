#!/usr/bin/env bats

# 测试不同文件格式的处理

setup() {
  PROJECT_ROOT="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
  SRC="$PROJECT_ROOT/src/main.sh"
}

@test "should process DOC file correctly" {
    local input_file="$PROJECT_ROOT/test/fixtures/Untitled 1.doc"
    local output_file="/tmp/output_doc.md"
    
    run "$SRC" -i "$input_file" -o "$output_file"
    
    [ "$status" -eq 0 ]
    [ -f "$output_file" ]
    
    # 清理输出文件
    rm -f "$output_file"
}

@test "should process DOCX file correctly" {
    local input_file="$PROJECT_ROOT/test/fixtures/Untitled 1.docx"
    local output_file="/tmp/output_docx.md"
    
    run "$SRC" -i "$input_file" -o "$output_file"
    
    [ "$status" -eq 0 ]
    [ -f "$output_file" ]
    
    # 清理输出文件
    rm -f "$output_file"
}

@test "should process PPT file correctly" {
    local input_file="$PROJECT_ROOT/test/fixtures/测试部门年度述职报告.ppt"
    local output_file="/tmp/output_ppt.md"
    
    run "$SRC" -i "$input_file" -o "$output_file"
    
    [ "$status" -eq 0 ]
    [ -f "$output_file" ]
    
    # 清理输出文件
    rm -f "$output_file"
}

@test "should process PPTX file correctly" {
    local input_file="$PROJECT_ROOT/test/fixtures/测试部门年度述职报告.pptx"
    local output_file="/tmp/output_pptx.md"
    
    run "$SRC" -i "$input_file" -o "$output_file"
    
    [ "$status" -eq 0 ]
    [ -f "$output_file" ]
    
    # 清理输出文件
    rm -f "$output_file"
}

@test "should process PDF file correctly" {
    local input_file="$PROJECT_ROOT/test/fixtures/real_sample.pdf"
    local output_file="/tmp/output_pdf.md"
    
    run "$SRC" -i "$input_file" -o "$output_file"
    
    [ "$status" -eq 0 ]
    [ -f "$output_file" ]
    
    # 清理输出文件
    rm -f "$output_file"
}

@test "should process XLSX file correctly" {
    local input_file="$PROJECT_ROOT/test/fixtures/real_sample.xlsx"
    local output_file="/tmp/output_xlsx.md"
    
    run "$SRC" -i "$input_file" -o "$output_file"
    
    [ "$status" -eq 0 ]
    [ -f "$output_file" ]
    
    # 清理输出文件
    rm -f "$output_file"
}

@test "should process TXT file correctly" {
    local input_file="$PROJECT_ROOT/test/fixtures/more_formats/sample.txt"
    local output_file="/tmp/output_txt.md"
    
    run "$SRC" -i "$input_file" -o "$output_file"
    
    [ "$status" -eq 0 ]
    [ -f "$output_file" ]
    
    # 清理输出文件
    rm -f "$output_file"
}

@test "should process HTML file correctly" {
    local input_file="$PROJECT_ROOT/test/fixtures/more_formats/sample.html"
    local output_file="/tmp/output_html.md"
    
    run "$SRC" -i "$input_file" -o "$output_file"
    
    [ "$status" -eq 0 ]
    [ -f "$output_file" ]
    
    # 清理输出文件
    rm -f "$output_file"
}

@test "should process PNG file correctly" {
    local input_file="$PROJECT_ROOT/test/fixtures/more_formats/sample.png"
    local output_file="/tmp/output_png.md"
    
    run "$SRC" -i "$input_file" -o "$output_file"
    
    [ "$status" -eq 0 ]
    [ -f "$output_file" ]
    
    # 清理输出文件
    rm -f "$output_file"
}

@test "should process JPG file correctly" {
    local input_file="$PROJECT_ROOT/test/fixtures/more_formats/sample.jpg"
    local output_file="/tmp/output_jpg.md"
    
    run "$SRC" -i "$input_file" -o "$output_file"
    
    [ "$status" -eq 0 ]
    [ -f "$output_file" ]
    
    # 清理输出文件
    rm -f "$output_file"
}
