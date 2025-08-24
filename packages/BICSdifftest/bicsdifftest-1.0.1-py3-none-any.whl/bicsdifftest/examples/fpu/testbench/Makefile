# Simple CocoTB Makefile for FPU testing

# Simulator
SIM ?= verilator

# Python paths
export PYTHONPATH := $(PWD)/../../..:$(PWD)/..

# RTL Design
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES += $(PWD)/../rtl/fpu.sv
TOPLEVEL ?= FPU

# Test module
MODULE ?= test_fpu_simple

# CocoTB configuration
COCOTB_LOG_LEVEL ?= INFO
RANDOM_SEED ?= 42

# Verilator specific
ifeq ($(SIM), verilator)
    COMPILE_ARGS += --trace --trace-depth 99
    COMPILE_ARGS += -Wall -Wno-TIMESCALEMOD -Wno-DECLFILENAME -Wno-UNUSEDSIGNAL -Wno-UNUSEDPARAM
    COMPILE_ARGS += --x-assign fast --x-initial fast
endif

# Include CocoTB makefiles
include $(shell cocotb-config --makefiles)/Makefile.sim

# Clean target
clean::
	rm -rf sim_build/
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -f results.xml