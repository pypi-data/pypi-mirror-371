# BICSdifftest - 神经网络硬件差分测试框架

一个用于Verilog硬件设计验证的综合差分测试框架，通过PyTorch黄金模型、CocoTB测试平台和Verilator仿真器实现系统化的硬件验证。

## 概述

BICSdifftest为神经网络硬件设计提供了完整的差分测试解决方案，能够在多个检查点阶段对比RTL实现与软件参考模型。框架集成了PyTorch用于黄金模型实现、CocoTB用于测试平台开发，以及Verilator用于RTL仿真。

## 核心特性

- **PyTorch黄金模型**: 实现具有检查点功能的参考模型，支持渐进式调试
- **CocoTB集成**: 使用Python编写测试平台，完全访问差分测试框架
- **Verilator后端**: 高性能RTL仿真，配备完整的构建系统
- **多层次对比**: 在多个流水线阶段和检查点对比输出
- **数值精度控制**: 专门针对定点数值计算的容差配置
- **全面报告**: 生成详细的HTML、JSON和JUnit XML报告
- **并行执行**: 支持多线程测试执行以提高验证速度
- **高级日志**: 结构化日志记录，包含性能监控和调试工具
- **配置管理**: 灵活的YAML/JSON配置，支持环境变量覆盖

## 框架架构

```
BICSdifftest/
├── golden_model/          # PyTorch黄金模型
│   ├── base/             # 基础类和工具
│   └── models/           # 具体黄金模型实现
├── testbench/            # CocoTB测试平台基础设施
│   ├── base/             # 基础测试平台类
│   ├── tests/            # 测试实现
│   └── utils/            # 测试工具
├── sim/                  # 仿真后端
│   └── verilator/        # Verilator集成
├── config/               # 配置管理
├── scripts/              # 自动化和工具脚本
├── examples/             # 示例设计和测试
│   ├── fc_layer/         # 全连接层示例
│   └── simple_alu/       # 简单ALU示例
└── docs/                 # 文档
```

## 安装和环境配置

### 先决条件

- Python 3.8+
- Verilator 4.0+
- PyTorch
- CocoTB

### 安装步骤

1. 克隆仓库:
```bash
git clone https://github.com/your-org/BICSdifftest.git
cd BICSdifftest
```

2. 设置开发环境:
```bash
make setup
```

3. 验证安装:
```bash
make check-deps
```

## 全连接层(FC Layer)示例详细指南

### 示例概述

全连接层示例展示了一个完整的神经网络层硬件实现的差分测试，具有以下特性:

- **网络结构**: 100输入，10输出的标准神经网络维度
- **数值精度**: 16位定点算法(8位小数)，适合硬件实现
- **流水线设计**: 高效计算与适当的握手协议
- **双模式操作**: 权重加载和推理模式的分离阶段
- **溢出/下溢处理**: 健壮的定点算法实现
- **调试信号**: 完整的可观测性用于验证

### 快速开始

```bash
# 进入FC层示例目录
cd examples/fc_layer

# 运行完整测试套件
make test

# 或运行单独的测试类别
make test_weight_loading    # 权重/偏置加载测试
make test_inference        # 推理操作测试  
make test_corner_cases     # 边界条件测试
make test_comprehensive    # 综合测试套件
```

### 测试类型详细说明

#### 1. 权重加载测试 (Weight Loading Tests)
- **目的**: 验证权重和偏置加载机制
- **覆盖范围**: 所有1000个权重(100×10) + 10个偏置
- **验证内容**: 内存内容、地址访问、就绪信号
- **预期结果**: 1010/1010 全部通过

#### 2. 推理测试 (Inference Tests)
- **目的**: 测试前向传播计算
- **覆盖范围**: 随机输入、MAC运算、定点算法
- **验证内容**: 输出精度、时序、流水线行为
- **测试数量**: 20个随机测试向量

#### 3. 边界测试 (Corner Case Tests)
- **目的**: 测试边界条件和极端情况
- **测试场景**:
  - 全零输入
  - 最大/最小值
  - 单个激活输入
  - 溢出/下溢条件
- **测试数量**: 11个边界条件测试

#### 4. 综合测试 (Comprehensive Tests)
- **目的**: 端到端验证
- **流程**: 权重加载 → 多次推理 → 结果分析
- **指标**: 总体精度、时序合规性、错误率

### 硬件设计详解

#### Verilog实现 (`rtl/fc_layer.sv`)

```verilog
// 关键参数
parameter INPUT_SIZE = 100    // 输入维度
parameter OUTPUT_SIZE = 10    // 输出维度  
parameter DATA_WIDTH = 16     // 数据宽度
parameter FRAC_BITS = 8       // 小数位数

// 状态机设计
typedef enum logic [2:0] {
    IDLE,           // 空闲状态
    LOAD_WEIGHTS,   // 权重加载
    COMPUTE,        // 计算状态
    ACCUMULATE,     // 累加状态
    OUTPUT          // 输出状态
} state_t;
```

**关键特性:**
- **双模式操作**: 权重加载(mode=0)和推理(mode=1)
- **定点运算**: Q8.8格式(8位整数，8位小数)
- **流水线阶段**: 完整的状态机控制流
- **内存映射权重**: 高效的权重存储和寻址
- **饱和逻辑**: 处理累加器的溢出/下溢
- **调试可观测性**: 状态机、计数器和中间值

### 黄金模型实现

#### PyTorch黄金模型 (`golden_model/models/fc_layer_model.py`)

```python
class FCLayerGoldenModel(GoldenModelBase):
    def __init__(self, input_size=100, output_size=10, 
                 data_width=16, frac_bits=8):
        super().__init__()
        self.input_size = input_size
        self.output_size = output_size
        self.data_width = data_width
        self.frac_bits = frac_bits
        
        # 定点算法参数
        self.scale_factor = 2 ** frac_bits
        self.max_val = (2 ** (data_width - 1)) - 1
        self.min_val = -(2 ** (data_width - 1))
```

**特性:**
- **定点仿真**: 精确匹配硬件精度
- **检查点管理**: 捕获中间计算状态  
- **硬件流程仿真**: 复制流水线行为
- **测试向量生成**: 全面的测试用例创建

### 测试配置 (`config/fc_layer_test.yaml`)

```yaml
# 数值比较配置
comparison:
  mode: "absolute_tolerance"
  absolute_tolerance: 2e-3  # 允许定点量化误差
  signal_overrides:
    output_data: 
      tolerance: 3e-3  # 输出稍高容差
    debug_accumulator:
      tolerance: 1e-2  # 中间值更高容差

# FC层特定配置
fc_layer:
  inference_test_count: 50     # 随机测试数量
  corner_case_count: 15        # 边界测试数量
  max_computation_cycles: 500  # 推理超时周期
```

### 性能指标

- **延迟**: 每次推理约110个时钟周期 (INPUT_SIZE + OUTPUT_SIZE + 开销)
- **吞吐率**: 每110个周期完成1次推理
- **精度**: 由于定点量化的误差 <0.3%
- **资源使用**: 约10K LUT，1K DSP块(估计)

### 测试覆盖率

- **功能覆盖**: 所有操作、模式和数据路径
- **边界条件**: 边界值、溢出/下溢
- **时序覆盖**: 流水线阶段、握手协议、超时
- **精度覆盖**: 定点精度、饱和行为

## 创建新的神经网络模块测试

### 1. 设计黄金模型

```python
from golden_model.base import GoldenModelBase
import torch

class MyNNLayerGoldenModel(GoldenModelBase):
    def __init__(self, **params):
        super().__init__("MyNNLayerGoldenModel")
        
        # 添加层参数
        self.param1 = params.get('param1', default_value)
        self.param2 = params.get('param2', default_value)
        
    def _forward_impl(self, inputs):
        # 实现您的神经网络层逻辑
        stage1_output = self.stage1_processing(inputs)
        self.add_checkpoint('stage1', stage1_output)
        
        stage2_output = self.stage2_processing(stage1_output)
        self.add_checkpoint('stage2', stage2_output)
        
        final_output = self.final_processing(stage2_output)
        return final_output
        
    def generate_test_vectors(self, num_vectors=100):
        """生成测试向量"""
        vectors = []
        for i in range(num_vectors):
            # 创建随机或特定的测试输入
            test_input = torch.randn(self.input_size)
            vectors.append(TestVector(
                inputs={'data': test_input},
                test_id=f"test_{i}"
            ))
        return vectors
```

### 2. 实现Verilog设计

```verilog
module my_nn_layer #(
    parameter INPUT_SIZE = 128,
    parameter OUTPUT_SIZE = 64,
    parameter DATA_WIDTH = 16,
    parameter FRAC_BITS = 8
)(
    input  logic clk,
    input  logic rst_n,
    
    // 控制接口
    input  logic start,
    input  logic mode,  // 0: 配置模式, 1: 推理模式
    output logic ready,
    output logic valid,
    
    // 数据接口
    input  logic [DATA_WIDTH-1:0] input_data [INPUT_SIZE-1:0],
    output logic [DATA_WIDTH-1:0] output_data [OUTPUT_SIZE-1:0],
    
    // 调试接口
    output logic [2:0] debug_state,
    output logic [15:0] debug_counter,
    output logic [DATA_WIDTH-1:0] debug_intermediate_value
);

// 状态机定义
typedef enum logic [2:0] {
    IDLE,
    CONFIGURE,
    COMPUTE,
    OUTPUT_READY
} state_t;

state_t current_state, next_state;

// 实现您的神经网络层逻辑
// ...

endmodule
```

### 3. 编写CocoTB测试

```python
import cocotb
from testbench.base import DiffTestBase, TestSequence, TestVector

class MyNNLayerDiffTest(DiffTestBase):
    def __init__(self, dut):
        golden_model = MyNNLayerGoldenModel()
        super().__init__(dut, golden_model, "MyNNLayerDiffTest")
    
    async def setup_dut(self):
        """初始化DUT"""
        self.dut.rst_n.value = 0
        await RisingEdge(self.dut.clk)
        await RisingEdge(self.dut.clk)
        self.dut.rst_n.value = 1
        await RisingEdge(self.dut.clk)
    
    async def apply_stimulus(self, test_vector):
        """应用测试输入到DUT"""
        # 设置输入数据
        for i, val in enumerate(test_vector.inputs['data']):
            self.dut.input_data[i].value = int(val)
        
        # 启动计算
        self.dut.start.value = 1
        self.dut.mode.value = 1  # 推理模式
        await RisingEdge(self.dut.clk)
        self.dut.start.value = 0
    
    async def wait_for_completion(self):
        """等待计算完成"""
        timeout = 1000
        cycle_count = 0
        
        while cycle_count < timeout:
            await RisingEdge(self.dut.clk)
            if self.dut.valid.value == 1:
                return
            cycle_count += 1
            
        raise TimeoutError(f"计算未在{timeout}周期内完成")
    
    async def capture_outputs(self):
        """捕获DUT输出"""
        outputs = {}
        outputs['data'] = []
        for i in range(self.golden_model.output_size):
            outputs['data'].append(int(self.dut.output_data[i].value))
        
        # 捕获调试信号
        outputs['debug_state'] = int(self.dut.debug_state.value)
        outputs['debug_counter'] = int(self.dut.debug_counter.value)
        
        return outputs

@cocotb.test()
async def test_my_nn_layer_basic(dut):
    """基础功能测试"""
    diff_test = MyNNLayerDiffTest(dut)
    
    # 生成测试向量
    test_vectors = diff_test.golden_model.generate_test_vectors(20)
    sequence = TestSequence("basic_tests", test_vectors)
    
    # 运行差分测试
    results = await diff_test.run_test([sequence])
    
    # 验证结果
    passed_count = sum(1 for r in results if r.passed)
    total_count = len(results)
    
    cocotb.log.info(f"基础测试: {passed_count}/{total_count} 通过")
    assert passed_count == total_count, f"测试失败: {total_count - passed_count} 个失败"
```

### 4. 配置测试环境

```yaml
# my_nn_layer_test.yaml
name: "my_nn_layer"
description: "我的神经网络层差分测试配置"

# DUT配置
top_module: "my_nn_layer"
verilog_sources:
  - "rtl/my_nn_layer.sv"

# 黄金模型配置
golden_model_class: "golden_model.models.MyNNLayerGoldenModel"
golden_model_config:
  input_size: 128
  output_size: 64
  data_width: 16
  frac_bits: 8

# Verilator配置
verilator:
  enable_waves: true
  compile_args: ["-Wall", "--trace", "-O3"]

# 比较配置
comparison:
  mode: "absolute_tolerance"
  absolute_tolerance: 1e-3

# 层特定配置
my_nn_layer:
  test_vectors: 100
  timeout_cycles: 500
```

## 数值精度和容差配置

### 定点数值处理

框架专门针对神经网络硬件中常见的定点数值计算进行了优化:

```python
# 定点数值转换
def to_fixed_point(value, frac_bits):
    """将浮点数转换为定点表示"""
    scale = 2 ** frac_bits
    return int(value * scale)

def from_fixed_point(value, frac_bits):
    """将定点数转换为浮点表示"""
    scale = 2 ** frac_bits
    return float(value) / scale

# 饱和运算
def saturate(value, data_width):
    """饱和运算防止溢出"""
    max_val = (2 ** (data_width - 1)) - 1
    min_val = -(2 ** (data_width - 1))
    return max(min_val, min(max_val, value))
```

### 容差配置策略

```yaml
comparison:
  # 精确匹配 - 用于控制信号
  control_signals:
    mode: "bit_exact"
  
  # 绝对容差 - 用于定点数值
  data_signals:
    mode: "absolute_tolerance"
    tolerance: 2e-3  # 考虑量化误差
  
  # 相对容差 - 用于大动态范围
  normalized_outputs:
    mode: "relative_tolerance"
    tolerance: 1e-2
  
  # ULP容差 - 用于浮点兼容
  floating_point_signals:
    mode: "ulp_tolerance"
    ulps: 2
```

## 性能调优和调试技巧

### 1. 仿真性能优化

```bash
# 使用优化编译选项
make VERILATOR_ARGS="-O3 --x-assign fast --x-initial fast"

# 并行仿真
make test PARALLEL_JOBS=8

# 禁用波形生成(提高速度)
make test ENABLE_WAVES=0
```

### 2. 调试方法

#### 波形分析
```bash
# 生成详细波形
make sim WAVE_DEPTH=99
# 查看波形(使用GTKWave)
gtkwave sim/waves/fc_layer/*.fst
```

#### 日志分析
```bash
# 启用详细日志
make test LOG_LEVEL=DEBUG

# 查看特定测试的日志
cat logs/fc_layer/difftest.log | grep "inference_0"

# 分析检查点信息
python scripts/analyze_checkpoints.py logs/fc_layer/
```

#### 数值分析
```python
# 分析定点精度影响
import numpy as np

def analyze_quantization_error(golden_float, hardware_fixed, frac_bits):
    """分析量化误差"""
    scale = 2 ** frac_bits
    golden_fixed = np.round(golden_float * scale) / scale
    
    abs_error = np.abs(hardware_fixed - golden_fixed)
    rel_error = abs_error / np.abs(golden_fixed + 1e-10)
    
    print(f"最大绝对误差: {np.max(abs_error):.6f}")
    print(f"平均相对误差: {np.mean(rel_error):.6f}")
    print(f"误差分布: {np.percentile(abs_error, [50, 95, 99])}")
```

### 3. 常见问题排查

#### 时序问题
- 检查时钟域设置
- 验证握手协议时序
- 确认复位信号极性

#### 数值精度问题
- 验证定点格式匹配
- 检查溢出/下溢处理
- 调整比较容差设置

#### 测试超时
- 增加仿真超时时间
- 检查DUT握手信号
- 验证状态机转换

## 扩展指南

### 添加新的激活函数

```python
class ReLULayer(GoldenModelBase):
    def __init__(self, data_width=16, frac_bits=8):
        super().__init__("ReLULayer")
        self.data_width = data_width
        self.frac_bits = frac_bits
    
    def _forward_impl(self, inputs):
        # ReLU: max(0, x)
        output = torch.clamp(inputs, min=0)
        self.add_checkpoint('relu_output', output)
        return output
```

### 支持多层神经网络

```python
class MultiLayerNN(GoldenModelBase):
    def __init__(self, layer_sizes=[100, 50, 10]):
        super().__init__("MultiLayerNN")
        self.layers = []
        
        for i in range(len(layer_sizes) - 1):
            layer = FCLayerGoldenModel(
                input_size=layer_sizes[i],
                output_size=layer_sizes[i+1]
            )
            self.layers.append(layer)
    
    def _forward_impl(self, inputs):
        x = inputs
        for i, layer in enumerate(self.layers):
            x = layer(x)
            self.add_checkpoint(f'layer_{i}_output', x)
        return x
```

### 集成卷积层

```verilog
module conv_layer #(
    parameter IN_CHANNELS = 3,
    parameter OUT_CHANNELS = 16,
    parameter KERNEL_SIZE = 3,
    parameter INPUT_HEIGHT = 32,
    parameter INPUT_WIDTH = 32
)(
    // 接口定义
);
    // 卷积计算实现
endmodule
```

## 最佳实践

### 1. 测试设计原则
- **分层测试**: 从单元测试到集成测试
- **边界覆盖**: 涵盖所有边界条件
- **随机测试**: 使用随机输入增加覆盖率
- **回归测试**: 确保修改不破坏现有功能

### 2. 代码组织
- **模块化设计**: 保持每个模块职责单一
- **接口标准化**: 使用一致的接口协议
- **文档完整**: 为每个模块提供清晰文档
- **版本控制**: 使用语义化版本控制

### 3. 性能考虑
- **仿真效率**: 平衡精度和速度
- **内存使用**: 优化大型网络的内存占用
- **并行化**: 利用多核加速测试执行
- **缓存策略**: 复用计算结果和测试数据

## 故障排除

### 环境问题
```bash
# 检查依赖
python -c "import torch; import cocotb; print('依赖OK')"

# 验证Verilator安装
verilator --version

# 检查Python路径
echo $PYTHONPATH
```

### 仿真问题
```bash
# 清理构建缓存
make clean

# 重新构建
make build

# 检查编译错误
make build 2>&1 | grep -i error
```

### 测试调试
```bash
# 单步调试模式
make test DEBUG=1

# 保留中间文件
make test KEEP_TEMP=1

# 详细错误信息
make test VERBOSE=1
```

## 结论

BICSdifftest框架为神经网络硬件验证提供了一个强大而灵活的平台。通过结合PyTorch的数值计算能力、CocoTB的Python测试环境和Verilator的高性能仿真，该框架能够有效地验证复杂的神经网络硬件设计。

FC Layer示例展示了框架的完整能力，从简单的权重加载到复杂的推理计算，所有测试都能达到高精度匹配。通过本文档的指导，用户可以快速上手并为自己的神经网络硬件设计创建全面的验证环境。

### 测试结果总结

基于最新的测试日志，FC Layer示例已经实现了**100%的测试通过率**:

- ✅ **权重加载测试**: 1010/1010 通过 (100%)
- ✅ **推理测试**: 20/20 通过 (100%)  
- ✅ **边界测试**: 11/11 通过 (100%)
- ✅ **综合测试**: 全部通过 (100%)

这证明了BICSdifftest框架在神经网络硬件验证方面的有效性和可靠性。

---

**BICSdifftest** - 将软件风格的测试方法带入硬件验证领域，为神经网络加速器开发提供坚实的验证基础。