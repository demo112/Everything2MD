# Everything2MD Makefile

# 默认目标
.PHONY: test unit-test integration-test coverage clean

# 测试目录
TEST_DIR := test
UNIT_TEST_DIR := $(TEST_DIR)/unit
INTEGRATION_TEST_DIR := $(TEST_DIR)/integration

# Bats可执行文件路径
BATS := $(TEST_DIR)/bats/bin/bats

# 运行所有测试
test:
	$(BATS) $(UNIT_TEST_DIR) $(INTEGRATION_TEST_DIR)

# 运行单元测试
unit-test:
	$(BATS) $(UNIT_TEST_DIR)

# 运行集成测试
integration-test:
	$(BATS) $(INTEGRATION_TEST_DIR)

# 清理测试生成的文件
clean:
	rm -f *.md
	rm -rf output/