# Fully Connected Layer CocoTB Test Makefile
# This demonstrates how to run the differential testing framework for FC Layer

# Paths
PWD=$(shell pwd)
FRAMEWORK_ROOT=$(PWD)/../..

# DUT configuration
TOPLEVEL_LANG = verilog
VERILOG_SOURCES = $(PWD)/rtl/fc_layer.sv

# Test configuration  
TOPLEVEL = fc_layer
MODULE = testbench.test_fc_layer

# Export environment
export PYTHONPATH := $(FRAMEWORK_ROOT):$(PYTHONPATH)

# Simulator selection
SIM ?= verilator

# Verilator specific options
ifeq ($(SIM),verilator)
    COMPILE_ARGS += -Wall
    COMPILE_ARGS += -Wno-TIMESCALEMOD
    COMPILE_ARGS += -Wno-DECLFILENAME
    COMPILE_ARGS += -Wno-UNUSEDSIGNAL
    COMPILE_ARGS += -Wno-UNUSEDPARAM
    COMPILE_ARGS += --trace
    EXTRA_ARGS += --trace-fst --trace-structs
    # Add optimization for large designs
    COMPILE_ARGS += -O3
    COMPILE_ARGS += --x-assign fast
    COMPILE_ARGS += --x-initial fast
endif

# Include cocotb makefiles
include $(shell cocotb-config --makefiles)/Makefile.sim

# Test targets
.PHONY: test_weight_loading test_inference test_corner_cases test_comprehensive
test_weight_loading:
	TESTCASE=test_fc_layer_weight_loading $(MAKE) sim

test_inference:
	TESTCASE=test_fc_layer_inference $(MAKE) sim

test_corner_cases:
	TESTCASE=test_fc_layer_corner_cases $(MAKE) sim

test_comprehensive:
	TESTCASE=test_fc_layer_comprehensive $(MAKE) sim

# Run all tests
.PHONY: test_all
test_all: test_weight_loading test_inference test_corner_cases test_comprehensive

.PHONY: clean
clean::
	rm -rf __pycache__
	rm -rf sim_build
	rm -rf *.vcd *.fst
	rm -rf results.xml
	rm -rf logs/
	rm -rf reports/
	rm -rf waves/