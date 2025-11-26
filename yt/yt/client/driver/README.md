# YTsaurus Driver 模块

## 概述

Driver 模块是 YTsaurus 客户端架构中的核心驱动层，提供了统一的命令执行框架和代理发现机制。它作为客户端应用程序与 YTsaurus 集群之间的桥梁，负责命令调度、请求路由、连接管理和代理选择等关键功能。

## 核心架构

### 1. 驱动器 (IDriver)
```cpp
DECLARE_REFCOUNTED_STRUCT(IDriver)
```
驱动器是整个模块的核心接口，负责：
- 命令执行和调度
- 代理服务器发现和选择
- 连接生命周期管理
- 请求路由和负载均衡

### 2. 命令系统
```cpp
struct ICommand {
    virtual ~ICommand() = default;
    virtual void Execute(ICommandContextPtr context) = 0;
};
```
提供统一的命令执行框架：
- 命令抽象接口
- 执行上下文管理
- 输入输出处理
- 错误处理机制

### 3. 代理发现 (IProxyDiscoveryCache)
```cpp
struct IProxyDiscoveryCache : public virtual TRefCounted {
    virtual TFuture<TProxyDiscoveryResponse> Discover(
        const TProxyDiscoveryRequest& request) = 0;
};
```
智能代理发现和缓存系统：
- RPC 代理服务器发现
- 地址类型和网络选择
- 负载均衡支持
- 缓存优化

## 主要功能模块

### 1. 命令类型分类

#### 管理命令 (admin_commands)
- 集群管理操作
- 系统配置修改
- 节点状态监控

#### 认证命令 (authentication_commands)
- 用户身份验证
- 令牌管理
- 密码操作

#### Cypress 命令 (cypress_commands)
- 元数据树操作
- 节点创建和删除
- 路径解析

#### 分布式文件命令 (distributed_file_commands)
- 文件上传下载
- 分布式存储管理
- 文件系统操作

#### 分布式表命令 (distributed_table_commands)
- 表数据操作
- 查询执行
- 数据分布管理

#### 调度命令 (scheduler_commands)
- 作业提交和管理
- 操作监控
- 资源调度

#### 事务命令 (transaction_commands)
- 事务管理
- 锁操作
- 一致性控制

### 2. 配置系统 (TDriverConfig)

```cpp
struct TDriverConfig : public NYTree::TYsonStruct {
    NApi::TFileReaderConfigPtr FileReader;
    NApi::TFileWriterConfigPtr FileWriter;
    NTableClient::TTableReaderConfigPtr TableReader;
    NTableClient::TTableWriterConfigPtr TableWriter;
    int ApiVersion;  // 支持 v3 和 v4 API
    i64 ReadBufferRowCount;
    i64 ReadBufferSize;
    i64 WriteBufferSize;
    TSlruCacheConfigPtr ClientCache;
    std::optional<TString> Token;
    std::optional<std::string> MultiproxyTargetCluster;
    TAsyncExpiringCacheConfigPtr ProxyDiscoveryCache;
    bool EnableInternalCommands;
    // ... 更多配置选项
};
```

## 核心组件详解

### 1. 驱动请求 (TDriverRequest)

```cpp
struct TDriverRequest {
    TGuid Id;  // 请求标识符
    TString CommandName;  // 命令名称
    NConcurrency::IAsyncZeroCopyInputStreamPtr InputStream;
    NConcurrency::IFlushableAsyncOutputStreamPtr OutputStream;
    NYTree::IMapNodePtr Parameters;  // 命令参数
    std::string AuthenticatedUser;  // 认证用户
    std::optional<std::string> UserTag;  // 用户标签
    std::optional<std::string> UserRemoteAddress;  // 远程地址
    std::optional<TString> UserToken;  // 用户令牌
    std::optional<TString> ServiceTicket;  // TVM 服务票据
    IMemoryUsageTrackerPtr MemoryUsageTracker;  // 内存使用跟踪
};
```

### 2. 命令执行上下文 (ICommandContext)

```cpp
struct ICommandContext : public virtual TRefCounted {
    virtual const TDriverConfigPtr& GetConfig() const = 0;
    virtual const NApi::IClientPtr& GetClient() const = 0;
    virtual const NApi::IClientPtr& GetRootClient() const = 0;
    virtual const IDriverPtr& GetDriver() const = 0;
    virtual const TDriverRequest& Request() const = 0;
    virtual const NFormats::TFormat& GetInputFormat() = 0;
    virtual const NFormats::TFormat& GetOutputFormat() = 0;
    virtual void ProduceOutputValue(const NYson::TYsonString& yson) = 0;
    virtual NYson::TYsonString ConsumeInputValue() = 0;
};
```

### 3. 代理发现机制

#### 请求结构
```cpp
struct TProxyDiscoveryRequest {
    NApi::EProxyKind Kind = NApi::EProxyKind::Rpc;
    std::string Role = NApi::DefaultRpcProxyRole;
    NApi::NRpcProxy::EAddressType AddressType = NApi::NRpcProxy::DefaultAddressType;
    std::string NetworkName = NApi::NRpcProxy::DefaultNetworkName;
    bool IgnoreBalancers = false;
};
```

#### 响应结构
```cpp
struct TProxyDiscoveryResponse {
    std::vector<std::string> Addresses;  // 可用代理地址列表
};
```

## 使用方法

### 1. 基本驱动器使用

```cpp
#include <yt/yt/client/driver/public.h>
#include <yt/yt/client/driver/driver.h>

using namespace NYT::NDriver;

// 创建驱动器配置
auto config = New<TDriverConfig>();
config->ApiVersion = ApiVersion4;
config->Token = "your-auth-token";

// 创建驱动器
auto driver = CreateDriver(config);

// 执行命令
TDriverRequest request;
request.CommandName = "read";
request.Parameters = BuildYsonNodeFluently()
    .BeginMap()
        .Item("path").Value("/path/to/table")
        .Item("format").Value("yson")
    .EndMap();

auto response = driver->Execute(request);
```

### 2. 自定义命令实现

```cpp
class TMyCommand : public TCommandBase {
public:
    void Execute(ICommandContextPtr context) override {
        // 获取客户端连接
        auto client = context->GetClient();

        // 获取输入参数
        auto parameters = context->Request().Parameters;

        // 执行业务逻辑
        auto result = DoWork(client, parameters);

        // 产生输出
        ProduceSingleOutputValue(context, "result", result);
    }
};

// 注册命令
RegisterCommand<TMyCommand>("my_command");
```

### 3. 代理发现缓存使用

```cpp
// 创建代理发现缓存
auto cacheConfig = New<TAsyncExpiringCacheConfig>();
cacheConfig->ExpireAfterSuccessfulUpdateTime = TDuration::Minutes(5);
cacheConfig->ExpireAfterFailedUpdateTime = TDuration::Minutes(1);

auto cache = CreateProxyDiscoveryCache(cacheConfig, client);

// 发现代理
TProxyDiscoveryRequest request;
request.AddressType = NApi::NRpcProxy::EAddressType::Internet;
request.Role = "heavy";

auto future = cache->Discover(request);
future.Subscribe([] (const TErrorOr<TProxyDiscoveryResponse>& result) {
    if (result.IsOK()) {
        for (const auto& address : result.Value().Addresses) {
            YT_LOG_INFO("Found proxy: %v", address);
        }
    } else {
        YT_LOG_ERROR("Failed to discover proxies: %v", result);
    }
});
```

## 性能优化

### 1. 缓存策略
- **代理缓存**: 减少代理发现开销
- **连接池**: 复用 TCP 连接
- **配置缓存**: 避免重复配置解析

### 2. 异步处理
- 非阻塞 I/O 操作
- 异步代理发现
- 并行命令执行

### 3. 内存管理
- 零拷贝数据传输
- 缓冲区复用
- 内存使用跟踪

### 4. 负载均衡
- 智能代理选择
- 故障转移机制
- 健康检查

## 监控和诊断

### 关键指标
- 命令执行延迟
- 代理发现时间
- 连接池状态
- 错误率和重试次数

### 日志记录
```cpp
// 结构化日志
YT_LOG_INFO("Command executed (Command: %v, Duration: %v, Success: %v)",
    request.CommandName, duration, success);

// 性能日志
YT_LOG_DEBUG("Proxy discovery completed (Request: %v, ProxyCount: %v, Duration: %v)",
    request, response.Addresses.size(), discoveryTime);
```

## 扩展性设计

### 1. 插件架构
- 自定义命令插件
- 代理发现策略插件
- 负载均衡算法插件

### 2. 配置扩展
- 动态配置更新
- 环境特定配置
- 用户自定义配置

### 3. 协议扩展
- 多版本 API 支持
- 自定义序列化格式
- 扩展错误处理

## 错误处理

### 错误分类
- **网络错误**: 连接超时、网络分区
- **认证错误**: 令牌失效、权限不足
- **命令错误**: 参数错误、执行失败
- **系统错误**: 资源不足、服务不可用

### 重试策略
```cpp
// 指数退避重试
int maxRetries = 3;
TDuration baseDelay = TDuration::MilliSeconds(100);

for (int attempt = 0; attempt <= maxRetries; ++attempt) {
    try {
        return ExecuteCommand(request);
    } catch (const TNetworkException& e) {
        if (attempt == maxRetries) {
            throw;
        }
        auto delay = baseDelay * (1 << attempt);
        TDelay::Wait(delay);
    }
}
```

## 依赖项

### 内部依赖
- `yt/yt/client/api/public.h` - API 客户端接口
- `yt/yt/client/formats/format.h` - 数据格式支持
- `yt/yt/client/security_client/public.h` - 安全客户端
- `yt/yt/core/concurrency/async_stream.h` - 异步流
- `yt/yt/core/rpc/public.h` - RPC 框架

### 外部依赖
- 网络库 (libcurl, asio)
- 压缩库 (zlib, lz4)
- 加密库 (openssl)
- JSON/YAML 解析库

## 构建配置

该模块支持多种构建配置：
- **平台支持**: Linux (x86_64, aarch64), macOS (x86_64, arm64)
- **编译器**: Clang-18+, GCC-10+
- **构建系统**: CMake + Ninja, YaTool
- **依赖管理**: Conan 2.4.1+

## 最佳实践

### 1. 资源管理
- 及时释放连接和资源
- 合理设置缓冲区大小
- 监控内存使用情况

### 2. 错误处理
- 实现完善的重试机制
- 提供有意义的错误信息
- 记录详细的诊断日志

### 3. 性能优化
- 使用连接池和缓存
- 批量操作减少网络往返
- 合理设置超时时间

### 4. 安全考虑
- 使用 HTTPS/TLS 加密通信
- 定期更新认证令牌
- 实施访问控制和审计

## 版本兼容性

- **API 版本**: 支持 v3 和 v4 API
- **向后兼容**: 保持旧版本命令支持
- **迁移指南**: 提供版本升级路径

## 相关文档

- [YTsaurus 架构设计](../../../docs/architecture.md)
- [命令行工具使用指南](../../../docs/cli.md)
- [客户端配置参考](../../../docs/client-config.md)
- [API 版本兼容性](../../../docs/api-compatibility.md)

## 贡献指南

在贡献代码时：
1. 遵循代码风格规范
2. 添加完整的测试覆盖
3. 更新相关文档
4. 考虑性能和安全影响
5. 确保向后兼容性