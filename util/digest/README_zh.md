# 哈希摘要库

本模块提供多种哈希算法实现，包括 City Hash、Murmur Hash、FNV 等高性能哈希函数。

## 功能特性

### 哈希算法支持
- **City Hash** - Google 开发的高性能哈希算法
- **Murmur Hash** - 非加密型哈希函数
- **FNV** - 简单的哈希算法
- **组合哈希** - 多种算法组合使用

### 流式处理
- 支持流式哈希计算
- 增量更新哈希值
- 大文件分块处理

### 多平台优化
- 针对不同 CPU 架构优化
- SIMD 指令集支持
- 缓存友好的实现

## 主要组件

### 核心算法
- **city.h/cpp** - City Hash 算法实现
- **murmur.h/cpp** - Murmur Hash 算法
- **fnv.h/cpp** - FNV 哈希算法
- **multi.h/cpp** - 组合哈希算法

### 流式接口
- **city_streaming.h** - City Hash 流式接口
- **numeric.h/cpp** - 数值哈希

### 性能测试
- **benchmark/** - 性能基准测试

## 使用方法

### City Hash
```cpp
#include "util/digest/city.h"

// 64位哈希
uint64_t hash64 = CityHash64(data, length);

// 128位哈希
uint128_t hash128 = CityHash128(data, length);

// 带种子的哈希
uint64_t hashSeeded = CityHash64WithSeed(data, length, seed);

// 带两个种子的哈希
uint64_t hashDoubleSeeded = CityHash64WithSeeds(
    data, length, seed1, seed2);
```

### Murmur Hash
```cpp
#include "util/digest/murmur.h"

// MurmurHash2
uint32_t hash32 = MurmurHash2(data, length, seed);

// MurmurHash64A (64位平台)
uint64_t hash64a = MurmurHash64A(data, length, seed);

// MurmurHash64B (32位平台)
uint64_t hash64b = MurmurHash64B(data, length, seed);

// MurmurHash2A (改进版本)
uint32_t hash2a = MurmurHash2A(data, length, seed);
```

### FNV 哈希
```cpp
#include "util/digest/fnv.h"

// FNV-1 32位
uint32_t fnv1_32 = FNV1a32(data, length, seed);

// FNV-1 64位
uint64_t fnv1_64 = FNV1a64(data, length, seed);
```

### 组合哈希
```cpp
#include "util/digest/multi.h"

// 组合多个哈希值
uint64_t combined = CombineHashes(hash1, hash2, hash3);

// 哈希范围
uint64_t rangeHash = HashRange(begin, end);
```

### 流式哈希
```cpp
#include "util/digest/city_streaming.h"

// 创建流式哈希器
TCityHash64 hasher;

// 更新数据
hasher.Update(data1, length1);
hasher.Update(data2, length2);

// 获取结果
uint64_t result = hasher.Digest();
```

## 性能特性

### 性能指标
- **CityHash64**: ~10 GB/s
- **CityHash128**: ~8 GB/s
- **MurmurHash**: ~12 GB/s
- **FNV**: ~4 GB/s

### 优化策略
- 字节级处理优化
- 分支预测优化
- 缓存行对齐
- SIMD 指令使用（如果可用）

## 哈希算法选择

### 使用场景
- **City Hash**: 通用场景，性能优秀
- **Murmur Hash**: 需要更好的分布性
- **FNV**: 简单快速，适用于小型数据
- **组合哈希**: 需要更强抗碰撞性

### 特性对比

| 算法 | 速度 | 分布性 | 碰撞率 | 适用场景 |
|------|------|--------|--------|----------|
| CityHash64 | 极快 | 优秀 | 低 | 通用哈希表 |
| CityHash128 | 快 | 极优秀 | 极低 | 大规模数据 |
| MurmurHash | 极快 | 优秀 | 低 | 分布式系统 |
| FNV | 快 | 一般 | 中等 | 简单场景 |

## 基准测试

### 运行基准测试
```bash
cd util/digest/benchmark

# 运行所有基准测试
python run_all.py

# 运行特定算法
python run_all.py --algorithm cityhash

# 生成性能报告
python run_all.py --report > performance_report.txt
```

### 自定义测试
```cpp
// 基准测试示例
void BenchmarkHash() {
    const size_t dataSize = 1024 * 1024;  // 1MB
    std::vector<char> data(dataSize);

    // 填充随机数据
    FillRandom(data);

    // 计时开始
    auto start = std::chrono::high_resolution_clock::now();

    // 运行哈希算法
    uint64_t hash = CityHash64(data.data(), dataSize);

    // 计时结束
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(end - start);

    // 计算吞吐量
    double throughput = dataSize * 1e9 / duration.count() / (1024.0 * 1024.0);
    std::cout << "Throughput: " << throughput << " MB/s" << std::endl;
}
```

## 测试

### 单元测试
```bash
# 运行所有测试
./ut/digest_ut

# 运行特定算法测试
./ut/digest_ut --gtest_filter="CityHashTest.*"
```

### 测试向量
```cpp
// 已知的测试向量
ASSERT_EQ(CityHash64("", 0), 0x9ae16a3b2f90404fULL);
ASSERT_EQ(CityHash64("hello", 5), 0xaf63dc4c8601ec8cULL);
```

## 最佳实践

1. **哈希选择**
   - 通用场景使用 CityHash64
   - 需要更高质量使用 CityHash128
   - 注意哈希值的分布均匀性

2. **性能优化**
   - 批量处理数据
   - 重用哈希器对象
   - 使用 SIMD 优化版本

3. **碰撞处理**
   - 实现合适的冲突解决策略
   - 使用二次哈希技术
   - 考虑使用布隆过滤器

## 高级用法

### 自定义哈希函数
```cpp
// 实现自定义哈希器
template<typename T>
class CustomHasher {
public:
    uint64_t operator()(const T& value) const {
        return CityHash64(reinterpret_cast<const char*>(&value),
                         sizeof(value));
    }
};
```

### 哈希表集成
```cpp
// 与标准库容器配合使用
std::unordered_map<std::string, int, CityHashHash> myMap;

// 自定义键类型
struct MyKey {
    std::string name;
    int id;

    bool operator==(const MyKey& other) const {
        return name == other.name && id == other.id;
    }
};

struct MyKeyHash {
    size_t operator()(const MyKey& key) const {
        return CombineHashes(
            CityHash64(key.name.data(), key.name.size()),
            static_cast<uint64_t>(key.id));
    }
};
```

## 依赖项

- 标准 C++ 库
- C++11 或更高版本
- 无外部依赖

## 平台支持

- Linux (x86_64, ARM64)
- macOS (x86_64, ARM64)
- Windows (x86_64)

## 版本历史

- v3.0: 添加流式接口
- v2.5: 性能优化
- v2.0: 重构 API
- v1.0: 初始版本