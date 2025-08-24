# Simple ALU CocoTB Test Makefile
# This demonstrates how to run the differential testing framework

# Paths
PWD=$(shell pwd)
FRAMEWORK_ROOT=$(PWD)/../..

# DUT configuration
TOPLEVEL_LANG = verilog
VERILOG_SOURCES = $(PWD)/rtl/simple_alu.sv

# Test configuration  
TOPLEVEL = simple_alu
MODULE = testbench.test_simple_alu

# Export environment
export PYTHONPATH := $(FRAMEWORK_ROOT):$(PYTHONPATH)

# Simulator selection
SIM ?= verilator

# Verilator specific options
ifeq ($(SIM),verilator)
    COMPILE_ARGS += -Wall
    COMPILE_ARGS += -Wno-TIMESCALEMOD
    COMPILE_ARGS += --trace
    EXTRA_ARGS += --trace-fst --trace-structs
endif

# Include cocotb makefiles
include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: clean
clean::
	rm -rf __pycache__
	rm -rf sim_build
	rm -rf *.vcd *.fst
	rm -rf results.xml