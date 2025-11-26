# YTsaurus 客户端缓存

## 概述

`cache` 目录提供了 YTsaurus 客户端的缓存管理功能。该模块实现了客户端连接的缓存和管理，支持多个集群的客户端连接池管理，提高客户端连接的复用性和性能。

## 核心功能

### 客户端缓存管理
- **连接池**: 管理与多个 YTsaurus 集群的连接
- **客户端复用**: 复用已建立的客户端连接
- **自动配置**: 支持基于配置的自动连接创建
- **连接生命周期**: 管理连接的创建、复用和销毁

### 多集群支持
- **集群配置**: 支持多个集群的独立配置
- **动态连接**: 根据需要动态创建集群连接
- **负载均衡**: 支持集群间的负载均衡
- **故障转移**: 自动处理集群故障和切换

### 认证管理
- **统一认证**: 支持统一的认证配置
- **集群特定认证**: 支持每个集群的独立认证配置
- **环境变量**: 支持从环境变量读取认证信息
- **代理角色**: 支持 Proxy 角色配置

## 主要文件说明

### 核心缓存接口
- `cache.h/.cpp`: 客户端缓存核心实现
  - `IClientsCache`: 客户端缓存接口
  - 多种缓存创建函数：支持不同配置方式的缓存创建
  - `GetConnectionConfig`: 获取集群连接配置的辅助函数

### 配置管理
- `config.h/.cpp`: 缓存配置定义
  - `TClientsCacheConfig`: 客户端缓存配置结构
  - `TClientsCacheAuthentificationOptions`: 认证选项配置
  - 支持默认配置和集群特定配置

### RPC 辅助
- `rpc.h/.cpp`: RPC 连接辅助函数
  - 集群 URL 解析和处理
  - 客户端创建的多种快捷方式
  - Proxy 角色管理

### 基础实现
- `cache_base.h/.cpp`: 缓存基础实现

### 公共接口
- `public.h`: 公共类型声明和命名空间定义

## 使用示例

### 基本客户端缓存使用
```cpp
#include <yt/yt/client/cache/cache.h>

// 创建默认客户端缓存
auto cache = NYT::NClient::NCache::CreateClientsCache();

// 获取客户端连接
auto client = cache->GetClient("my_cluster");
```

### 使用配置创建缓存
```cpp
#include <yt/yt/client/cache/cache.h>

// 创建带配置的客户端缓存
auto config = New<NYT::NClient::NCache::TClientsCacheConfig>();
// 配置连接参数...

auto authOptions = New<NYT::NClient::NCache::TClientsCacheAuthentificationOptions>();
// 配置认证信息...

auto cache = NYT::NClient::NCache::CreateClientsCache(config, authOptions);
```

### 使用连接配置创建缓存
```cpp
#include <yt/yt/client/cache/cache.h>

// 从连接配置创建缓存
auto connectionConfig = New<NYT::NApi::NRpcProxy::TConnectionConfig>();
connectionConfig->ClusterName = "my_cluster";
connectionConfig->AddProxyAddress("proxy1.my_cluster.yt:9013");

auto options = NYT::NApi::TClientOptions::FromUser("my_user");

auto cache = NYT::NClient::NCache::CreateClientsCache(connectionConfig, options);
```

### 直接创建客户端
```cpp
#include <yt/yt/client/cache/rpc.h>

// 使用环境变量创建客户端
auto client = NYT::NClient::NCache::CreateClient();

// 指定集群创建客户端
auto client = NYT::NClient::NCache::CreateClient("my_cluster");

// 指定集群和代理角色创建客户端
auto client = NYT::NClient::NCache::CreateClient("my_cluster", "data_proxy");

// 使用自定义选项创建客户端
auto options = NYT::NApi::TClientOptions::FromUser("my_user");
auto client = NYT::NClient::NCache::CreateClient("my_cluster", options);
```

## 配置详细说明

### 缓存配置
```cpp
struct TClientsCacheConfig {
    // 默认连接配置
    NApi::NRpcProxy::TConnectionConfigPtr DefaultConnection;

    // 每个集群的特定连接配置
    THashMap<std::string, NApi::NRpcProxy::TConnectionConfigPtr> PerClusterConnection;
};
```

### 认证配置
```cpp
struct TClientsCacheAuthentificationOptions {
    // 默认客户端选项
    NApi::TClientOptions DefaultOptions;

    // 每个集群的特定客户端选项
    THashMap<std::string, NApi::TClientOptions> ClusterOptions;
};
```

### 集群 URL 格式
支持多种集群 URL 格式：
- `cluster`: 简单集群名称
- `cluster/proxy_role`: 带代理角色的集群名称
- `ip:port`: IP 地址和端口
- `ip:port/proxy_role`: 带代理角色的 IP 地址

## 缓存策略

### 连接复用
- **智能复用**: 相同配置的连接会被复用
- **连接池**: 维护活跃连接池以提高性能
- **超时管理**: 自动清理长时间未使用的连接
- **错误处理**: 连接失败时的重试和故障转移

### 内存管理
- **引用计数**: 使用智能指针管理连接生命周期
- **自动清理**: 定期清理无效连接
- **内存限制**: 支持缓存大小限制
- **资源监控**: 监控连接资源使用情况

## 性能优化

### 连接预热
- **预连接**: 支持启动时预连接常用集群
- **并发创建**: 支持并发创建多个连接
- **连接重用**: 最大化连接重用率
- **连接保持**: 保持长连接以减少建连开销

### 配置优化
- **配置缓存**: 缓存解析后的配置信息
- **DNS 解析**: 缓存 DNS 解析结果
- **负载均衡**: 智能选择最优连接
- **压缩传输**: 支持数据压缩传输

## 错误处理

### 连接错误
- **重试机制**: 连接失败时自动重试
- **故障转移**: 自动切换到备用连接
- **超时处理**: 合理的连接超时设置
- **错误日志**: 详细的连接错误日志

### 配置错误
- **格式验证**: 验证配置格式正确性
- **参数检查**: 检查必需参数
- **默认值**: 提供合理的默认配置
- **错误提示**: 清晰的错误信息

## 最佳实践

### 连接管理
1. **合理复用**: 充分利用连接池复用连接
2. **及时释放**: 使用完毕后及时释放连接
3. **监控使用**: 监控连接池使用情况
4. **配置优化**: 根据业务特点优化连接配置

### 性能调优
1. **连接预热**: 应用启动时预热关键连接
2. **批量操作**: 批量获取和释放连接
3. **异步处理**: 使用异步连接操作
4. **内存优化**: 控制连接池大小

### 错误处理
1. **异常安全**: 确保异常情况下的资源清理
2. **重试策略**: 实现合理的重试策略
3. **降级处理**: 连接失败时的降级方案
4. **监控告警**: 设置连接异常监控告警

## 线程安全

- **并发访问**: 支持多线程并发访问
- **原子操作**: 关键操作使用原子操作
- **锁机制**: 使用适当的锁保护共享资源
- **无锁设计**: 在可能的地方使用无锁设计

## 监控和诊断

### 性能指标
- **连接数**: 监控活跃连接数
- **命中率**: 监控连接缓存命中率
- **响应时间**: 监控连接建立时间
- **错误率**: 监控连接失败率

### 诊断工具
- **连接状态**: 查看连接池状态
- **配置信息**: 查看当前配置
- **错误统计**: 错误统计和分析
- **性能分析**: 性能瓶颈分析

## 注意事项

1. **资源限制**: 注意连接池大小限制，避免资源耗尽
2. **网络安全**: 确保连接配置的安全性
3. **版本兼容**: 保持客户端和服务端版本兼容
4. **配置管理**: 合理管理多集群配置
5. **清理工作**: 应用关闭时正确清理连接资源

## 扩展性

该模块设计支持：
- **自定义缓存策略**: 支持自定义缓存策略
- **插件化认证**: 支持自定义认证插件
- **监控集成**: 与外部监控系统集成
- **配置热更新**: 支持配置的热更新