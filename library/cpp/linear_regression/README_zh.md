# 线性回归库 (Linear Regression Library)

## 项目概述

本库提供了一套完整的线性回归分析工具，包括多种求解器、统计分析器和优化算法。支持快速线性回归、加权回归、单峰优化等功能，适用于各种机器学习和数据分析场景。

## 文件说明

### 核心算法

- **`linear_regression.h/cpp`** - 主要线性回归实现
  - `TFastLinearRegressionSolver`: 快速线性回归求解器
  - `TLinearRegressionSolver`: 标准线性回归求解器
  - `TTypedFastSLRSolver`: 类型化的单变量线性回归求解器
  - 支持加权最小二乘法和正则化

- **`linear_model.h`** - 线性模型定义
  - `TLinearModel`: 线性模型类，存储系数和截距
  - 支持模型序列化和反序列化
  - 提供预测功能

### 统计计算

- **`welford.h/cpp`** - Welford 算法实现
  - `TMeanCalculator`: 精确加权均值计算器
  - `TCovariationCalculator`: 协方差计算器
  - `TDeviationCalculator`: 标准差计算器
  - 使用 Kahan 累加器保证数值精度

### 优化算法

- **`unimodal.h/cpp`** - 单峰优化
  - `MakeUnimodal`: 单峰化算法
  - `TOptimizationParams`: 优化参数配置
  - `TGreedyParams`: 贪心算法参数
  - 支持自适应参数调整

### 构建文件

- **`ya.make`** - Ytsaurus 构建系统配置

## 实现原理

### 线性回归核心

线性回归模型：`y = β₀ + β₁x₁ + β₂x₂ + ... + βₙxₙ`

通过最小二乘法求解：
```
min Σ(wᵢ × (yᵢ - ŷᵢ)²)
```

其中：
- `yᵢ`: 实际值
- `ŷᵢ`: 预测值
- `wᵢ`: 权重

### 快速求解器

```cpp
class TFastLinearRegressionSolver {
    TKahanAccumulator<double> SumSquaredGoals;  // 目标值平方和
    TVector<double> LinearizedOLSMatrix;        // 线性化 OLS 矩阵
    TVector<double> OLSVector;                  // OLS 向量
};
```

使用 Kahan 累加器避免浮点精度损失。

### Welford 算法

Welford 算法提供了数值稳定的增量统计计算：

```cpp
class TMeanCalculator {
    double Mean = 0.;
    TKahanAccumulator<double> SumWeights;

    void Add(const double value, const double weight = 1.) {
        // 增量更新均值
        double newSumWeights = SumWeights + weight;
        Mean += (value - Mean) * weight / newSumWeights;
        SumWeights = newSumWeights;
    }
};
```

### 单峰优化

单峰化算法通过调整数据使其呈现单一峰值的特性：

```cpp
struct TOptimizationParams {
    TGreedyParams ModeParams;        // 模式参数
    TGreedyParams NormalizerParams;  // 归一化参数
    double OptimizationShrinkage;    // 优化收缩率
    double RegressionShrinkage;      // 回归收缩率
    size_t IterationsCount;          // 迭代次数
};
```

## 使用示例

### 基本线性回归

```cpp
#include "linear_regression.h"

// 创建求解器
TFastLinearRegressionSolver solver;

// 添加训练数据
TVector<double> features1 = {1.0, 2.0, 3.0};
TVector<double> features2 = {4.0, 5.0, 6.0};
solver.Add(features1, 10.0);  // y = 10.0
solver.Add(features2, 15.0);  // y = 15.0

// 求解模型
TLinearModel model = solver.Solve();

// 预测
TVector<double> testFeatures = {2.5, 4.5};
double prediction = model.Prediction(testFeatures);
```

### 加权线性回归

```cpp
TFastLinearRegressionSolver solver;

// 添加带权重的数据
solver.Add(features1, 10.0, 0.5);  // 权重 0.5
solver.Add(features2, 15.0, 1.0);  // 权重 1.0

TLinearModel model = solver.Solve();
```

### 单变量快速回归

```cpp
TTypedFastSLRSolver<double> solver;

// 添加数据点
solver.Add(1.0, 2.0);  // x=1.0, y=2.0
solver.Add(2.0, 4.0);  // x=2.0, y=4.0
solver.Add(3.0, 6.0);  // x=3.0, y=6.0

// 求解斜率和截距
double factor, intercept;
solver.Solve(factor, intercept, 0.1);  // 正则化参数 0.1

// factor ≈ 2.0, intercept ≈ 0.0
```

### 使用统计计算器

```cpp
#include "welford.h"

// 均值计算
TMeanCalculator meanCalc;
meanCalc.Add(10.0, 1.0);
meanCalc.Add(20.0, 2.0);
double mean = meanCalc.GetMean();

// 协方差计算
TCovariationCalculator covCalc;
covCalc.Add(1.0, 2.0);  // x=1.0, y=2.0
covCalc.Add(2.0, 4.0);  // x=2.0, y=4.0
double cov = covCalc.GetCovariation();
```

### 单峰优化

```cpp
#include "unimodal.h"

TVector<double> values = {1.0, 3.0, 2.0, 4.0, 1.0};

// 使用默认参数进行单峰化
double error = MakeUnimodal(values);

// 使用自定义参数
TOptimizationParams params;
params.IterationsCount = 500;
params.OptimizationShrinkage = 0.01;
error = MakeUnimodal(values, params);
```

### 模型序列化

```cpp
TLinearModel model({1.5, -0.5}, 2.0);  // 系数 [1.5, -0.5]，截距 2.0

// 序列化到字符串
TString serialized = SerializeToString(model);

// 反序列化
TLinearModel restored;
DeserializeFromString(serialized, restored);
```

## 应用场景

### 1. 机器学习

- **特征工程**: 分析特征与目标变量的线性关系
- **模型基线**: 作为更复杂模型的基准对比
- **特征选择**: 通过系数评估特征重要性
- **集成学习**: 作为集成模型的基础组件

### 2. 数据分析

- **趋势分析**: 分析时间序列数据的发展趋势
- **相关性研究**: 研究变量间的线性关系
- **预测建模**: 基于历史数据进行未来预测
- **异常检测**: 识别偏离线性模式的异常点

### 3. 金融分析

- **风险建模**: 评估投资组合的风险暴露
- **收益预测**: 预测股票或基金的收益
- **因子模型**: 构建多因子定价模型
- **套利策略**: 发现价格偏离均衡的机会

### 4. 工程应用

- **质量控制**: 分析工艺参数与产品质量的关系
- **设备维护**: 预测设备故障和维护需求
- **性能优化**: 分析系统参数与性能指标的关系
- **资源规划**: 预测资源需求和分配策略

### 5. 科学研究

- **实验分析**: 分析实验变量与结果的线性关系
- **数据拟合**: 对实验数据进行线性拟合
- **参数估计**: 估计科学模型的未知参数
- **验证理论**: 检验理论预测与实验数据的一致性

## 技术特点

### 性能优势

1. **高效算法**: 优化的线性代数实现
2. **数值稳定**: 使用 Kahan 累加器避免精度损失
3. **增量更新**: 支持在线学习，动态添加数据
4. **内存优化**: 紧凑的数据结构设计

### 功能特性

1. **多求解器**: 提供不同场景的优化求解方案
2. **加权支持**: 支持样本权重的不均衡数据处理
3. **正则化**: 防止过拟合的 L2 正则化
4. **统计工具**: 完整的统计分析功能

### 易用性

1. **简洁接口**: 直观的 API 设计
2. **类型安全**: 强类型模板设计
3. **文档完善**: 详细的接口说明
4. **示例丰富**: 提供多种使用场景示例

## 算法复杂度

- **时间复杂度**: O(n×m²)，其中 n 是样本数，m 是特征数
- **空间复杂度**: O(m²)，主要是协方差矩阵存储
- **增量更新**: O(m²) 每次添加新样本

## 数值精度

- 使用 Kahan 累加器保证 15+ 位有效数字精度
- 支持双精度浮点数计算
- 针对大规模数据优化数值稳定性

## 扩展性

1. **模块化设计**: 各组件独立，便于扩展
2. **模板支持**: 支持自定义数据类型
3. **插件架构**: 易于添加新的求解器
4. **标准接口**: 与其他机器学习库兼容