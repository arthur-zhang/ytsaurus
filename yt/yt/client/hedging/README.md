# YTsaurus Hedging Client 模块

## 概述

Hedging Client 模块是 YTsaurus 的智能请求分发和故障转移系统，通过同时向多个集群发送请求来优化延迟和可用性。该模块实现了基于动态惩罚的负载均衡机制，能够自动适应集群健康状况和复制延迟，为用户提供高性能、高可用的客户端体验。

## 核心特性

### 1. 智能请求分发
- **并行请求**: 同时向多个集群发送相同请求
- **早期返回**: 第一个成功响应立即返回结果
- **请求取消**: 成功响应后自动取消其他待处理请求
- **延迟优化**: 基于惩罚值的智能调度

### 2. 动态惩罚系统
- **初始惩罚**: 为每个集群设置基础延迟
- **自适应惩罚**: 基于历史性能动态调整
- **外部惩罚**: 考虑复制延迟等外部因素
- **惩罚衰减**: 过期的惩罚自动失效

### 3. 复制延迟感知
- **实时监控**: 定期检查复制延迟状态
- **自动切换**: 延迟过高时自动切换集群
- **恢复检测**: 延迟恢复后自动重新启用

### 4. 故障恢复
- **自动封禁**: 失败集群自动封禁一段时间
- **渐进恢复**: 封禁期满后逐步恢复使用
- **健康检查**: 定期检查集群健康状态

## 架构设计

### 1. 核心组件

#### HedgingClient (对冲客户端)
```cpp
/*!
 * HedgingClient 是多个 YT 客户端的包装器，支持异步重试相同请求到不同客户端
 * 实现了 IClient 接口，支持不改变 YT 数据状态的方法
 * 支持的方法: LookupRows, VersionedLookupRows, SelectRows, ExplainQuery,
 *            CreateTableReader, GetNode, ListNode, NodeExists, CreateFileReader
 *
 * 每个客户端需要 InitialPenalty 值来决定使用顺序
 * MinInitialPenalty: 所有客户端中的最小重试超时值
 * EffectivePenalty: 对应客户端开始请求的延迟值
 * 对于每个客户端: EffectivePenalty = InitialPenalty - MinInitialPenalty
 *
 * 任何一个客户端成功响应时，其他客户端的请求会被取消
 *
 * 客户端错误响应时，其 InitialPenalty 会在 BanDuration 内增加 BanPenalty
 */
```

#### HedgingExecutor (对冲执行器)
```cpp
class THedgingExecutor {
    struct TNode {
        NApi::IClientPtr Client;        // 客户端实例
        TCounterPtr Counter;           // 性能计数器
        std::string ClusterName;       // 集群名称
        TDuration InitialPenalty;      // 初始惩罚值
        TDuration AdaptivePenalty;     // 自适应惩罚值
        TDuration ExternalPenalty;     // 外部惩罚值
        TInstant BanUntil;             // 封禁结束时间
    };

    template <typename T>
    TFuture<T> DoWithHedging(TCallback<TFuture<T>(NApi::IClientPtr)> callback);
};
```

#### PenaltyProvider (惩罚提供器)
```cpp
struct IPenaltyProvider : public TRefCounted {
    virtual TDuration Get(const std::string& cluster) = 0;
};
```

### 2. 配置体系

#### 基础连接配置 (TConnectionWithPenaltyConfig)
```cpp
struct TConnectionWithPenaltyConfig : public TConnectionConfig {
    TDuration InitialPenalty;  // 初始惩罚值

    REGISTER_YSON_STRUCT(TConnectionWithPenaltyConfig);
};
```

#### 对冲客户端配置 (THedgingClientOptions)
```cpp
struct THedgingClientOptions : public NYTree::TYsonStruct {
    std::vector<TConnectionWithPenaltyConfigPtr> Connections;  // 连接配置列表
    TDuration BanPenalty;        // 封禁惩罚增量
    TDuration BanDuration;       // 封禁持续时间
    THashMap<TString, TString> Tags;  // 标签信息

    REGISTER_YSON_STRUCT(THedgingClientOptions);
};
```

#### 复制延迟惩罚配置 (TReplicationLagPenaltyProviderOptions)
```cpp
struct TReplicationLagPenaltyProviderOptions : public NYTree::TYsonStruct {
    std::vector<std::string> ReplicaClusters;  // 副本集群列表
    NYPath::TYPath TablePath;                   // 监控的表路径
    TDuration LagPenalty;                       // 延迟惩罚值
    TDuration MaxReplicaLag;                    // 最大允许延迟
    TDuration CheckPeriod;                      // 检查周期
    bool ClearPenaltiesOnErrors;                // 错误时清除惩罚

    REGISTER_YSON_STRUCT(TReplicationLagPenaltyProviderOptions);
};
```

## 工作原理

### 1. 请求调度算法

```cpp
// 请求调度的核心逻辑
template <typename T>
TFuture<T> DoWithHedging(TCallback<TFuture<T>(NApi::IClientPtr)> callback) {
    auto now = TInstant::Now();

    // 1. 更新自适应惩罚值
    UpdateAdaptivePenalties(now);

    // 2. 获取外部惩罚值
    for (auto& node : nodes) {
        node.ExternalPenalty = PenaltyProvider_->Get(node.ClusterName);
    }

    // 3. 计算最小初始惩罚
    auto minInitialPenalty = FindMinInitialPenalty(nodes);

    // 4. 创建延迟执行的任务
    std::vector<TFuture<T>> futures;
    for (const auto& node : nodes) {
        auto effectivePenalty = CalculateEffectivePenalty(
            node.InitialPenalty,
            node.AdaptivePenalty,
            node.ExternalPenalty,
            minInitialPenalty
        );

        auto future = ExecuteWithDelay(node.Client, callback, effectivePenalty);
        futures.push_back(future);
    }

    // 5. 等待第一个成功结果
    return AnySucceeded(std::move(futures));
}
```

### 2. 惩罚值计算

```cpp
// 有效惩罚值计算
TDuration CalculateEffectivePenalty(
    TDuration initialPenalty,
    TDuration adaptivePenalty,
    TDuration externalPenalty,
    TDuration minInitialPenalty) {

    return initialPenalty + adaptivePenalty + externalPenalty - minInitialPenalty;
}
```

### 3. 自适应惩罚更新

```cpp
// 基于请求结果更新自适应惩罚
void OnFinishRequest(
    int index,
    TDuration effectivePenalty,
    TInstant start,
    const TError& error) {

    if (error.IsOK()) {
        // 成功请求: 减少惩罚
        UpdateSuccessPenalty(index, effectivePenalty);
    } else {
        // 失败请求: 增加惩罚并可能封禁
        UpdateFailurePenalty(index, error);
    }

    // 更新统计信息
    UpdateMetrics(index, start, error);
}
```

## 使用方法

### 1. 基本对冲客户端创建

```cpp
#include <yt/yt/client/hedging/public.h>
#include <yt/yt/client/hedging/hedging.h>

using namespace NYT::NClient::NHedging::NRpc;

// 创建连接配置
auto cluster1Config = New<TConnectionWithPenaltyConfig>();
cluster1Config->Addresses = {"cluster1.proxy.ytsaurus.net:9013"};
cluster1Config->InitialPenalty = TDuration::MilliSeconds(0);  // 优先集群

auto cluster2Config = New<TConnectionWithPenaltyConfig>();
cluster2Config->Addresses = {"cluster2.proxy.ytsaurus.net:9013"};
cluster2Config->InitialPenalty = TDuration::MilliSeconds(100);  // 备用集群

// 创建对冲客户端配置
auto hedgingConfig = New<THedgingClientOptions>();
hedgingConfig->Connections = {cluster1Config, cluster2Config};
hedgingConfig->BanPenalty = TDuration::Seconds(5);     // 失败增加5秒惩罚
hedgingConfig->BanDuration = TDuration::Minutes(1);   // 封禁1分钟

// 创建对冲客户端
auto hedgingClient = CreateHedgingClient(hedgingConfig);
```

### 2. 使用复制延迟感知的惩罚提供器

```cpp
// 配置复制延迟检查
auto lagConfig = New<TReplicationLagPenaltyProviderOptions>();
lagConfig->ReplicaClusters = {"replica1", "replica2"};
lagConfig->TablePath = "/path/to/replicated/table";
lagConfig->LagPenalty = TDuration::Seconds(10);
lagConfig->MaxReplicaLag = TDuration::Minutes(5);
lagConfig->CheckPeriod = TDuration::Seconds(30);
lagConfig->ClearPenaltiesOnErrors = true;

// 创建主客户端用于检查复制延迟
auto masterClient = CreateClient("master-cluster");

// 创建惩罚提供器
auto penaltyProvider = CreateReplicationLagPenaltyProvider(lagConfig, masterClient);

// 创建带惩罚提供器的对冲客户端
NApi::TClientOptions clientOptions;
clientOptions.Token = "your-auth-token";

auto hedgingClient = CreateHedgingClient(
    hedgingConfig,
    penaltyProvider,
    clientOptions);
```

### 3. 使用客户端缓存

```cpp
#include <yt/yt/client/cache/public.h>

// 创建客户端缓存
auto clientsCache = CreateClientsCache(cacheConfig);

// 创建对冲客户端（使用缓存）
auto hedgingClient = CreateHedgingClient(hedgingConfig, clientsCache);
```

### 4. 执行查询

```cpp
// 使用对冲客户端执行查询
auto selectRowsResult = hedgingClient->SelectRows("select * from `/table` where key = 42");
auto rows = WaitFor(selectRowsResult).ValueOrThrow();

// 查找行
auto lookupRowsResult = hedgingClient->LookupRows(
    "/table",
    NTableClient::TNameTablePtr(),
    NTableClient::TVersionedRowMapperPtr(),
    lookupRequest);

// 获取节点信息
auto nodeResult = hedgingClient->GetNode("/path/to/node", options);
```

## 高级配置

### 1. 惩罚值调优

```cpp
// 根据网络延迟调优初始惩罚
struct ClusterLatencyProfile {
    TString ClusterName;
    TDuration AverageLatency;
    TDuration P99Latency;
    double Availability;
};

std::vector<ClusterLatencyProfile> profiles = {
    {"primary", TDuration::MilliSeconds(50), TDuration::MilliSeconds(200), 0.99},
    {"secondary", TDuration::MilliSeconds(100), TDuration::MilliSeconds(400), 0.95},
    {"tertiary", TDuration::MilliSeconds(200), TDuration::MilliSeconds(800), 0.90}
};

auto CreateOptimizedConfig(const std::vector<ClusterLatencyProfile>& profiles) {
    auto config = New<THedgingClientOptions>();

    for (const auto& profile : profiles) {
        auto connectionConfig = New<TConnectionWithPenaltyConfig>();
        connectionConfig->Addresses = {profile.ClusterName + ".proxy.ytsaurus.net:9013"};

        // 基于延迟和可用性计算初始惩罚
        double score = profile.Availability * 1000.0 / profile.AverageLatency.MilliSeconds();
        connectionConfig->InitialPenalty = TDuration::MilliSeconds(static_cast<i64>(1000.0 / score));

        config->Connections.push_back(connectionConfig);
    }

    return config;
}
```

### 2. 自定义惩罚提供器

```cpp
// 实现自定义惩罚逻辑
class CustomPenaltyProvider : public IPenaltyProvider {
private:
    std::unordered_map<std::string, TDuration> customPenalties_;

public:
    TDuration Get(const std::string& cluster) override {
        auto it = customPenalties_.find(cluster);
        if (it != customPenalties_.end()) {
            return it->second;
        }

        // 基于外部系统获取惩罚值
        return GetExternalPenalty(cluster);
    }

    void UpdatePenalty(const std::string& cluster, TDuration penalty) {
        customPenalties_[cluster] = penalty;
    }

private:
    TDuration GetExternalPenalty(const std::string& cluster) {
        // 查询监控系统获取集群健康状态
        return TDuration::Zero();
    }
};
```

### 3. 性能监控

```cpp
// 自定义计数器
struct THedgingMetrics {
    std::atomic<i64> TotalRequests{0};
    std::atomic<i64> SuccessfulRequests{0};
    std::atomic<i64> FailedRequests{0};

    std::unordered_map<std::string, std::atomic<i64>> ClusterRequests;
    std::unordered_map<std::string, std::atomic<i64>> ClusterSuccesses;
    std::unordered_map<std::string, TAtomicDuration> ClusterResponseTimes;

    void RecordRequest(const std::string& cluster, bool success, TDuration responseTime) {
        TotalRequests++;
        ClusterRequests[cluster]++;

        if (success) {
            SuccessfulRequests++;
            ClusterSuccesses[cluster]++;
        } else {
            FailedRequests++;
        }

        ClusterResponseTimes[cluster].Store(responseTime);
    }

    void PrintMetrics() const {
        double successRate = static_cast<double>(SuccessfulRequests) / TotalRequests;
        YT_LOG_INFO("Hedging metrics (Total: %v, Success Rate: %.2f%%)",
            TotalRequests.load(), successRate * 100);

        for (const auto& [cluster, requests] : ClusterRequests) {
            auto successes = ClusterSuccesses.at(cluster).load();
            auto avgTime = ClusterResponseTimes.at(cluster).Load();
            double clusterSuccessRate = static_cast<double>(successes) / requests;

            YT_LOG_INFO("Cluster metrics (Name: %v, Requests: %v, Success Rate: %.2f%%, Avg Time: %v)",
                cluster, requests, clusterSuccessRate * 100, avgTime);
        }
    }
};
```

## 性能优化

### 1. 网络优化

```cpp
// 连接池配置
struct ConnectionPoolConfig {
    int MaxConnectionsPerCluster = 10;
    TDuration ConnectionTimeout = TDuration::Seconds(10);
    TDuration RequestTimeout = TDuration::Minutes(5);
    bool EnableConnectionReuse = true;
    bool EnableCompression = true;
};

// HTTP 优化
struct HttpOptimizationConfig {
    bool EnableHttp2 = true;           // HTTP/2 多路复用
    bool EnableTcpKeepAlive = true;     // TCP Keep-Alive
    TDuration TcpKeepAliveTimeout = TDuration::Seconds(30);
    int MaxConcurrentRequests = 100;
};
```

### 2. 内存管理

```cpp
// 内存池管理
class HedgingMemoryPool {
private:
    std::vector<std::unique_ptr<char[]>> buffers_;
    std::queue<char*> availableBuffers_;
    size_t bufferSize_;

public:
    char* AcquireBuffer() {
        if (availableBuffers_.empty()) {
            buffers_.emplace_back(std::make_unique<char[]>(bufferSize_));
            return buffers_.back().get();
        }
        auto* buffer = availableBuffers_.front();
        availableBuffers_.pop();
        return buffer;
    }

    void ReleaseBuffer(char* buffer) {
        availableBuffers_.push(buffer);
    }
};
```

### 3. 并发控制

```cpp
// 请求限制器
class RequestLimiter {
private:
    std::atomic<int> activeRequests_{0};
    int maxConcurrentRequests_;

public:
    RequestLimiter(int maxConcurrent) : maxConcurrentRequests_(maxConcurrent) {}

    bool TryAcquire() {
        int current = activeRequests_.load();
        while (current < maxConcurrentRequests_) {
            if (activeRequests_.compare_exchange_weak(current, current + 1)) {
                return true;
            }
        }
        return false;
    }

    void Release() {
        activeRequests_.fetch_sub(1);
    }
};
```

## 监控和诊断

### 1. 关键指标

```cpp
struct HedgingClientMetrics {
    // 请求统计
    std::atomic<i64> TotalRequests{0};
    std::atomic<i64> HedgedRequests{0};
    std::atomic<i64> CancelledRequests{0};

    // 延迟统计
    TDuration AverageResponseTime;
    TDuration P95ResponseTime;
    TDuration P99ResponseTime;

    // 集群状态
    std::unordered_map<std::string, ClusterHealthMetrics> ClusterMetrics;

    // 惩罚统计
    std::unordered_map<std::string, TDuration> CurrentPenalties;
    std::unordered_map<std::string, int> BanCount;
};

struct ClusterHealthMetrics {
    double Availability;
    TDuration AverageLatency;
    TDuration CurrentPenalty;
    TInstant LastSuccessfulRequest;
    TInstant LastFailedRequest;
    bool IsCurrentlyBanned;
};
```

### 2. 日志记录

```cpp
// 结构化日志
class HedgingLogger {
public:
    void LogRequestStart(
        const std::string& requestId,
        const std::vector<std::string>& clusters) {

        YT_LOG_INFO("Hedging request started (RequestId: %v, Clusters: [%v])",
            requestId, JoinStrings(clusters, ", "));
    }

    void LogClusterAttempt(
        const std::string& requestId,
        const std::string& cluster,
        TDuration penalty) {

        YT_LOG_DEBUG("Attempting cluster (RequestId: %v, Cluster: %v, Penalty: %v)",
            requestId, cluster, penalty);
    }

    void LogRequestCompletion(
        const std::string& requestId,
        const std::string& winningCluster,
        TDuration totalTime,
        const std::vector<std::string>& cancelledClusters) {

        YT_LOG_INFO("Hedging request completed (RequestId: %v, Winner: %v, Time: %v, Cancelled: [%v])",
            requestId, winningCluster, totalTime, JoinStrings(cancelledClusters, ", "));
    }
};
```

### 3. 健康检查

```cpp
// 集群健康检查
class ClusterHealthChecker {
private:
    std::unordered_map<std::string, TInstant> lastHealthCheck_;
    TDuration checkInterval_;

public:
    bool IsHealthy(const std::string& cluster) {
        auto now = TInstant::Now();
        auto it = lastHealthCheck_.find(cluster);

        if (it == lastHealthCheck_.end() ||
            now - it->second > checkInterval_) {

            // 执行健康检查
            bool isHealthy = PerformHealthCheck(cluster);
            lastHealthCheck_[cluster] = now;
            return isHealthy;
        }

        return true;  // 假设仍然健康
    }

private:
    bool PerformHealthCheck(const std::string& cluster) {
        try {
            auto client = GetClientForCluster(cluster);
            auto result = WaitFor(client->GetNode("//sys/@cluster_name", {}))
                .ValueOrThrow();
            return true;
        } catch (const std::exception& e) {
            YT_LOG_WARNING("Health check failed (Cluster: %v, Error: %v)",
                cluster, e.what());
            return false;
        }
    }
};
```

## 最佳实践

### 1. 集群选择策略

```cpp
// 集群选择策略
enum class EClusterSelectionStrategy {
    PrimaryFirst,      // 优先使用主集群
    RoundRobin,        // 轮询
    LatencyBased,      // 基于延迟
    LoadBalanced       // 负载均衡
};

class ClusterSelector {
public:
    std::vector<std::string> SelectClusters(
        EClusterSelectionStrategy strategy,
        const std::vector<ClusterInfo>& availableClusters) {

        switch (strategy) {
            case EClusterSelectionStrategy::PrimaryFirst:
                return SelectPrimaryFirst(availableClusters);
            case EClusterSelectionStrategy::RoundRobin:
                return SelectRoundRobin(availableClusters);
            case EClusterSelectionStrategy::LatencyBased:
                return SelectByLatency(availableClusters);
            case EClusterSelectionStrategy::LoadBalanced:
                return SelectLoadBalanced(availableClusters);
        }
    }
};
```

### 2. 错误处理

```cpp
// 分层错误处理
class HedgingErrorHandler {
public:
    TError HandleHedgingError(
        const std::vector<TError>& clusterErrors,
        const std::string& requestId) {

        // 分析错误模式
        auto errorAnalysis = AnalyzeErrors(clusterErrors);

        if (errorAnalysis.AllClustersTimeout) {
            return TError("All clusters timed out")
                << TErrorAttribute("request_id", requestId);
        }

        if (errorAnalysis.MostClustersUnavailable) {
            return TError("Most clusters unavailable")
                << TErrorAttribute("available_clusters", errorAnalysis.AvailableCount)
                << TErrorAttribute("total_clusters", errorAnalysis.TotalCount);
        }

        // 返回最有意义的错误
        return SelectMostRelevantError(clusterErrors);
    }

private:
    struct ErrorAnalysis {
        bool AllClustersTimeout = false;
        bool MostClustersUnavailable = false;
        int AvailableCount = 0;
        int TotalCount = 0;
    };

    ErrorAnalysis AnalyzeErrors(const std::vector<TError>& errors) {
        ErrorAnalysis analysis;
        analysis.TotalCount = errors.size();

        int timeoutCount = 0;
        int unavailableCount = 0;

        for (const auto& error : errors) {
            if (error.FindMatching(NYT::NRpc::EErrorCode::Timeout)) {
                timeoutCount++;
            }
            if (error.FindMatching(NYT::NRpc::EErrorCode::Unavailable)) {
                unavailableCount++;
            }

            if (error.IsOK()) {
                analysis.AvailableCount++;
            }
        }

        analysis.AllClustersTimeout = (timeoutCount == errors.size());
        analysis.MostClustersUnavailable =
            (unavailableCount > errors.size() / 2);

        return analysis;
    }
};
```

### 3. 配置模板

```cpp
// 生产环境配置模板
THedgingClientOptionsPtr CreateProductionConfig() {
    auto config = New<THedgingClientOptions>();

    // 主集群（优先）
    auto primaryConfig = New<TConnectionWithPenaltyConfig>();
    primaryConfig->Addresses = {"primary-cluster.proxy.ytsaurus.net:9013"};
    primaryConfig->InitialPenalty = TDuration::Zero();

    // 备用集群1（同城）
    auto secondaryConfig = New<TConnectionWithPenaltyConfig>();
    secondaryConfig->Addresses = {"secondary-cluster.proxy.ytsaurus.net:9013"};
    secondaryConfig->InitialPenalty = TDuration::MilliSeconds(50);

    // 备用集群2（异地）
    auto tertiaryConfig = New<TConnectionWithPenaltyConfig>();
    tertiaryConfig->Addresses = {"tertiary-cluster.proxy.ytsaurus.net:9013"};
    tertiaryConfig->InitialPenalty = TDuration::MilliSeconds(200);

    config->Connections = {primaryConfig, secondaryConfig, tertiaryConfig};
    config->BanPenalty = TDuration::Seconds(10);      // 保守的惩罚策略
    config->BanDuration = TDuration::Minutes(2);      // 较长的封禁时间

    return config;
}
```

## 依赖项

### 内部依赖
- `yt/yt/client/cache/public.h` - 客户端缓存
- `yt/yt/client/api/public.h` - API 客户端接口
- `yt/yt/client/api/rpc_proxy/config.h` - RPC 代理配置
- `yt/yt/core/profiling/public.h` - 性能分析
- `yt/yt/core/rpc/dispatcher.h` - RPC 调度器

### 外部依赖
- 网络通信库
- 性能监控库
- 线程库
- 时间和日期库

## 扩展性

### 1. 自定义对冲策略

```cpp
// 对冲策略接口
class IHedgingStrategy {
public:
    virtual std::vector<TFuture<TResult>>> ExecuteWithHedging(
        const std::vector<NApi::IClientPtr>& clients,
        const TRequest& request) = 0;
};

// 实现自定义策略
class CustomHedgingStrategy : public IHedgingStrategy {
public:
    std::vector<TFuture<TResult>> ExecuteWithHedging(
        const std::vector<NApi::IClientPtr>& clients,
        const TRequest& request) override {

        // 自定义对冲逻辑
        return ImplementCustomHedging(clients, request);
    }
};
```

### 2. 插件架构

```cpp
// 惩罚提供器插件
class IPenaltyProviderPlugin {
public:
    virtual std::string GetName() const = 0;
    virtual IPenaltyProviderPtr CreateProvider(const NYTree::IMapNodePtr& config) = 0;
    virtual void ValidateConfig(const NYTree::IMapNodePtr& config) const = 0;
};
```

## 版本兼容性

- **API 兼容性**: 保持向后兼容的接口
- **配置兼容性**: 新配置项有默认值
- **协议兼容性**: 支持多版本客户端和集群

## 相关模块

- **Cache Client**: 客户端缓存系统
- **RPC Client**: RPC 通信层
- **Table Client**: 表数据操作
- **Object Client**: 对象存储接口

## 参考文档

- [YTsaurus 对冲客户端指南](../../../docs/hedging-client.md)
- [多集群故障转移策略](../../../docs/multi-cluster-failover.md)
- [复制延迟监控](../../../docs/replication-lag.md)
- [性能优化最佳实践](../../../docs/performance-optimization.md)

## 贡献指南

在修改此模块时：
1. 确保线程安全
2. 添加充分的性能测试
3. 考虑网络分区和故障场景
4. 更新监控指标
5. 保持配置向后兼容
6. 添加详细的错误日志