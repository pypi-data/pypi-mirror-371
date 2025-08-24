# Makefile for FPU differential testing using BICSdifftest framework
#
# This Makefile provides targets for running FPU differential tests
# using CocoTB and the BICSdifftest framework.

# Project configuration
PROJECT_NAME := fpu
TOP_MODULE := FPU
VERILOG_SOURCES := rtl/fpu.sv

# Framework paths
FRAMEWORK_ROOT := ../..
PYTHON_PATH := $(FRAMEWORK_ROOT):$(shell pwd)

# Directories
BUILD_DIR := sim_build
TEST_DIR := testbench
CONFIG_DIR := config
SCRIPTS_DIR := scripts
OUTPUT_DIR := test_output
LOGS_DIR := logs
REPORTS_DIR := reports
WAVES_DIR := waves

# Python configuration
export PYTHONPATH := $(PYTHON_PATH)
PYTHON := python3

# CocoTB configuration
TOPLEVEL_LANG := verilog
TOPLEVEL := $(TOP_MODULE)
MODULE := test_fpu

# Verilator configuration
SIM := verilator
COMPILE_ARGS := -Wall -Wno-TIMESCALEMOD -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL -Wno-UNUSEDPARAM
COMPILE_ARGS += --trace --trace-depth 99 -O3 --x-assign fast --x-initial fast

# Test configuration
TEST_CONFIG := $(CONFIG_DIR)/fpu_test.yaml
COCOTB_LOG_LEVEL := INFO
COCOTB_REDUCED_LOG_FMT := 1
RANDOM_SEED := 42

# Export CocoTB variables
export TOPLEVEL_LANG
export TOPLEVEL  
export MODULE
export SIM
export COMPILE_ARGS
export COCOTB_LOG_LEVEL
export COCOTB_REDUCED_LOG_FMT
export RANDOM_SEED

# Default target
.PHONY: all
all: clean generate-test-data test

# Clean all generated files
.PHONY: clean
clean:
	@echo "Cleaning FPU test environment..."
	rm -rf $(BUILD_DIR)
	rm -rf $(OUTPUT_DIR)
	rm -rf $(LOGS_DIR)
	rm -rf $(REPORTS_DIR)
	rm -rf $(WAVES_DIR)
	rm -f results.xml
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	@echo "Clean completed."

# Create necessary directories
.PHONY: setup-dirs
setup-dirs:
	@echo "Setting up directories..."
	mkdir -p $(BUILD_DIR)
	mkdir -p $(OUTPUT_DIR)
	mkdir -p $(LOGS_DIR)
	mkdir -p $(REPORTS_DIR)
	mkdir -p $(WAVES_DIR)

# Generate test data
.PHONY: generate-test-data
generate-test-data: setup-dirs
	@echo "Generating FPU test data..."
	cd $(SCRIPTS_DIR) && $(PYTHON) generate_test_data.py \
		--output-dir ../$(OUTPUT_DIR) \
		--random-count 20 \
		--seed $(RANDOM_SEED) \
		--verify

# Run simple test
.PHONY: test-simple
test-simple: setup-dirs generate-test-data
	@echo "Running FPU simple test..."
	cd $(TEST_DIR) && $(PYTHON) -m cocotb.regression test_fpu.test_fpu_simple

# Run corner case tests
.PHONY: test-corner
test-corner: setup-dirs generate-test-data
	@echo "Running FPU corner case tests..."
	cd $(TEST_DIR) && $(PYTHON) -m cocotb.regression test_fpu.test_fpu_corner_cases

# Run random tests
.PHONY: test-random
test-random: setup-dirs generate-test-data
	@echo "Running FPU random tests..."
	cd $(TEST_DIR) && $(PYTHON) -m cocotb.regression test_fpu.test_fpu_random

# Run comprehensive tests
.PHONY: test-comprehensive
test-comprehensive: setup-dirs generate-test-data
	@echo "Running FPU comprehensive tests..."
	cd $(TEST_DIR) && $(PYTHON) -m cocotb.regression test_fpu.test_fpu_comprehensive

# Run all tests
.PHONY: test
test: setup-dirs generate-test-data
	@echo "Running all FPU tests..."
	cd $(TEST_DIR) && $(PYTHON) -m pytest -v test_fpu.py::test_fpu_simple -s
	cd $(TEST_DIR) && $(PYTHON) -m pytest -v test_fpu.py::test_fpu_corner_cases -s
	cd $(TEST_DIR) && $(PYTHON) -m pytest -v test_fpu.py::test_fpu_random -s
	cd $(TEST_DIR) && $(PYTHON) -m pytest -v test_fpu.py::test_fpu_comprehensive -s

# Alternative test runner using cocotb directly
.PHONY: test-cocotb
test-cocotb: setup-dirs generate-test-data
	@echo "Running FPU tests with cocotb..."
	cd $(TEST_DIR) && make

# Run tests with different log levels
.PHONY: test-debug
test-debug: COCOTB_LOG_LEVEL := DEBUG
test-debug: test

.PHONY: test-quiet
test-quiet: COCOTB_LOG_LEVEL := WARNING
test-quiet: test

# Generate test report
.PHONY: report
report:
	@echo "Generating test report..."
	@if [ -f results.xml ]; then \
		echo "Test results summary:"; \
		grep -o 'tests="[0-9]*"' results.xml | head -1 | cut -d'"' -f2 | xargs -I {} echo "Total tests: {}"; \
		grep -o 'failures="[0-9]*"' results.xml | head -1 | cut -d'"' -f2 | xargs -I {} echo "Failed tests: {}"; \
		grep -o 'errors="[0-9]*"' results.xml | head -1 | cut -d'"' -f2 | xargs -I {} echo "Error tests: {}"; \
	else \
		echo "No test results found. Run tests first."; \
	fi

# Check framework dependencies
.PHONY: check-deps
check-deps:
	@echo "Checking framework dependencies..."
	@$(PYTHON) -c "import cocotb; print(f'CocoTB version: {cocotb.__version__}')" 2>/dev/null || echo "CocoTB not found"
	@$(PYTHON) -c "import torch; print(f'PyTorch version: {torch.__version__}')" 2>/dev/null || echo "PyTorch not found"
	@$(PYTHON) -c "import numpy; print(f'NumPy version: {numpy.__version__}')" 2>/dev/null || echo "NumPy not found"
	@which verilator >/dev/null && echo "Verilator found: $(shell which verilator)" || echo "Verilator not found"

# Validate RTL syntax
.PHONY: validate-rtl
validate-rtl:
	@echo "Validating RTL syntax..."
	verilator --lint-only -Wall $(VERILOG_SOURCES)

# Show make targets
.PHONY: help
help:
	@echo "FPU Differential Testing Makefile"
	@echo "================================="
	@echo ""
	@echo "Main targets:"
	@echo "  all                 - Clean, generate test data, and run all tests"
	@echo "  test                - Run all tests using pytest"
	@echo "  test-cocotb         - Run tests using cocotb directly"
	@echo "  clean               - Clean all generated files"
	@echo ""
	@echo "Individual test targets:"
	@echo "  test-simple         - Run simple test case"
	@echo "  test-corner         - Run corner case tests"
	@echo "  test-random         - Run random tests"
	@echo "  test-comprehensive  - Run comprehensive test suite"
	@echo ""
	@echo "Utility targets:"
	@echo "  generate-test-data  - Generate test vectors and reference data"
	@echo "  setup-dirs          - Create necessary directories"
	@echo "  validate-rtl        - Validate RTL syntax"
	@echo "  check-deps          - Check framework dependencies"
	@echo "  report              - Generate test results summary"
	@echo ""
	@echo "Debug targets:"
	@echo "  test-debug          - Run tests with DEBUG log level"
	@echo "  test-quiet          - Run tests with WARNING log level"
	@echo ""
	@echo "Configuration:"
	@echo "  PROJECT_NAME = $(PROJECT_NAME)"
	@echo "  TOP_MODULE = $(TOP_MODULE)"
	@echo "  TEST_CONFIG = $(TEST_CONFIG)"
	@echo "  RANDOM_SEED = $(RANDOM_SEED)"

# Show current configuration
.PHONY: config
config:
	@echo "FPU Test Configuration"
	@echo "====================="
	@echo "Project: $(PROJECT_NAME)"
	@echo "Top Module: $(TOP_MODULE)"
	@echo "Verilog Sources: $(VERILOG_SOURCES)"
	@echo "Framework Root: $(FRAMEWORK_ROOT)"
	@echo "Python Path: $(PYTHON_PATH)"
	@echo "Build Directory: $(BUILD_DIR)"
	@echo "Test Config: $(TEST_CONFIG)"
	@echo "Random Seed: $(RANDOM_SEED)"
	@echo "Simulator: $(SIM)"
	@echo "Log Level: $(COCOTB_LOG_LEVEL)"