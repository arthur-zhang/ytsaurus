# TCP 代理服务 (TCP Proxy)

## 概述

TCP Proxy 是 YTsaurus 分布式存储系统中的 TCP 协议代理服务，为基于 TCP 协议的客户端提供统一的访问入口。它负责处理 TCP 连接的建立、维护和路由，支持多种 TCP 协议的代理和转发，确保可靠、高效的 TCP 通信服务。

## 功能特性

### 核心功能
- **TCP 连接管理**: 管理客户端的 TCP 连接和会话
- **协议路由**: 根据 TCP 协议类型路由到相应服务
- **负载均衡**: 在多个后端服务间实现负载均衡
- **连接复用**: 优化连接资源的使用效率
- **故障转移**: 处理后端服务的故障和恢复

### 高级特性
- **协议识别**: 自动识别和分类 TCP 协议
- **连接优化**: 优化 TCP 连接参数和性能
- **流量控制**: 实施 QoS 和流量限制
- **安全防护**: 防御网络攻击和异常流量
- **监控统计**: 详细的连接和流量统计

## 架构设计

### 组件架构
```
TCP Proxy
├── Connection Manager (连接管理器)
│   ├── Connection Acceptor (连接接收器)
│   ├── Session Manager (会话管理器)
│   └── Connection Pool (连接池)
├── Protocol Handler (协议处理器)
│   ├── Protocol Detector (协议检测器)
│   ├── Protocol Router (协议路由器)
│   └── Protocol Adapters (协议适配器)
├── Router (路由器)
│   ├── Routing Engine (路由引擎)
│   ├── Load Balancer (负载均衡器)
│   └── Health Checker (健康检查器)
├── Security Layer (安全层)
│   ├── Access Control (访问控制)
│   ├── Rate Limiter (限流器)
│   └── Firewall (防火墙)
└── Monitoring System (监控系统)
    ├── Connection Metrics (连接指标)
    ├── Traffic Statistics (流量统计)
    └── Performance Monitor (性能监控器)
```

### 关键组件说明

#### 1. Connection Manager (连接管理器)
- 接受和处理客户端 TCP 连接
- 管理连接的生命周期和状态
- 维护连接池和资源复用
- 处理连接超时和清理

#### 2. Protocol Detector (协议检测器)
- 检测和识别 TCP 协议类型
- 分析协议特征和参数
- 支持自定义协议识别规则
- 提供协议元数据信息

#### 3. Router (路由器)
- 根据协议和目标路由连接
- 实施负载均衡策略
- 处理服务发现和更新
- 管理路由规则和策略

#### 4. Security Layer (安全层)
- 实施访问控制和安全策略
- 防护网络攻击和异常流量
- 管理连接限制和配额
- 提供安全审计和日志

## 支持的协议类型

### 1. HTTP/HTTPS
```yaml
protocol: "http"
features:
  - "request_routing"
  - "load_balancing"
  - "ssl_termination"
  - "compression"
```

### 2. MySQL
```yaml
protocol: "mysql"
features:
  - "connection_pooling"
  - "read_write_splitting"
  - "query_routing"
  - "authentication_proxy"
```

### 3. Redis
```yaml
protocol: "redis"
features:
  - "cluster_support"
  - "pubsub_proxy"
  - "pipelining"
  - "failover_support"
```

### 4. 自定义 TCP
```yaml
protocol: "custom"
features:
  - "raw_tcp_proxy"
  - "protocol_detection"
  - "custom_routing"
  - "transparent_proxy"
```

## 配置说明

### 基本配置结构
```yaml
tcp_proxy:
  # 服务器配置
  server:
    listen_port: 3306               # TCP 监听端口
    max_connections: 10000          # 最大连接数
    connection_timeout: 30000ms     # 连接超时时间
    idle_timeout: 60000ms           # 空闲超时时间
    buffer_size: 64KB               # 缓冲区大小

  # 路由配置
  routing:
    default_backend: "cluster_mysql"
    enable_protocol_detection: true # 启用协议检测
    routing_rules:
      - protocol: "mysql"
        backend: "mysql_cluster"
      - protocol: "redis"
        backend: "redis_cluster"

  # 后端服务配置
  backends:
    mysql_cluster:
      type: "mysql"
      instances: [
        "mysql1:3306",
        "mysql2:3306",
        "mysql3:3306"
      ]
      load_balance: "round_robin"
      health_check:
        enabled: true
        interval: 30s
        timeout: 5s
```

### 负载均衡配置
```yaml
tcp_proxy:
  load_balancer:
    default_algorithm: "least_connections"  # 默认算法
    algorithms:
      round_robin:
        enabled: true
      least_connections:
        enabled: true
      weighted_round_robin:
        enabled: true
      consistent_hash:
        enabled: true
        hash_function: "crc32"

    # 权重配置
    weights:
      "mysql1:3306": 1
      "mysql2:3306": 2
      "mysql3:3306": 1
```

### 安全配置
```yaml
tcp_proxy:
  security:
    enable_access_control: true   # 启用访问控制
    max_connections_per_ip: 100   # 每IP最大连接数
    enable_rate_limiting: true    # 启用限流

    # 访问控制列表
    acl:
      - action: "allow"
        source: "10.0.0.0/8"
      - action: "allow"
        source: "192.168.0.0/16"
      - action: "deny"
        source: "0.0.0.0/0"

    # 限流配置
    rate_limiting:
      global_limit: 10000          # 全局连接限制
      per_ip_limit: 100           # 每IP连接限制
      burst_size: 50              # 突发大小
```

### 性能优化配置
```yaml
tcp_proxy:
  performance:
    # TCP 参数优化
    tcp_options:
      enable_tcp_nodelay: true     # 启用 TCP_NODELAY
      enable_keepalive: true       # 启用 keepalive
      keepalive_idle: 60s          # keepalive 空闲时间
      keepalive_intvl: 30s         # keepalive 间隔
      keepalive_cnt: 3             # keepalive 重试次数

    # 缓冲区配置
    buffers:
      read_buffer_size: 64KB       # 读取缓冲区
      write_buffer_size: 64KB      # 写入缓冲区
      buffer_pool_size: 1000       # 缓冲池大小

    # 线程配置
    threads:
      io_threads: 4               # IO 线程数
      worker_threads: 8            # 工作线程数
      max_pending_connections: 10000 # 最大挂起连接
```

## 使用方法

### 启动服务
```bash
# 从构建目录启动
./yt/yt/server/all/ytserver-all --config tcp_proxy.config.yson

# 或使用特定配置
./ytserver-tcp-proxy --config config.yson
```

### 客户端连接
```bash
# MySQL 客户端连接
mysql -h tcp-proxy -P 3306 -u user -p database

# Redis 客户端连接
redis-cli -h tcp-proxy -p 6379

# Telnet 测试连接
telnet tcp-proxy 3306
```

### 管理操作
```bash
# 获取代理状态
curl http://tcp-proxy:8084/status

# 查看连接统计
curl http://tcp-proxy:8084/connections

# 获取后端状态
curl http://tcp-proxy:8084/backends

# 查看路由信息
curl http://tcp-proxy:8084/routing
```

### 配置管理
```bash
# 重新加载配置
curl -X POST http://tcp-proxy:8084/reload_config

# 更新后端服务
curl -X PUT http://tcp-proxy:8084/backends/mysql_cluster \
  -H "Content-Type: application/json" \
  -d '{"instances": ["mysql1:3306", "mysql2:3306"]}'

# 启用/禁用后端
curl -X POST http://tcp-proxy:8084/backends/mysql_cluster/enable \
  -d '{"enabled": false}'
```

## 实现原理

### 连接处理机制
1. **连接建立**: 接受客户端 TCP 连接
2. **协议检测**: 分析连接数据识别协议
3. **路由决策**: 根据协议和规则选择后端
4. **连接转发**: 建立与后端的连接并转发数据
5. **状态维护**: 维护连接状态和会话信息

### 协议检测机制
1. **初始分析**: 分析连接的初始数据包
2. **特征匹配**: 与已知协议特征进行匹配
3. **状态机检测**: 使用状态机进行协议识别
4. **学习机制**: 基于历史数据学习协议模式
5. **自适应更新**: 动态更新协议识别规则

### 负载均衡机制
1. **权重计算**: 根据后端性能计算权重
2. **连接选择**: 按算法选择后端连接
3. **健康检查**: 定期检查后端健康状态
4. **动态调整**: 根据负载动态调整
5. **故障处理**: 处理后端故障和恢复

### 安全防护机制
1. **访问控制**: 基于IP和规则的访问控制
2. **连接限制**: 限制连接数和频率
3. **攻击防护**: 识别和防御网络攻击
4. **流量监控**: 监控异常流量模式
5. **自动响应**: 自动响应安全事件

## 性能优化

### 连接优化
- 连接池管理和复用
- 长连接和 keepalive 优化
- 连接预热和批量建立
- 智能连接调度

### 数据传输优化
- 零拷贝数据传输
- 批量数据处理
- 数据压缩和缓存
- 流控制和背压处理

### 资源使用优化
- 内存池管理
- CPU 亲和性设置
- 线程池优化
- 缓冲区复用

## 监控和调试

### 关键指标
- 连接数量和状态
- 数据传输量和速度
- 后端服务状态
- 错误率和重试次数
- 系统资源使用情况

### 监控端点
```bash
# 服务状态
GET /status

# 连接统计
GET /connections

# 后端状态
GET /backends

# 流量统计
GET /traffic

# 性能指标
GET /metrics
```

### 调试工具
```bash
# 启用详细日志
export TCP_PROXY_LOG_LEVEL=debug

# 连接跟踪
curl http://tcp-proxy:8084/debug/connections

# 协议检测信息
curl http://tcp-proxy:8084/debug/protocols

# 路由决策信息
curl http://tcp-proxy:8084/debug/routing
```

## 故障排除

### 常见问题
1. **连接被拒绝**: 检查监听端口和防火墙
2. **协议识别失败**: 验证协议配置和数据
3. **后端连接失败**: 检查后端服务状态
4. **性能下降**: 分析负载和资源配置

### 调试步骤
1. 检查服务启动日志
2. 验证网络连接和端口
3. 测试后端服务可用性
4. 分析连接和流量统计
5. 检查配置文件设置

### 恢复策略
- 自动重连和重试
- 后端故障转移
- 服务降级处理
- 紧急配置回滚

## 相关组件

- **Master**: 集群主节点服务
- **HTTP Proxy**: HTTP 协议代理
- **RPC Proxy**: RPC 通信代理
- **Node**: 数据节点服务

## 最佳实践

### 部署建议
- 高可用部署配置
- 网络拓扑优化
- 负载均衡器配置
- 监控告警设置

### 性能调优
- 根据流量调整参数
- 优化 TCP 参数设置
- 合理配置资源限制
- 定期性能评估

### 安全管理
- 定期更新安全配置
- 监控异常流量
- 实施访问控制
- 加强网络安全

## 版本历史

- 初始版本支持基本 TCP 代理
- 增加协议检测和路由
- 增强负载均衡功能
- 增加安全防护机制
- 性能优化和稳定性改进