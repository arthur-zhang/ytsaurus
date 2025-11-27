# Quantile Digest (分位数摘要)

Quantile Digest 是 YTsaurus 中用于计算数据分位数的算法库，主要实现了 TDigest 算法，提供了高效的数据流分位数估计功能。

## 概述

Quantile Digest 库提供以下核心功能：
- 数据流分位数计算
- TDigest 算法实现
- 内存高效的统计摘要
- 序列化和反序列化支持
- 可配置的压缩参数

## 核心组件

### 1. IQuantileDigest (分位数摘要接口)
```cpp
struct IQuantileDigest : public TRefCounted {
    // 添加值到摘要
    virtual void AddValue(double value) = 0;

    // 获取值的数量
    virtual i64 GetCount() const = 0;

    // 获取指定分位数的值
    virtual double GetQuantile(double quantile) = 0;

    // 获取值的排名（百分比）
    virtual double GetRank(double value) = 0;

    // 序列化摘要
    virtual TString Serialize() = 0;
};
```

### 2. TTDigestConfig (TDigest 配置)
```cpp
struct TTDigestConfig : public NYTree::TYsonStruct {
    // 压缩参数，控制精度和内存的平衡
    double Delta;

    // 压缩频率，控制何时触发压缩
    double CompressionFrequency;

    REGISTER_YSON_STRUCT(TTDigestConfig);

    static void Register(TRegistrar registrar);
};
```

## 使用方法

### 基本使用
```cpp
#include <yt/yt/library/quantile_digest/quantile_digest.h>

using namespace NYT;

// 创建 TDigest 配置
auto config = New<TTDigestConfig>();
config->SetDelta(100.0);              // 压缩参数
config->SetCompressionFrequency(0.1); // 10% 的数据量后触发压缩

// 创建分位数摘要
auto digest = CreateTDigest(config);

// 添加数据
std::vector<double> values = {1.0, 2.0, 3.0, 4.0, 5.0, 10.0, 20.0};
for (double value : values) {
    digest->AddValue(value);
}

// 获取分位数
double p50 = digest->GetQuantile(0.5);   // 中位数
double p95 = digest->GetQuantile(0.95); // 95分位数
double p99 = digest->GetQuantile(0.99); // 99分位数

std::cout << "50th percentile: " << p50 << std::endl;
std::cout << "95th percentile: " << p95 << std::endl;
std::cout << "99th percentile: " << p99 << std::endl;
```

### 流式数据处理
```cpp
class MetricsAggregator {
public:
    MetricsAggregator() {
        auto config = New<TTDigestConfig>();
        config->SetDelta(100.0);
        config->SetCompressionFrequency(0.1);

        latencyDigest_ = CreateTDigest(config);
    }

    void RecordLatency(double milliseconds) {
        latencyDigest_->AddValue(milliseconds);
    }

    double GetP50Latency() const {
        return latencyDigest_->GetQuantile(0.5);
    }

    double GetP95Latency() const {
        return latencyDigest_->GetQuantile(0.95);
    }

    double GetP99Latency() const {
        return latencyDigest_->GetQuantile(0.99);
    }

    i64 GetSampleCount() const {
        return latencyDigest_->GetCount();
    }

private:
    IQuantileDigestPtr latencyDigest_;
};
```

### 序列化和反序列化
```cpp
// 创建并填充摘要
auto digest = CreateTDigest(config);
for (int i = 0; i < 10000; ++i) {
    double value = /* 生成随机值 */;
    digest->AddValue(value);
}

// 序列化
TString serialized = digest->Serialize();

// 存储到文件或通过网络传输
std::ofstream out("digest.bin");
out.write(serialized.Data(), serialized.Size());
out.close();

// 反序列化
std::ifstream in("digest.bin");
std::string buffer(std::istreambuf_iterator<char>(in), {});
auto restoredDigest = LoadQuantileDigest(buffer);

// 验证恢复的摘要
std::cout << "Restored 95th percentile: "
          << restoredDigest->GetQuantile(0.95) << std::endl;
```

### 多摘要合并
```cpp
class DistributedQuantileCalculator {
public:
    void AddLocalData(const std::vector<double>& values) {
        auto config = New<TTDigestConfig>();
        config->SetDelta(100.0);
        auto localDigest = CreateTDigest(config);

        for (double value : values) {
            localDigest->AddValue(value);
        }

        localDigests_.push_back(localDigest);
    }

    IQuantileDigestPtr GetGlobalDigest() {
        if (localDigests_.empty()) {
            return nullptr;
        }

        // 创建全局摘要
        auto config = New<TTDigestConfig>();
        config->SetDelta(100.0);
        auto globalDigest = CreateTDigest(config);

        // 合并所有本地摘要
        for (const auto& local : localDigests_) {
            // 通过序列化-反序列化合并
            TString serialized = local->Serialize();
            auto restored = LoadQuantileDigest(serialized);

            // 需要实现合并逻辑或使用分位数近似
            for (int i = 0; i <= 100; ++i) {
                double q = i / 100.0;
                double value = restored->GetQuantile(q);
                globalDigest->AddValue(value);
            }
        }

        return globalDigest;
    }

private:
    std::vector<IQuantileDigestPtr> localDigests_;
};
```

## TDigest 算法

### 算法原理

TDigest 是一种用于计算分位数的数据结构，特点包括：

1. **分块存储**: 将相似值分组存储
2. **质心表示**: 每个组用均值和权重表示
3. **动态压缩**: 当组数超过限制时合并相似的组
4. **精确边界**: 保证最小值和最大值的精确性

### 参数说明

#### Delta (δ) 参数
- **含义**: 控制压缩程度和精度的平衡
- **取值**: 通常在 10 到 1000 之间
- **影响**:
  - 小值: 更高精度，更多内存使用
  - 大值: 更低精度，更少内存使用

#### CompressionFrequency (压缩频率)
- **含义**: 控制何时触发压缩操作
- **取值**: 0.0 到 1.0 之间
- **影响**:
  - 小值: 频繁压缩，更多CPU开销
  - 大值: 延迟压缩，更好性能

## 应用场景

### 1. 性能监控
```cpp
class ServiceMetrics {
public:
    void RecordRequestTime(double milliseconds) {
        requestTimeDigest_.AddValue(milliseconds);
    }

    void ReportMetrics() {
        std::cout << "P50: " << requestTimeDigest_.GetQuantile(0.5) << "ms" << std::endl;
        std::cout << "P95: " << requestTimeDigest_.GetQuantile(0.95) << "ms" << std::endl;
        std::cout << "P99: " << requestTimeDigest_.GetQuantile(0.99) << "ms" << std::endl;
    }

private:
    IQuantileDigestPtr requestTimeDigest_ = CreateTDigest();
};
```

### 2. 网络延迟分析
```cpp
class NetworkMonitor {
public:
    void RecordPingTime(double milliseconds) {
        pingDigest_.AddValue(milliseconds);
    }

    bool IsNetworkHealthy() {
        double p95 = pingDigest_.GetQuantile(0.95);
        return p95 < 100.0; // 95分位数小于100ms认为健康
    }

private:
    IQuantileDigestPtr pingDigest_ = CreateTDigest();
};
```

### 3. 数据分布分析
```cpp
class DataAnalyzer {
public:
    void AddDataPoint(double value) {
        dataDigest_.AddValue(value);
    }

    void PrintDistribution() {
        std::cout << "Min: " << dataDigest_.GetQuantile(0.0) << std::endl;
        std::cout << "Q1: " << dataDigest_.GetQuantile(0.25) << std::endl;
        std::cout << "Median: " << dataDigest_.GetQuantile(0.5) << std::endl;
        std::cout << "Q3: " << dataDigest_.GetQuantile(0.75) << std::endl;
        std::cout << "Max: " << dataDigest_.GetQuantile(1.0) << std::endl;

        // 检测异常值
        double q1 = dataDigest_.GetQuantile(0.25);
        double q3 = dataDigest_.GetQuantile(0.75);
        double iqr = q3 - q1;
        double lowerBound = q1 - 1.5 * iqr;
        double upperBound = q3 + 1.5 * iqr;

        std::cout << "Outlier bounds: [" << lowerBound << ", " << upperBound << "]" << std::endl;
    }

private:
    IQuantileDigestPtr dataDigest_ = CreateTDigest();
};
```

## 性能特性

### 时间复杂度
- **添加值**: O(1) 平均，O(log n) 最坏
- **查询分位数**: O(log n)
- **压缩**: O(n log n)

### 空间复杂度
- **内存使用**: O(delta)，其中 delta 是压缩参数

### 精度保证
- **极端分位数**: P0 和 P100 是精确的
- **中间分位数**: 误差随数据分布变化
- **相对误差**: 通常在 1% 以内

## 最佳实践

### 1. 参数选择
```cpp
// 高精度场景（关键业务指标）
auto highPrecisionConfig = New<TTDigestConfig>();
highPrecisionConfig->SetDelta(1000.0);
highPrecisionConfig->SetCompressionFrequency(0.05);

// 一般场景
auto normalConfig = New<TTDigestConfig>();
normalConfig->SetDelta(100.0);
normalConfig->SetCompressionFrequency(0.1);

// 内存受限场景
auto memoryEfficientConfig = New<TTDigestConfig>();
memoryEfficientConfig->SetDelta(10.0);
memoryEfficientConfig->SetCompressionFrequency(0.2);
```

### 2. 数据预处理
```cpp
void AddValueSafe(IQuantileDigestPtr digest, double value) {
    // 处理特殊值
    if (std::isnan(value) || std::isinf(value)) {
        return; // 忽略无效值
    }

    // 限制范围（可选）
    if (value < 0) {
        value = 0;
    } else if (value > 1e9) {
        value = 1e9;
    }

    digest->AddValue(value);
}
```

### 3. 批量操作
```cpp
void AddValues(IQuantileDigestPtr digest, const std::vector<double>& values) {
    // 批量添加比逐个添加更高效
    for (double value : values) {
        digest->AddValue(value);
    }
}
```

### 4. 内存管理
```cpp
class QuantileSummary {
public:
    QuantileSummary() {
        Reset();
    }

    void Reset() {
        auto config = New<TTDigestConfig>();
        config->SetDelta(100.0);
        digest_ = CreateTDigest(config);
    }

    void PeriodicReset() {
        // 定期重置以避免内存无限增长
        if (digest_->GetCount() > 1000000) {
            Reset();
        }
    }

private:
    IQuantileDigestPtr digest_;
};
```

## 依赖项

- YTsaurus 核心库 (`yt/yt/core/`)
- YTree 库 (`yt/yt/core/ytree/`)
- Protobuf 库

## 注意事项

1. **精度和内存权衡**: 根据需求选择合适的 delta 参数
2. **数据分布**: 对极端分布（如长尾分布）精度可能下降
3. **内存使用**: 虽然是 O(delta)，但实际使用可能略高
4. **线程安全**: 当前实现不是线程安全的，需要外部同步
5. **压缩策略**: 压缩频率影响性能和精度平衡
6. **序列化格式**: 序列化格式可能在版本间不兼容