# FPU 差分测试示例

本示例演示如何使用 BICSdifftest 框架为简单的 FPU（浮点处理单元）设计创建差分测试。

## 项目概览

这个 FPU 实际上是一个简单的比较器，实现了 `max(a, b)` 功能：
- 输入：两个 32位无符号整数 `a` 和 `b`
- 输出：两个输入中的较大值
- 类型：纯组合逻辑（无时钟）

## 文件结构

```
examples/fpu/
├── README.md                 # 本文件
├── Makefile                  # 主Makefile
├── config/
│   └── fpu_test.yaml        # 测试配置文件
├── rtl/
│   └── fpu.sv               # FPU RTL设计
├── testbench/
│   ├── Makefile             # CocoTB测试Makefile
│   ├── test_fpu.py          # 完整框架测试（时钟版本）
│   └── test_fpu_simple.py   # 简化测试（组合逻辑版本）
├── scripts/
│   └── generate_test_data.py # 测试数据生成脚本
└── test_output/             # 生成的测试数据和报告
    ├── fpu_test_suite.json
    ├── fpu_test_suite.pkl
    └── test_suite_report.txt
```

## 核心组件

### 1. PyTorch 黄金模型
位置：`/home/yanggl/code/BICSdifftest/golden_model/models/fpu_model.py`

```python
class FPUGoldenModel(GoldenModelBase):
    """FPU设计的PyTorch黄金模型，实现max(a, b)操作"""
    
    def _forward_impl(self, inputs):
        a = inputs.get('a', 0)
        b = inputs.get('b', 0)
        result = max(a, b)
        return {'result': torch.tensor(result, dtype=torch.int64)}
```

### 2. RTL设计
```systemverilog
module FPU (
    input [31:0] a,
    input [31:0] b,
    output reg [31:0] result
);
    always @(*) begin
        if (a > b) begin
            result = a;
        end else begin
            result = b;
        end
    end
endmodule
```

### 3. 测试框架
- **完整框架版本** (`test_fpu.py`)：使用完整的 BICSdifftest 框架，但需要时钟信号
- **简化版本** (`test_fpu_simple.py`)：直接使用 CocoTB，适用于组合逻辑

## 测试覆盖

### 测试类型
1. **简单测试**：基本功能验证 (`max(100, 200) = 200`)
2. **边界测试**：包含12个边界情况
   - 零值测试：`max(0, 0)`, `max(0, 1)`
   - 最大值测试：`max(MAX_VAL, 0)`
   - 相等值测试：`max(100, 100)`
   - 相邻值测试：`max(100, 101)`
3. **随机测试**：10个随机生成的测试用例
4. **综合测试**：以上所有测试的组合

### 测试结果
```
=== Test Summary ===
Total tests: 23
Passed: 23
Failed: 0
Pass rate: 100.0%

Test breakdown by type:
  simple: 1/1 passed
  corner_case: 12/12 passed
  random: 10/10 passed
```

## 使用方法

### 1. 快速运行
```bash
cd examples/fpu
make clean
make validate-rtl          # 验证RTL语法
make generate-test-data    # 生成测试数据
cd testbench && make       # 运行CocoTB测试
```

### 2. 分步运行
```bash
# 检查依赖
make check-deps

# 生成测试数据
make generate-test-data

# 验证RTL
make validate-rtl

# 运行测试
cd testbench
make clean
make MODULE=test_fpu_simple
```

### 3. 查看结果
```bash
# 查看测试数据报告
cat test_output/test_suite_report.txt

# 查看CocoTB测试结果
cat testbench/results.xml
```

## 学习要点

### 1. 框架适应性
这个示例展示了如何将 BICSdifftest 框架适配到不同类型的硬件设计：
- 对于有时钟的设计，使用完整框架
- 对于组合逻辑，使用简化的 CocoTB 测试

### 2. 黄金模型设计
- 继承 `GoldenModelBase` 类
- 实现 `_forward_impl` 方法
- 提供检查点机制用于调试

### 3. 测试向量生成
- 系统性的边界测试
- 随机测试用于覆盖率
- 可重现的测试（固定种子）

### 4. RTL验证
- Verilator 语法检查
- CocoTB 功能验证
- 自动化测试流程

## 关键特性

### ✅ 已实现功能
- [x] PyTorch 黄金模型
- [x] RTL 语法验证
- [x] 边界测试覆盖
- [x] 随机测试生成
- [x] CocoTB 集成
- [x] 自动化测试流程
- [x] 测试报告生成

### 🎯 学习目标
- [x] 理解差分测试概念
- [x] 学会创建黄金模型
- [x] 掌握 CocoTB 使用方法
- [x] 了解测试向量设计
- [x] 体验自动化验证流程

## 扩展建议

1. **增加测试覆盖**：
   - 添加性能测试
   - 增加功耗分析
   - 实现时序验证

2. **框架增强**：
   - 支持更复杂的FPU操作（加法、乘法等）
   - 添加浮点数支持
   - 实现流水线设计

3. **自动化改进**：
   - 集成CI/CD流程
   - 添加覆盖率分析
   - 实现回归测试

## 总结

这个FPU差分测试示例提供了一个完整的学习框架，展示了从RTL设计到验证完成的全流程。通过简单的 `max(a, b)` 功能，新用户可以快速理解差分测试的核心概念和BICSdifftest框架的使用方法。

示例代码简洁清晰，测试覆盖全面，是学习硬件验证和差分测试的理想起点。