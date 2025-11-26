# Orchid (服务监控与诊断)

## 项目概述

Orchid 模块提供了 YTsaurus 系统的服务监控和诊断功能。该模块基于 YPath 服务架构，提供了一个统一的接口来访问和监控系统中各种服务的状态、配置和性能指标。

## 核心功能

### 服务监控
- **树形结构监控**: 以树形结构组织监控数据
- **实时状态更新**: 提供实时的服务状态信息
- **配置管理**: 动态查看和修改服务配置
- **性能指标**: 收集和展示性能相关指标

### RPC 服务集成
- **认证支持**: 集成身份验证机制保护敏感数据
- **并发访问**: 支持多客户端并发访问
- **服务发现**: 自动发现和注册监控服务
- **路径导航**: 通过 YPath 路径导航监控数据

### 诊断工具
- **服务诊断**: 提供服务健康状态诊断
- **配置验证**: 验证服务配置的正确性
- **问题定位**: 帮助快速定位系统问题
- **历史数据**: 支持历史监控数据查看

## 主要接口

### 服务创建接口

```cpp
namespace NYT::NOrchid {

// 创建 Orchid 服务
NRpc::IServicePtr CreateOrchidService(
    NYTree::INodePtr root,              // 根节点
    IInvokerPtr invoker,                // 调用器
    NRpc::IAuthenticatorPtr authenticator);  // 认证器

} // namespace NYT::NOrchid
```

### 代理服务接口

```cpp
// Orchid 服务代理
class IOrchidServiceProxy
{
public:
    // 获取服务状态
    TFuture<NYTree::INodePtr> GetServiceStatus();

    // 获取配置信息
    TFuture<NYTree::INodePtr> GetConfiguration();

    // 执行诊断操作
    TFuture<NYTree::INodePtr> ExecuteDiagnostic(const TString& operation);
};
```

## 使用方法

### 基本服务创建示例

```cpp
#include <yt/yt/library/orchid/orchid_service.h>
#include <yt/yt/library/orchid/orchid_service_proxy.h>

using namespace NYT;
using namespace NYT::NOrchid;

class ApplicationWithOrchid {
public:
    ApplicationWithOrchid() {
        SetupOrchidService();
    }

    void Start() {
        // 启动 RPC 服务器
        StartRpcServer();

        // 注册服务组件
        RegisterServiceComponents();

        Cout << "Orchid service started" << Endl;
    }

private:
    void SetupOrchidService() {
        // 创建根节点
        auto rootNode = CreateServiceRoot();

        // 创建调用器
        auto invoker = CreateInvoker();

        // 创建认证器
        auto authenticator = CreateAuthenticator();

        // 创建 Orchid 服务
        orchidService_ = CreateOrchidService(rootNode, invoker, authenticator);
    }

    NYTree::INodePtr CreateServiceRoot() {
        // 创建监控树根节点
        auto root = NYTree::GetEphemeralNodeFactory()->CreateMap();

        // 添加基本服务信息
        NYTree::SetChild(root, "service", CreateServiceInfoNode());
        NYTree::SetChild(root, "monitoring", CreateMonitoringNode());
        NYTree::SetChild(root, "configuration", CreateConfigurationNode());

        return root;
    }

    IInvokerPtr CreateInvoker() {
        // 创建专用调用器
        return CreateSerializedInvoker();
    }

    NRpc::IAuthenticatorPtr CreateAuthenticator() {
        // 创建认证器（可以支持多种认证方式）
        return NRpc::CreateNoAuthenticator();  // 无认证（开发环境）
        // return NRpc::CreateTokenAuthenticator();  // Token认证（生产环境）
    }

    void StartRpcServer() {
        // 启动 RPC 服务器并注册 Orchid 服务
        rpcServer_ = NRpc::CreateServer();
        rpcServer_->RegisterService(orchidService_);
        rpcServer_->Configure(GetRpcServerConfig());
        rpcServer_->Start();
    }

private:
    NRpc::IServicePtr orchidService_;
    NRpc::IServerPtr rpcServer_;
};
```

### 监控节点创建示例

```cpp
class MonitoringNodeProvider {
public:
    static NYTree::INodePtr CreateMonitoringNode() {
        auto factory = NYTree::GetEphemeralNodeFactory();
        auto monitoringNode = factory->CreateMap();

        // 添加性能指标
        NYTree::SetChild(monitoringNode, "performance", CreatePerformanceNode());

        // 添加健康检查
        NYTree::SetChild(monitoringNode, "health", CreateHealthNode());

        // 添加资源使用情况
        NYTree::SetChild(monitoringNode, "resources", CreateResourcesNode());

        return monitoringNode;
    }

    static NYTree::INodePtr CreatePerformanceNode() {
        auto factory = NYTree::GetEphemeralNodeFactory();
        auto perfNode = factory->CreateMap();

        // 创建动态更新的性能指标
        auto requestCountProducer = NYTree::CreateProducerHolder(BIND([] (NYson::IYsonConsumer* consumer) {
            NYson::BuildYsonFluently(consumer)
                .BeginMap()
                    .Item("total_requests").Value(GetTotalRequestCount())
                    .Item("requests_per_second").Value(GetRequestsPerSecond())
                    .Item("average_latency_ms").Value(GetAverageLatency())
                .EndMap();
        }));

        NYTree::SetChild(perfNode, "requests", std::move(requestCountCountProducer));

        return perfNode;
    }

    static NYTree::INodePtr CreateHealthNode() {
        auto factory = NYTree::GetEphemeralNodeFactory();
        auto healthNode = factory->CreateMap();

        auto healthProducer = NYTree::CreateProducerHolder(BIND([] (NYson::IYsonConsumer* consumer) {
            auto healthStatus = CheckSystemHealth();

            NYson::BuildYsonFluently(consumer)
                .BeginMap()
                    .Item("status").Value(healthStatus.Status)
                    .Item("last_check").Value(TInstant::Now().ToString())
                    .Item("components").BeginMap()
                        .DoFor(healthStatus.Components, [&] (auto&& builder, const auto& pair) {
                            builder.Item(pair.first).BeginMap()
                                .Item("healthy").Value(pair.second.Healthy)
                                .Item("message").Value(pair.second.Message)
                            .EndMap();
                        })
                    .EndMap()
                .EndMap();
        }));

        NYTree::SetChild(healthNode, "status", std::move(healthProducer));

        return healthNode;
    }

private:
    struct HealthStatus {
        TString Status;
        THashMap<TString, std::pair<bool, TString>> Components;
    };

    static HealthStatus CheckSystemHealth() {
        HealthStatus status;
        status.Status = "healthy";

        // 检查各个组件的健康状态
        status.Components["database"] = {true, "operational"};
        status.Components["cache"] = {true, "normal"};
        status.Components["network"] = {true, "connected"};

        return status;
    }

    static i64 GetTotalRequestCount() { return 123456; }
    static double GetRequestsPerSecond() { return 45.67; }
    static double GetAverageLatency() { return 12.34; }
};
```

### 客户端访问示例

```cpp
class OrchidClient {
public:
    OrchidClient(const NRpc::IChannelPtr& channel)
        : proxy_(channel)
    {}

    // 获取服务状态
    TFuture<TString> GetServiceStatusAsync() {
        return proxy_.Execute(NRpc::NProto::TReqGetService{})
            .Apply(BIND([] (const NRpc::NProto::TRspGetService& response) {
                return NYson::ConvertToYsonString(response.result(), NYson::EYsonFormat::Text).ToString();
            }));
    }

    // 获取特定路径的数据
    TFuture<NYTree::INodePtr> GetPathAsync(const NYPath::TYPath& path) {
        auto request = NRpc::NProto::TReqGetYPath();
        request.set_path(path);

        return proxy_.Execute(request)
            .Apply(BIND([] (const NRpc::NProto::TRspGetYPath& response) {
                return NYTree::ConvertToNode(NYson::TYsonString(response.result()));
            }));
    }

    // 监控数据变更
    void WatchPath(const NYPath::TYPath& path, std::function<void(NYTree::INodePtr)> callback) {
        auto watcher = CreatePathWatcher();
        watcher->Watch(path, callback);
        watchers_.push_back(watcher);
    }

private:
    NRpc::TProxy<NOrchid::NProto::TOrchidService> proxy_;
    std::vector<NYPath::IYPathWatcherPtr> watchers_;
};
```

### 配置管理示例

```cpp
class ConfigurationManager {
public:
    ConfigurationManager(NYTree::INodePtr rootNode)
        : rootNode_(rootNode)
    {
        configNode_ = FindOrCreateConfigNode();
    }

    // 更新配置
    void UpdateConfiguration(const THashMap<TString, NYTree::INodePtr>& updates) {
        for (const auto& [key, value] : updates) {
            NYTree::SetChild(configNode_, key, value);
        }

        // 触发配置变更事件
        NotifyConfigurationChange();
    }

    // 获取配置值
    template<typename T>
    T GetConfigValue(const TString& key, const T& defaultValue = T{}) {
        auto child = NYTree::FindChild(configNode_, key);
        if (!child) {
            return defaultValue;
        }

        return NYTree::ConvertTo<T>(child);
    }

    // 验证配置
    bool ValidateConfiguration() {
        try {
            // 检查必需的配置项
            auto requiredKeys = GetRequiredConfigKeys();
            for (const auto& key : requiredKeys) {
                if (!NYTree::FindChild(configNode_, key)) {
                    Cerr << "Missing required configuration: " << key << Endl;
                    return false;
                }
            }

            // 验证配置值的合理性
            return ValidateConfigValues();
        } catch (const std::exception& e) {
            Cerr << "Configuration validation failed: " << e.what() << Endl;
            return false;
        }
    }

private:
    NYTree::INodePtr rootNode_;
    NYTree::INodePtr configNode_;

    NYTree::INodePtr FindOrCreateConfigNode() {
        auto factory = NYTree::GetEphemeralNodeFactory();
        auto configNode = factory->CreateMap();
        NYTree::SetChild(rootNode_, "configuration", configNode);
        return configNode;
    }

    std::vector<TString> GetRequiredConfigKeys() {
        return {"service_name", "port", "log_level"};
    }

    bool ValidateConfigValues() {
        // 验证端口号
        auto port = GetConfigValue<int>("port");
        if (port <= 0 || port > 65535) {
            Cerr << "Invalid port number: " << port << Endl;
            return false;
        }

        // 验证日志级别
        auto logLevel = GetConfigValue<TString>("log_level");
        std::vector<TString> validLevels = {"DEBUG", "INFO", "WARNING", "ERROR"};
        if (std::find(validLevels.begin(), validLevels.end(), logLevel) == validLevels.end()) {
            Cerr << "Invalid log level: " << logLevel << Endl;
            return false;
        }

        return true;
    }

    void NotifyConfigurationChange() {
        // 通知配置变更
        // 可以通过事件系统或回调机制实现
    }
};
```

## 配置说明

### 服务配置

```cpp
struct TOrchidServiceConfig {
    // RPC 服务器配置
    NRpc::IServerConfigPtr RpcServer;

    // 认证配置
    bool RequireAuthentication = false;
    TString AuthToken;

    // 监控配置
    TDuration MetricsUpdateInterval = TDuration::Seconds(1);
    size_t MaxMetricHistorySize = 1000;

    // 安全配置
    TString AllowedPathPrefix = "/";
    bool EnableWriteOperations = false;
};
```

### 监控配置

```cpp
struct TMonitoringConfig {
    // 性能指标配置
    bool EnablePerformanceMetrics = true;
    bool EnableResourceMetrics = true;
    bool EnableHealthChecks = true;

    // 历史数据配置
    TDuration HistoryRetentionPeriod = TDuration::Hours(24);
    size_t MaxHistoryEntries = 10000;

    // 告警配置
    std::vector<TAlertConfig> AlertConfigs;
};
```

## 性能考虑

### 内存使用
- **节点缓存**: 合理缓存监控节点减少内存分配
- **历史数据**: 限制历史数据大小避免内存溢出
- **延迟加载**: 按需加载监控数据减少内存占用

### 网络开销
- **数据压缩**: 对大型监控数据进行压缩传输
- **批量操作**: 支持批量获取多个监控指标
- **增量更新**: 只传输变更的监控数据

### 访问性能
- **路径索引**: 优化 YPath 路径查找性能
- **并发控制**: 合理控制并发访问避免资源竞争
- **缓存策略**: 实现智能缓存提高访问速度

## 最佳实践

### 1. 服务组织结构

```cpp
class ServiceOrchidStructure {
public:
    static NYTree::INodePtr CreateServiceStructure(const TString& serviceName) {
        auto factory = NYTree::GetEphemeralNodeFactory();
        auto root = factory->CreateMap();

        // 基本信息
        NYTree::SetChild(root, "name", factory->CreateStringNode(serviceName));
        NYTree::SetChild(root, "version", factory->CreateStringNode(GetVersion()));
        NYTree::SetChild(root, "uptime", factory->CreateStringNode(GetUptime()));

        // 子系统监控
        NYTree::SetChild(root, "subsystems", CreateSubsystemsNode());

        // 运行时统计
        NYTree::SetChild(root, "statistics", CreateStatisticsNode());

        return root;
    }

private:
    static NYTree::INodePtr CreateSubsystemsNode() {
        auto factory = NYTree::GetEphemeralNodeFactory();
        auto subsystems = factory->CreateMap();

        // 数据库子系统
        NYTree::SetChild(subsystems, "database", CreateDatabaseSubSystem());

        // 缓存子系统
        NYTree::SetChild(subsystems, "cache", CreateCacheSubSystem());

        // 网络子系统
        NYTree::SetChild(subsystems, "network", CreateNetworkSubSystem());

        return subsystems;
    }
};
```

### 2. 错误处理和恢复

```cpp
class ResilientOrchidService {
public:
    ResilientOrchidService() {
        SetupErrorHandling();
    }

    void SafeExecute(std::function<void()> operation) {
        try {
            operation();
        } catch (const std::exception& e) {
            HandleOrchidError(e);
        }
    }

private:
    void SetupErrorHandling() {
        // 设置全局错误处理器
        SetErrorHandler([this] (const std::exception& e) {
            HandleOrchidError(e);
        });
    }

    void HandleOrchidError(const std::exception& e) {
        // 记录错误
        Cerr << "Orchid service error: " << e.what() << Endl;

        // 更新错误统计
        UpdateErrorStatistics(e);

        // 尝试恢复
        AttemptRecovery();
    }

    void UpdateErrorStatistics(const std::exception& e) {
        errorCount_++;
        lastError_ = e.what();
        lastErrorTime_ = TInstant::Now();
    }

    void AttemptRecovery() {
        // 实现恢复逻辑
        if (ShouldTriggerRecovery()) {
            PerformRecovery();
        }
    }

    bool ShouldTriggerRecovery() {
        return errorCount_ > 5 ||
               (lastErrorTime_ && TInstant::Now() - *lastErrorTime_ > TDuration::Minutes(5));
    }

private:
    std::atomic<int> errorCount_{0};
    std::optional<TString> lastError_;
    std::optional<TInstant> lastErrorTime_;
};
```

## 依赖项

- **YT RPC**: RPC 服务框架
- **YT YTree**: 树形数据结构
- **YT YPath**: 路径导航服务
- **YT Core**: 基础服务框架

## 注意事项

### 1. 安全性
- 适当配置认证机制保护敏感监控数据
- 限制客户端的写入权限
- 定期更新认证凭据

### 2. 性能影响
- 监控数据的频繁更新可能影响服务性能
- 合理设置更新频率平衡实时性和性能
- 监控系统本身不应成为性能瓶颈

### 3. 可扩展性
- 设计可扩展的监控结构
- 支持动态添加新的监控指标
- 考虑分布式环境下的数据聚合

### 4. 数据一致性
- 确保监控数据的时序一致性
- 处理并发访问导致的数据竞争
- 实现适当的数据同步机制