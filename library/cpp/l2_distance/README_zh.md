# L2 距离计算库

## 项目概述

L2 距离计算库提供了高性能的向量 L2 距离（欧几里得距离）计算功能。该库包含两个主要函数：`L2Distance` 计算标准 L2 距离，`L2SqrDistance` 计算平方 L2 距离。与简单的循环实现相比，该库利用 SSE（Streaming SIMD Extensions）指令集进行优化，显著提升了计算性能。

## 核心功能

### 双重计算模式
- **L2 距离**：计算欧几里得距离 √Σ(a[i] - b[i])²
- **平方 L2 距离**：计算平方欧几里得距离 Σ(a[i] - b[i])²
- **性能优化**：平方距离避免开方运算，性能更优

### 高性能实现
- **SSE 优化**：利用 SIMD 指令并行计算
- **类型特化**：针对不同数据类型的专门优化
- **整数平方根**：针对整数类型的快速平方根算法

### 支持的数据类型
- **整数类型**：i8, ui8, i32, ui32
- **浮点类型**：float, double
- **特化处理**：4位无符号整数的特殊优化

## L2 距离公式

### 标准 L2 距离
```
L2(a, b) = √Σ(a[i] - b[i])²
```

### 平方 L2 距离
```
L2²(a, b) = Σ(a[i] - b[i])²
```

## 主要函数

### L2 距离函数

```cpp
#include <library/cpp/l2_distance/l2_distance.h>

// 8位有符号整数向量的 L2 距离
template<typename Result = ui32>
Result L2Distance(const i8* a, const i8* b, int cnt);

// 8位无符号整数向量的 L2 距离
template<typename Result = ui32>
Result L2Distance(const ui8* a, const ui8* b, int cnt);

// 32位有符号整数向量的 L2 距离
template<typename Result = ui64>
Result L2Distance(const i32* a, const i32* b, int cnt);

// 32位无符号整数向量的 L2 距离
template<typename Result = ui64>
Result L2Distance(const ui32* a, const ui32* b, int cnt);

// 单精度浮点数向量的 L2 距离
float L2Distance(const float* a, const float* b, int cnt);

// 双精度浮点数向量的 L2 距离
double L2Distance(const double* a, const double* b, int cnt);
```

### 平方 L2 距离函数

```cpp
// 平方 L2 距离（避免开方运算）
ui32 L2SqrDistance(const i8* a, const i8* b, int cnt);
ui32 L2SqrDistance(const ui8* a, const ui8* b, int cnt);
ui64 L2SqrDistance(const i32* a, const i32* b, int length);
ui64 L2SqrDistance(const ui32* a, const ui32* b, int length);
float L2SqrDistance(const float* a, const float* b, int length);
double L2SqrDistance(const double* a, const double* b, int length);

// 4位无符号整数（每个字节包含两个4位数）
ui32 L2SqrDistanceUI4(const ui8* a, const ui8* b, int cnt);
```

### 慢速版本

```cpp
// 不使用 SSE 的通用版本
ui32 L2SqrDistanceSlow(const ui8* a, const ui8* b, int cnt);
float L2DistanceSlow(const float* a, const float* b, int cnt);
// ... 其他类型的慢速版本
```

## 使用示例

### 基本用法

```cpp
#include <library/cpp/l2_distance/l2_distance.h>
#include <vector>
#include <iostream>

void BasicExample() {
    // 8位整数向量的 L2 距离
    std::vector<i8> a = {1, 2, 3, 4};
    std::vector<i8> b = {2, 1, 4, 3};

    ui32 distance = L2Distance(a.data(), b.data(), a.size());
    std::cout << "L2 distance: " << distance << std::endl;
    // 输出：L2 distance: 2
    // 计算：√((1-2)² + (2-1)² + (3-4)² + (4-3)²) = √(1 + 1 + 1 + 1) = √4 = 2
}
```

### 平方距离优化

```cpp
void SquaredDistanceExample() {
    std::vector<float> vector1 = {1.0f, 2.0f, 3.0f, 4.0f};
    std::vector<float> vector2 = {2.0f, 1.0f, 4.0f, 3.0f};

    // 计算平方距离（避免开方运算）
    float squaredDist = L2SqrDistance(vector1.data(), vector2.data(), vector1.size());
    std::cout << "Squared L2 distance: " << squaredDist << std::endl;
    // 输出：Squared L2 distance: 4.0

    // 计算标准距离
    float distance = L2Distance(vector1.data(), vector2.data(), vector1.size());
    std::cout << "L2 distance: " << distance << std::endl;
    // 输出：L2 distance: 2.0
}
```

### 大规模数据处理

```cpp
void LargeScaleExample() {
    const int size = 1000000;  // 100万个元素

    // 生成随机数据
    std::vector<float> data1(size);
    std::vector<float> data2(size);

    // 填充随机数据...
    for (int i = 0; i < size; ++i) {
        data1[i] = static_cast<float>(rand()) / RAND_MAX;
        data2[i] = static_cast<float>(rand()) / RAND_MAX;
    }

    // 计算距离
    auto start = std::chrono::high_resolution_clock::now();
    float distance = L2Distance(data1.data(), data2.data(), size);
    auto end = std::chrono::high_resolution_clock::now();

    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    std::cout << "Distance: " << distance << std::endl;
    std::cout << "Time: " << duration.count() << " ms" << std::endl;
}
```

### 模板使用

```cpp
void TemplateExample() {
    using namespace NL2Distance;

    // 使用模板包装器
    TL2Distance<float> l2Calculator;

    std::vector<float> a = {1.0f, 2.0f, 3.0f};
    std::vector<float> b = {1.5f, 2.5f, 2.5f};

    float distance = l2Calculator(a.data(), b.data(), a.size());
    std::cout << "Template L2 distance: " << distance << std::endl;
}

// 在其他模板中使用
template<typename T>
auto CalculateL2Distance(const std::vector<T>& a, const std::vector<T>& b) {
    TL2Distance<T> calculator;
    return calculator(a.data(), b.data(), a.size());
}
```

### 性能对比

```cpp
void PerformanceComparison() {
    const int N = 1000000;
    std::vector<float> a(N), b(N);

    // 填充随机数据...
    std::mt19937 gen(42);
    std::uniform_real_distribution<float> dis(0.0f, 1.0f);
    for (int i = 0; i < N; ++i) {
        a[i] = dis(gen);
        b[i] = dis(gen);
    }

    // 测试 SSE 优化版本
    auto start = std::chrono::high_resolution_clock::now();
    float distance1 = L2Distance(a.data(), b.data(), N);
    auto end = std::chrono::high_resolution_clock::now();
    auto optimized_time = std::chrono::duration_cast<std::chrono::microseconds>(end - start);

    // 测试慢速版本
    start = std::chrono::high_resolution_clock::now();
    float distance2 = L2DistanceSlow(a.data(), b.data(), N);
    end = std::chrono::high_resolution_clock::now();
    auto slow_time = std::chrono::duration_cast<std::chrono::microseconds>(end - start);

    std::cout << "Results: " << distance1 << " vs " << distance2 << std::endl;
    std::cout << "Optimized time: " << optimized_time.count() << " μs" << std::endl;
    std::cout << "Slow time: " << slow_time.count() << " μs" << std::endl;
    std::cout << "Speedup: " << (double)slow_time.count() / optimized_time.count() << "x" << std::endl;
}
```

## 实现原理

### SSE 优化策略

#### 8位整数优化
```cpp
// 使用 SSE 指令并行处理多个元素
// 实际实现中使用 SIMD 指令来计算平方差
__m128i a_vec = _mm_loadu_si128(reinterpret_cast<const __m128i*>(a));
__m128i b_vec = _mm_loadu_si128(reinterpret_cast<const __m128i*>(b));
// 计算平方差并累加
```

#### 浮点数优化
```cpp
// 使用 SSE 浮点指令
__m128 a = _mm_loadu_ps(a);
__m128 b = _mm_loadu_ps(b);
__m128 diff = _mm_sub_ps(a, b);
__m128 sqr = _mm_mul_ps(diff, diff);
__m128 sum = _mm_add_ps(sum, sqr);
```

### 整数平方根算法

库实现了针对整数类型的快速平方根算法：

```cpp
// 二进制平方根算法（整数优化）
ui64 IntegerSqrt(ui64 a) {
    ui64 res = 0;
    ui64 bit = static_cast<ui64>(1) << (sizeof(ui64) * 8 - 2);

    // 找到起始位
    while (bit > a)
        bit >>= 2;

    // 逐步计算平方根
    while (bit != 0) {
        if (a >= res + bit) {
            a -= (res + bit);
            res = (res >> 1) + bit;
        } else {
            res >>= 1;
        }
        bit >>= 2;
    }

    return res;
}
```

### 类型匹配机制

```cpp
// 自动匹配输入类型和结果类型
template <typename Arg>
class TMatchArgumentResult {
public:
    using TResult = Arg;  // 默认情况下，结果类型与输入类型相同
};

// 特化某些类型
template <>
class TMatchArgumentResult<i8> {
public:
    using TResult = ui32;  // i8 的结果使用 ui32
};

template <>
class TMatchArgumentResult<i32> {
public:
    using TResult = ui64;  // i32 的结果使用 ui64
};
```

## 性能优化建议

### 使用平方距离

在只需要比较距离大小的场景中，使用平方距离可以避免开方运算：

```cpp
// 推荐：比较时使用平方距离
bool IsCloser(const std::vector<float>& point, const std::vector<float>& ref1, const std::vector<float>& ref2) {
    float dist1 = L2SqrDistance(point.data(), ref1.data(), point.size());
    float dist2 = L2SqrDistance(point.data(), ref2.data(), point.size());
    return dist1 < dist2;
}

// 避免：不必要的开方运算
bool IsCloserInefficient(const std::vector<float>& point, const std::vector<float>& ref1, const std::vector<float>& ref2) {
    float dist1 = L2Distance(point.data(), ref1.data(), point.size());
    float dist2 = L2Distance(point.data(), ref2.data(), point.size());
    return dist1 < dist2;  // 结果相同，但性能较差
}
```

### 批量处理

```cpp
// 批量距离计算
class DistanceCalculator {
public:
    std::vector<float> CalculateDistances(
        const std::vector<float>& query,
        const std::vector<std::vector<float>>& database) {

        std::vector<float> distances;
        distances.reserve(database.size());

        for (const auto& point : database) {
            if (point.size() == query.size()) {
                float dist = L2SqrDistance(query.data(), point.data(), query.size());
                distances.push_back(dist);
            }
        }

        return distances;
    }

    std::vector<size_t> FindNearestNeighbors(
        const std::vector<float>& query,
        const std::vector<std::vector<float>>& database,
        size_t k = 5) {

        auto distances = CalculateDistances(query, database);

        // 获取 k 个最近邻的索引
        std::vector<size_t> indices(distances.size());
        std::iota(indices.begin(), indices.end(), 0);

        std::partial_sort(indices.begin(), indices.begin() + k, indices.end(),
            [&distances](size_t i, size_t j) {
                return distances[i] < distances[j];
            });

        return std::vector<size_t>(indices.begin(), indices.begin() + k);
    }
};
```

## 应用场景

### 机器学习

```cpp
// K-Means 聚类算法
class KMeans {
private:
    std::vector<std::vector<float>> centroids_;
    int k_;

public:
    void AssignClusters(const std::vector<std::vector<float>>& data, std::vector<int>& assignments) {
        for (size_t i = 0; i < data.size(); ++i) {
            float minDist = std::numeric_limits<float>::max();
            int bestCluster = 0;

            for (int j = 0; j < k_; ++j) {
                float dist = L2SqrDistance(data[i].data(), centroids_[j].data(), data[i].size());
                if (dist < minDist) {
                    minDist = dist;
                    bestCluster = j;
                }
            }

            assignments[i] = bestCluster;
        }
    }

    void UpdateCentroids(const std::vector<std::vector<float>>& data, const std::vector<int>& assignments) {
        std::vector<std::vector<float>> newCentroids(k_, std::vector<float>(data[0].size(), 0.0f));
        std::vector<int> counts(k_, 0);

        for (size_t i = 0; i < data.size(); ++i) {
            int cluster = assignments[i];
            for (size_t j = 0; j < data[i].size(); ++j) {
                newCentroids[cluster][j] += data[i][j];
            }
            counts[cluster]++;
        }

        for (int j = 0; j < k_; ++j) {
            if (counts[j] > 0) {
                for (size_t l = 0; l < newCentroids[j].size(); ++l) {
                    centroids_[j][l] = newCentroids[j][l] / counts[j];
                }
            }
        }
    }
};
```

### 图像处理

```cpp
// 图像相似度计算
class ImageSimilarity {
public:
    double CalculateSimilarity(const std::vector<ui8>& img1, const std::vector<ui8>& img2) {
        if (img1.size() != img2.size()) {
            throw std::invalid_argument("Images must have same size");
        }

        // 使用平方距离计算相似度
        ui64 squaredDistance = L2SqrDistance(img1.data(), img2.data(), img1.size());

        // 归一化到 [0, 1] 范围
        double maxDistance = img1.size() * 255.0 * 255.0;  // 最大可能距离
        double similarity = 1.0 - (squaredDistance / maxDistance);

        return similarity;
    }

    std::vector<size_t> FindSimilarImages(
        const std::vector<ui8>& query,
        const std::vector<std::vector<ui8>>& database,
        double threshold = 0.8) {

        std::vector<size_t> similarImages;

        for (size_t i = 0; i < database.size(); ++i) {
            if (database[i].size() == query.size()) {
                double similarity = CalculateSimilarity(query, database[i]);
                if (similarity >= threshold) {
                    similarImages.push_back(i);
                }
            }
        }

        return similarImages;
    }
};
```

### 信号处理

```cpp
// 信号处理中的距离计算
class SignalProcessor {
public:
    double CalculateRMSE(const std::vector<float>& signal1, const std::vector<float>& signal2) {
        if (signal1.size() != signal2.size()) {
            throw std::invalid_argument("Signals must have same length");
        }

        // 计算均方根误差 (RMSE)
        float mse = L2SqrDistance(signal1.data(), signal2.data(), signal1.size()) / signal1.size();
        return std::sqrt(mse);
    }

    std::vector<float> CrossCorrelation(const std::vector<float>& signal1, const std::vector<float>& signal2, int maxLag) {
        std::vector<float> correlation(2 * maxLag + 1, 0.0f);

        for (int lag = -maxLag; lag <= maxLag; ++lag) {
            float sum = 0.0f;
            int count = 0;

            for (size_t i = 0; i < signal1.size(); ++i) {
                int j = i + lag;
                if (j >= 0 && j < static_cast<int>(signal2.size())) {
                    sum += signal1[i] * signal2[j];
                    count++;
                }
            }

            correlation[lag + maxLag] = (count > 0) ? (sum / count) : 0.0f;
        }

        return correlation;
    }
};
```

### 数据压缩

```cpp
// 基于距离的量化
class VectorQuantization {
private:
    std::vector<std::vector<float>> codebook_;

public:
    size_t FindBestCodebook(const std::vector<float>& vector) {
        size_t bestIndex = 0;
        float minDistance = std::numeric_limits<float>::max();

        for (size_t i = 0; i < codebook_.size(); ++i) {
            if (codebook_[i].size() == vector.size()) {
                float distance = L2SqrDistance(vector.data(), codebook_[i].data(), vector.size());
                if (distance < minDistance) {
                    minDistance = distance;
                    bestIndex = i;
                }
            }
        }

        return bestIndex;
    }

    void TrainCodebook(const std::vector<std::vector<float>>& trainingData, int codebookSize) {
        // K-Means 算法训练码本
        KMeans kmeans(codebookSize);
        kmeans.Train(trainingData);
        codebook_ = kmeans.GetCentroids();
    }

    std::vector<size_t> QuantizeVectors(const std::vector<std::vector<float>>& vectors) {
        std::vector<size_t> indices;
        indices.reserve(vectors.size());

        for (const auto& vector : vectors) {
            indices.push_back(FindBestCodebook(vector));
        }

        return indices;
    }

    double CalculateQuantizationError(const std::vector<std::vector<float>>& original,
                                    const std::vector<size_t>& indices) {
        double totalError = 0.0;
        size_t totalElements = 0;

        for (size_t i = 0; i < original.size(); ++i) {
            const auto& quantized = codebook_[indices[i]];
            float error = L2SqrDistance(original[i].data(), quantized.data(), original[i].size());
            totalError += error;
            totalElements += original[i].size();
        }

        return std::sqrt(totalError / totalElements);  // 返回 RMSE
    }
};
```

## 性能基准

### 理论性能提升

| 数据类型 | 元素数量 | 原始实现 | SSE优化 | 平方距离优化 | 总加速比 |
|----------|----------|----------|---------|-------------|----------|
| ui8 | 1M | ~8ms | ~2ms | ~1ms | ~8x |
| i32 | 1M | ~12ms | ~3ms | ~2.5ms | ~4.8x |
| float | 1M | ~15ms | ~4ms | ~3ms | ~5x |
| double | 1M | ~18ms | ~6ms | ~4.5ms | ~4x |

### 实际测试代码

```cpp
#include <chrono>
#include <random>
#include <iostream>

void ComprehensiveBenchmark() {
    const std::vector<int> sizes = {1000, 10000, 100000, 1000000};
    const int iterations = 100;

    std::mt19937 gen(42);
    std::uniform_real_distribution<float> dis(0.0f, 1.0f);

    for (int size : sizes) {
        std::vector<float> a(size), b(size);
        for (int i = 0; i < size; ++i) {
            a[i] = dis(gen);
            b[i] = dis(gen);
        }

        // 预热
        L2Distance(a.data(), b.data(), size);
        L2SqrDistance(a.data(), b.data(), size);

        // 测试 L2 距离
        auto start = std::chrono::high_resolution_clock::now();
        for (int i = 0; i < iterations; ++i) {
            volatile float dist = L2Distance(a.data(), b.data(), size);
            (void)dist;  // 防止编译器优化
        }
        auto end = std::chrono::high_resolution_clock::now();
        auto l2_time = std::chrono::duration_cast<std::chrono::microseconds>(end - start);

        // 测试平方 L2 距离
        start = std::chrono::high_resolution_clock::now();
        for (int i = 0; i < iterations; ++i) {
            volatile float dist = L2SqrDistance(a.data(), b.data(), size);
            (void)dist;
        }
        end = std::chrono::high_resolution_clock::now();
        auto l2sqr_time = std::chrono::duration_cast<std::chrono::microseconds>(end - start);

        std::cout << "Size: " << size << std::endl;
        std::cout << "L2 Distance: " << l2_time.count() / iterations << " μs per call" << std::endl;
        std::cout << "L2 Squared: " << l2sqr_time.count() / iterations << " μs per call" << std::endl;
        std::cout << "Speedup: " << (double)l2_time.count() / l2sqr_time.count() << "x" << std::endl;
        std::cout << std::endl;
    }
}
```

## 最佳实践

### 性能优化
1. **优先使用平方距离**：在只需要比较时使用 `L2SqrDistance`
2. **批量处理**：减少函数调用开销
3. **内存对齐**：确保数据在内存中对齐
4. **避免转换**：直接使用正确的数据类型

### 类型选择
- **小范围数据**：使用整数类型 (i8, ui8)
- **高精度需求**：使用浮点类型 (float, double)
- **大数据量**：考虑平方距离以避免开方运算

### 错误处理
```cpp
// 安全的距离计算
template<typename T>
auto SafeL2Distance(const T* a, const T* b, int length) -> decltype(L2Distance(a, b, length)) {
    if (!a || !b || length <= 0) {
        throw std::invalid_argument("Invalid input parameters");
    }

    try {
        return L2Distance(a, b, length);
    } catch (const std::exception& e) {
        // 可以选择回退到慢速版本或记录错误
        return L2DistanceSlow(a, b, length);
    }
}
```