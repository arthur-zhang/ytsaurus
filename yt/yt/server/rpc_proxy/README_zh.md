# RPC 代理服务 (RPC Proxy)

## 概述

RPC Proxy 是 YTsaurus 分布式存储系统中的核心 RPC 通信代理，为客户端提供统一的 RPC 访问接口。它作为客户端与集群服务之间的通信桥梁，提供连接管理、负载均衡、故障转移、认证授权等功能，确保高效、可靠的 RPC 通信。

## 功能特性

### 核心功能
- **RPC 路由**: 智能路由客户端请求到相应服务
- **连接管理**: 管理与后端服务的连接池和生命周期
- **负载均衡**: 在多个服务实例间实现负载均衡
- **故障转移**: 自动检测和处理服务故障
- **认证授权**: 集成多种认证和授权机制

### 高级特性
- **动态发现**: 自动发现和更新服务实例
- **性能监控**: 详细的 RPC 性能统计和分析
- **限流保护**: 实施 QPS 和并发限制
- **协议优化**: 优化 RPC 协议和传输效率
- **多租户支持**: 支持多租户环境下的隔离和配额

## 架构设计

### 组件架构
```
RPC Proxy
├── RPC Server (RPC 服务器)
│   ├── Request Handler (请求处理器)
│   ├── Response Builder (响应构建器)
│   └── Protocol Handler (协议处理器)
├── Connection Management (连接管理)
│   ├── Connection Pool (连接池)
│   ├── Session Manager (会话管理器)
│   └── Load Balancer (负载均衡器)
├── Service Discovery (服务发现)
│   ├── Discovery Client (发现客户端)
│   ├── Service Registry (服务注册表)
│   └── Health Monitor (健康监控器)
├── Security Layer (安全层)
│   ├── Authenticator (认证器)
│   ├── Authorizer (授权器)
│   └── Access Control (访问控制)
├── Performance Layer (性能层)
│   ├── Throttler (限流器)
│   ├── Caching Layer (缓存层)
│   └── Metrics Collector (指标收集器)
└── Management Layer (管理层)
    ├── Config Manager (配置管理器)
    ├── Debug Interface (调试接口)
    └── Health Checker (健康检查器)
```

### 关键组件说明

#### 1. Request Handler (请求处理器)
- 解析和验证 RPC 请求
- 路由请求到合适的服务
- 处理请求的超时和重试
- 管理请求的并发控制

#### 2. Connection Pool (连接池)
- 管理与后端服务的连接
- 实施连接复用和回收
- 监控连接的健康状态
- 优化连接的数量和分布

#### 3. Service Discovery (服务发现)
- 动态发现服务实例
- 维护服务地址列表
- 处理服务实例的变化
- 提供服务健康检查

#### 4. Authenticator (认证器)
- 验证客户端身份
- 支持多种认证方式
- 管理 Token 和会话
- 实施安全策略

## 支持的服务类型

### 核心服务路由
```yaml
services:
  master:
    type: "master"
    instances: ["master1:9000", "master2:9000", "master3:9000"]
    load_balance: "round_robin"
    retry_policy: "exponential_backoff"

  scheduler:
    type: "scheduler"
    instances: ["scheduler1:9010", "scheduler2:9010"]
    load_balance: "least_connections"

  node:
    type: "node"
    discovery: "auto"
    health_check: true
    load_balance: "consistent_hash"
```

### 代理服务支持
```yaml
proxies:
  cypress_proxy:
    type: "cypress"
    instances: ["cypress1:8080", "cypress2:8080"]
    route_pattern: "/cypress/*"

  job_proxy:
    type: "job_proxy"
    instances: ["job1:8081", "job2:8081"]
    route_pattern: "/job/*"
```

## 配置说明

### 基本配置结构
```yaml
rpc_proxy:
  # 服务器配置
  server:
    listen_port: 9000               # RPC 服务端口
    max_connections: 10000          # 最大连接数
    connection_timeout: 30000ms     # 连接超时时间
    request_timeout: 60000ms        # 请求超时时间
    read_buffer_size: 1MB           # 读取缓冲区大小
    write_buffer_size: 1MB          # 写入缓冲区大小

  # 连接池配置
  connection_pool:
    max_connections_per_service: 100 # 每个服务最大连接数
    connection_idle_timeout: 300s   # 连接空闲超时
    max_idle_connections: 50        # 最大空闲连接数
    health_check_interval: 30s      # 健康检查间隔

  # 负载均衡配置
  load_balancer:
    default_strategy: "round_robin" # 默认负载均衡策略
    health_check_enabled: true      # 启用健康检查
    failover_timeout: 5000ms        # 故障转移超时
```

### 服务发现配置
```yaml
rpc_proxy:
  discovery:
    enabled: true
    discovery_server: "discovery-server:21345"
    refresh_interval: 30s           # 服务列表刷新间隔
    health_check_interval: 10s      # 健康检查间隔
    service_timeout: 5000ms         # 服务请求超时

    # 服务过滤规则
    filters:
      - name: "environment"
        value: "production"
      - name: "cluster"
        value: "main"
```

### 安全配置
```yaml
rpc_proxy:
  security:
    enable_authentication: true     # 启用认证
    enable_authorization: true      # 启用授权

    # 认证配置
    authentication:
      methods: ["token", "tls", "cookie"]
      token_validation_endpoint: "http://auth-server:8080/validate"
      tls_cert_file: "/etc/ssl/rpc_proxy.crt"
      tls_key_file: "/etc/ssl/rpc_proxy.key"

    # 授权配置
    authorization:
      rbac_enabled: true
      policy_file: "/etc/ytsaurus/rbac_policies.yaml"
      default_deny: true            # 默认拒绝访问
```

### 性能优化配置
```yaml
rpc_proxy:
  performance:
    # 限流配置
    throttling:
      enabled: true
      global_qps_limit: 10000       # 全局 QPS 限制
      per_user_qps_limit: 100       # 每用户 QPS 限制
      per_service_qps_limit: 1000   # 每服务 QPS 限制

    # 缓存配置
    caching:
      enabled: true
      cache_size: 1000              # 缓存大小
      cache_ttl: 60s                # 缓存 TTL
      cache_key_prefix: "rpc_proxy"

    # 连接优化
    connection_optimization:
      enable_tcp_nodelay: true      # 启用 TCP_NODELAY
      enable_keepalive: true        # 启用 TCP keepalive
      keepalive_interval: 30s       # keepalive 间隔
      max_retries: 3                # 最大重试次数
```

## 使用方法

### 启动服务
```bash
# 从构建目录启动
./yt/yt/server/all/ytserver-all --config rpc_proxy.config.yson

# 或使用特定配置
./ytserver-rpc-proxy --config config.yson
```

### 客户端连接
```cpp
// C++ 客户端连接示例
#include <yt/yt/client/api/native.h>

// 通过 RPC Proxy 连接
auto connection = NApi::NNative::CreateConnection({
    .ClusterUrl = "rpc://rpc-proxy:9000",
    .Token = "your-token-here"
});

auto client = connection->CreateClient();

// 执行 RPC 调用
auto result = client->GetNode("/path/to/node");
```

### 服务管理
```bash
# 获取代理统计信息
curl http://rpc-proxy:8080/statistics

# 查看活跃连接
curl http://rpc-proxy:8080/connections

# 获取服务列表
curl http://rpc-proxy:8080/services

# 健康检查
curl http://rpc-proxy:8080/health
```

### 调试接口
```bash
# 查看请求统计
curl http://rpc-proxy:8080/debug/request_stats

# 查看连接池状态
curl http://rpc-proxy:8080/debug/connection_pool

# 启用详细日志
curl -X POST http://rpc-proxy:8080/debug/set_log_level \
  -d '{"level": "debug"}'

# 查看配置
curl http://rpc-proxy:8080/config
```

## 实现原理

### 请求路由机制
1. **请求接收**: 接收客户端的 RPC 请求
2. **身份验证**: 验证客户端身份和权限
3. **服务发现**: 查找目标服务实例
4. **负载均衡**: 选择最优的服务实例
5. **请求转发**: 转发请求到目标服务
6. **响应处理**: 处理响应并返回客户端

### 连接管理机制
1. **连接创建**: 按需创建与后端服务的连接
2. **连接复用**: 复用现有连接减少开销
3. **健康检查**: 定期检查连接健康状态
4. **连接回收**: 回收和关闭无用连接
5. **故障转移**: 处理连接故障和转移

### 负载均衡策略
1. **轮询算法**: 依次选择服务实例
2. **最少连接**: 选择连接数最少的实例
3. **一致性哈希**: 基于请求内容选择实例
4. **加权轮询**: 根据实例性能加权选择
5. **自适应**: 根据实例性能动态调整

### 故障处理机制
1. **故障检测**: 检测服务实例故障
2. **自动重试**: 自动重试失败的请求
3. **故障转移**: 转移请求到健康实例
4. **服务恢复**: 自动恢复故障服务
5. **降级处理**: 在部分故障时降级服务

## 性能优化

### 连接优化
- 连接池管理和复用
- 长连接和 keepalive
- 连接预热和批量创建
- 智能连接调度

### 协议优化
- 消息压缩和批处理
- 异步 IO 和事件驱动
- 协议序列化优化
- 传输层优化

### 缓存优化
- 响应结果缓存
- 服务发现缓存
- 路由规则缓存
- 元数据缓存

## 监控和调试

### 关键指标
- 请求处理数量和延迟
- 连接池使用情况
- 错误率和重试次数
- 负载均衡效果
- 服务健康状态

### 监控端点
```bash
# 性能指标
GET /metrics

# 连接状态
GET /connections

# 服务状态
GET /services

# 请求统计
GET /request_stats

# 错误统计
GET /errors
```

### 调试工具
```bash
# 启用详细日志
export RPC_PROXY_LOG_LEVEL=debug

# 跟踪请求
curl http://rpc-proxy:8080/debug/trace?request_id=xxx

# 查看堆栈信息
curl http://rpc-proxy:8080/debug/pprof/heap

# CPU 性能分析
curl http://rpc-proxy:8080/debug/pprof/profile
```

## 故障排除

### 常见问题
1. **连接超时**: 检查网络配置和服务状态
2. **认证失败**: 验证 Token 和权限配置
3. **性能下降**: 检查负载和资源配置
4. **服务发现失败**: 检查 Discovery Server 连接

### 调试步骤
1. 检查服务启动日志
2. 验证网络连接和防火墙
3. 检查后端服务状态
4. 分析性能指标
5. 测试配置和权限

### 恢复策略
- 自动重试和重连
- 服务实例替换
- 配置回滚
- 紧急降级处理

## 相关组件

- **Discovery Server**: 服务发现服务
- **Master**: 集群主节点服务
- **Scheduler**: 作业调度服务
- **Node**: 数据节点服务
- **HTTP Proxy**: HTTP 代理服务

## 最佳实践

### 部署建议
- 多实例部署提高可用性
- 地理分布减少延迟
- 负载均衡器前端
- 健康检查配置

### 性能调优
- 根据负载调整连接池大小
- 优化负载均衡策略
- 配置适当的超时时间
- 监控和调优瓶颈

### 安全管理
- 定期更新认证配置
- 实施网络隔离
- 监控异常访问
- 加密敏感通信

## 版本历史

- 初始版本支持基本 RPC 代理功能
- 增加服务发现和负载均衡
- 增强认证和授权机制
- 增加性能监控和调试功能
- 性能优化和稳定性改进