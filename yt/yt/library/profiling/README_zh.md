# Profiling (性能监控)

Profiling 是 YTsaurus 的核心监控库，提供了全面的指标收集、聚合和分析功能。

## 概述

Profiling 库提供以下核心功能：
- 多维计数器的本地聚合
- 无锁计数器注册
- 高精度时间序列数据
- 稀疏计数器支持
- 全局注册表
- 调试页面支持

## 主要特性

### 1. 本地聚合
- 支持多维计数器聚合
- 减少网络传输开销
- 提高查询性能

### 2. 无锁设计
- 运行时动态创建计数器
- 避免不必要的锁竞争
- 高并发性能优化

### 3. 时间网格
- 5秒网格步长高精度存储
- 30秒标准收集间隔
- 历史数据压缩

### 4. 稀疏计数器
- 支持高基数标签（如用户、表路径）
- 自动注销旧计数器
- 减少资源占用

### 5. 接口分离
- 清晰的接口/实现分离
- 避免循环依赖
- 模块化设计

## 核心组件

### 1. 计数器类型

#### TCounter (计数器)
```cpp
class TCounter {
public:
    // 增加计数值
    void Increment(i64 delta = 1) const;

    // 检查计数器是否有效
    explicit operator bool() const;
};
```

#### TGauge (仪表盘)
```cpp
class TGauge {
public:
    // 更新仪表盘值
    void Update(double value) const;

    // 检查仪表盘是否有效
    explicit operator bool() const;
};
```

#### TTimeCounter (时间计数器)
```cpp
class TTimeCounter {
public:
    // 添加时间间隔
    void Add(TDuration delta) const;

    // 检查计数器是否有效
    explicit operator bool() const;
};
```

#### TTimeGauge (时间仪表盘)
```cpp
class TTimeGauge {
public:
    // 更新时间值
    void Update(TDuration value) const;

    // 检查仪表盘是否有效
    explicit operator bool() const;
};
```

#### THistogram (直方图)
```cpp
class THistogram {
public:
    // 记录值
    void Record(double value) const;

    // 记录带权重的值
    void Record(double value, double weight) const;

    // 检查直方图是否有效
    explicit operator bool() const;
};
```

### 2. 接口定义

#### ICounter (计数器接口)
```cpp
struct ICounter : public TRefCounted {
    virtual void Increment(i64 delta) = 0;
};
```

#### IGauge (仪表盘接口)
```cpp
struct IGauge : public TRefCounted {
    virtual void Update(double value) = 0;
};
```

#### IHistogram (直方图接口)
```cpp
struct IHistogram : public TRefCounted {
    virtual void Record(double value) = 0;
    virtual void Record(double value, double weight) = 0;
};
```

### 3. 注册表
```cpp
struct IRegistry : public TRefCounted {
    // 注册计数器
    virtual ICounterPtr RegisterCounter(
        const TString& name,
        const TTagSet& tags = {}) = 0;

    // 注册仪表盘
    virtual IGaugePtr RegisterGauge(
        const TString& name,
        const TTagSet& tags = {}) = 0;

    // 注册时间计数器
    virtual ITimeCounterPtr RegisterTimeCounter(
        const TString& name,
        const TTagSet& tags = {}) = 0;

    // 注册直方图
    virtual IHistogramPtr RegisterHistogram(
        const TString& name,
        const TTagSet& tags = {}) = 0;
};
```

## 使用方法

### 基本使用
```cpp
#include <yt/yt/library/profiling/sensor.h>

namespace NYT::NProfiling {

// 创建 Profiler
TProfiler profiler("/my_service");

// 注册计数器
TCounter requestCounter = profiler.Counter("/requests");
TCounter errorCounter = profiler.Counter("/errors", {{"service", "api"}});

// 注册仪表盘
TGauge activeConnectionsGauge = profiler.Gauge("/connections/active");

// 注册直方图
THistogram requestLatency = profiler.Histogram("/latency", ExponentialHistogram(10, 0.01, 100));

// 使用计数器
void HandleRequest() {
    auto start = TCpuInstant::Now();

    // 增加请求计数
    requestCounter.Increment();

    try {
        ProcessRequest();

        // 记录延迟
        auto duration = TCpuInstant::Now() - start;
        requestLatency.Record(duration.MilliSeconds());

    } catch (const std::exception& e) {
        // 增加错误计数
        errorCounter.Increment();
        throw;
    }
}

// 更新仪表盘
void UpdateActiveConnections(int count) {
    activeConnectionsGauge.Update(count);
}

}  // namespace NYT::NProfiling
```

### 使用标签
```cpp
// 创建带标签的 Profiler
TProfiler profiler("/requests");

// 使用标签
TCounter counter = profiler.Counter({
    {"method", "GET"},
    {"endpoint", "/api/v1/data"}
});

// 动态标签
TDynamicTags dynamicTags;
dynamicTags.Add("user", userId);
dynamicTags.Add("table", tableName);

TCounter requestCounter = profiler.Counter("/read_requests", dynamicTags);
requestCounter.Increment();
```

### 稀疏计数器
```cpp
// 创建稀疏计数器
auto options = New<TProfilerOptions>();
options->SetSparse(true);
options->SetLingerTimeout(TDuration::Minutes(5));

TProfiler sparseProfiler("/sparse/metrics", options);

// 计数器在值为零时不会被导出
TCounter userRequestCounter = sparseProfiler.Counter({
    {"user", userId}
});

// 只有当值非零时才会导出
if (requestCount > 0) {
    userRequestCounter.Increment(requestCount);
}
```

### 时间测量
```cpp
// 使用时间计数器
TTimeCounter processingTime = profiler.TimeCounter("/processing_time");

void ProcessJob() {
    auto timer = processingTime.Timer();
    // 处理任务
    // timer 析构时自动记录时间
}

// 或者手动记录
TTimeCounter totalTime = profiler.TimeCounter("/total_time");
totalTime.Add(TDuration::Seconds(10));
```

### 直方图配置
```cpp
// 创建自定义直方图
auto histogram = CreateCustomHistogram(
    {0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 300.0}
);

THistogram latencyHistogram = profiler.Histogram("/custom_latency", histogram);
latencyHistogram.Record(latency);
```

### 全局计数器
```cpp
// 创建全局计数器（不添加进程标签）
auto options = New<TProfilerOptions>();
options->SetGlobal(true);

TProfiler globalProfiler("/cluster/metrics", options);
TCounter clusterRequestCounter = globalProfiler.Counter("/total_requests");

// 确保只有一个进程在使用
if (IsLeaderProcess()) {
    clusterRequestCounter.Increment();
}
```

## 高级功能

### 1. 传感器生产者
```cpp
class MySensorProducer : public ISensorProducer {
public:
    void CollectSensors(ISensorWriter* writer) override {
        // 动态生成传感器数据
        writer->AddCounter("/dynamic/metric", value);
        writer->AddGauge("/dynamic/gauge", gaugeValue);
    }
};

// 注册生产者
auto producer = New<MySensorProducer>();
profiler.AddProducer("/dynamic", producer);
```

### 2. 聚合函数
```cpp
// 配置聚合规则
TProfiler profiler("/my_service");

// 在 Solomon 侧计算平均值
profiler.SetAggregationMode(EAggregationMode::Average);

// 计算最大值
profiler.SetAggregationMode(EAggregationMode::Max);

// 计算总和（默认）
profiler.SetAggregationMode(EAggregationMode::Sum);
```

### 3. 调试页面
```cpp
// 获取调试信息
auto registry = GetGlobalRegistry();
auto debugInfo = registry->GetDebugInfo();

// 检查传感器溢出
if (debugInfo.SensorCount > debugInfo.MaxSensors) {
    YT_LOG_ERROR("Sensor overflow detected!");
}

// 监控收集状态
auto collectionStatus = registry->GetCollectionStatus();
if (!collectionStatus.IsHealthy) {
    YT_LOG_ERROR("Metric collection issues: %v", collectionStatus.ErrorMessage);
}
```

## 最佳实践

### 1. 命名约定
```cpp
// 使用层次化命名
TProfiler profiler("/service/subsystem/component");

// 使用有意义的名称
TCounter databaseConnections = profiler.Counter("/db/connections");
TGauge memoryUsage = profiler.Gauge("/memory/usage");
THistogram queryDuration = profiler.Histogram("/query/duration");
```

### 2. 标签设计
```cpp
// 限制标签基数
// 好的做法
TCounter methodCounter = profiler.Counter("/requests", {
    {"method", "GET"},      // 有限值
    {"endpoint", "/api"}    // 有限值
});

// 避免的做法
TCounter userCounter = profiler.Counter("/requests", {
    {"user_id", userId},    // 高基数，用户稀疏计数器
    {"request_id", reqId}   // 超高基数，绝对避免
});
```

### 3. 性能考虑
```cpp
// 缓存 Profiler 对象
class MyClass {
public:
    MyClass()
        : Profiler_("/my_class")  // 初始化时创建
        , RequestCounter_(Profiler_.Counter("/requests"))  // 预创建计数器
    { }

    void Process() {
        RequestCounter_.Increment();  // 直接使用，避免查找开销
    }

private:
    TProfiler Profiler_;
    TCounter RequestCounter_;
};
```

### 4. 测试支持
```cpp
// 使用测试模式
TEST(MyTest, BasicCounting) {
    auto testing = NYT::NProfiling::CreateTesting();
    testing->Enable();

    TProfiler profiler("/test");
    auto counter = profiler.Counter("/my_counter");

    counter.Increment(5);

    // 验证值
    EXPECT_EQ(testing->GetCounter("/test/my_counter"), 5);
}
```

## 与 monlib 比较

| 特性 | YTsaurus Profiling | monlib |
| ----- | ------------------ | ------ |
| 稀疏传感器 | ✓ | ✗ |
| 调试页面 | ✓ | ✓ |
| 5秒网格步长 | ✓ | ✗ |
| 本地投影 | ✓ | ✗ |
| 传感器注销 | ✓ | ✗ |
| 仅内存指标 | ✓ | ✓ |

## 性能指标

- **注册开销**: O(1) 无锁
- **更新开销**: O(1) 原子操作
- **内存使用**: 每个传感器约 100 字节
- **缓冲延迟**: 默认 5 秒
- **导出间隔**: 默认 30 秒

## 依赖项

- YTsaurus 核心库 (`yt/yt/core/`)
- CPU 时钟库 (`library/cpp/yt/cpu_clock/`)
- 紧凑容器库 (`library/cpp/yt/compact_containers/`)

## 注意事项

1. **标签基数**: 避免高基数标签，考虑使用稀疏计数器
2. **内存管理**: 监控传感器数量，避免内存泄漏
3. **线程安全**: 所有操作都是线程安全的
4. **性能**: 避免在热路径创建新传感器
5. **全局计数器**: 确保全局计数器只在一个进程中活跃