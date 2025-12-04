# Everything2MD Makefile

# 默认目标
.PHONY: test test-bats test-python unit-test integration-test coverage clean

# 测试目录
TEST_DIR := test
UNIT_TEST_DIR := $(TEST_DIR)/unit
INTEGRATION_TEST_DIR := $(TEST_DIR)/integration
PYTHON_TEST_DIR := $(TEST_DIR)/python

# 可执行文件路径
BATS := $(TEST_DIR)/bats/bin/bats
# Windows path for pytest in venv
PYTEST := venv/Scripts/pytest

# 运行所有测试
test: test-bats test-python

# 运行 Bats 测试
test-bats:
	$(BATS) $(UNIT_TEST_DIR) $(INTEGRATION_TEST_DIR)

# 运行 Python 测试
test-python:
	$(PYTEST) $(PYTHON_TEST_DIR)

# 运行单元测试 (Legacy Bats)
unit-test:
	$(BATS) $(UNIT_TEST_DIR)

# 运行集成测试 (Legacy Bats)
integration-test:
	$(BATS) $(INTEGRATION_TEST_DIR)

# 清理测试生成的文件
clean:
	rm -f *.md
	rm -rf output/
