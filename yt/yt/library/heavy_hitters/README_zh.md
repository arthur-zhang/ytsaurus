# Heavy Hitters (高频元素检测)

## 项目概述

Heavy Hitters 模块实现了基于 Misra-Gries 算法的高频元素检测功能。该模块用于在数据流中识别出现频率超过特定阈值的元素，适用于实时监控、异常检测和统计分析等场景。

## 核心功能

### Misra-Gries 算法实现
- **流式处理**: 支持连续数据流的高频元素检测
- **时间窗口**: 可配置的时间窗口长度，支持滑动窗口统计
- **阈值设置**: 灵活的频率阈值配置，支持百分比和绝对数量
- **权重支持**: 支持带权重元素的统计
- **内存优化**: 使用有限的内存空间跟踪大量候选元素

### 主要特性
- **实时统计**: 提供实时的元素频率统计信息
- **动态配置**: 支持运行时重新配置算法参数
- **线程安全**: 内置线程锁，支持多线程并发访问
- **自动清理**: 自动清理过期数据和低频元素
- **统计信息**: 提供详细的统计信息和性能指标

## 主要接口

### 核心类：TMisraGriesHeavyHitters

```cpp
template <class TKey>
class TMisraGriesHeavyHitters : public TRefCounted
```

#### 构造函数

```cpp
// 使用参数直接构造
TMisraGriesHeavyHitters(double threshold, TDuration window, i64 defaultLimit);

// 使用配置对象构造
explicit TMisraGriesHeavyHitters(const TMisraGriesHeavyHittersConfigPtr config);
```

#### 主要方法

```cpp
// 注册多个元素
void Register(const std::vector<TKey>& keys, TInstant now);

// 注册带权重的多个元素
void RegisterWeighted(const std::vector<std::pair<TKey, double>>& weightedKeys, TInstant now);

// 重新配置算法参数
void Reconfigure(const TMisraGriesHeavyHittersConfigPtr newConfig);

// 获取统计信息
TStatistics GetStatistics(TInstant now, std::optional<i64> limit = {}) const;
```

#### 统计信息结构

```cpp
struct TStatistics
{
    double Total = 0;                                    // 总计数
    THashMap<TKey, double> Fractions;                    // 各元素的比例
};
```

### 配置结构：TMisraGriesHeavyHittersConfig

```cpp
struct TMisraGriesHeavyHittersConfig : public NYTree::TYsonStruct
{
    bool Enable;           // 是否启用高频元素检测
    TDuration Window;      // 时间窗口长度
    double Threshold;      // 频率阈值
    i64 DefaultLimit;      // 默认返回结果数量限制
};
```

## 使用方法

### 基本使用示例

```cpp
#include <yt/yt/library/heavy_hitters/public.h>
#include <yt/yt/library/heavy_hitters/misra_gries.h>

using namespace NYT;

// 创建配置
auto config = New<TMisraGriesHeavyHittersConfig>();
config->Enable = true;
config->Window = TDuration::Minutes(5);
config->Threshold = 0.1;  // 10% 阈值
config->DefaultLimit = 100;

// 创建高频元素检测器
auto heavyHitters = New<TMisraGriesHeavyHitters<TString>>(config);

// 注册元素
std::vector<TString> keys = {"apple", "banana", "apple", "orange", "apple"};
heavyHitters->Register(keys, TInstant::Now());

// 获取统计信息
auto stats = heavyHitters->GetStatistics(TInstant::Now());
for (const auto& [key, fraction] : stats.Fractions) {
    Cout << key << ": " << fraction << Endl;
}
```

### 带权重使用示例

```cpp
// 注册带权重的元素
std::vector<std::pair<TString, double>> weightedKeys = {
    {"apple", 5.0},
    {"banana", 2.0},
    {"orange", 1.0}
};
heavyHitters->RegisterWeighted(weightedKeys, TInstant::Now());
```

### 动态配置示例

```cpp
// 创建新配置
auto newConfig = New<TMisraGriesHeavyHittersConfig>();
newConfig->Enable = true;
newConfig->Window = TDuration::Minutes(10);  // 延长时间窗口
newConfig->Threshold = 0.05;                 // 降低阈值
newConfig->DefaultLimit = 200;

// 动态重新配置
heavyHitters->Reconfigure(newConfig);
```

## 配置说明

### 关键参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| Enable | bool | false | 是否启用高频元素检测 |
| Window | TDuration | - | 统计时间窗口长度 |
| Threshold | double | - | 频率阈值 (0.0-1.0) |
| DefaultLimit | i64 | - | 默认返回结果数量限制 |

### 配置建议

- **时间窗口选择**: 根据业务场景选择合适的时间窗口，通常建议 1-60 分钟
- **阈值设置**:
  - 严格检测: 0.01-0.05 (1%-5%)
  - 适中检测: 0.05-0.15 (5%-15%)
  - 宽松检测: 0.15-0.30 (15%-30%)
- **内存限制**: DefaultLimit 控制返回结果数量，避免内存过度使用

## 性能考虑

### 时间复杂度
- **注册操作**: O(1) 平均时间复杂度
- **统计查询**: O(k log k)，其中 k 为候选元素数量
- **配置更新**: O(1)

### 空间复杂度
- **内存使用**: O(k)，其中 k 为候选元素数量
- **最大候选数量**: 受 DefaultLimit 和内存限制约束

### 性能优化建议

1. **合理设置阈值**: 过低的阈值会导致大量候选元素，影响性能
2. **适当的时间窗口**: 平衡统计准确性和内存使用
3. **批量操作**: 使用 Register 和 RegisterWeighted 批量处理元素
4. **定期清理**: 系统会自动清理过期数据，无需手动干预

## 最佳实践

### 1. 使用场景
- **实时监控**: 监控系统日志中的错误关键词
- **用户行为分析**: 识别高频访问的资源或操作
- **异常检测**: 检测流量异常 spikes
- **负载均衡**: 识别热点数据分布

### 2. 集成建议
```cpp
// 在监控系统中集成
class MetricsCollector {
public:
    MetricsCollector() {
        auto config = New<TMisraGriesHeavyHittersConfig>();
        config->Enable = true;
        config->Window = TDuration::Minutes(5);
        config->Threshold = 0.1;
        config->DefaultLimit = 50;

        heavyHitters_ = New<TMisraGriesHeavyHitters<TString>>(config);
    }

    void RecordMetric(const TString& metricName) {
        heavyHitters_->Register({metricName}, TInstant::Now());
    }

    std::vector<TString> GetHotMetrics() {
        auto stats = heavyHitters_->GetStatistics(TInstant::Now());
        std::vector<TString> hotMetrics;
        for (const auto& [name, fraction] : stats.Fractions) {
            if (fraction >= 0.1) {  // 过滤阈值
                hotMetrics.push_back(name);
            }
        }
        return hotMetrics;
    }

private:
    TMisraGriesHeavyHitters<TString>::TPtr heavyHitters_;
};
```

### 3. 错误处理
```cpp
try {
    auto stats = heavyHitters->GetStatistics(TInstant::Now());
    // 处理统计结果
} catch (const std::exception& e) {
    // 记录错误并处理
    Cerr << "Failed to get heavy hitters statistics: " << e.what() << Endl;
}
```

## 依赖项

- **YT Core**: 基础数据结构和并发支持
- **YT YTree**: 配置管理和序列化
- **Standard Library**: STL 容器和算法

## 注意事项

### 1. 算法特性
- Misra-Gries 算法是近似算法，可能存在假阳性
- 频率估计值可能略高于实际值
- 算法保证频率超过阈值的元素都会被检测到

### 2. 内存管理
- 系统会自动清理过期数据，但建议合理设置窗口大小
- 大量候选元素可能导致内存压力，需要监控内存使用情况

### 3. 线程安全
- 所有公共方法都是线程安全的
- 内部使用自旋锁保证并发访问的正确性
- 高并发场景下可能存在性能影响

### 4. 时钟同步
- 建议使用统一的时钟源
- 时间戳准确性影响统计结果的正确性

### 5. 数据类型限制
- 键类型必须是可哈希的 (std::hash)
- 支持任意可拷贝的键类型
- 权重值必须为非负数