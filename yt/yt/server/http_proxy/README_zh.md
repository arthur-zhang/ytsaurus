# HTTP 代理服务 (HTTP Proxy)

## 概述

HTTP Proxy 是 YTsaurus 分布式存储系统中的核心 HTTP 网关服务，为客户端提供基于 HTTP/HTTPS 协议的统一访问接口。它支持 RESTful API、数据上传下载、查询执行、监控数据收集等多种功能，是外部系统与 YTsaurus 集群交互的主要入口点。

## 功能特性

### 核心功能
- **HTTP/HTTPS 接口**: 提供完整的 RESTful API 支持
- **数据操作**: 支持文件的读写、删除和元数据查询
- **查询执行**: 支持 SQL 查询和 MapReduce 作业执行
- **认证授权**: 集成多种认证方式和权限控制
- **格式转换**: 支持多种数据格式之间的转换

### 高级特性
- **ClickHouse 集成**: 提供 CHYT (ClickHouse on YTsaurus) 支持
- **数据监控**: 集成 Solomon 监控系统
- **分布式追踪**: 支持 Jaeger 链路追踪
- **缓存优化**: 智能缓存机制提高性能
- **负载均衡**: 支持多实例部署和负载分发

## 架构设计

### 组件架构
```
HTTP Proxy
├── HTTP Server (HTTP 服务器)
│   ├── Request Handler (请求处理器)
│   ├── Response Builder (响应构建器)
│   └── Connection Manager (连接管理器)
├── API Layer (API 层)
│   ├── Data API (数据操作 API)
│   ├── Query API (查询执行 API)
│   ├── Admin API (管理 API)
│   └── Monitoring API (监控 API)
├── Security Layer (安全层)
│   ├── Authentication (认证模块)
│   ├── Authorization (授权模块)
│   └── Access Control (访问控制)
├── Integration Layer (集成层)
│   ├── ClickHouse Integration (CHYT 集成)
│   ├── Solomon Proxy (监控代理)
│   └── Tracing Support (链路追踪)
└── Performance Layer (性能层)
    ├── Response Caching (响应缓存)
    ├── Request Throttling (请求限流)
    └── Load Balancing (负载均衡)
```

### 关键组件说明

#### 1. HTTP Server (HTTP 服务器)
- 处理 HTTP/HTTPS 请求和响应
- 支持多种 HTTP 方法和协议版本
- 管理连接池和会话状态

#### 2. API Layer (API 层)
- 提供统一的 API 接口定义
- 处理不同类型的请求路由
- 实现数据格式转换和验证

#### 3. Security Layer (安全层)
- 用户身份验证和权限验证
- 支持 Token、Cookie、TLS 等认证方式
- 实现细粒度的访问控制

#### 4. Integration Layer (集成层)
- 与 ClickHouse 和其他系统集成
- 监控数据收集和转发
- 分布式链路追踪支持

## 配置说明

### 基本配置结构
```yaml
http_proxy:
  # 服务器配置
  server:
    listen_port: 80                 # HTTP 监听端口
    listen_port_secure: 443         # HTTPS 监听端口
    max_concurrent_requests: 1000   # 最大并发请求数
    request_timeout: 30000ms        # 请求超时时间
    keep_alive_timeout: 60000ms     # 连接保活时间

  # API 客户端配置
  api_client:
    connection_timeout: 5000ms
    request_timeout: 30000ms
    retry_count: 3
    backoff_policy: exponential

  # 安全配置
  security:
    enable_authentication: true
    enable_authorization: true
    authentication_methods: ["token", "cookie", "tls"]

  # 缓存配置
  cache:
    enable_response_cache: true
    max_cache_size: 1GB
    cache_ttl: 300s

  # 限流配置
  throttling:
    enable_request_throttling: true
    max_requests_per_second: 100
    burst_size: 200
```

### ClickHouse 集成配置
```yaml
http_proxy:
  clickhouse:
    enable_chyt: true
    default_settings:
      max_execution_time: 600s
      max_result_rows: 1000000
      max_memory_usage: 4GB
    cluster_config:
      cluster_name: "default"
      max_threads: 4
```

### 监控配置
```yaml
http_proxy:
  monitoring:
    enable_solomon: true
    solomon_endpoint: "http://solomon-proxy:10042"
    profiling_interval: 15s
    export_system_metrics: true

  tracing:
    enable_jaeger: true
    jaeger_endpoint: "http://jaeger-collector:14268/api/traces"
    sample_rate: 0.1
```

## 使用方法

### 基本 API 操作
```bash
# 获取节点信息
curl -X GET "http://http-proxy:80/api/v1/nodes" \
  -H "Authorization: Bearer <token>"

# 上传文件
curl -X PUT "http://http-proxy:80/api/v1/file" \
  -H "Authorization: Bearer <token>" \
  -F "file=@local_file.txt" \
  -F "path=/tmp/uploaded_file.txt"

# 下载文件
curl -X GET "http://http-proxy:80/api/v1/file?path=/tmp/data.txt" \
  -H "Authorization: Bearer <token>" \
  -o downloaded_file.txt
```

### 查询执行
```bash
# 执行 SQL 查询
curl -X POST "http://http-proxy:80/api/v1/query" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT * FROM `/tmp/table` WHERE value > 100",
    "format": "json"
  }'

# 执行 MapReduce 作业
curl -X POST "http://http-proxy:80/api/v1/mapreduce" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "mapper": "/usr/bin/mapper.py",
    "reducer": "/usr/bin/reducer.py",
    "input_table": "/tmp/input",
    "output_table": "/tmp/output"
  }'
```

### ClickHouse 查询
```bash
# 执行 CHYT 查询
curl -X POST "http://http-proxy:80/api/v1/chyt/query" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT count(*) FROM `yt://tmp/table`",
    "settings": {
      "max_execution_time": 60
    }
  }'
```

### 监控和管理
```bash
# 获取服务状态
curl -X GET "http://http-proxy:80/api/v1/status"

# 获取统计信息
curl -X GET "http://http-proxy:80/api/v1/statistics"

# 健康检查
curl -X GET "http://http-proxy:80/health"
```

## 实现原理

### 请求处理流程
1. **请求接收**: HTTP 服务器接收客户端请求
2. **认证验证**: 验证用户身份和访问权限
3. **请求解析**: 解析请求参数和内容
4. **路由分发**: 根据请求类型分发到相应处理器
5. **业务处理**: 调用后端 API 执行实际操作
6. **结果处理**: 格式化处理结果和响应
7. **返回响应**: 构建并返回 HTTP 响应
8. **日志记录**: 记录请求日志和性能指标

### 安全机制
1. **身份认证**: 支持 Token、Cookie、TLS 等多种方式
2. **权限验证**: 基于角色和资源的访问控制
3. **请求过滤**: 防止恶意请求和攻击
4. **数据加密**: 支持 TLS 加密传输

### 缓存策略
1. **响应缓存**: 缓存常用查询结果
2. **连接复用**: 复用后端连接减少开销
3. **内存管理**: 智能缓存淘汰机制
4. **一致性保证**: 确保缓存数据的一致性

### 负载均衡
1. **请求分发**: 在多个实例间分发请求
2. **健康检查**: 监控实例健康状态
3. **故障转移**: 自动处理实例故障
4. **权重调整**: 根据性能调整负载权重

## 监控和调试

### 关键指标
- 请求处理数量和延迟分布
- 错误率和成功率统计
- 资源使用情况 (CPU、内存、网络)
- 缓存命中率和性能
- 并发连接数和吞吐量

### 监控端点
```bash
# Prometheus 指标
curl http://http-proxy:80/metrics

# 服务健康状态
curl http://http-proxy:80/health

# 详细统计信息
curl http://http-proxy:80/statistics
```

### 日志配置
```yaml
logging:
  level: info
  request_logging: true
  response_logging: false
  slow_request_threshold: 1000ms

  # 组件级别日志
  components:
    http_server: info
    api_handler: debug
    authentication: warn
```

### 调试工具
```bash
# 启用调试模式
curl "http://http-proxy:80/api/v1/debug?enable=true"

# 查看请求详情
curl -v "http://http-proxy:80/api/v1/nodes" \
  -H "X-Debug: true"

# 性能分析
curl "http://http-proxy:80/api/v1/performance"
```

## 性能优化

### 连接优化
- 使用连接池减少连接开销
- 启用 HTTP Keep-Alive
- 优化 TCP 参数配置

### 缓存优化
- 合理设置缓存大小和 TTL
- 实施智能缓存策略
- 使用内存映射文件

### 并发处理
- 调整工作线程数量
- 使用异步 I/O 模型
- 实施请求队列管理

## 安全考虑

### 认证安全
- 强制使用 HTTPS
- 定期轮换访问令牌
- 实施多因素认证

### 数据安全
- 敏感数据加密存储
- 实施审计日志
- 防止数据泄露

### 网络安全
- 配置防火墙规则
- 实施 DDoS 防护
- 使用安全的网络协议

## 故障排除

### 常见问题
1. **认证失败**: 检查 Token 有效性和权限配置
2. **请求超时**: 调整超时配置和检查网络连接
3. **性能问题**: 分析负载分布和资源使用
4. **缓存问题**: 检查缓存配置和一致性

### 调试步骤
1. 检查服务日志和错误信息
2. 验证网络连接和 DNS 解析
3. 分析性能指标和资源使用
4. 测试后端服务可用性

## 相关组件

- **Cypress Proxy**: 元数据操作代理
- **RPC Proxy**: RPC 通信代理
- **Master**: 集群主节点服务
- **Node**: 数据存储和计算节点
- **Scheduler**: 作业调度器

## 最佳实践

### 部署建议
- 使用负载均衡器分发请求
- 配置适当的实例数量
- 启用健康检查和监控

### 性能调优
- 根据负载调整资源配置
- 优化缓存策略
- 监控性能瓶颈

### 安全管理
- 定期更新安全补丁
- 实施安全审计
- 加强访问控制

## 版本历史

- 初始版本支持基本 HTTP API
- 增加 ClickHouse 集成支持
- 增强安全认证机制
- 性能优化和稳定性改进
- 增加监控和调试功能