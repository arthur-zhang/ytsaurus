# MonLib 监控库

## 项目概述

MonLib 是 YTsaurus 的核心监控库，提供了全面的系统监控、指标收集、指标展示和 HTTP 监控服务功能。该库支持多种指标类型（计数器、仪表盘、直方图、摘要等），提供高并发安全的指标操作，内置 HTTP 监控服务，支持指标导出和可视化，是构建分布式系统监控解决方案的核心组件。

## 文件说明

### 核心指标系统

#### `metrics/` 目录 - 新一代指标系统

- **`metric.h`** - 指标接口定义
  - `IMetric`: 基础指标接口
  - `IGauge`: 浮点数仪表盘接口
  - `IIntGauge`: 整数仪表盘接口
  - `ICounter`: 计数器接口
  - `ISummary`: 摘要统计接口
  - `IHistogram`: 直方图接口

- **`metric_type.h/cpp`** - 指标类型定义
  - `EMetricType`: 指标类型枚举
  - 指标元数据管理

- **`metric_value.h/cpp`** - 指标值封装
  - 类型安全的指标值操作
  - 指标值的序列化和反序列化

- **`metric_registry.h/cpp`** - 指标注册表
  - 指标的注册和管理
  - 指标查找和组织
  - 线程安全的指标操作

- **`metric_consumer.h/cpp`** - 指标消费者接口
  - 指标数据的消费和处理
  - 支持多种导出格式
  - 实时指标推送

#### `counters/` 目录 - 传统计数器（已弃用）

- **`counters.h`** - 传统原子计数器
  - `TDeprecatedCounter`: 原子操作计数器
  - 线程安全的增减操作
  - 已标记为弃用，推荐使用 metrics 目录

### 指标收集器

- **`histogram_collector.h/cpp`** - 直方图收集器
  - 线性分布和指数分布直方图
  - 明确配置和自动配置的收集器
  - 高效的分桶统计

- **`summary_collector.h/cpp`** - 摘要收集器
  - 分位数统计（P50, P95, P99 等）
  - 滑动窗口统计
  - 内存高效的数据结构

- **`log_histogram_collector.h/cpp`** - 对数直方图
  - 对数分桶的直方图收集
  - 适用于大范围数值统计

### 监控服务

#### `service/` 目录 - HTTP 监控服务

- **`monservice.h/cpp`** - 监控服务主体
  - `TMonService2`: 多线程 HTTP 监控服务器
  - 支持自定义端口、主机、线程数配置
  - 内置认证和压缩功能

- **`service.h/cpp`** - 基础服务接口
  - 监控页面的注册和管理
  - 请求路由和处理

- **`auth.h/cpp`** - 认证模块
  - 基础认证接口实现
  - 支持自定义认证策略

- **`format.h/cpp`** - 响应格式化
  - HTML/JSON/XML 等格式支持
  - 模板化的响应生成

#### `pages/` 子目录 - 监控页面

- **`mon_page.h`** - 基础监控页面
- **`index_mon_page.h`** - 首页监控页面

### 编码和序列化

#### `encode/` 目录 - 指标编码

- 支持 Prometheus 格式导出
- JSON 格式序列化
- 自定义二进制格式
- 压缩和优化编码

### 消息总线集成

#### `messagebus/` 目录

- 与 MessageBus 的集成接口
- 分布式指标收集
- 指标的网络传输

### 动态计数器

#### `dynamic_counters/` 目录

- 运行时动态创建指标
- 指标的生命周期管理
- 热重载和配置更新

### 工具和辅助

#### `exception/` 目录

- 监控异常处理
- 错误统计和报告

#### `consumers/` 目录

- 指标消费者实现
- 外部系统集成
- 指标数据推送

## 实现原理

### 指标类型系统

```cpp
// 基础指标接口
class IMetric : public TThrRefBase {
public:
    virtual EMetricType Type() const noexcept = 0;
    virtual void Accept(TInstant time, IMetricConsumer* consumer) const = 0;
    virtual void Reset() noexcept = 0;
};

// 计数器（只增不减）
class ICounter : public IMetric {
public:
    EMetricType Type() const noexcept final {
        return EMetricType::COUNTER;
    }
    virtual i64 Inc() noexcept = 0;
    virtual i64 Add(i64 value) noexcept = 0;
};

// 仪表盘（可增可减）
class IGauge : public IMetric {
public:
    EMetricType Type() const noexcept final {
        return EMetricType::GAUGE;
    }
    virtual void Set(double value) noexcept = 0;
    virtual double Add(double value) noexcept = 0;
    virtual double Get() const noexcept = 0;
};
```

### 指标注册表

```cpp
class TMetricRegistry {
private:
    THashMap<TString, IMetricPtr> Metrics_;
    THashMap<TString, TLabels> Labels_;
    TAdaptiveLock Lock_;

public:
    template<typename T>
    TIntrusivePtr<T> Register(const TString& name, const TLabels& labels = {}) {
        with_lock (Lock_) {
            TString key = MakeKey(name, labels);
            auto metric = MakeHolder<T>();
            Metrics_[key] = metric;
            return metric;
        }
    }

    void ForEachMetric(std::function<void(const TString&, IMetricPtr)> func) {
        with_lock (Lock_) {
            for (const auto& [name, metric] : Metrics_) {
                func(name, metric);
            }
        }
    }
};
```

### 直方图实现

```cpp
class THistogramCollector {
private:
    TVector<double> Bounds_;     // 分桶边界
    TVector<TAtomic> Buckets_;   // 分桶计数
    TAtomic TotalCount_;         // 总计数
    TAtomic TotalSum_;           // 总和

public:
    void Record(double value) {
        // 找到对应的桶
        size_t bucket = FindBucket(value);
        AtomicIncrement(Buckets_[bucket]);
        AtomicIncrement(TotalCount_);
        AtomicAdd(TotalSum_, value);
    }

    THistogramSnapshot GetSnapshot() const {
        return THistogramSnapshot(Bounds_, Buckets_,
                                 AtomicGet(TotalCount_),
                                 AtomicGet(TotalSum_));
    }
};
```

### HTTP 监控服务

```cpp
class TMonService2: public TMtHttpServer {
private:
    TIntrusivePtr<TIndexMonPage> IndexMonPage;
    THolder<IAuthProvider> AuthProvider_;
    TMetricRegistry Registry_;

public:
    TMonService2(ui16 port, const TString& title = GetProgramName())
        : TMtHttpServer(HttpServerOptions(port, std::thread::hardware_concurrency()))
        , Title(title)
    {
        // 注册默认页面
        RegisterPages();
    }

    template<typename TPage>
    void RegisterPage(const TString& path) {
        auto page = MakeHolder<TPage>();
        Register(new TMonRequestHandler(path, page.Get()));
    }

    void RegisterMetric(const TString& name, IMetricPtr metric) {
        Registry_.Register(name, metric);
    }
};
```

## 使用示例

### 基础指标使用

```cpp
#include <library/cpp/monlib/metrics/metric.h>
#include <library/cpp/monlib/metrics/metric_registry.h>
#include <library/cpp/monlib/metrics/histogram_collector.h>

class ApplicationMetrics {
private:
    TMetricRegistry Registry_;
    TIntrusivePtr<ICounter> RequestCounter_;
    TIntrusivePtr<IGauge> ActiveConnections_;
    TIntrusivePtr<IHistogram> ResponseLatency_;

public:
    ApplicationMetrics() {
        // 注册指标
        RequestCounter_ = Registry_.Register<ICounter>("http_requests_total");
        ActiveConnections_ = Registry_.Register<IGauge>("active_connections");

        // 创建直方图（线性分桶: 0, 10ms, 20ms, ..., 1000ms）
        ResponseLatency_ = Registry_.Register<IHistogram>(
            "http_response_latency_ms",
            TExplicitHistogramCollector::CreateLinear(0, 10, 100)
        );
    }

    void OnRequestStart() {
        ActiveConnections_->Add(1);
        RequestCounter_->Inc();
    }

    void OnRequestComplete(TDuration latency) {
        ActiveConnections_->Sub(1);
        ResponseLatency_->Record(latency.MilliSeconds());
    }

    TMetricRegistry& GetRegistry() {
        return Registry_;
    }
};
```

### 监控服务集成

```cpp
#include <library/cpp/monlib/service/monservice.h>
#include <library/cpp/monlib/metrics/metric_registry.h>

class MonitoredApplication {
private:
    ApplicationMetrics Metrics_;
    TIntrusivePtr<TMonService2> MonService_;

public:
    void StartMonitoring(ui16 port = 8080) {
        // 创建监控服务
        MonService_ = MakeHolder<TMonService2>(port, "My Application");

        // 注册指标页面
        MonService_->RegisterPage<TMetricsPage>("metrics");
        MonService_->RegisterPage<TJsonMetricsPage>("metrics/json");

        // 将指标注册到监控服务
        auto& registry = Metrics_.GetRegistry();
        registry.ForEachMetric([this](const TString& name, IMetricPtr metric) {
            MonService_->RegisterMetric(name, metric);
        });

        // 启动监控服务
        MonService_->Start();
        std::cout << "Monitoring started at http://localhost:" << port << std::endl;
    }

    void StopMonitoring() {
        if (MonService_) {
            MonService_->Stop();
        }
    }
};
```

### 自定义监控页面

```cpp
#include <library/cpp/monlib/service/pages/mon_page.h>

class TCustomMetricsPage: public TMonPage {
private:
    TMetricRegistry* Registry_;

public:
    TCustomMetricsPage(TMetricRegistry* registry)
        : TMonPage("custom", "Custom Metrics")
        , Registry_(registry)
    {}

    void Output(IOutputStream& out) override {
        // HTML 头部
        HTML(out) {
            HEAD() {
                TITLE() << "Custom Metrics" << ENDTITLE();
                STYLE() << R"(
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    table { border-collapse: collapse; width: 100%; }
                    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                    th { background-color: #f2f2f2; }
                )" << ENDSTYLE();
            } << ENDHEAD();

            BODY() {
                H1() << "Application Metrics" << ENDH1();

                TABLE() {
                    TR() {
                        TH() << "Metric Name" << ENDTH();
                        TH() << "Type" << ENDTH();
                        TH() << "Value" << ENDTH();
                        TH() << "Description" << ENDTH();
                    } << ENDTR();

                    // 输出所有指标
                    Registry_->ForEachMetric([&](const TString& name, IMetricPtr metric) {
                        TR() {
                            TD() << name << ENDTD();
                            TD() << ToString(metric->Type()) << ENDTD();
                            TD() << GetMetricValue(metric) << ENDTD();
                            TD() << GetMetricDescription(name) << ENDTD();
                        } << ENDTR();
                    });
                } << ENDTABLE();
            } << ENDBODY();
        } << ENDHTML();
    }

private:
    TString GetMetricValue(IMetricPtr metric) {
        // 根据指标类型获取当前值
        switch (metric->Type()) {
            case EMetricType::GAUGE: {
                auto gauge = DynamicCast<IGauge>(metric);
                return ToString(gauge->Get());
            }
            case EMetricType::COUNTER: {
                // 计数器的值需要特殊处理
                return "N/A (use consumer)";
            }
            default:
                return "N/A";
        }
    }

    TString GetMetricDescription(const TString& name) {
        // 返回指标描述
        if (name.contains("http_requests")) {
            return "Total HTTP requests received";
        } else if (name.contains("active_connections")) {
            return "Currently active connections";
        } else {
            return "Custom metric";
        }
    }
};
```

### Prometheus 格式导出

```cpp
#include <library/cpp/monlib/encode/prometheus_encoder.h>

class TPrometheusExporter {
private:
    TMetricRegistry* Registry_;

public:
    TPrometheusExporter(TMetricRegistry* registry)
        : Registry_(registry)
    {}

    TString ExportMetrics() {
        TStringStream out;
        TPrometheusEncoder encoder(out);

        // 导出所有指标
        Registry_->ForEachMetric([&](const TString& name, IMetricPtr metric) {
            metric->Accept(TInstant::Now(), &encoder);
        });

        return out.Str();
    }

    void ServeMetrics(ui16 port = 9090) {
        TThread prometheusThread([this, port]() {
            THttpServer server(port);
            server.Register("/metrics", new THttpRequestHandler([this]() {
                return ExportMetrics();
            }));
            server.Start();
        });

        prometheusThread.Start();
    }
};
```

### 动态指标注册

```cpp
#include <library/cpp/monlib/dynamic_counters/dynamic_counters.h>

class DynamicMetricsExample {
private:
    TDynamicCounterProvider Provider_;

public:
    void ProcessUserData(const TString& userId, const TString& action) {
        // 动态创建用户级别的指标
        TString metricName = "user_action_" + action;
        auto counter = Provider_.GetCounter(metricName, {{"user_id", userId}});

        // 增加计数
        counter->Inc();

        // 动态创建延迟指标
        TString latencyMetric = "user_latency_" + action;
        auto histogram = Provider_.GetHistogram(latencyMetric,
            {{"user_id", userId}},
            TExplicitHistogramCollector::CreateExponential(1, 2, 10));

        histogram->Record(GetActionLatency());
    }

    void CleanupUserMetrics(const TString& userId) {
        // 清理特定用户的指标
        Provider_.RemoveMetricsWithLabel("user_id", userId);
    }
};
```

### 指标聚合和统计

```cpp
class MetricAggregator {
private:
    TIntrusivePtr<ISummaryCollector> ResponseTimeSummary_;
    TIntrusivePtr<IHistogramCollector> RequestSizeHistogram_;
    TMetricRegistry Registry_;

public:
    MetricAggregator() {
        // 创建摘要统计（分位数：0.5, 0.9, 0.95, 0.99）
        ResponseTimeSummary_ = CreateSummaryCollector({
            0.5, 0.9, 0.95, 0.99
        });

        // 创建请求大小直方图
        RequestSizeHistogram_ = CreateExponentialHistogram(1, 2, 20);

        // 注册到注册表
        Registry_.Register("response_time_summary", ResponseTimeSummary_);
        Registry_.Register("request_size_histogram", RequestSizeHistogram_);
    }

    void RecordRequest(double responseTimeMs, size_t requestSizeBytes) {
        ResponseTimeSummary_->Record(responseTimeMs);
        RequestSizeHistogram_->Record(requestSizeBytes);
    }

    void PrintStatistics() {
        auto summarySnapshot = ResponseTimeSummary_->GetSnapshot();
        auto histogramSnapshot = RequestSizeHistogram_->GetSnapshot();

        std::cout << "Response Time Statistics:\n";
        for (double quantile : {0.5, 0.9, 0.95, 0.99}) {
            double value = summarySnapshot.GetQuantile(quantile);
            std::cout << "  P" << (int)(quantile * 100) << ": " << value << "ms\n";
        }

        std::cout << "Request Size Statistics:\n";
        std::cout << "  Mean: " << histogramSnapshot.GetMean() << " bytes\n";
        std::cout << "  Max: " << histogramSnapshot.GetMax() << " bytes\n";
        std::cout << "  Count: " << histogramSnapshot.GetCount() << " requests\n";
    }
};
```

## 支持的指标类型

### 1. Counter (计数器)
- **特性**: 只增不减的累积值
- **用途**: 请求总数、错误总数、处理任务数
- **操作**: `Inc()`, `Add(value)`
- **示例**: `http_requests_total`, `errors_total`

### 2. Gauge (仪表盘)
- **特性**: 可增可减的瞬时值
- **用途**: 当前连接数、内存使用量、队列长度
- **操作**: `Set(value)`, `Add(value)`, `Get()`
- **示例**: `active_connections`, `memory_usage_bytes`

### 3. Histogram (直方图)
- **特性**: 值分布统计，固定分桶
- **用途**: 延迟分布、请求大小分布
- **分桶类型**: 线性分桶、指数分桶、自定义分桶
- **示例**: `http_request_duration_ms`

### 4. Summary (摘要)
- **特性**: 可配置分位数的滑动窗口统计
- **用途**: 响应时间分位数、吞吐量统计
- **分位数**: 支持任意分位数配置
- **示例**: `response_time_seconds`

### 5. Lazy Gauge (懒加载仪表盘)
- **特性**: 按需计算值，避免性能开销
- **用途**: 系统信息、配置值、状态查询
- **优势**: 减少不必要的计算
- **示例**: `system_load`, `config_version`

## 应用场景

### 1. Web 应用监控

- **请求指标**: QPS、延迟、错误率
- **资源使用**: CPU、内存、磁盘、网络
- **业务指标**: 用户活跃度、功能使用统计
- **系统健康**: 服务可用性、依赖检查

### 2. 微服务架构

- **服务间调用**: 调用次数、延迟、错误率
- **服务发现**: 实例状态、负载均衡指标
- **熔断器**: 熔断状态、恢复时间
- **配置管理**: 配置版本、更新次数

### 3. 数据库监控

- **查询性能**: 查询次数、执行时间、慢查询
- **连接管理**: 连接数、等待队列
- **存储使用**: 表大小、索引效率
- **复制状态**: 主从延迟、同步状态

### 4. 消息队列

- **吞吐量**: 生产/消费速率
- **队列状态**: 队列长度、积压情况
- **消费者**: 消费者状态、处理延迟
- **消息统计**: 成功/失败消息数

### 5. 容器和云原生

- **容器资源**: CPU/内存限制和使用
- **网络流量**: 入站/出站流量
- **存储 I/O**: 磁盘读写性能
- **健康检查**: 存活探针、就绪探针

## 技术特性

### 性能优化

1. **原子操作**: 无锁的并发安全操作
2. **内存高效**: 紧凑的数据结构，最小化内存占用
3. **CPU 缓存友好**: 数据布局优化，提高缓存命中率
4. **批量操作**: 支持批量指标更新，减少系统调用

### 可扩展性

1. **插件架构**: 支持自定义指标类型和消费者
2. **模块化设计**: 核心功能独立，易于扩展
3. **配置灵活**: 运行时配置修改，支持热重载
4. **多格式支持**: 支持 Prometheus、JSON、XML 等格式

### 可靠性

1. **线程安全**: 所有操作都是线程安全的
2. **异常安全**: 完善的异常处理机制
3. **内存安全**: 避免内存泄漏和访问越界
4. **降级策略**: 高负载时的自动降级保护

### 易用性

1. **简洁 API**: 直观的接口设计
2. **丰富文档**: 详细的 API 文档和示例
3. **调试支持**: 内置调试和诊断功能
4. **类型安全**: 强类型的指标操作

## 性能指标

### 延迟特性

- **计数器操作**: < 10ns (原子操作)
- **仪表盘操作**: < 20ns
- **直方图记录**: < 100ns
- **摘要记录**: < 200ns

### 内存开销

- **基础指标**: ~64 bytes
- **直方图**: ~1KB + 分桶存储
- **摘要**: ~512KB + 滑动窗口
- **注册表**: ~100 bytes + 指标存储

### 并发性能

- **QPS 支持**: > 1M operations/second
- **并发线程**: > 1000 线程安全访问
- **扩展性**: 近似线性扩展

## 最佳实践

### 1. 指标命名

```cpp
// ✅ 好的命名规范
auto httpRequests = Registry_.Register<ICounter>("http_requests_total");
auto dbConnections = Registry_.Register<IGauge>("db_connections_active");
auto requestLatency = Registry_.Register<IHistogram>("http_request_duration_seconds");

// ✅ 使用标签区分维度
auto httpRequests = Registry_.Register<ICounter>(
    "http_requests_total",
    {{"method", "GET"}, {"status", "200"}}
);
```

### 2. 指标选择

```cpp
// ✅ 选择合适的指标类型
class UserServiceMetrics {
public:
    // 累积计数用 Counter
    TIntrusivePtr<ICounter> UserRegistrations;

    // 瞬时值用 Gauge
    TIntrusivePtr<IGauge> ActiveUsers;

    // 延迟分布用 Histogram
    TIntrusivePtr<IHistogram> LoginLatency;

    // 关键业务指标用 Summary
    TIntrusivePtr<ISummary> RevenuePerTransaction;
};
```

### 3. 标签使用

```cpp
// ✅ 合理使用标签，避免基数爆炸
auto requestCounter = Registry_.Register<ICounter>(
    "http_requests_total",
    {
        {"method", "GET"},      // 低基数：少量固定值
        {"service", "api"}      // 低基数：服务名称
    }
);

// ❌ 避免高基数标签
// auto userCounter = Registry_.Register<ICounter>(
//     "user_requests_total",
//     {{"user_id", userId}}   // 高基数：大量用户ID
// );
```

### 4. 性能优化

```cpp
// ✅ 批量操作减少开销
void BatchRecordMetrics(const TVector<RequestInfo>& requests) {
    for (const auto& req : requests) {
        RequestCounter_->Add(1);  // 快速原子操作
        ResponseLatency_->Record(req.Latency);
    }
}

// ✅ 使用懒加载仪表盘避免计算开销
class SystemMetrics {
    double CalculateCpuUsage() {
        // 昂贵的系统调用
        return GetSystemCpuUsage();
    }

public:
    TIntrusivePtr<ILazyGauge> CpuUsage =
        Registry_.RegisterLazyGauge("system_cpu_usage", [this]() {
            return CalculateCpuUsage();
        });
};
```

### 5. 监控页面设计

```cpp
// ✅ 提供清晰的监控界面
class ProductionMonPage: public TMonPage {
public:
    void Output(IOutputStream& out) override {
        HTML(out) {
            BODY() {
                // 关键指标优先显示
                H1() << "Service Health" << ENDH1();
                OutputHealthIndicators();

                // 详细指标分组显示
                H2() << "Performance Metrics" << ENDH2();
                OutputPerformanceMetrics();

                H2() << "Business Metrics" << ENDH2();
                OutputBusinessMetrics();

                // 提供数据导出
                H2() << "Data Export" << ENDH2();
                OutputExportLinks();
            } << ENDBODY();
        } << ENDHTML();
    }
};
```