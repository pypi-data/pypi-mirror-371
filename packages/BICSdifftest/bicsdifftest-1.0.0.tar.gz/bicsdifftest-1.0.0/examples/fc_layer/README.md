# Fully Connected Layer Differential Testing Example

This example demonstrates comprehensive differential testing for a single-layer fully connected neural network hardware implementation using the BICSdifftest framework.

## Overview

The FC Layer implementation features:
- **100 inputs, 10 outputs** - Standard neural network dimensions
- **16-bit fixed-point arithmetic** (8 fractional bits) - Hardware-friendly precision
- **Pipeline design** - Efficient computation with proper handshaking
- **Weight loading and inference modes** - Separate phases for configuration and operation
- **Overflow/underflow handling** - Robust fixed-point arithmetic
- **Comprehensive debug signals** - Full observability for verification

## Architecture

### Hardware Design (`rtl/fc_layer.sv`)

The Verilog implementation includes:

```verilog
// Key parameters
parameter INPUT_SIZE = 100
parameter OUTPUT_SIZE = 10  
parameter DATA_WIDTH = 16
parameter FRAC_BITS = 8
```

**Key Features:**
- **Dual-mode operation**: Weight loading (mode=0) and inference (mode=1)
- **Fixed-point arithmetic**: Q8.8 format (8 integer, 8 fractional bits)
- **Pipeline stages**: IDLE → LOAD_WEIGHTS → COMPUTE → ACCUMULATE → OUTPUT
- **Memory-mapped weights**: Efficient weight storage with addressing
- **Saturation logic**: Handles overflow/underflow in accumulator
- **Debug observability**: State machine, counters, and intermediate values

### Golden Model (`golden_model/models/fc_layer_model.py`)

The PyTorch golden model provides:

```python
class FCLayerGoldenModel(GoldenModelBase):
    def __init__(self, input_size=100, output_size=10, 
                 data_width=16, frac_bits=8):
        # Exact fixed-point arithmetic matching hardware
        # Checkpoint-based verification
        # Bit-accurate computation flow
```

**Features:**
- **Fixed-point simulation** - Matches hardware precision exactly
- **Checkpoint management** - Captures intermediate computation states  
- **Hardware flow simulation** - Replicates pipeline behavior
- **Test vector generation** - Comprehensive test case creation

## Test Scenarios

### 1. Weight Loading Tests
- **Purpose**: Verify weight and bias loading mechanism
- **Coverage**: All 1000 weights (100×10) + 10 biases
- **Verification**: Memory contents, addressing, ready signals

### 2. Inference Tests
- **Purpose**: Test forward pass computation
- **Coverage**: Random inputs, MAC operations, fixed-point arithmetic
- **Verification**: Output accuracy, timing, pipeline behavior

### 3. Corner Case Tests
- **Purpose**: Test boundary conditions and edge cases
- **Scenarios**:
  - All-zero inputs
  - Maximum/minimum values
  - Single active input
  - Overflow/underflow conditions

### 4. Comprehensive Tests
- **Purpose**: End-to-end validation
- **Flow**: Weight loading → Multiple inference → Results analysis
- **Metrics**: Overall accuracy, timing compliance, error rates

## Usage

### Quick Start

```bash
# Navigate to FC layer example
cd examples/fc_layer

# Run individual test categories
make test_weight_loading    # Test weight/bias loading
make test_inference        # Test inference operations  
make test_corner_cases     # Test edge conditions
make test_comprehensive    # Full test suite

# Run all tests
make test_all
```

### Test Configuration

The test behavior can be customized via `config/fc_layer_test.yaml`:

```yaml
# Adjust test parameters
fc_layer:
  inference_test_count: 50     # Number of random tests
  corner_case_count: 15        # Number of corner cases
  max_computation_cycles: 500  # Timeout for inference

# Modify comparison tolerances  
comparison:
  absolute_tolerance: 2e-3     # Fixed-point quantization tolerance
  output_data:
    tolerance: 3e-3            # Higher tolerance for final outputs
```

## Expected Results

### Performance Metrics
- **Latency**: ~110 clock cycles per inference (INPUT_SIZE + OUTPUT_SIZE + overhead)
- **Throughput**: 1 inference per 110 cycles
- **Accuracy**: <0.3% error due to fixed-point quantization
- **Resource Usage**: ~10K LUTs, ~1K DSP blocks (estimated)

### Test Coverage
- **Functional**: All operations, modes, and data paths
- **Corner cases**: Boundary values, overflow/underflow
- **Timing**: Pipeline stages, handshaking, timeouts
- **Accuracy**: Fixed-point precision, saturation behavior

## Debug and Analysis

### Waveform Analysis
```bash
# Generate FST waveforms
make sim
# View with GTKWave or similar: waves/fc_layer/*.fst
```

### Log Analysis
```bash
# Check detailed logs
ls logs/fc_layer/
cat logs/fc_layer/difftest.log
```

### Checkpoint Inspection
The golden model saves detailed checkpoints:
- Input preprocessing
- Weight loading operations
- MAC computation steps
- Accumulator evolution
- Output saturation

## Extending the Example

### Adding New Test Scenarios

1. **Extend Test Vector Generator**:
```python
# In golden_model/models/fc_layer_model.py
class FCLayerTestVectorGenerator:
    def generate_custom_vectors(self):
        # Add your test scenarios
```

2. **Add New Test Functions**:
```python
# In testbench/test_fc_layer.py
@cocotb.test()
async def test_custom_scenario(dut):
    # Your custom test logic
```

### Hardware Modifications

1. **Different Dimensions**: Modify `INPUT_SIZE`, `OUTPUT_SIZE` parameters
2. **Precision Changes**: Adjust `DATA_WIDTH`, `FRAC_BITS` 
3. **Pipeline Depth**: Add stages to `state_t` enum and FSM
4. **Activation Functions**: Extend with ReLU, sigmoid, etc.

## Integration with BICSdifftest Framework

This example demonstrates key framework features:

- **`DiffTestBase` inheritance** - Structured test organization
- **Checkpoint-based comparison** - Detailed state verification  
- **Configurable tolerances** - Fixed-point aware comparisons
- **Pipeline-aware testing** - Multi-cycle operation support
- **Debug signal integration** - Hardware observability

The FC Layer example serves as a template for testing more complex neural network accelerator designs while maintaining the rigorous verification methodology of the BICSdifftest framework.