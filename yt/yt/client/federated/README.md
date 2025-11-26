# YTsaurus Federated Client 模块

## 概述

Federated Client 模块是 YTsaurus 的联邦客户端实现，提供了跨多个 YTsaurus 集群的统一访问接口。该模块支持自动故障转移、负载均衡和跨集群数据访问，为用户提供了透明的多集群操作体验。

## 核心特性

### 1. 多集群统一访问
- 支持同时连接多个 YTsaurus 集群
- 统一的客户端接口，隐藏集群差异
- 透明的跨集群操作支持

### 2. 自动故障转移
- 集群不可用时自动切换到可用集群
- 智能重试机制和错误处理
- 优先选择同数据中心的集群

### 3. 健康检查机制
- 定期检查集群健康状态
- Cypress 根节点可用性检查
- 动态更新集群可用性信息

### 4. 客户端缓存
- 集群客户端缓存和复用
- 联邦客户端和通用客户端统一管理
- 连接池优化

## 主要组件

### 1. 联邦客户端 (IFederatedClient)

```cpp
//! 联邦客户端是多个底层客户端的包装器
//! 支持在出现错误时异步重试不同集群的请求
//! 每个 YT 客户端通常对应不同的 YT 集群
//! 同数据中心的客户端具有更高的优先级
NApi::IClientPtr CreateClient(
    std::vector<NApi::IClientPtr> clients,
    TFederationConfigPtr config);
```

#### 特性
- 实现 `IClient` 接口
- 支持跨集群重试
- 优先同数据中心访问
- 事务内支持有限的可变操作

### 2. 联邦配置 (TFederationConfig)

```cpp
struct TFederationConfig : public virtual NYTree::TYsonStruct {
    std::optional<std::string> BundleName;           // Bundle 名称
    TDuration ClusterHealthCheckPeriod;             // 健康检查周期
    bool CheckCypressRoot;                          // 检查 Cypress 根节点
    int ClusterRetryAttempts;                       // 重试次数
    bool RetryAnyError;                             // 重试任意错误（测试用）
};
```

### 3. 连接配置 (TConnectionConfig)

```cpp
struct TConnectionConfig : public TFederationConfig {
    std::vector<NApi::NRpcProxy::TConnectionConfigPtr> RpcProxyConnections;
    // 继承 TFederationConfig 的所有配置
};
```

### 4. 客户端缓存

```cpp
NCache::IClientsCachePtr CreateFederatedClientsCache(
    TConnectionConfigPtr federatedConfig,
    const NCache::TClientsCacheConfigPtr& clientsCacheConfig,
    const NYT::NApi::TClientOptions& options,
    TString clusterSeparator = "+");
```

## 使用方法

### 1. 基本联邦客户端创建

```cpp
#include <yt/yt/client/federated/public.h>
#include <yt/yt/client/federated/client.h>

using namespace NYT::NClient::NFederated;

// 创建多个集群的客户端
std::vector<NApi::IClientPtr> clients;
clients.push_back(CreateClientForCluster("cluster1"));
clients.push_back(CreateClientForCluster("cluster2"));

// 配置联邦客户端
auto config = New<TFederationConfig>();
config->ClusterRetryAttempts = 3;
config->ClusterHealthCheckPeriod = TDuration::Seconds(30);
config->CheckCypressRoot = true;
config->BundleName = "my-bundle";

// 创建联邦客户端
auto federatedClient = CreateClient(clients, config);
```

### 2. 使用连接配置

```cpp
// 创建连接配置
auto connectionConfig = New<TConnectionConfig>();
connectionConfig->ClusterRetryAttempts = 5;
connectionConfig->ClusterHealthCheckPeriod = TDuration::Minutes(1);

// 添加多个集群的 RPC 代理连接
auto cluster1Config = New<NApi::NRpcProxy::TConnectionConfig>();
cluster1Config->Addresses = {"cluster1.proxy.ytsaurus.net:9013"};

auto cluster2Config = New<NApi::NRpcProxy::TConnectionConfig>();
cluster2Config->Addresses = {"cluster2.proxy.ytsaurus.net:9013"};

connectionConfig->RpcProxyConnections = {cluster1Config, cluster2Config};

// 创建连接选项
NApi::NRpcProxy::TConnectionOptions options;
options.Token = "your-auth-token";

// 创建联邦连接
auto federatedConnection = CreateConnection(connectionConfig, options);
auto client = federatedConnection->CreateClient(options);
```

### 3. 客户端缓存使用

```cpp
// 创建联邦客户端缓存
auto cacheConfig = New<NCache::TClientsCacheConfig>();
cacheConfig->ExpireAfterSuccessfulUpdateTime = TDuration::Minutes(10);
cacheConfig->ExpireAfterFailedUpdateTime = TDuration::Minutes(1);

auto federatedConfig = New<TConnectionConfig>();
// ... 配置联邦客户端

NApi::TClientOptions options;
options.Token = "your-token";

auto clientsCache = CreateFederatedClientsCache(
    federatedConfig, cacheConfig, options);

// 使用缓存获取客户端
auto singleClient = clientsCache->GetClient("single-cluster");
auto federatedClient = clientsCache->GetClient("cluster1+cluster2+cluster3");
```

### 4. 事务支持

```cpp
// 创建事务（在联邦客户端中）
auto transaction = federatedClient->StartTransaction(NApi::ETransactionType::Master);

// 尝试获取粘性代理地址（如果支持）
if (auto* federatedTx = dynamic_cast<IFederatedClientTransactionMixin*>(transaction.Get())) {
    if (auto stickyProxy = federatedTx->TryGetStickyProxyAddress()) {
        YT_LOG_INFO("Transaction sticky proxy: %v", *stickyProxy);
    }
}

// 执行事务操作
transaction->CreateNode("/my-path", EObjectType::MapNode);
transaction->Commit();
```

## 配置详解

### 1. 核心配置参数

#### BundleName
- **类型**: `std::optional<std::string>`
- **描述**: Bundle 名称，用于健康检查
- **用途**: 监控特定 Bundle 的可用性
- **示例**: `"production-bundle"`

#### ClusterHealthCheckPeriod
- **类型**: `TDuration`
- **描述**: 集群健康检查间隔
- **默认**: 几分钟
- **建议**: 根据集群稳定性调整

#### CheckCypressRoot
- **类型**: `bool`
- **描述**: 是否检查 Cypress 根节点可用性
- **用途**: 更准确的健康检查
- **开销**: 增加少量网络请求

#### ClusterRetryAttempts
- **类型**: `int`
- **描述**: 跨集群重试次数
- **默认**: 3
- **建议**: 根据集群数量和可靠性调整

#### RetryAnyError
- **类型**: `bool`
- **描述**: 是否重试任意错误（仅用于测试）
- **生产环境**: 应设置为 `false`

### 2. 高级配置

```cpp
// 生产环境推荐配置
auto config = New<TFederationConfig>();
config->BundleName = "production";
config->ClusterHealthCheckPeriod = TDuration::Minutes(2);
config->CheckCypressRoot = true;
config->ClusterRetryAttempts = 3;
config->RetryAnyError = false;  // 生产环境必须为 false

// 开发环境配置
auto devConfig = New<TFederationConfig>();
devConfig->ClusterHealthCheckPeriod = TDuration::Seconds(30);
devConfig->CheckCypressRoot = false;  // 开发环境可以跳过
devConfig->ClusterRetryAttempts = 5;
devConfig->RetryAnyError = true;     // 测试时启用
```

## 故障转移机制

### 1. 集群优先级
1. **同数据中心集群**: 最高优先级
2. **相邻数据中心**: 中等优先级
3. **远程数据中心**: 最低优先级

### 2. 错误处理策略
```cpp
// 错误分类和处理
enum class EErrorCategory {
    Transient,    // 临时错误，可重试
    Persistent,   // 持久错误，切换集群
    Validation    // 验证错误，不重试
};

bool ShouldRetryError(const TError& error) {
    if (error.IsRetriable()) {
        return true;
    }
    // 检查特定的可重试错误
    return error.GetErrorCode() == SomeNetworkErrorCode;
}
```

### 3. 重试算法
- **指数退避**: 避免重试风暴
- **抖动**: 防止同步重试
- **熔断机制**: 快速失败避免级联故障

## 性能优化

### 1. 连接复用
```cpp
// 客户端缓存优化
struct ClientCacheMetrics {
    size_t ActiveConnections;      // 活跃连接数
    size_t IdleConnections;        // 空闲连接数
    TDuration AverageLatency;      // 平均延迟
    double CacheHitRate;          // 缓存命中率
};
```

### 2. 健康检查优化
```cpp
// 高效的健康检查
class HealthChecker {
private:
    TConcurrentHashMap<TString, THealthStatus> clusterHealth_;
    std::atomic<TDuration> lastCheckTime_;

public:
    bool IsClusterHealthy(const TString& clusterName) {
        auto it = clusterHealth_.find(clusterName);
        return it != clusterHealth_.end() &&
               it->second.Status == EHealthStatus::Healthy &&
               (TInstant::Now() - it->second.LastCheck) < MaxStaleTime;
    }
};
```

### 3. 负载均衡策略
```cpp
// 基于性能的负载均衡
struct ClusterMetrics {
    double CpuUtilization;        // CPU 使用率
    double MemoryUtilization;     // 内存使用率
    double NetworkLatency;        // 网络延迟
    int ActiveRequests;           // 活跃请求数
    double SuccessRate;          // 成功率

    double GetScore() const {
        // 综合评分算法
        return (1.0 - CpuUtilization) * 0.3 +
               (1.0 - MemoryUtilization) * 0.3 +
               (1.0 / (1.0 + NetworkLatency)) * 0.2 +
               (1.0 - ActiveRequests / 1000.0) * 0.1 +
               SuccessRate * 0.1;
    }
};
```

## 监控和诊断

### 1. 关键指标
```cpp
struct FederatedClientMetrics {
    // 请求指标
    i64 TotalRequests;           // 总请求数
    i64 SuccessfulRequests;      // 成功请求数
    i64 FailedRequests;          // 失败请求数
    i64 RetriedRequests;         // 重试请求数

    // 延迟指标
    TDuration AverageLatency;    // 平均延迟
    TDuration P95Latency;        // 95分位延迟
    TDuration P99Latency;        // 99分位延迟

    // 集群指标
    std::unordered_map<TString, i64> ClusterRequestCounts;
    std::unordered_map<TString, bool> ClusterHealthStatus;
    std::unordered_map<TString, TDuration> ClusterResponseTimes;
};
```

### 2. 日志记录
```cpp
// 结构化日志示例
YT_LOG_INFO("Federated client request (Cluster: %v, Operation: %v, Duration: %v, Success: %v)",
    clusterName, operationName, duration, success);

YT_LOG_WARNING("Cluster failover (From: %v, To: %v, Reason: %v)",
    fromCluster, toCluster, failoverReason);

YT_LOG_DEBUG("Health check completed (Cluster: %v, Status: %v, Latency: %v)",
    clusterName, healthStatus, checkLatency);
```

### 3. 诊断工具
```cpp
// 集群状态查询
struct ClusterStatus {
    TString ClusterName;
    bool IsHealthy;
    TDuration LastCheckTime;
    double SuccessRate;
    i64 ActiveConnections;
    TDuration AverageResponseTime;
};

std::vector<ClusterStatus> GetClusterStatuses(IFederatedClientPtr client);
```

## 最佳实践

### 1. 配置建议
```cpp
// 生产环境配置模板
auto CreateProductionConfig() {
    auto config = New<TFederationConfig>();
    config->BundleName = "production";
    config->ClusterHealthCheckPeriod = TDuration::Minutes(5);
    config->CheckCypressRoot = true;
    config->ClusterRetryAttempts = 3;
    config->RetryAnyError = false;
    return config;
}

// 开发环境配置模板
auto CreateDevelopmentConfig() {
    auto config = New<TFederationConfig>();
    config->ClusterHealthCheckPeriod = TDuration::Seconds(30);
    config->CheckCypressRoot = false;
    config->ClusterRetryAttempts = 5;
    config->RetryAnyError = true;
    return config;
}
```

### 2. 错误处理
```cpp
// 完善的错误处理
template<typename T>
TResult<T> ExecuteWithFallback(std::function<T()> operation) {
    std::vector<std::exception_ptr> errors;

    for (int attempt = 0; attempt < maxRetryAttempts_; ++attempt) {
        try {
            return operation();
        } catch (const TFederatedClientException& e) {
            errors.push_back(std::current_exception());
            YT_LOG_WARNING("Federated client operation failed (Attempt: %v, Error: %v)",
                attempt, e);
            continue;
        }
    }

    throw TFederatedClientException("All retries failed", errors);
}
```

### 3. 性能调优
```cpp
// 性能优化配置
struct PerformanceConfig {
    TDuration ConnectionTimeout = TDuration::Seconds(10);
    TDuration RequestTimeout = TDuration::Minutes(5);
    int MaxConcurrentRequests = 100;
    int MaxConnectionsPerCluster = 10;
    bool EnableConnectionPooling = true;
    bool EnableRequestCaching = false;  // 数据一致性考虑
};
```

## 依赖项

### 内部依赖
- `yt/yt/client/api/public.h` - API 客户端接口
- `yt/yt/client/api/rpc_proxy/public.h` - RPC 代理接口
- `yt/yt/client/cache/cache.h` - 客户端缓存
- `yt/yt/core/ytree/yson_struct.h` - YSON 结构支持

### 外部依赖
- 网络库 (libcurl, asio)
- 压缩库
- 加密库
- 监控和指标库

## 扩展性

### 1. 自定义健康检查
```cpp
class ICustomHealthChecker {
public:
    virtual TFuture<THealthCheckResult> CheckCluster(
        const TString& clusterName) = 0;
    virtual void UpdateMetrics(const THealthCheckResult& result) = 0;
};
```

### 2. 自定义负载均衡
```cpp
class ICustomLoadBalancer {
public:
    virtual TString SelectCluster(
        const std::vector<TString>& availableClusters,
        const TRequestContext& context) = 0;
};
```

### 3. 插件架构
- 健康检查插件
- 负载均衡插件
- 监控插件
- 认证插件

## 故障排除

### 1. 常见问题

#### 连接超时
- **原因**: 网络问题或集群过载
- **解决**: 检查网络连接，调整超时配置

#### 认证失败
- **原因**: 令牌过期或权限不足
- **解决**: 更新令牌，检查权限配置

#### 集群不可用
- **原因**: 集群维护或故障
- **解决**: 等待恢复或切换其他集群

### 2. 调试工具
```cpp
// 启用详细日志
NYT::NLogging::TLogger Logger{"FederatedClient"};
Logger.SetLevel(NYT::NLogging::ELogLevel::Debug);

// 集群状态检查
void PrintClusterStatus(IFederatedClientPtr client) {
    auto statuses = GetClusterStatuses(client);
    for (const auto& status : statuses) {
        std::cout << "Cluster: " << status.ClusterName
                  << ", Healthy: " << status.IsHealthy
                  << ", Success Rate: " << status.SuccessRate << std::endl;
    }
}
```

## 版本兼容性

- **API 兼容性**: 保持向后兼容
- **配置兼容性**: 新增配置项有默认值
- **协议兼容性**: 支持多版本协议

## 相关文档

- [YTsaurus 多集群架构](../../../docs/multi-cluster.md)
- [联邦客户端使用指南](../../../docs/federated-client.md)
- [故障转移最佳实践](../../../docs/failover.md)
- [客户端配置参考](../../../docs/client-config.md)

## 贡献指南

在贡献代码时：
1. 确保新功能向后兼容
2. 添加充分的测试覆盖
3. 考虑性能影响
4. 更新相关文档
5. 遵循错误处理最佳实践