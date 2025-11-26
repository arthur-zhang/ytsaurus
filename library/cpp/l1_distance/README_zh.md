# L1 距离计算库

## 项目概述

L1 距离计算库提供了高性能的向量 L1 距离（曼哈顿距离）计算功能。与简单的循环实现相比，该库利用 SSE（Streaming SIMD Extensions）指令集进行优化，显著提升了计算性能。L1 距离定义为两个向量对应元素绝对差之和。

## 核心功能

### 高性能计算
- **SSE 优化**：利用 SIMD 指令并行计算多个元素
- **内存对齐**：自动处理内存对齐以提高访问效率
- **循环展开**：减少循环开销，提高指令级并行度
- **类型特化**：针对不同数据类型的专门优化

### 支持的数据类型
- **整数类型**：i8, ui8, i32, ui32
- **浮点类型**：float, double
- **特化处理**：4位无符号整数的特殊优化

### 灵活的接口
- **快速版本**：使用 SSE 优化的高性能版本
- **慢速版本**：不使用 SSE 的通用版本
- **模板包装器**：支持模板参数传递

## L1 距离公式

L1 距离（曼哈顿距离）的计算公式：
```
L1(a, b) = Σ|a[i] - b[i]|
```

## 主要函数

### 基础 L1 距离函数

```cpp
#include <library/cpp/l1_distance/l1_distance.h>

// 8位有符号整数向量
ui32 L1Distance(const i8* lhs, const i8* rhs, int length);

// 8位无符号整数向量
ui32 L1Distance(const ui8* lhs, const ui8* rhs, int length);

// 32位有符号整数向量
ui64 L1Distance(const i32* lhs, const i32* rhs, int length);

// 32位无符号整数向量
ui64 L1Distance(const ui32* lhs, const ui32* rhs, int length);

// 单精度浮点数向量
float L1Distance(const float* lhs, const float* rhs, int length);

// 双精度浮点数向量
double L1Distance(const double* lhs, const double* rhs, int length);
```

### 特殊函数

```cpp
// 4位无符号整数（每个字节包含两个4位数）
ui32 L1DistanceUI4(const ui8* lhs, const ui8* rhs, int lengthInBytes);

// 不使用 SSE 的慢速版本（用于对比）
ui32 L1DistanceSlow(const ui8* lhs, const ui8* rhs, int length);
float L1DistanceSlow(const float* lhs, const float* rhs, int length);
// ... 其他类型的慢速版本
```

## 使用示例

### 基本用法

```cpp
#include <library/cpp/l1_distance/l1_distance.h>
#include <vector>
#include <iostream>

void BasicExample() {
    // 8位整数向量的 L1 距离
    std::vector<i8> a = {1, 2, 3, 4, 5};
    std::vector<i8> b = {2, 1, 4, 3, 6};

    ui32 distance = L1Distance(a.data(), b.data(), a.size());
    std::cout << "L1 distance: " << distance << std::endl;
    // 输出：L1 distance: 4
    // 计算：|1-2| + |2-1| + |3-4| + |4-3| + |5-6| = 1 + 1 + 1 + 1 + 1 = 5
}
```

### 浮点数向量

```cpp
void FloatExample() {
    std::vector<float> vector1 = {1.0f, 2.5f, -3.2f, 4.7f};
    std::vector<float> vector2 = {2.0f, 1.5f, -3.2f, 5.0f};

    float distance = L1Distance(vector1.data(), vector2.data(), vector1.size());
    std::cout << "Float L1 distance: " << distance << std::endl;
    // 输出：Float L1 distance: 3.3
}
```

### 大规模数据处理

```cpp
void LargeScaleExample() {
    const int size = 1000000;  // 100万个元素

    // 生成随机数据
    std::vector<ui32> data1(size);
    std::vector<ui32> data2(size);

    // 填充随机数据...
    for (int i = 0; i < size; ++i) {
        data1[i] = rand();
        data2[i] = rand();
    }

    // 计算距离（SSE 优化版本）
    auto start = std::chrono::high_resolution_clock::now();
    ui64 distance = L1Distance(data1.data(), data2.data(), size);
    auto end = std::chrono::high_resolution_clock::now();

    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    std::cout << "Distance: " << distance << std::endl;
    std::cout << "Time: " << duration.count() << " ms" << std::endl;
}
```

### 模板使用

```cpp
void TemplateExample() {
    using namespace NL1Distance;

    // 使用模板包装器
    TL1Distance<float> l1Calculator;

    std::vector<float> a = {1.0f, 2.0f, 3.0f};
    std::vector<float> b = {1.5f, 2.5f, 2.5f};

    float distance = l1Calculator(a.data(), b.data(), a.size());
    std::cout << "Template L1 distance: " << distance << std::endl;
}

// 在其他模板中使用
template<typename T>
auto CalculateDistance(const std::vector<T>& a, const std::vector<T>& b) {
    TL1Distance<T> calculator;
    return calculator(a.data(), b.data(), a.size());
}
```

### 4位整数特例

```cpp
void UI4Example() {
    // 4位无符号整数（每个字节包含两个4位数）
    std::vector<ui8> packed1 = {0x12, 0x34, 0x56, 0x78};  // {1,2,3,4,5,6,7,8}
    std::vector<ui8> packed2 = {0x13, 0x35, 0x57, 0x79};  // {1,3,3,5,5,7,7,9}

    ui32 distance = L1DistanceUI4(packed1.data(), packed2.data(), packed1.size());
    std::cout << "4-bit L1 distance: " << distance << std::endl;
    // 计算：|1-1| + |2-3| + |3-3| + |4-5| + |5-5| + |6-7| + |7-7| + |8-9| = 6
}
```

## 性能优化

### SSE 优化详解

#### 8位整数优化
```cpp
// 使用 SSE 的 _mm_sad_epu8 指令计算绝对差和
__m128i a = _mm_loadu_si128((const __m128i*)lhs);
__m128i b = _mm_loadu_si128((const __m128i*)rhs);
__m128i sum = _mm_sad_epu8(a, b);  // 一次处理16个字节
```

#### 32位整数优化
```cpp
// 使用条件比较和位操作
__m128i mask = _mm_cmpgt_epi32(a, b);
__m128i diff = _mm_or_si128(
    _mm_and_si128(mask, _mm_sub_epi32(a, b)),
    _mm_andnot_si128(mask, _mm_sub_epi32(b, a))
);
```

#### 浮点数优化
```cpp
// 使用掩码实现绝对值
__m128 absMask = _mm_castsi128_ps(_mm_set1_epi32(0x7fffffff));
__m128 diff = _mm_sub_ps(a, b);
__m128 absDiff = _mm_and_ps(diff, absMask);
```

### 内存访问优化

```cpp
// 检查内存对齐，选择最优加载方式
if ((reinterpret_cast<uintptr_t>(lhs) & 0x0f) || (reinterpret_cast<uintptr_t>(rhs) & 0x0f)) {
    // 非对齐内存，使用 _mm_loadu_si128
    for (int i = 0; i < l16; i += 16) {
        __m128i a = _mm_loadu_si128((const __m128i*)(&lhs[i]));
        __m128i b = _mm_loadu_si128((const __m128i*)(&rhs[i]));
        // ...
    }
} else {
    // 对齐内存，使用直接加载
    for (int i = 0; i < l16; i += 16) {
        __m128i a = *(const __m128i*)(&lhs[i]);
        __m128i b = *(const __m128i*)(&rhs[i]);
        // ...
    }
}
```

### 循环展开

```cpp
// 展开循环减少分支预测失败
template <typename Result, typename Number>
inline Result L1DistanceImpl4(const Number* lhs, const Number* rhs, int length) {
    Result s0 = 0, s1 = 0, s2 = 0, s3 = 0;

    while (length >= 4) {
        s0 += AbsDelta(lhs[0], rhs[0]);
        s1 += AbsDelta(lhs[1], rhs[1]);
        s2 += AbsDelta(lhs[2], rhs[2]);
        s3 += AbsDelta(lhs[3], rhs[3]);
        lhs += 4;
        rhs += 4;
        length -= 4;
    }

    // 处理剩余元素
    while (length--) {
        s0 += AbsDelta(*lhs++, *rhs++);
    }

    return s0 + s1 + s2 + s3;
}
```

## 性能基准

### 理论性能提升

| 数据类型 | 元素数量 | 原始实现 | SSE优化 | 加速比 |
|----------|----------|----------|---------|--------|
| ui8 | 1M | ~5ms | ~1ms | ~5x |
| i32 | 1M | ~8ms | ~2ms | ~4x |
| float | 1M | ~12ms | ~3ms | ~4x |
| double | 1M | ~15ms | ~5ms | ~3x |

### 实际测试代码

```cpp
#include <chrono>
#include <random>

void Benchmark() {
    const int N = 1000000;  // 100万个元素
    std::vector<ui8> a(N), b(N);

    // 填充随机数据
    std::mt19937 gen(42);
    std::uniform_int_distribution<> dis(0, 255);
    for (int i = 0; i < N; ++i) {
        a[i] = dis(gen);
        b[i] = dis(gen);
    }

    // 测试 SSE 优化版本
    auto start = std::chrono::high_resolution_clock::now();
    ui64 result1 = L1Distance(a.data(), b.data(), N);
    auto end = std::chrono::high_resolution_clock::now();
    auto sse_time = std::chrono::duration_cast<std::chrono::microseconds>(end - start);

    // 测试慢速版本
    start = std::chrono::high_resolution_clock::now();
    ui64 result2 = L1DistanceSlow(a.data(), b.data(), N);
    end = std::chrono::high_resolution_clock::now();
    auto slow_time = std::chrono::duration_cast<std::chrono::microseconds>(end - start);

    std::cout << "Results: " << result1 << " vs " << result2 << std::endl;
    std::cout << "SSE time: " << sse_time.count() << " μs" << std::endl;
    std::cout << "Slow time: " << slow_time.count() << " μs" << std::endl;
    std::cout << "Speedup: " << (double)slow_time.count() / sse_time.count() << "x" << std::endl;
}
```

## 应用场景

### 图像处理

```cpp
// 图像相似度计算
double CalculateImageSimilarity(const std::vector<ui8>& img1,
                               const std::vector<ui8>& img2) {
    if (img1.size() != img2.size()) {
        throw std::invalid_argument("Image sizes must match");
    }

    ui64 distance = L1Distance(img1.data(), img2.data(), img1.size());

    // 归一化到 [0, 1] 范围
    double maxDistance = img1.size() * 255.0;
    double similarity = 1.0 - (distance / maxDistance);

    return similarity;
}
```

### 机器学习

```cpp
// k-NN 算法中的距离计算
class KNNClassifier {
private:
    std::vector<std::vector<float>> training_data_;
    std::vector<int> labels_;

public:
    int Predict(const std::vector<float>& test_point, int k = 3) {
        std::vector<std::pair<float, int>> distances;

        // 计算到所有训练点的距离
        for (size_t i = 0; i < training_data_.size(); ++i) {
            float distance = L1Distance(test_point.data(),
                                      training_data_[i].data(),
                                      test_point.size());
            distances.emplace_back(distance, labels_[i]);
        }

        // 找到 k 个最近邻
        std::partial_sort(distances.begin(), distances.begin() + k, distances.end());

        // 投票
        std::map<int, int> votes;
        for (int i = 0; i < k; ++i) {
            votes[distances[i].second]++;
        }

        return std::max_element(votes.begin(), votes.end())->first;
    }
};
```

### 信号处理

```cpp
// 信号相似度分析
class SignalAnalyzer {
public:
    double CompareSignals(const std::vector<float>& signal1,
                         const std::vector<float>& signal2) {
        if (signal1.size() != signal2.size()) {
            throw std::invalid_argument("Signals must have same length");
        }

        float totalDistance = L1Distance(signal1.data(), signal2.data(), signal1.size());

        // 归一化
        float maxPossibleDistance = signal1.size() * 2.0f;  // 假设信号范围 [-1, 1]
        float similarity = 1.0f - (totalDistance / maxPossibleDistance);

        return similarity;
    }

    std::vector<float> FindSimilarSegments(const std::vector<float>& long_signal,
                                         const std::vector<float>& pattern,
                                         float threshold = 0.8) {
        std::vector<float> similarities;

        for (size_t i = 0; i + pattern.size() <= long_signal.size(); ++i) {
            std::vector<float> segment(long_signal.begin() + i,
                                     long_signal.begin() + i + pattern.size());

            float distance = L1Distance(segment.data(), pattern.data(), pattern.size());
            float similarity = 1.0f - (distance / (pattern.size() * 2.0f));

            similarities.push_back(similarity);
        }

        return similarities;
    }
};
```

### 数据压缩

```cpp
// 简单的差分编码
class DifferentialEncoder {
public:
    std::vector<ui8> Encode(const std::vector<ui8>& data) {
        if (data.empty()) return {};

        std::vector<ui8> encoded;
        encoded.reserve(data.size());

        encoded.push_back(data[0]);  // 第一个值直接存储

        for (size_t i = 1; i < data.size(); ++i) {
            ui8 diff = std::abs((int)data[i] - (int)data[i-1]);
            encoded.push_back(diff);
        }

        return encoded;
    }

    std::vector<ui8> Decode(const std::vector<ui8>& encoded) {
        if (encoded.empty()) return {};

        std::vector<ui8> decoded;
        decoded.reserve(encoded.size());

        decoded.push_back(encoded[0]);

        for (size_t i = 1; i < encoded.size(); ++i) {
            // 简化解码，实际应用中需要更多信息来恢复原始值
            decoded.push_back(encoded[i]);
        }

        return decoded;
    }

    // 计算压缩后的相似度
    double CalculateCompressionSimilarity(const std::vector<ui8>& original,
                                        const std::vector<ui8>& compressed) {
        if (original.size() != compressed.size()) {
            throw std::invalid_argument("Vectors must have same size");
        }

        ui64 distance = L1Distance(original.data(), compressed.data(), original.size());
        return 1.0 - (double)distance / (original.size() * 255.0);
    }
};
```

## 最佳实践

### 内存对齐

```cpp
// 确保内存对齐以获得最佳性能
class AlignedVector {
private:
    std::vector<float> data_;

public:
    AlignedVector(size_t size) {
        data_.resize(size + 16);  // 额外空间用于对齐
        size_t aligned = (reinterpret_cast<size_t>(data_.data()) + 15) & ~15;
        // 使用对齐的指针...
    }

    float* getAlignedData() {
        size_t aligned = (reinterpret_cast<size_t>(data_.data()) + 15) & ~15;
        return reinterpret_cast<float*>(aligned);
    }
};
```

### 批量处理

```cpp
// 批量处理多个距离计算
class BatchDistanceCalculator {
public:
    std::vector<ui64> CalculateDistances(
        const std::vector<std::vector<ui8>>& vectors,
        const std::vector<ui8>& query) {

        std::vector<ui64> distances;
        distances.reserve(vectors.size());

        for (const auto& vec : vectors) {
            if (vec.size() == query.size()) {
                ui64 dist = L1Distance(vec.data(), query.data(), vec.size());
                distances.push_back(dist);
            }
        }

        return distances;
    }
};
```

### 错误处理

```cpp
// 安全的 L1 距离计算
ui64 SafeL1Distance(const ui8* a, const ui8* b, int length) {
    if (!a || !b || length <= 0) {
        throw std::invalid_argument("Invalid input parameters");
    }

    try {
        return L1Distance(a, b, length);
    } catch (const std::exception& e) {
        // 回退到慢速版本
        return L1DistanceSlow(a, b, length);
    }
}
```

## 编译条件

该库根据编译时是否定义 `ARCADIA_SSE` 宏来选择实现：

- **启用 SSE**：`#define ARCADIA_SSE` - 使用 SIMD 优化版本
- **禁用 SSE**：未定义宏 - 使用通用版本

建议在支持 SSE 的平台上启用优化以获得最佳性能。