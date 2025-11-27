# 队列代理服务 (Queue Agent)

## 概述

Queue Agent 是 YTsaurus 分布式存储系统中的队列管理代理服务，专门负责管理和处理分布式消息队列。它提供高性能的消息传递、队列路由、消费者管理和故障恢复功能，为 YTsaurus 生态系统中的异步通信和事件驱动架构提供可靠的消息队列服务。

## 功能特性

### 核心功能
- **队列管理**: 创建、删除和管理消息队列
- **消息传递**: 高效的消息发送、接收和路由
- **消费者管理**: 消费者注册、订阅和负载均衡
- **数据导出**: 队列数据的导出和转换
- **分片管理**: 队列数据的分片和分布

### 高级特性
- **动态分片**: 支持队列的动态分片和重分片
- **配置文件支持**: 从配置文件批量创建队列
- **性能监控**: 详细的队列性能统计和监控
- **容错机制**: 自动故障检测和恢复
- **多协议支持**: 兼容多种消息队列协议

## 架构设计

### 组件架构
```
Queue Agent
├── Queue Management (队列管理)
│   ├── Queue Registry (队列注册表)
│   ├── Queue Controller (队列控制器)
│   └── Queue Storage (队列存储)
├── Consumer Management (消费者管理)
│   ├── Consumer Registry (消费者注册表)
│   ├── Subscription Manager (订阅管理器)
│   └── Load Balancer (负载均衡器)
├── Data Processing (数据处理)
│   ├── Message Processor (消息处理器)
│   ├── Queue Exporter (队列导出器)
│   ├── Sharding Manager (分片管理器)
│   └── Profile Manager (配置管理器)
├── Synchronization (同步层)
│   ├── Cypress Synchronizer (Cypress 同步器)
│   ├── State Manager (状态管理器)
│   └── Consistency Manager (一致性管理器)
└── Monitoring System (监控系统)
    ├── Performance Metrics (性能指标)
    ├── Queue Statistics (队列统计)
    └── Alert Manager (告警管理器)
```

### 关键组件说明

#### 1. Queue Controller (队列控制器)
- 管理队列的生命周期
- 处理队列配置和参数
- 协调队列操作和事务
- 维护队列状态和元数据

#### 2. Consumer Registry (消费者注册表)
- 维护消费者信息
- 管理消费者订阅关系
- 处理消费者加入和离开
- 实施消费者认证和授权

#### 3. Queue Exporter (队列导出器)
- 导出队列数据到外部系统
- 支持多种数据格式和协议
- 处理数据转换和过滤
- 管理导出任务和调度

#### 4. Sharding Manager (分片管理器)
- 管理队列数据分片
- 处理分片分配和迁移
- 优化分片分布策略
- 处理分片故障和恢复

## 支持的队列类型

### 1. FIFO Queue (先进先出队列)
```yaml
queue_type: "fifo"
properties:
  max_message_size: "1MB"
  message_retention: "7d"
  max_queue_size: 1000000
```

### 2. Priority Queue (优先级队列)
```yaml
queue_type: "priority"
properties:
  priority_levels: 5
  max_message_size: "1MB"
  message_retention: "30d"
```

### 3. Delay Queue (延迟队列)
```yaml
queue_type: "delay"
properties:
  max_delay: "30d"
  min_delay: "1s"
  max_message_size: "1MB"
```

### 4. Dead Letter Queue (死信队列)
```yaml
queue_type: "dead_letter"
properties:
  source_queue: "main_queue"
  max_receive_count: 3
  message_retention: "30d"
```

## 配置说明

### 基本配置结构
```yaml
queue_agent:
  # 服务配置
  service:
    listen_port: 8081
    max_concurrent_requests: 10000
    request_timeout: 30000ms

  # 队列存储配置
  storage:
    backend: "yt"                  # 存储后端
    table_prefix: "//sys/queues"
    chunk_size: 1000               # 块大小
    compression: "lz4"             # 压缩算法

  # 消费者配置
  consumers:
    max_consumers_per_queue: 1000
    heartbeat_interval: 30s
    session_timeout: 120s
    auto_acknowledge: true

  # 分片配置
  sharding:
    enabled: true
    default_shard_count: 16
    rebalance_threshold: 0.2
    rebalance_interval: 300s
```

### 队列配置文件支持
```yaml
queue_configs:
  - name: "user_events"
    type: "fifo"
    partition_count: 8
    retention_period: "7d"
    max_message_size: "1MB"

  - name: "priority_tasks"
    type: "priority"
    priority_levels: 5
    partition_count: 4
    retention_period: "30d"

  - name: "delayed_jobs"
    type: "delay"
    max_delay: "24h"
    partition_count: 2
    retention_period: "7d"
```

### 导出配置
```yaml
queue_agent:
  export:
    enabled: true
    export_interval: 60s
    batch_size: 1000

    # 导出目标
    targets:
      - name: "elasticsearch"
        type: "elasticsearch"
        endpoint: "http://elasticsearch:9200"
        index_pattern: "queue-logs-{date}"

      - name: "kafka"
        type: "kafka"
        brokers: ["kafka1:9092", "kafka2:9092"]
        topic: "queue-exports"
```

## 使用方法

### 队列操作
```bash
# 创建队列
curl -X POST http://queue-agent:8081/api/v1/queues \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_queue",
    "type": "fifo",
    "partition_count": 4,
    "retention_period": "7d"
  }'

# 发送消息
curl -X POST http://queue-agent:8081/api/v1/queues/my_queue/messages \
  -H "Content-Type: application/json" \
  -d '{
    "data": "Hello World",
    "attributes": {
      "priority": "high",
      "source": "web"
    }
  }'

# 接收消息
curl -X GET http://queue-agent:8081/api/v1/queues/my_queue/messages?max_count=10

# 删除队列
curl -X DELETE http://queue-agent:8081/api/v1/queues/my_queue
```

### 消费者管理
```bash
# 注册消费者
curl -X POST http://queue-agent:8081/api/v1/consumers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_consumer",
    "queue": "my_queue",
    "subscription": {
      "type": "pull",
      "batch_size": 10,
      "wait_time": 30
    }
  }'

# 订阅队列
curl -X POST http://queue-agent:8081/api/v1/consumers/my_consumer/subscribe \
  -H "Content-Type: application/json" \
  -d '{"queue": "my_queue"}'

# 取消订阅
curl -X DELETE http://queue-agent:8081/api/v1/consumers/my_consumer/subscriptions/my_queue
```

### 配置文件管理
```bash
# 从配置文件创建队列
./ytserver-queue-agent --config queue_agent.yson \
  --load-queue-configs /path/to/queue_configs.yaml

# 重新加载配置
curl -X POST http://queue-agent:8081/api/v1/reload-config

# 查看当前配置
curl -X GET http://queue-agent:8081/api/v1/config
```

## 实现原理

### 消息传递机制
1. **消息接收**: 接收来自生产者的消息
2. **消息验证**: 验证消息格式和内容
3. **消息存储**: 将消息持久化到存储后端
4. **消息路由**: 根据规则路由消息到分片
5. **消息分发**: 将消息分发给订阅的消费者

### 分片策略
1. **哈希分片**: 基于消息键的哈希值
2. **轮询分片**: 按顺序分配消息到分片
3. **负载均衡**: 基于分片负载的动态分配
4. **一致性分片**: 保证消息的顺序性

### 消费者负载均衡
1. **轮询分配**: 消费者间轮流分配消息
2. **公平分配**: 基于消费者处理能力的分配
3. **粘性会话**: 保持消费者和分片的关联
4. **动态调整**: 根据负载动态调整分配

### 导出机制
1. **数据抽取**: 从队列中提取消息数据
2. **格式转换**: 转换为目标系统格式
3. **批量处理**: 批量发送数据提高效率
4. **错误处理**: 处理导出过程中的错误

## 性能优化

### 吞吐量优化
- 批量消息处理
- 异步IO操作
- 数据压缩传输
- 连接池管理

### 延迟优化
- 预取机制
- 缓存热点数据
- 快速路径处理
- 减少序列化开销

### 可扩展性优化
- 水平分片扩展
- 负载均衡优化
- 缓存策略优化
- 存储分层管理

## 监控和调试

### 关键指标
- 消息吞吐量和延迟
- 队列深度和增长速度
- 消费者处理速度
- 错误率和重试次数
- 分片负载分布

### 监控端点
```bash
# 队列统计
curl http://queue-agent:8081/api/v1/queues/stats

# 消费者状态
curl http://queue-agent:8081/api/v1/consumers/stats

# 系统性能指标
curl http://queue-agent:8081/api/v1/metrics

# 导出状态
curl http://queue-agent:8081/api/v1/export/status
```

### 调试工具
```bash
# 启用详细日志
export QUEUE_AGENT_LOG_LEVEL=debug

# 查看队列详情
curl http://queue-agent:8081/api/v1/queues/my_queue/details

# 查看消费者详情
curl http://queue-agent:8081/api/v1/consumers/my_consumer/details

# 跟踪消息流转
curl http://queue-agent:8081/api/v1/trace/message/{message_id}
```

## 故障排除

### 常见问题
1. **消息积压**: 检查消费者处理能力和网络状况
2. **消费者离线**: 检查心跳和连接状态
3. **分片不均**: 检查分片配置和负载均衡
4. **导出失败**: 检查目标系统和网络连接

### 调试步骤
1. 检查队列和消费者状态
2. 分析消息处理日志
3. 验证网络和存储连接
4. 检查资源使用情况
5. 分析性能指标

## 相关组件

- **Master**: 集群主节点服务
- **Node**: 数据存储节点
- **HTTP Proxy**: HTTP 网关服务
- **Kafka Proxy**: Kafka 协议代理

## 最佳实践

### 队列设计
- 合理设置队列参数
- 选择合适的队列类型
- 规划分片策略
- 配置适当的保留期

### 消费者设计
- 实现幂等处理
- 合理设置批处理大小
- 实现优雅关闭
- 处理异常和重试

### 性能调优
- 监控关键指标
- 优化配置参数
- 扩展分片数量
- 优化网络配置

## 版本历史

- 初始版本支持基本队列功能
- 增加多队列类型支持
- 增强消费者管理功能
- 增加配置文件支持
- 性能优化和稳定性改进