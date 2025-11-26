# ClickHouse 服务发现库

## 概述

这个库为 ClickHouse 集群提供了服务发现功能，用于维护和更新集群中活跃参与者的列表。它支持动态成员管理、属性存储、版本控制和故障检测等特性。

## 功能特性

### 服务发现核心功能

- **动态成员管理**：支持节点的加入和离开
- **属性存储**：为每个节点存储自定义属性
- **版本控制**：维护发现服务的版本信息
- **轮询更新**：定期更新参与者列表
- **故障检测**：自动检测失效节点

### 高级功能

- **Ban/Unban 机制**：临时或永久排除节点
- **多版本支持**：支持 v1 和 v2 两种发现协议
- **异步操作**：所有操作都是异步的
- **容错设计**：处理网络分区和节点故障

## 文件说明

### 核心接口

- `discovery.h` - 主要接口定义，包含 IDiscovery 接口
- `discovery_base.h/cpp` - 发现服务的基础实现
- `public.h` - 公共接口定义

### 版本实现

- `discovery_v1.h/cpp` - v1 版本发现服务实现
- `discovery_v2.h/cpp` - v2 版本发现服务实现（推荐使用）

### 配置和工具

- `config.h/cpp` - 发现服务配置定义
- `helpers.h/cpp` - 辅助函数

### 测试文件

- `unittests/` - 单元测试目录

## 核心接口

### IDiscovery 接口

```cpp
struct IDiscovery : public virtual TRefCounted {
    // 加入组
    virtual TFuture<void> Enter(TString name,
                               NYTree::IAttributeDictionaryPtr attributes) = 0;

    // 离开组
    virtual TFuture<void> Leave() = 0;

    // 列出所有参与者
    virtual THashMap<TString, NYTree::IAttributeDictionaryPtr>
        List(bool includeBanned = false) const = 0;

    // 禁用参与者
    virtual void Ban(const TString& name) = 0;
    virtual void Ban(const std::vector<TString>& names) = 0;

    // 解禁参与者
    virtual void Unban(const TString& name) = 0;
    virtual void Unban(const std::vector<TString>& names) = 0;

    // 更新列表
    virtual TFuture<void> UpdateList(TDuration maxDivergency = TDuration::Zero()) = 0;

    // 开始轮询
    virtual TFuture<void> StartPolling() = 0;

    // 停止轮询
    virtual TFuture<void> StopPolling() = 0;

    // 获取版本
    virtual int Version() const = 0;
};
```

## 使用示例

### 创建发现服务

```cpp
#include <yt/yt/library/clickhouse_discovery/discovery.h>
#include <yt/yt/library/clickhouse_discovery/discovery_v2.h>

using namespace NYT::NClickHouseServer;

// 创建配置
auto config = New<TClickHouseDiscoveryConfig>();
config->GroupId = "clickhouse_cluster_01";
config->UpdatePeriod = TDuration::Seconds(10);
config->BanTimeout = TDuration::Minutes(5);

// 创建发现服务
auto discovery = CreateClickHouseDiscoveryV2(config);

// 启动轮询
WaitFor(discovery->StartPolling())
    .ThrowOnError();
```

### 节点注册和管理

```cpp
// 节点加入集群
auto attributes = NYTree::CreateEphemeralAttributes();
attributes->Set("host", "192.168.1.100");
attributes->Set("port", 9000);
attributes->Set("role", "shard");

WaitFor(discovery->Enter("node_01", attributes))
    .ThrowOnError();

// 获取集群成员
auto members = discovery->List();
for (const auto& [name, attrs] : members) {
    Cout << "Node: " << name << Endl;
    Cout << "  Host: " << attrs->Get<TString>("host") << Endl;
    Cout << "  Port: " << attrs->Get<int>("port") << Endl;
}

// 节点离开集群
WaitFor(discovery->Leave())
    .ThrowOnError();
```

### Ban/Unban 操作

```cpp
// 禁用节点
discovery->Ban({"node_01", "node_02"});

// 获取未被禁用的节点
auto activeMembers = discovery->List(false);

// 解禁节点
discovery->Unban("node_01");
```

## 配置选项

### TClickHouseDiscoveryConfig

```cpp
struct TClickHouseDiscoveryConfig {
    TString GroupId;                    // 组标识符
    TDuration UpdatePeriod;             // 更新周期
    TDuration BanTimeout;               // 禁用超时时间
    TDuration MaxDivergency;            // 最大数据不一致时间
    bool EnableBanList;                 // 是否启用禁用列表
    int MaxRetries;                     // 最大重试次数
    TDuration RetryTimeout;             // 重试超时
};
```

## 版本差异

### v1 版本

- 基础的服务发现功能
- 简单的成员列表管理
- 有限的属性支持

### v2 版本

- 增强的属性系统
- 更好的性能和可扩展性
- 改进的错误处理
- 支持更复杂的查询

## 实现原理

### 一致性模型

- **最终一致性**：节点列表最终会达到一致
- ** gossip 协议**：节点间传播状态信息
- **故障检测**：通过心跳检测节点存活

### 数据结构

- 使用哈希表存储参与者信息
- 维护版本号用于冲突解决
- 时间戳用于判断信息新鲜度

### 通信模式

- 点对点通信
- 定期状态同步
- 增量更新减少网络开销

## 性能特性

- **O(1)** 查找复杂度
- 增量更新减少网络流量
- 异步操作避免阻塞
- 内存高效的数据结构

## 错误处理

### 常见错误类型

- `EErrorCode::Timeout` - 操作超时
- `EErrorCode::NodeNotFound` - 节点不存在
- `EErrorCode::AlreadyExists` - 节点已存在
- `EErrorCode::PermissionDenied` - 权限不足

### 错误恢复

- 自动重试机制
- 优雅降级
- 错误日志记录

## 安全考虑

- 认证和授权机制
- 加密通信支持
- 访问控制列表
- 审计日志

## 监控和指标

- 成员数量统计
- 更新延迟指标
- 错误率监控
- 网络流量统计

## 依赖项

- YTsaurus 核心库
- YTsaurus HTTP 客户端
- YTsaurus 配置系统
- YTsaurus 日志系统

## 平台支持

- Linux x86_64
- Linux aarch64
- macOS x86_64
- macOS arm64

## 最佳实践

1. **合理设置更新周期**：平衡实时性和网络开销
2. **使用有意义的节点名称**：便于调试和监控
3. **正确处理异步操作**：使用 Future 和回调
4. **实施适当的错误处理**：确保系统健壮性
5. **定期清理无效节点**：避免内存泄漏

## 故障排除

### 常见问题

1. **节点列表不同步**
   - 检查网络连接
   - 验证配置参数
   - 查看错误日志

2. **性能问题**
   - 调整更新周期
   - 检查节点数量
   - 优化属性数据

3. **连接失败**
   - 验证服务地址
   - 检查防火墙设置
   - 确认服务运行状态