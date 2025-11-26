# Monitoring (监控管理)

## 项目概述

Monitoring 模块提供了一个统一的监控管理框架，用于收集、组织和暴露系统监控数据。该模块通过注册 Yson Producer 来构建监控树，支持周期性数据更新和缓存，为 YTsaurus 系统提供了完整的监控基础设施。

## 核心功能

### 监控树管理
- **层级结构**: 支持树状的监控数据组织结构
- **动态注册**: 运行时注册和注销监控数据生产者
- **路径映射**: 通过 YPath 路径访问监控数据
- **缓存机制**: 自动缓存监控数据，提高访问性能

### 数据生产者管理
- **Producer 注册**: 注册 NYson::TYsonProducer 生产监控数据
- **生命周期管理**: 管理生产者的注册和注销
- **周期更新**: 定期更新监控数据，保持数据时效性
- **并发安全**: 支持多线程并发访问

### 服务集成
- **YPath 服务**: 提供标准的 YPath 服务接口
- **HTTP 集成**: 通过 HTTP 接口暴露监控数据
- **RPC 服务**: 支持 RPC 协议访问监控数据
- **认证支持**: 集成认证机制保护敏感监控数据

## 主要接口

### 核心接口：IMonitoringManager

```cpp
struct IMonitoringManager
    : public TRefCounted
{
    // 注册生产者
    virtual void Register(const NYPath::TYPath& path, NYson::TYsonProducer producer) = 0;

    // 注销生产者
    virtual void Unregister(const NYPath::TYPath& path) = 0;

    // 获取 YPath 服务
    virtual NYTree::IYPathServicePtr GetService() = 0;

    // 启动周期更新
    virtual void Start() = 0;

    // 停止周期更新
    virtual void Stop() = 0;
};
```

#### 工厂函数

```cpp
// 创建监控管理器实例
IMonitoringManagerPtr CreateMonitoringManager();
```

### HTTP 集成

```cpp
// HTTP 监控集成
namespace NYT::NMonitoring {

// 创建 HTTP 监控处理器
NHttp::IHandlerPtr CreateMonitoringHandler(IMonitoringManagerPtr manager);

// 集成 HTTP 服务器
void SetupMonitoringHttpServer(NHttp::IServerPtr httpServer, IMonitoringManagerPtr manager);

} // namespace NYT::NMonitoring
```

## 使用方法

### 基本监控设置示例

```cpp
#include <yt/yt/library/monitoring/public.h>
#include <yt/yt/library/monitoring/monitoring_manager.h>

using namespace NYT;
using namespace NYT::NMonitoring;

class ApplicationMonitor {
public:
    ApplicationMonitor() {
        // 创建监控管理器
        monitoringManager_ = CreateMonitoringManager();
    }

    void Initialize() {
        // 注册应用级监控指标
        RegisterApplicationMetrics();

        // 注册系统级监控指标
        RegisterSystemMetrics();

        // 启动监控服务
        monitoringManager_->Start();
    }

    void Shutdown() {
        // 停止监控服务
        monitoringManager_->Stop();
    }

    NYTree::IYPathServicePtr GetMonitoringService() {
        return monitoringManager_->GetService();
    }

private:
    void RegisterApplicationMetrics() {
        // 注册应用计数器
        monitoringManager_->Register("/app/requests", BIND(&ApplicationMonitor::ProduceRequestMetrics, this));
        monitoringManager_->Register("/app/errors", BIND(&ApplicationMonitor::ProduceErrorMetrics, this));
        monitoringManager_->Register("/app/performance", BIND(&ApplicationMonitor::ProducePerformanceMetrics, this));
    }

    void RegisterSystemMetrics() {
        // 注册系统资源监控
        monitoringManager_->Register("/system/memory", BIND(&ApplicationMonitor::ProduceMemoryMetrics, this));
        monitoringManager_->Register("/system/cpu", BIND(&ApplicationMonitor::ProduceCpuMetrics, this));
        monitoringManager_->Register("/system/disk", BIND(&ApplicationMonitor::ProduceDiskMetrics, this));
    }

    void ProduceRequestMetrics(NYson::IYsonConsumer* consumer) {
        NYson::BuildYsonFluently(consumer)
            .BeginMap()
                .Item("total_requests").Value(totalRequests_.load())
                .Item("successful_requests").Value(successfulRequests_.load())
                .Item("failed_requests").Value(failedRequests_.load())
                .Item("average_latency_ms").Value(CalculateAverageLatency())
            .EndMap();
    }

    void ProduceErrorMetrics(NYson::IYsonConsumer* consumer) {
        NYson::BuildYsonFluently(consumer)
            .BeginMap()
                .Item("error_count").Value(errorCount_.load())
                .Item("last_error_time").Value(lastErrorTime_.load())
                .Item("error_types").Value(errorTypes_)
            .EndMap();
    }

    void ProducePerformanceMetrics(NYson::IYsonConsumer* consumer) {
        NYson::BuildYsonFluently(consumer)
            .BeginMap()
                .Item("cpu_usage_percent").Value(GetCpuUsage())
                .Item("memory_usage_mb").Value(GetMemoryUsage())
                .Item("active_connections").Value(activeConnections_.load())
            .EndMap();
    }

private:
    IMonitoringManagerPtr monitoringManager_;
    std::atomic<i64> totalRequests_{0};
    std::atomic<i64> successfulRequests_{0};
    std::atomic<i64> failedRequests_{0};
    std::atomic<i64> errorCount_{0};
    std::atomic<i64> activeConnections_{0};
    std::atomic<ui64> lastErrorTime_{0};
    THashMap<TString, i64> errorTypes_;
};
```

### HTTP 监控端点集成示例

```cpp
#include <yt/yt/library/monitoring/http_integration.h>

class MonitoringHttpServer {
public:
    MonitoringHttpServer(IMonitoringManagerPtr monitoringManager)
        : monitoringManager_(monitoringManager)
    {
        // 创建 HTTP 服务器
        httpServer_ = NHttp::CreateServer();

        // 设置监控处理器
        SetupMonitoringEndpoints();
    }

    void Start(int port) {
        // 启动 HTTP 服务器
        httpServer_->Start(port);
        Cout << "Monitoring HTTP server started on port " << port << Endl;
    }

    void Stop() {
        httpServer_->Stop();
    }

private:
    void SetupMonitoringEndpoints() {
        // 主监控端点
        httpServer_->AddHandler("/monitoring", CreateMonitoringHandler(monitoringManager_));

        // 健康检查端点
        httpServer_->AddHandler("/health", CreateHealthCheckHandler());

        // 自定义监控端点
        httpServer_->AddHandler("/metrics/prometheus", CreatePrometheusHandler(monitoringManager_));
        httpServer_->AddHandler("/metrics/json", CreateJsonHandler(monitoringManager_));
    }

    NHttp::IHandlerPtr CreateHealthCheckHandler() {
        return NHttp::CreateCallbackHandler([](const NHttp::IRequestPtr& request, const NHttp::IResponseWriterPtr& response) {
            NYson::BuildYsonFluently(NYson::CreateYsonConsumer(response->GetOutput()))
                .BeginMap()
                    .Item("status").Value("healthy")
                    .Item("timestamp").Value(TInstant::Now().ToString())
                .EndMap();
        });
    }

    NHttp::IHandlerPtr CreatePrometheusHandler(IMonitoringManagerPtr manager) {
        return NHttp::CreateCallbackHandler([manager](const NHttp::IRequestPtr& request, const NHttp::IResponseWriterPtr& response) {
            // 转换 Yson 格式到 Prometheus 格式
            ConvertToPrometheusFormat(manager->GetService(), response->GetOutput());
        });
    }

private:
    IMonitoringManagerPtr monitoringManager_;
    NHttp::IServerPtr httpServer_;
};
```

### 动态监控指标注册示例

```cpp
class DynamicMetricsCollector {
public:
    DynamicMetricsCollector(IMonitoringManagerPtr monitoringManager)
        : monitoringManager_(monitoringManager)
    {}

    void RegisterComponentMetrics(const TString& componentName) {
        auto metricsPath = "/components/" + componentName;

        // 动态注册组件监控指标
        monitoringManager_->Register(
            metricsPath + "/stats",
            BIND(&DynamicMetricsCollector::ProduceComponentStats, this, componentName)
        );

        monitoringManager_->Register(
            metricsPath + "/health",
            BIND(&DynamicMetricsCollector::ProduceComponentHealth, this, componentName)
        );

        registeredComponents_.push_back(componentName);
    }

    void UnregisterComponentMetrics(const TString& componentName) {
        auto metricsPath = "/components/" + componentName;

        // 注销组件监控指标
        monitoringManager_->Unregister(metricsPath + "/stats");
        monitoringManager_->Unregister(metricsPath + "/health");

        // 从注册列表中移除
        auto it = std::find(registeredComponents_.begin(), registeredComponents_.end(), componentName);
        if (it != registeredComponents_.end()) {
            registeredComponents_.erase(it);
        }
    }

private:
    void ProduceComponentStats(NYson::IYsonConsumer* consumer, const TString& componentName) {
        if (auto it = componentStats_.find(componentName); it != componentStats_.end()) {
            NYson::BuildYsonFluently(consumer)
                .BeginMap()
                    .Item("operations").Value(it->second.operations)
                    .Item("errors").Value(it->second.errors)
                    .Item("latency_ms").Value(it->second.latencyMs)
                    .Item("last_activity").Value(it->second.lastActivity.ToString())
                .EndMap();
        } else {
            NYson::BuildYsonFluently(consumer)
                .BeginMap()
                    .Item("status").Value("not_found")
                .EndMap();
        }
    }

    void ProduceComponentHealth(NYson::IYsonConsumer* consumer, const TString& componentName) {
        NYson::BuildYsonFluently(consumer)
            .BeginMap()
                .Item("healthy").Value(IsComponentHealthy(componentName))
                .Item("last_check").Value(TInstant::Now().ToString())
            .EndMap();
    }

    bool IsComponentHealthy(const TString& componentName) {
        // 简化的健康检查逻辑
        return componentStats_.find(componentName) != componentStats_.end();
    }

private:
    struct ComponentStats {
        i64 operations = 0;
        i64 errors = 0;
        double latencyMs = 0.0;
        TInstant lastActivity = TInstant::Zero();
    };

    IMonitoringManagerPtr monitoringManager_;
    THashMap<TString, ComponentStats> componentStats_;
    std::vector<TString> registeredComponents_;
};
```

### 自定义监控数据生产者示例

```cpp
class CustomMetricsProducer {
public:
    CustomMetricsProducer() {
        // 初始化计数器
        InitializeCounters();
    }

    NYson::TYsonProducer CreateProducer() {
        return BIND(&CustomMetricsProducer::ProduceMetrics, this);
    }

    void IncrementCounter(const TString& counterName, i64 delta = 1) {
        counters_[counterName] += delta;
    }

    void SetGauge(const TString& gaugeName, double value) {
        gauges_[gaugeName] = value;
    }

private:
    void InitializeCounters() {
        counters_["requests_processed"] = 0;
        counters_["errors_encountered"] = 0;
        counters_["connections_accepted"] = 0;

        gauges_["active_connections"] = 0.0;
        gauges_["queue_size"] = 0.0;
        gauges_["cpu_usage"] = 0.0;
    }

    void ProduceMetrics(NYson::IYsonConsumer* consumer) {
        NYson::BuildYsonFluently(consumer)
            .BeginMap()
                // 计数器
                .Item("counters").BeginMap()
                    .DoFor(counters_, [&] (T auto& builder, const auto& pair) {
                        builder.Item(pair.first).Value(pair.second);
                    })
                .EndMap()
                // 仪表盘
                .Item("gauges").BeginMap()
                    .DoFor(gauges_, [&] (T auto& builder, const auto& pair) {
                        builder.Item(pair.first).Value(pair.second);
                    })
                .EndMap()
                // 时间戳
                .Item("timestamp").Value(TInstant::Now().ToString())
            .EndMap();
    }

private:
    THashMap<TString, i64> counters_;
    THashMap<TString, double> gauges_;
};
```

## 配置说明

### 监控管理器配置

```cpp
struct TMonitoringManagerConfig {
    TDuration UpdateInterval = TDuration::Seconds(1);  // 更新间隔
    bool EnableCaching = true;                         // 启用缓存
    TDuration CacheTimeout = TDuration::Seconds(5);    // 缓存超时
    int MaxConcurrentRequests = 100;                   // 最大并发请求数
};
```

### HTTP 集成配置

```cpp
struct TMonitoringHttpConfig {
    int Port = 8080;                                   // HTTP 端口
    TString BindAddress = "0.0.0.0";                   // 绑定地址
    bool EnableSsl = false;                            // 启用 SSL
    TString SslCertificatePath;                        // SSL 证书路径
    TString SslPrivateKeyPath;                         // SSL 私钥路径
    TDuration RequestTimeout = TDuration::Seconds(30); // 请求超时
};
```

## 性能考虑

### 缓存策略
- **数据缓存**: 自动缓存生产者产生的监控数据
- **缓存更新**: 周期性更新缓存，平衡数据时效性和性能
- **内存管理**: 合理设置缓存大小，避免内存溢出

### 并发性能
- **线程安全**: 监控管理器支持多线程并发访问
- **异步更新**: 使用异步机制更新监控数据
- **负载均衡**: 合理分配监控请求负载

### 网络开销
- **数据压缩**: 支持数据压缩减少网络传输
- **批量请求**: 支持批量获取多个监控指标
- **增量更新**: 支持增量获取变更的监控数据

## 最佳实践

### 1. 监控数据结构设计

```cpp
class WellStructuredMetrics {
public:
    NYson::TYsonProducer GetProducer() {
        return BIND(&WellStructuredMetrics::ProduceStructuredMetrics, this);
    }

private:
    void ProduceStructuredMetrics(NYson::IYsonConsumer* consumer) {
        NYson::BuildYsonFluently(consumer)
            .BeginMap()
                // 应用层指标
                .Item("application").BeginMap()
                    .Item("requests").BeginMap()
                        .Item("total").Value(requestMetrics_.total)
                        .Item("success").Value(requestMetrics_.success)
                        .Item("error").Value(requestMetrics_.error)
                        .Item("rate_per_second").Value(CalculateRequestRate())
                    .EndMap()
                    .Item("latency").BeginMap()
                        .Item("p50").Value(latencyMetrics_.p50)
                        .Item("p95").Value(latencyMetrics_.p95)
                        .Item("p99").Value(latencyMetrics_.p99)
                    .EndMap()
                .EndMap()
                // 系统层指标
                .Item("system").BeginMap()
                    .Item("memory").BeginMap()
                        .Item("used_mb").Value(memoryMetrics_.usedMb)
                        .Item("available_mb").Value(memoryMetrics_.availableMb)
                        .Item("usage_percent").Value(memoryMetrics_.usagePercent)
                    .EndMap()
                    .Item("cpu").BeginMap()
                        .Item("usage_percent").Value(cpuMetrics_.usagePercent)
                        .Item("load_average").Value(cpuMetrics_.loadAverage)
                    .EndMap()
                .EndMap()
                // 业务层指标
                .Item("business").BeginMap()
                    .Item("active_users").Value(businessMetrics_.activeUsers)
                    .Item("transactions").Value(businessMetrics_.transactions)
                    .Item("revenue").Value(businessMetrics_.revenue)
                .EndMap()
            .EndMap();
    }

private:
    struct RequestMetrics {
        i64 total = 0;
        i64 success = 0;
        i64 error = 0;
    };

    struct LatencyMetrics {
        double p50 = 0.0;
        double p95 = 0.0;
        double p99 = 0.0;
    };

    struct MemoryMetrics {
        i64 usedMb = 0;
        i64 availableMb = 0;
        double usagePercent = 0.0;
    };

    struct CpuMetrics {
        double usagePercent = 0.0;
        double loadAverage = 0.0;
    };

    struct BusinessMetrics {
        i64 activeUsers = 0;
        i64 transactions = 0;
        double revenue = 0.0;
    };

    RequestMetrics requestMetrics_;
    LatencyMetrics latencyMetrics_;
    MemoryMetrics memoryMetrics_;
    CpuMetrics cpuMetrics_;
    BusinessMetrics businessMetrics_;
};
```

### 2. 错误处理和恢复

```cpp
class ResilientMonitoring {
public:
    ResilientMonitoring(IMonitoringManagerPtr manager) : manager_(manager) {}

    void RegisterSafeProducer(const TString& path, NYson::TYsonProducer producer) {
        auto safeProducer = CreateSafeProducer(producer);
        manager_->Register(path, safeProducer);
    }

private:
    NYson::TYsonProducer CreateSafeProducer(NYson::TYsonProducer originalProducer) {
        return [this, originalProducer] (NYson::IYsonConsumer* consumer) {
            try {
                originalProducer(consumer);
            } catch (const std::exception& e) {
                // 记录错误但不中断监控
                LogProducerError(e.what());

                // 产生错误指标
                NYson::BuildYsonFluently(consumer)
                    .BeginMap()
                        .Item("error").Value(true)
                        .Item("error_message").Value(e.what())
                        .Item("timestamp").Value(TInstant::Now().ToString())
                    .EndMap();
            }
        };
    }

    void LogProducerError(const TString& errorMessage) {
        // 记录生产者错误到日志系统
        Cout << "Monitoring producer error: " << errorMessage << Endl;
    }

private:
    IMonitoringManagerPtr manager_;
};
```

### 3. 监控数据采样和聚合

```cpp
class SamplingMetricsCollector {
public:
    SamplingMetricsCollector(int sampleSize = 1000) : sampleSize_(sampleSize) {}

    void AddSample(double value) {
        std::lock_guard<std::mutex> lock(mutex_);
        samples_.push_back(value);

        // 保持采样大小限制
        if (samples_.size() > sampleSize_) {
            samples_.pop_front();
        }
    }

    NYson::TYsonProducer GetProducer() {
        return BIND(&SamplingMetricsCollector::ProduceSamplingMetrics, this);
    }

private:
    void ProduceSamplingMetrics(NYson::IYsonConsumer* consumer) {
        std::lock_guard<std::mutex> lock(mutex_);

        if (samples_.empty()) {
            NYson::BuildYsonFluently(consumer)
                .BeginMap()
                    .Item("status").Value("no_data")
                .EndMap();
            return;
        }

        auto sortedSamples = samples_;
        std::sort(sortedSamples.begin(), sortedSamples.end());

        auto stats = CalculateStatistics(sortedSamples);

        NYson::BuildYsonFluently(consumer)
            .BeginMap()
                .Item("count").Value(sortedSamples.size())
                .Item("min").Value(stats.min)
                .Item("max").Value(stats.max)
                .Item("mean").Value(stats.mean)
                .Item("median").Value(stats.median)
                .Item("p95").Value(stats.p95)
                .Item("p99").Value(stats.p99)
                .Item("std_dev").Value(stats.stdDev)
            .EndMap();
    }

    struct Statistics {
        double min = 0.0;
        double max = 0.0;
        double mean = 0.0;
        double median = 0.0;
        double p95 = 0.0;
        double p99 = 0.0;
        double stdDev = 0.0;
    };

    Statistics CalculateStatistics(const std::vector<double>& sortedSamples) {
        Statistics stats;

        if (sortedSamples.empty()) return stats;

        stats.min = sortedSamples.front();
        stats.max = sortedSamples.back();

        // 计算平均值
        double sum = std::accumulate(sortedSamples.begin(), sortedSamples.end(), 0.0);
        stats.mean = sum / sortedSamples.size();

        // 计算中位数
        size_t middle = sortedSamples.size() / 2;
        stats.median = (sortedSamples.size() % 2 == 0) ?
            (sortedSamples[middle - 1] + sortedSamples[middle]) / 2.0 :
            sortedSamples[middle];

        // 计算百分位数
        stats.p95 = sortedSamples[static_cast<size_t>(sortedSamples.size() * 0.95)];
        stats.p99 = sortedSamples[static_cast<size_t>(sortedSamples.size() * 0.99)];

        // 计算标准差
        double variance = 0.0;
        for (double value : sortedSamples) {
            variance += (value - stats.mean) * (value - stats.mean);
        }
        variance /= sortedSamples.size();
        stats.stdDev = std::sqrt(variance);

        return stats;
    }

private:
    std::deque<double> samples_;
    int sampleSize_;
    std::mutex mutex_;
};
```

## 依赖项

- **YT Core**: 基础服务框架和 YPath 支持
- **YT YTree**: 树形数据结构和 Yson 支持
- **YT Yson**: Yson 格式处理
- **YT RPC**: RPC 服务框架
- **YT HTTP**: HTTP 服务器和客户端

## 注意事项

### 1. 性能影响
- 频繁的监控数据更新可能影响系统性能
- 合理设置更新间隔，避免过度监控
- 监控系统本身不应成为性能瓶颈

### 2. 内存管理
- 监控数据缓存会占用额外内存
- 长期运行的系统需要监控内存使用情况
- 及时清理不再需要的监控指标

### 3. 安全考虑
- 监控数据可能包含敏感信息
- 适当的访问控制和认证机制
- 考虑数据传输的加密需求

### 4. 可靠性
- 监控系统不应影响主业务逻辑
- 异常情况下监控系统应能正常恢复
- 提供降级机制保证基本监控功能

### 5. 扩展性
- 支持动态添加和删除监控指标
- 考虑分布式环境下的监控数据聚合
- 提供标准化的监控数据格式