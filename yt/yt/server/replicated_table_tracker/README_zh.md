# 复制表跟踪服务 (Replicated Table Tracker)

## 概述

Replicated Table Tracker 是 YTsaurus 分布式存储系统中负责跟踪和管理复制表状态的服务。它监控复制表的复制进度、健康状况和一致性，为分布式存储系统提供可靠的数据复制保障，确保多个副本之间的数据同步和一致性。

## 功能特性

### 核心功能
- **复制状态监控**: 实时监控复制表的复制状态和进度
- **健康检查**: 持续检查复制表的健康状况和可用性
- **一致性验证**: 验证副本间的数据一致性
- **故障检测**: 检测复制过程中的故障和异常
- **自动恢复**: 支持自动故障检测和恢复机制

### 高级特性
- **多集群支持**: 支持跨集群的表复制
- **性能监控**: 提供复制性能统计和分析
- **告警机制**: 复制异常时的告警和通知
- **配置管理**: 动态配置复制参数和策略
- **历史追踪**: 维护复制历史和变更记录

## 架构设计

### 组件架构
```
Replicated Table Tracker
├── Tracker Core (跟踪核心)
│   ├── Table Registry (表注册表)
│   ├── Replication Monitor (复制监控器)
│   └── Health Checker (健康检查器)
├── State Management (状态管理)
│   ├── State Tracker (状态跟踪器)
│   ├── Consistency Validator (一致性验证器)
│   └── History Manager (历史管理器)
├── Communication Layer (通信层)
│   ├── Master Connector (主节点连接器)
│   ├── Cluster Bridge (集群桥接器)
│   └── Event Dispatcher (事件分发器)
├── Alert System (告警系统)
│   ├── Alert Manager (告警管理器)
│   ├── Notification Service (通知服务)
│   └── Escalation Handler (升级处理器)
└── Monitoring System (监控系统)
    ├── Performance Metrics (性能指标)
    ├── Replication Statistics (复制统计)
    └── Health Metrics (健康指标)
```

### 关键组件说明

#### 1. Replication Monitor (复制监控器)
- 监控复制表的复制状态
- 跟踪复制进度和延迟
- 检测复制异常和中断
- 计算复制性能指标

#### 2. Health Checker (健康检查器)
- 定期检查副本健康状况
- 验证副本的可用性
- 检测数据一致性问题
- 评估复制质量

#### 3. State Tracker (状态跟踪器)
- 维护复制表的状态信息
- 跟踪状态变化和转换
- 管理状态的持久化存储
- 提供状态查询接口

#### 4. Consistency Validator (一致性验证器)
- 验证副本间的数据一致性
- 检测数据丢失和损坏
- 执行数据校验和比对
- 生成一致性报告

## 支持的复制类型

### 1. 异步复制
```yaml
replication_type: "async"
properties:
  replication_lag_threshold: "5min"
  max_replication_delay: "30min"
  consistency_check_interval: "1h"
```

### 2. 同步复制
```yaml
replication_type: "sync"
properties:
  commit_timeout: "30s"
  ack_timeout: "10s"
  min_replicas: 2
```

### 3. 半同步复制
```yaml
replication_type: "semi_sync"
properties:
  ack_timeout: "5s"
  async_fallback: true
  min_sync_replicas: 1
```

## 配置说明

### 基本配置结构
```yaml
replicated_table_tracker:
  # 服务配置
  service:
    listen_port: 8082
    check_interval: 30s
    health_check_interval: 60s

  # 主节点连接配置
  master_connection:
    addresses: ["master1:9000", "master2:9000"]
    connection_timeout: 10s
    request_timeout: 30s
    retry_count: 3

  # 复制监控配置
  replication_monitor:
    enabled: true
    check_interval: 30s
    lag_threshold: "5min"
    error_threshold: 10

  # 健康检查配置
  health_checker:
    enabled: true
    check_interval: 60s
    timeout: 30s
    retry_count: 3
    consistency_check: true
```

### 告警配置
```yaml
replicated_table_tracker:
  alerts:
    enabled: true

    # 告警规则
    rules:
      - name: "replication_lag"
        condition: "replication_lag > 10m"
        severity: "warning"
        cooldown: "5m"

      - name: "replication_failure"
        condition: "replication_status != 'healthy'"
        severity: "critical"
        cooldown: "1m"

      - name: "consistency_mismatch"
        condition: "consistency_check != 'passed'"
        severity: "error"
        cooldown: "10m"

    # 通知配置
    notifications:
      - type: "email"
        recipients: ["admin@example.com"]
        template: "replication_alert"

      - type: "slack"
        webhook_url: "https://hooks.slack.com/..."
        channel: "#alerts"
```

### 性能配置
```yaml
replicated_table_tracker:
  performance:
    monitoring_interval: 15s
    statistics_retention: "7d"
    batch_size: 100
    concurrent_checks: 5

    # 资源限制
    resource_limits:
      max_memory_usage: "2GB"
      max_cpu_usage: 0.5
      max_concurrent_operations: 50
```

## 使用方法

### 启动服务
```bash
# 从构建目录启动
./yt/yt/server/all/ytserver-all --config replicated_table_tracker.config.yson

# 或使用特定配置
./ytserver-replicated-table-tracker --config config.yson
```

### 监控操作
```bash
# 获取所有复制表状态
curl http://replicated-table-tracker:8082/api/v1/tables

# 获取特定表状态
curl http://replicated-table-tracker:8082/api/v1/tables/table_name

# 获取复制统计
curl http://replicated-table-tracker:8082/api/v1/statistics

# 获取健康检查结果
curl http://replicated-table-tracker:8082/api/v1/health
```

### 配置管理
```bash
# 重新加载配置
curl -X POST http://replicated-table-tracker:8082/api/v1/reload_config

# 更新监控参数
curl -X PUT http://replicated-table-tracker:8082/api/v1/config \
  -H "Content-Type: application/json" \
  -d '{"check_interval": "60s"}'

# 启用/禁用表监控
curl -X POST http://replicated-table-tracker:8082/api/v1/tables/table_name/monitoring \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'
```

### 手动操作
```bash
# 手动触发一致性检查
curl -X POST http://replicated-table-tracker:8082/api/v1/tables/table_name/consistency_check

# 强制复制
curl -X POST http://replicated-table-tracker:8082/api/v1/tables/table_name/force_replication

# 获取复制历史
curl http://replicated-table-tracker:8082/api/v1/tables/table_name/history
```

## 实现原理

### 状态监控机制
1. **定期检查**: 定期查询复制表状态
2. **状态分析**: 分析复制进度和健康状况
3. **状态更新**: 更新内部状态信息
4. **事件生成**: 生成状态变化事件
5. **告警触发**: 根据状态触发告警

### 健康检查机制
1. **连通性检查**: 检查副本的连通性
2. **数据验证**: 验证数据的完整性
3. **性能评估**: 评估复制性能
4. **一致性检查**: 检查数据一致性
5. **健康评分**: 计算健康评分

### 故障检测机制
1. **异常检测**: 检测复制异常和错误
2. **性能下降**: 检测性能下降和延迟
3. **数据丢失**: 检测数据丢失和损坏
4. **连接中断**: 检测网络连接中断
5. **故障分类**: 对故障进行分类和评级

### 恢复机制
1. **自动恢复**: 自动尝试修复常见故障
2. **手动干预**: 提供手动修复接口
3. **故障隔离**: 隔离故障副本防止扩散
4. **故障记录**: 记录故障信息和处理过程

## 性能优化

### 检查优化
- 并行健康检查
- 智能检查间隔调整
- 批量状态查询
- 缓存查询结果

### 资源优化
- 连接池管理
- 内存使用优化
- CPU 使用控制
- 网络带宽管理

### 存储优化
- 状态信息压缩
- 历史数据归档
- 索引优化
- 分区存储

## 监控和调试

### 关键指标
- 复制延迟和吞吐量
- 错误率和故障次数
- 健康检查通过率
- 一致性检查结果
- 资源使用情况

### 监控端点
```bash
# 服务健康状态
GET /health

# 表状态概览
GET /api/v1/tables

# 详细统计信息
GET /api/v1/statistics

# 告警状态
GET /api/v1/alerts

# 性能指标
GET /api/v1/metrics
```

### 调试工具
```bash
# 启用详细日志
export REPLICATED_TABLE_TRACKER_LOG_LEVEL=debug

# 查看特定表状态
curl http://localhost:8082/api/v1/tables/table_name?verbose=true

# 获取调试信息
curl http://localhost:8082/api/v1/debug/status

# 手动触发检查
curl -X POST http://localhost:8082/api/v1/debug/force_check
```

## 故障排除

### 常见问题
1. **连接失败**: 检查网络配置和防火墙
2. **权限错误**: 验证访问权限和认证信息
3. **性能问题**: 检查资源配置和负载状况
4. **状态不一致**: 检查配置和数据一致性

### 调试步骤
1. 检查服务启动日志
2. 验证主节点连接
3. 检查表权限配置
4. 分析性能指标
5. 检查告警配置

### 恢复策略
- 自动重试机制
- 服务重启和重连
- 配置回滚
- 手动数据修复

## 相关组件

- **Master**: 集群主节点，管理表元数据
- **Node**: 数据节点，存储实际数据副本
- **Tablet Balancer**: 表平衡器，优化表分布
- **Chaos Monkey**: 混沌测试，验证系统健壮性

## 最佳实践

### 部署建议
- 高可用部署配置
- 资源隔离和限制
- 监控告警配置
- 备份和恢复策略

### 运维管理
- 定期状态检查
- 性能监控和调优
- 故障预案和演练
- 文档和知识库维护

### 配置优化
- 根据集群规模调整参数
- 优化检查间隔和阈值
- 配置适当的告警规则
- 设置合理的资源限制

## 版本历史

- 初始版本支持基本复制监控
- 增加健康检查和告警功能
- 增强一致性和性能监控
- 增加多集群支持
- 性能优化和稳定性改进