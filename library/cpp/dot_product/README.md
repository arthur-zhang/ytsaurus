# 点积（Dot Product）库

向量的点积（内积或标量积）计算库。

## 概述

该库提供了 `DotProduct` 函数，用于计算各种类型向量的点积。与简单的循环实现相比，该库使用 SSE 指令集，能够显著提升计算性能。

## 核心特性

### 高性能计算
- 使用 SSE 和 AVX2 指令集优化
- 支持多种数据类型的高效计算
- 比传统循环实现快数倍

### 数据类型支持
- **i8**: 8位有符号整数
- **ui8**: 8位无符号整数
- **i32**: 32位有符号整数
- **float**: 单精度浮点数
- **double**: 双精度浮点数

### 特殊功能
- **L2NormSquared**: 计算向量的 L2 范数平方
- **TriWayDotProduct**: 一次性计算三个点积（L·L、L·R、R·R）
- **ComputeMask**: 灵活控制计算哪些部分

## 主要组件

### 基础函数
```cpp
// 点积计算
i32 DotProduct(const i8* lhs, const i8* rhs, size_t length) noexcept;
ui32 DotProduct(const ui8* lhs, const ui8* rhs, size_t length) noexcept;
i64 DotProduct(const i32* lhs, const i32* rhs, size_t length) noexcept;
float DotProduct(const float* lhs, const float* rhs, size_t length) noexcept;
double DotProduct(const double* lhs, const double* rhs, size_t length) noexcept;

// L2 范数平方
float L2NormSquared(const float* v, size_t length) noexcept;
```

### 三重点积
```cpp
enum class ETriWayDotProductComputeMask: unsigned {
    LL = 0b100,   // 计算 L·L
    LR = 0b010,   // 计算 L·R
    RR = 0b001,   // 计算 R·R
    All = 0b111,  // 计算全部
    Left = 0b110, // 跳过 R·R
    Right = 0b011 // 跳过 L·L
};

TTriWayDotProduct<float> TriWayDotProduct(
    const float* lhs, const float* rhs,
    size_t length, ETriWayDotProductComputeMask mask) noexcept;
```

### 配置控制
```cpp
namespace NDotProduct {
    void DisableAvx2();  // 禁用 AVX2 优化
}
```

## 使用示例

### 替换传统循环
```cpp
// 传统实现
float dot_product = 0.0f;
for (int i = 0; i < len; i++) {
    dot_product += a[i] * b[i];
}

// 使用点积库
float dot_product = DotProduct(a, b, len);
```

### 三重点积计算
```cpp
auto result = TriWayDotProduct(lhs, rhs, length, ETriWayDotProductComputeMask::All);
// result.LL = L·L
// result.LR = L·R
// result.RR = R·R
```

### 模板参数使用
```cpp
template<typename T>
void processVectors(const T* a, const T* b, size_t n) {
    NDotProduct::TDotProduct<T> dotProduct;
    auto result = dotProduct(a, b, n);
    // 处理结果...
}
```

## 实现架构

### 优化层级
1. **AVX2 实现**: 最先进的向量指令优化
2. **SSE 实现**: 通用的向量指令优化
3. **简单实现**: 不支持向量指令时的回退实现

### 自动选择
库会根据 CPU 支持的指令集自动选择最优实现：
- 检测 CPU 是否支持 AVX2
- 回退到 SSE 实现
- 最后使用简单的循环实现

## 性能优势

### 基准测试
根据内置基准测试，相比传统循环实现：
- **SSE 优化**: 2-4倍性能提升
- **AVX2 优化**: 4-8倍性能提升
- **数据类型**: 浮点数类型提升最明显

### 优化原理
- **向量化**: 同时处理多个数据元素
- **内存访问优化**: 减少内存加载次数
- **CPU 流水线**: 充分利用 CPU 流水线执行

## 应用场景

### 机器学习
- 向量相似度计算
- 神经网络前向传播
- 特征向量内积

### 信号处理
- 滤波器计算
- 相关性分析
- 频谱分析

### 科学计算
- 物理模拟
- 数值分析
- 统计计算

### 图像处理
- 图像卷积
- 模板匹配
- 特征检测

## 技术细节

### 编译器支持
- 支持 GCC、Clang、MSVC
- 使用编译器内建函数
- 自动内联优化

### 内存对齐
- 库不要求特定的内存对齐
- 自动处理边界情况
- 保持数值精度

### 线程安全
- 所有函数都是纯函数
- 无全局状态修改
- 支持并发调用

## 注意事项

1. **数据长度**: 长度参数应与实际数组长度一致
2. **指针有效性**: 确保传入的指针有效且内存可访问
3. **数值溢出**: 整数类型需要注意溢出问题
4. **精度损失**: 浮点计算可能有精度损失

## 构建和依赖

- 无外部依赖
- 支持多种 CPU 架构（x86、x86-64、ARM）
- 兼容 C++17 标准