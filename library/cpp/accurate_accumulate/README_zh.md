# accurate_accumulate - 高精度浮点数累加库

## 概述

accurate_accumulate 是一个专门用于浮点数高精度累加的 C++ 库，实现了 Kahan 求和算法以及其他优化算法，显著提高了浮点数累加的精度，特别适合处理大量浮点数求和的场景。

## 核心功能

### 1. Kahan 求和算法

实现了经典的 Kahan 求和算法，通过补偿机制减少浮点数累加过程中的精度损失：
- 使用补偿项（Compensation）跟踪每次运算的误差
- 显著提高累加精度，特别是对于大量小数或大小差异很大的数值累加
- 支持所有基本的算术运算（+、-、*、/）

### 2. 优化的快速累加

提供了多种优化的累加方法：
- **普通累加**：标准的累加方法
- **快速累加**：使用循环展开（16个元素一组）提高性能
- **Kahan 累加**：结合 Kahan 算法和循环展开
- **内积计算**：支持两个向量的内积计算，同样提供普通和 Kahan 两种模式

## 文件说明

### accurate_accumulate.h
主要头文件，包含所有类和函数定义：
- `TKahanAccumulator<T>`：Kahan 累加器模板类
- `TypedFastAccumulate`：类型化的快速累加函数
- `TypedFastInnerProduct`：类型化的快速内积计算
- 各种便利函数如 `FastAccumulate`、`FastKahanAccumulate` 等

### accurate_accumulate.cpp
源文件，目前仅包含头文件引入。

## 使用示例

### 基本使用

```cpp
#include "accurate_accumulate.h"

// 创建 Kahan 累加器
TKahanAccumulator<double> acc(0.0);

// 添加数值
acc += 0.1;
acc += 0.2;
acc += 0.3;

// 获取结果
double result = acc.Get(); // 0.6000000000000001 (比普通累加更精确)
```

### 向量累加

```cpp
#include <vector>
#include "accurate_accumulate.h"

std::vector<double> data = {0.1, 0.2, 0.3, 0.4, 0.5};

// 普通快速累加
double sum1 = FastAccumulate(data);

// Kahan 快速累加（更精确）
double sum2 = FastKahanAccumulate(data);
```

### 向量内积

```cpp
std::vector<double> v1 = {1.0, 2.0, 3.0};
std::vector<double> v2 = {4.0, 5.0, 6.0};

// 普通内积
double dot1 = FastInnerProduct(v1, v2); // 32.0

// Kahan 内积（更精确）
double dot2 = FastKahanInnerProduct(v1, v2);
```

## 实现原理

### Kahan 求和算法

Kahan 算法通过以下步骤减少精度损失：
1. 计算要添加的值减去补偿项得到修正后的值
2. 将修正后的值加到累加和中
3. 计算新的补偿项（实际的加法结果减去理论结果）

### 性能优化

- **循环展开**：每次处理16个元素，减少循环开销
- **向量化友好**：代码结构有利于编译器向量化优化
- **模板化设计**：支持不同的浮点类型（float、double等）

## 应用场景

1. **科学计算**：处理大量浮点数的累加运算
2. **机器学习**：向量运算、梯度计算等
3. **统计分析**：计算平均值、方差等统计量
4. **数值模拟**：物理仿真、工程计算等
5. **金融计算**：需要高精度的数值累加

## 性能特征

- **精度**：Kahan 算法显著提高累加精度
- **性能**：循环展开的快速版本性能接近普通累加
- **空间**：仅需额外存储一个补偿项，空间开销很小
- **通用性**：支持所有标准浮点类型

## 注意事项

1. 虽然 Kahan 算法能显著提高精度，但不是绝对的精确
2. 对于极大量级的数值差异，仍可能存在精度问题
3. 并行计算时需要注意 Kahan 算法的顺序依赖性