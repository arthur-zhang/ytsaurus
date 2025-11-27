# 集群发现服务 (Discovery Server)

## 概述

Discovery Server 是 YTsaurus 分布式存储系统中的核心服务发现组件，负责管理和维护集群中所有服务实例的注册、发现和健康状态监控。它为系统中的各个组件提供服务定位和元数据查询功能，是整个集群服务治理的基础设施。

## 功能特性

### 核心功能
- **服务注册**: 自动接收和管理各服务实例的注册信息
- **服务发现**: 提供高效的服务查询和发现接口
- **健康检查**: 持续监控服务实例的健康状态
- **元数据管理**: 管理服务相关的配置和元数据信息
- **动态更新**: 支持服务信息的实时更新

### 高级特性
- **高可用性**: 支持多实例部署和故障转移
- **负载感知**: 提供服务实例的负载信息
- **版本管理**: 支持服务版本信息管理
- **多租户**: 支持多租户环境下的服务隔离
- **监控集成**: 集成监控和告警系统

## 架构设计

### 组件架构
```
Discovery Server
├── Bootstrap (启动引导)
├── Discovery Service (发现服务)
│   ├── Service Registry (服务注册表)
│   ├── Health Monitor (健康监控器)
│   └── MetaData Manager (元数据管理器)
├── Communication Layer (通信层)
│   ├── Bus Client (总线客户端)
│   └── RPC Interface (RPC 接口)
└── Worker Thread Pool (工作线程池)
```

### 关键组件说明

#### 1. Service Registry (服务注册表)
- 存储所有注册服务的信息
- 支持服务的动态添加和删除
- 提供高效的服务查询接口

#### 2. Health Monitor (健康监控器)
- 定期检查服务实例的健康状态
- 支持多种健康检查方式
- 自动标记不健康的服务实例

#### 3. MetaData Manager (元数据管理器)
- 管理服务的配置信息
- 支持版本控制和配置更新
- 提供元数据查询接口

#### 4. Communication Layer (通信层)
- 提供高性能的 RPC 通信
- 支持多种通信协议
- 处理客户端请求和响应

## 配置说明

### 基本配置结构
```yaml
discovery_server:
  # 启动配置
  abort_on_unrecognized_options: false

  # 工作线程池配置
  worker_thread_pool_size: 4

  # 总线客户端配置
  bus_client:
    read_buffer_size: 1MB
    write_buffer_size: 1MB
    connect_timeout: 5000ms
    read_timeout: 30000ms

  # 发现服务配置
  discovery_server:
    # 服务监听地址
    listen_addresses:
      - "0.0.0.0:21345"

    # 心跳配置
    heartbeat_interval: 5000ms
    heartbeat_timeout: 15000ms

    # 服务过期时间
    service_expiration_timeout: 60000ms

    # 健康检查配置
    health_check:
      enabled: true
      interval: 10000ms
      timeout: 5000ms
```

### 高级配置
```yaml
discovery_server:
  # 监控配置
  monitoring:
    enable_profiling: true
    enable_solomon_export: true

  # 安全配置
  security:
    enable_tls: false
    cert_file: ""
    key_file: ""

  # 性能调优
  performance:
    max_concurrent_requests: 1000
    request_timeout: 30000ms
    response_compression: true
```

## 使用方法

### 启动服务
```bash
# 从构建目录启动
./yt/yt/server/all/ytserver-all --config discovery_server.config.yson

# 或使用特定配置
./ytserver-discovery-server --config config.yson
```

### 服务注册
```cpp
// C++ 客户端注册服务示例
#include <yt/yt/server/lib/discovery_server/public.h>

// 创建发现客户端
auto discoveryClient = CreateDiscoveryClient(config);

// 注册服务
TServiceInfo serviceInfo;
serviceInfo.ServiceId = "my-service-001";
serviceInfo.ServiceName = "my-service";
serviceInfo.Addresses = {"10.0.0.1:8080", "10.0.0.2:8080"};
serviceInfo.Metadata = {
    {"version", "1.0.0"},
    {"role", "primary"}
};

await discoveryClient->RegisterService(serviceInfo);
```

### 服务发现
```cpp
// 发现服务实例
auto services = await discoveryClient->DiscoverServices("my-service");
for (const auto& service : services) {
    std::cout << "Service: " << service.ServiceId
              << " Addresses: ";
    for (const auto& addr : service.Addresses) {
        std::cout << addr << " ";
    }
    std::cout << std::endl;
}
```

### 健康检查
```cpp
// 设置健康检查回调
discoveryClient->SetHealthCheckHandler(
    []() -> bool {
        // 实现健康检查逻辑
        return IsServiceHealthy();
    }
);
```

### 配置管理
```yaml
# 动态配置更新
curl -X POST http://discovery-server:21345/config/set \
  -H "Content-Type: application/json" \
  -d '{
    "discovery_server": {
      "heartbeat_interval": 3000ms,
      "health_check": {
        "interval": 5000ms
      }
    }
  }'
```

## 实现原理

### 服务注册流程
1. **服务启动**: 服务实例启动后连接到 Discovery Server
2. **注册请求**: 发送服务注册信息，包括服务ID、地址、元数据等
3. **信息验证**: Discovery Server 验证注册信息的有效性
4. **存储记录**: 将服务信息存储到注册表中
5. **返回确认**: 向服务实例返回注册成功确认

### 健康检查机制
1. **心跳检测**: 定期接收服务实例的心跳消息
2. **主动探测**: 主动探测服务实例的可用性
3. **状态更新**: 根据检查结果更新服务健康状态
4. **故障转移**: 自动移除不健康的服务实例

### 服务发现流程
1. **查询请求**: 客户端发送服务发现请求
2. **条件过滤**: 根据查询条件过滤服务实例
3. **负载均衡**: 根据负载情况选择合适的服务实例
4. **返回结果**: 返回可用的服务实例列表
5. **缓存更新**: 更新本地缓存以提高查询效率

### 一致性保证
- **最终一致性**: 服务注册表采用最终一致性模型
- **故障恢复**: 支持故障恢复后数据同步
- **分布式协调**: 使用分布式锁确保操作原子性

## 监控和调试

### 关键指标
- 注册服务数量和变化趋势
- 服务健康状态统计
- 请求处理延迟和吞吐量
- 错误率统计
- 网络连接状态

### 监控端点
```bash
# 服务状态检查
curl http://discovery-server:21345/health

# 获取服务统计信息
curl http://discovery-server:21345/statistics

# 获取注册的所有服务
curl http://discovery-server:21345/services

# 获取特定服务详情
curl http://discovery-server:21345/services/my-service
```

### 日志配置
```yaml
logging:
  level: info                    # trace/debug/info/warn/error/fatal
  flush_period: 1000ms
  rate_limit: 10000

  # 组件级别日志
  components:
    discovery_server: debug
    health_monitor: info
```

## 性能优化

### 配置调优
- 合理设置工作线程池大小
- 优化网络缓冲区配置
- 调整心跳间隔和超时时间

### 扩展性
- 支持水平扩展
- 数据分片和负载均衡
- 缓存策略优化

### 网络优化
- 连接池管理
- 批量操作支持
- 压缩传输

## 故障排除

### 常见问题
1. **服务注册失败**: 检查网络连接和配置信息
2. **健康检查超时**: 调整超时配置和检查策略
3. **服务发现延迟**: 优化缓存和网络配置
4. **连接数过多**: 调整连接池和超时设置

### 调试工具
- 分布式跟踪系统
- 性能分析器
- 网络诊断工具
- 日志分析工具

### 故障恢复
- 自动故障检测
- 数据备份和恢复
- 优雅降级策略

## 安全考虑

### 认证和授权
- 客户端身份验证
- 访问权限控制
- API 密钥管理

### 网络安全
- TLS 加密通信
- 防火墙配置
- DDoS 防护

### 数据安全
- 敏感信息加密
- 访问审计日志
- 数据脱敏

## 相关组件

- **Master**: 集群主节点服务
- **RPC Proxy**: RPC 通信代理
- **Monitoring**: 监控和告警系统
- **Configuration**: 配置管理服务

## 最佳实践

### 部署建议
- 多实例部署确保高可用
- 地理分布提高可靠性
- 资源隔离防止相互影响

### 运维管理
- 定期健康检查
- 监控告警配置
- 自动化运维脚本

### 性能调优
- 根据负载调整配置
- 定期性能测试
- 持续优化改进

## 版本历史

- 初始版本支持基本服务发现功能
- 增加健康检查和监控功能
- 性能优化和稳定性改进
- 安全功能增强