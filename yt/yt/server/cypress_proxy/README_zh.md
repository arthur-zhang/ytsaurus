# Cypress 代理服务 (Cypress Proxy)

## 概述

Cypress Proxy 是 YTsaurus 分布式存储系统中的核心代理服务，负责处理客户端与 Cypress 元数据系统之间的交互。它作为元数据操作的入口点，提供了统一的对象服务接口，支持高效的元数据访问和事务处理。

## 功能特性

### 核心功能
- **对象服务 (Object Service)**: 提供统一的元数据操作接口
- **事务支持**: 支持 ACID 分布式事务处理
- **访问控制**: 实现细粒度的权限控制和用户认证
- **Sequoia 集成**: 与新一代分布式事务系统 Sequoia 深度集成
- **请求路由**: 智能的请求分发和负载均衡
- **响应缓存**: 支持响应缓存以提高性能

### 高级特性
- **用户目录同步**: 自动同步用户目录信息
- **分布式限流**: 基于用户和负载的智能请求限流
- **动态配置**: 支持运行时配置更新
- **多阶段执行**: 支持两阶段请求执行模式
- **主节点连接**: 与 Master 节点的高可用连接

## 架构设计

### 组件架构
```
Cypress Proxy
├── Bootstrap (启动引导)
├── Object Service (对象服务)
│   ├── Master Proxy (主节点代理)
│   ├── Node Proxy (节点代理)
│   └── Sequoia Service (Sequoia 服务)
├── Access Control (访问控制)
├── User Directory (用户目录)
├── Response Keeper (响应保持器)
└── Master Connector (主节点连接器)
```

### 关键组件说明

#### 1. Bootstrap (启动引导)
- 负责服务的初始化和启动
- 配置管理和服务发现
- 依赖注入和组件组装

#### 2. Object Service (对象服务)
- 核心的元数据处理服务
- 支持 CRUD 操作
- 事务管理和并发控制

#### 3. Sequoia 集成
- 新一代分布式事务系统
- 提供更好的性能和可扩展性
- 支持跨数据中心的事务一致性

#### 4. Access Control (访问控制)
- 用户身份验证和授权
- 细粒度的权限管理
- 支持多种认证方式

## 配置说明

### 基本配置结构
```yaml
cypress_proxy:
  # 启动配置
  abort_on_unrecognized_options: false

  # 用户目录同步配置
  user_directory_synchronizer:
    sync_period: 5000ms          # 同步周期
    sync_splay: 1000ms           # 同步抖动

  # 心跳配置
  heartbeat_period: 5000ms

  # 动态配置管理
  dynamic_config_manager:
    update_period: 5000ms
```

### 对象服务动态配置
```yaml
object_service:
  # 是否允许绕过 Master 解析
  allow_bypass_master_resolve: false

  # 分布式限流配置
  distributed_throttler:
    mode: local                   # local/remote/dynamic
    rpc_timeout: 5000ms

  # 按用户请求权重限流
  enable_per_user_request_weight_throttling: true

  # 转发请求超时保留
  forwarded_request_timeout_reserve: 1000ms
```

### Sequoia 响应保持器配置
```yaml
response_keeper:
  enable: true                   # 启用响应保持
```

## 使用方法

### 启动服务
```bash
# 从构建目录启动
./yt/yt/server/all/ytserver-all --config cypress_proxy.config.yson

# 或使用特定配置
./ytserver-cypress-proxy --config config.yson
```

### 客户端连接
```cpp
// C++ 客户端连接示例
#include <yt/yt/client/api/native.h>

auto connection = NApi::NNative::CreateConnection(config);
auto client = connection->CreateClient(NApi::TClientOptions{...});

// 执行元数据操作
auto result = client->GetNode("/path/to/node");
```

### 配置管理
```yaml
# 动态配置更新
curl -X POST http://cypress-proxy:8080/config/set \
  -H "Content-Type: application/json" \
  -d '{
    "object_service": {
      "thread_pool_size": 4,
      "default_get_response_size_limit": 1000000
    }
  }'
```

## 实现原理

### 请求处理流程
1. **请求接收**: 客户端发送请求到 Cypress Proxy
2. **身份验证**: 验证用户身份和权限
3. **路由决策**: 根据请求类型选择处理路径
4. **事务处理**: 如需要则启动分布式事务
5. **执行操作**: 在 Master 或 Sequoia 上执行操作
6. **结果返回**: 返回结果给客户端
7. **响应缓存**: 可选地缓存响应结果

### 两阶段执行模式
- **第一阶段**: 在 Sequoia 上进行请求解析
- **第二阶段**: 在 Master 上执行具体操作
- 支持跳过第一阶段以优化性能

### 一致性保证
- **强一致性**: 使用分布式共识确保一致性
- **事务隔离**: 支持快照隔离和串行化隔离
- **故障恢复**: 自动故障检测和恢复机制

## 监控和调试

### 关键指标
- 请求处理延迟和吞吐量
- 事务成功率
- 缓存命中率
- 连接池状态
- 错误率统计

### 日志级别
```yaml
logging:
  level: info                    # trace/debug/info/warn/error/fatal
 _flush_period: 1000ms
  _rate_limit: 10000
```

### 健康检查
```bash
# 检查服务状态
curl http://cypress-proxy:8080/health

# 检查组件状态
curl http://cypress-proxy:8080/components
```

## 性能优化

### 配置调优
- 合理设置线程池大小
- 优化缓存配置
- 调整限流参数

### 扩展性
- 支持水平扩展
- 负载均衡配置
- 多区域部署

## 故障排除

### 常见问题
1. **连接超时**: 检查网络配置和超时设置
2. **权限错误**: 验证用户权限和认证配置
3. **性能问题**: 检查缓存配置和资源使用
4. **事务失败**: 检查分布式一致性状态

### 调试工具
- 日志分析
- 性能分析器
- 分布式跟踪
- 监控仪表板

## 相关组件

- **Master**: 核心元数据管理服务
- **Sequoia**: 新一代分布式事务系统
- **RPC Proxy**: RPC 通信代理
- **Discovery Server**: 服务发现服务

## 版本历史

- 支持 Sequoia 集成
- 增强的访问控制
- 性能优化和稳定性改进