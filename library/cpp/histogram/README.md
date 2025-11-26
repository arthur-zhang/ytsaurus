# 直方图（Histogram）库

高性能的直方图统计和分析库，支持多种直方图实现。

## 概述

该库提供了多种直方图实现，用于数据的统计分析和聚合计算。包括自适应直方图、固定区间直方图、HDR直方图等多种类型，适用于不同的应用场景。

## 核心组件

### 自适应直方图（Adaptive）
位于 `adaptive/` 目录，提供智能的自适应区间划分：
- **THistogram**: 基础直方图接口
- **TAutoHistogram**: 自动调整区间的直方图
- **TAdaptiveHistogram**: 自适应直方图实现
- **TFixedBinHistogram**: 固定区间直方图
- **TBlockHistogram**: 块状直方图

### HDR 直方图
位于 `hdr/` 目录，提供高精度延迟测量：
- **HDR Histogram**: 高动态范围直方图
- 适用于延迟分布测量

### 简单直方图
位于 `simple/` 目录，提供基础的直方图功能：
- **THistogram**: 简单直方图实现

## 核心接口

### 基础直方图接口
```cpp
class IHistogram {
public:
    // 数据操作
    virtual void Clear() = 0;
    virtual void Add(double value, double weight) = 0;
    virtual void Add(const THistoRec& histoRec) = 0;

    // 合并操作
    virtual void Merge(const THistogram& histo, double multiplier) = 0;
    virtual void Merge(const TVector<THistogram>& histogramsToMerge) = 0;
    virtual void Merge(TVector<IHistogramPtr> histogramsToMerge) = 0;

    // 统计计算
    virtual double GetMinValue() = 0;
    virtual double GetMaxValue() = 0;
    virtual double GetSum() = 0;
    virtual double GetSumInRange(double leftBound, double rightBound) = 0;
    virtual double CalcUpperBound(double sum) = 0;

    // 属性
    virtual void SetId(ui64 id) = 0;
    virtual ui64 GetId() = 0;
    virtual bool Empty() = 0;
};
```

## 使用示例

### 自适应直方图
```cpp
#include <histogram/adaptive/histogram.h>

// 创建自适应直方图
auto histogram = MakeHolder<TAdaptiveHistogram>();

// 添加数据点
histogram->Add(10.5, 1.0);    // 值, 权重
histogram->Add(15.2, 1.0);
histogram->Add(8.7, 1.0);

// 获取统计信息
double min = histogram->GetMinValue();
double max = histogram->GetMaxValue();
double sum = histogram->GetSum();

// 范围查询
double rangeSum = histogram->GetSumInRange(10.0, 15.0);
```

### 固定区间直方图
```cpp
#include <histogram/adaptive/fixed_bin_histogram.h>

// 创建固定区间直方图（100个区间）
auto histogram = MakeHolder<TFixedBinHistogram>(100);

// 添加数据
for (double value : dataPoints) {
    histogram->Add(value, 1.0);
}

// 计算百分位数
double p50 = histogram->CalcUpperBound(0.5 * histogram->GetSum());
double p95 = histogram->CalcUpperBound(0.95 * histogram->GetSum());
double p99 = histogram->CalcUpperBound(0.99 * histogram->GetSum());
```

### 直方图合并
```cpp
// 合并多个直方图
TVector<IHistogramPtr> histograms;
histograms.push_back(histogram1);
histograms.push_back(histogram2);
histograms.push_back(histogram3);

// 合并到新的直方图
auto merged = MakeHolder<TAdaptiveHistogram>();
merged->Merge(histograms);

// 带权重的合并
auto weighted = MakeHolder<TAdaptiveHistogram>();
weighted->Merge(otherHistogram, 2.0);  // 乘以权重因子
```

## 直方图类型

### 自适应直方图（TAdaptiveHistogram）
- **特点**: 根据数据分布自动调整区间
- **适用**: 数据分布不均匀的场景
- **精度**: 在重要数据区域提供更高精度

### 固定区间直方图（TFixedBinHistogram）
- **特点**: 预定义的固定区间数量
- **适用**: 数据分布相对均匀的场景
- **性能**: 计算速度较快，内存占用固定

### 自动直方图（TAutoHistogram）
- **特点**: 智能选择最优的区间划分
- **适用**: 数据分布特征未知的场景
- **平衡**: 在精度和性能之间取得平衡

### HDR 直方图
- **特点**: 高精度、低内存开销
- **适用**: 延迟测量、性能监控
- **范围**: 支持高动态范围的数据

## 性能特性

### 内存效率
- **自适应**: 根据数据特征调整内存使用
- **压缩**: 智能的区间压缩算法
- **共享**: 支持直方图数据的共享存储

### 计算性能
- **增量更新**: 支持增量式的数据添加
- **批量操作**: 支持批量数据处理
- **缓存优化**: 优化的内存访问模式

### 并发支持
- **线程安全**: 支持多线程环境下的使用
- **原子操作**: 使用原子操作保证数据一致性
- **锁机制**: 最小化锁竞争

## 应用场景

### 性能监控
```cpp
// 延迟监控
auto latencyHist = MakeHolder<TAdaptiveHistogram>();

void RecordLatency(double milliseconds) {
    latencyHist->Add(milliseconds, 1.0);
}

void ReportLatencyStats() {
    double p50 = latencyHist->CalcUpperBound(0.5 * latencyHist->GetSum());
    double p95 = latencyHist->CalcUpperBound(0.95 * latencyHist->GetSum());
    double p99 = latencyHist->CalcUpperBound(0.99 * latencyHist->GetSum());

    printf("P50: %.2fms, P95: %.2fms, P99: %.2fms\n", p50, p95, p99);
}
```

### 数据分析
```cpp
// 数值分布分析
auto valueHist = MakeHolder<TAdaptiveHistogram>();

void AnalyzeValues(const TVector<double>& values) {
    for (double value : values) {
        valueHist->Add(value, 1.0);
    }

    printf("Min: %.2f, Max: %.2f, Mean: %.2f\n",
           valueHist->GetMinValue(),
           valueHist->GetMaxValue(),
           valueHist->GetSum() / values.size());
}
```

### 实时统计
```cpp
// 实时数据流统计
class RealTimeStats {
private:
    IHistogramPtr histogram_;

public:
    RealTimeStats() : histogram_(MakeHolder<TAutoHistogram>()) {}

    void Update(double value) {
        histogram_->Add(value, 1.0);
    }

    double GetPercentile(double p) {
        double targetSum = p * histogram_->GetSum();
        return histogram_->CalcUpperBound(targetSum);
    }
};
```

## 最佳实践

### 直方图选择
```cpp
// 根据数据特征选择合适的直方图类型
IHistogramPtr CreateHistogram(const TDataProfile& profile) {
    if (profile.IsUniformDistribution) {
        return MakeHolder<TFixedBinHistogram>(profile.SuggestedBins);
    } else if (profile.IsUnknownDistribution) {
        return MakeHolder<TAutoHistogram>();
    } else {
        return MakeHolder<TAdaptiveHistogram>();
    }
}
```

### 权重处理
```cpp
// 使用权重来处理不同重要性的数据
histogram->Add(criticalValue, 10.0);    // 高权重
histogram->Add(normalValue, 1.0);       // 正常权重
histogram->Add(noisyValue, 0.1);        // 低权重
```

### 范围查询优化
```cpp
// 高效的范围查询
double totalSum = histogram->GetSum();
double below10 = histogram->GetSumBelowBound(10.0);
double between10And20 = histogram->GetSumInRange(10.0, 20.0);
double above20 = histogram->GetSumAboveBound(20.0);

// 验证查询结果的正确性
assert(abs(totalSum - (below10 + between10And20 + above20)) < 1e-10);
```

## 序列化支持

### Protocol Buffer 支持
```cpp
// 序列化直方图到 protobuf
THistogram proto;
histogram->ToProto(proto);

// 从 protobuf 反序列化
auto restored = MakeHolder<TAdaptiveHistogram>();
restored->FromProto(proto);
```

### 数据格式
直方图支持标准的 Protocol Buffer 格式，便于：
- 网络传输
- 持久化存储
- 跨语言集成

## 扩展功能

### 自定义聚合器
```cpp
class TCustomHistogram: public IHistogram {
public:
    // 实现自定义的聚合逻辑
    void Add(double value, double weight) override {
        // 自定义添加逻辑
    }

    // 实现自定义的统计计算
    double GetCustomMetric() override {
        // 自定义指标计算
        return customMetric_;
    }
};
```

### 流式处理
```cpp
// 支持流式数据处理
class TStreamingHistogram {
private:
    IHistogramPtr histogram_;
    size_t batchSize_;

public:
    void ProcessStream(std::istream& input) {
        TVector<double> batch;
        double value;

        while (input >> value) {
            batch.push_back(value);
            if (batch.size() >= batchSize_) {
                ProcessBatch(batch);
                batch.clear();
            }
        }

        if (!batch.empty()) {
            ProcessBatch(batch);
        }
    }
};
```

## 注意事项

### 数据精度
- 浮点数精度可能影响统计结果
- 建议在需要高精度时使用适当的舍入策略

### 内存管理
- 长期运行的程序需要定期清理直方图数据
- 避免内存泄漏，正确管理直方图对象的生命周期

### 性能考虑
- 大量数据添加时考虑批量处理
- 在高频更新场景下注意性能优化

## 测试和验证

### 单元测试
每个直方图实现都包含完整的单元测试：
- 基础功能测试
- 边界条件测试
- 性能基准测试
- 并发安全测试

### 集成测试
与 YTsaurus 系统的集成测试确保：
- 系统兼容性
- 性能表现
- 数据一致性

这个直方图库为 YTsaurus 项目提供了强大的数据分析能力，支持从简单的统计到复杂的性能分析等各种场景。