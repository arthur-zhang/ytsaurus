# Incumbent Server 组件

## 概述

Incumbent Server 是 YTsaurus 系统中负责管理"占位符"（Incumbent）服务的组件。Incumbent 是一种特殊的单例服务，确保在集群中同一时间只有一个实例在运行。这种模式用于管理需要单点运行的服务，如调度器、时间戳提供者等。Incumbent Server 提供了选举机制、心跳监控、故障转移等功能，确保服务的单点性和高可用性。

## 核心功能

### 1. 单例服务管理
- **唯一性保证**: 确保每个 Incumbent 在集群中只有一个实例
- **选举机制**: 通过 Raft 或其他共识算法选举领导者
- **租约管理**: 使用租约机制维护领导者地位
- **故障检测**: 快速检测领导者故障

### 2. 心跳监控
- **心跳机制**: 定期发送心跳维持租约
- **超时检测**: 超时未收到心跳则触发重新选举
- **健康检查**: 监控 Incumbent 的健康状态
- **自动恢复**: 故障后自动启动新的实例

### 3. 动态配置
- **服务注册**: 动态注册新的 Incumbent 服务
- **配置更新**: 支持在线更新服务配置
- **分片支持**: 支持服务的多分片部署
- **负载分布**: 合理分布不同类型的 Incumbent

### 4. 监控和审计
- **状态监控**: 实时监控所有 Incumbent 状态
- **事件日志**: 记录所有选举和故障事件
- **性能指标**: 收集服务性能指标
- **告警通知**: 异常情况自动告警

## 关键组件

### Incumbent Manager (incumbent_manager.h/cpp)
- Incumbent Server 的核心管理器（22KB）
- 管理所有 Incumbent 的生命周期
- 处理选举和故障转移逻辑
- 维护 Incumbent 的注册信息

### Scheduler (scheduler.h/cpp)
- Incumbent 调度器实现
- 负责 Incumbent 的调度和分配
- 处理不同类型 Incumbent 的优先级
- 优化资源利用和性能

### Incumbent (incumbent.h/cpp)
- Incumbent 对象的基础定义
- 定义 Incumbent 的通用属性
- 实现心跳和租约机制
- 提供状态查询接口

### Incumbent Service (incumbent_service.h/cpp)
- Incumbent RPC 服务实现
- 提供远程访问接口
- 处理客户端请求
- 实现访问控制和安全检查

## 文件说明

### 核心管理文件
- `incumbent_manager.cpp/h`: Incumbent 管理器主实现
- `scheduler.cpp/h`: 调度器实现
- `incumbent.h/cpp`: Incumbent 基础定义
- `incumbent_detail.h/cpp`: Incumbent 详细实现

### 服务接口文件
- `incumbent_service.cpp/h`: RPC 服务实现

### 配置和定义文件
- `config.cpp/h`: 配置管理
- `public.h`: 公共接口定义
- `private.h`: 私有定义

## 使用方法

### 注册 Incumbent
```cpp
// 创建 Incumbent 描述符
auto descriptor = TIncumbentDescriptor{
    .Type = EIncumbentType::Scheduler,
    .ShardIndex = 0,
    .Priority = 100,
    .LeaseTimeout = TDuration::Seconds(30)
};

// 注册 Incumbent
incumbentManager->RegisterIncumbent(
    New<TIncumbent>(descriptor)
);
```

### 启动 Incumbent
```cpp
// 检查是否为领导者
if (incumbentManager->HasIncumbency(
        EIncumbentType::Scheduler,
        0)) {
    // 作为领导者启动服务
    startScheduler();
}

// 发送心跳
incumbentManager->OnHeartbeat(
    TInstant::Now() + leaseTimeout,
        incumbentMap
);
```

### 监控状态
```cpp
// 获取 Incumbent 数量
auto count = incumbentManager->GetIncumbentCount(
    EIncumbentType::Scheduler
);

// 获取 Incumbent 地址
auto address = incumbentManager->GetIncumbentAddress(
    EIncumbentType::Scheduler,
    0
);

// 检查状态
bool isActive = incumbentManager->HasIncumbency(
    EIncumbentType::Scheduler,
    0
);
```

## 配置参数

### Incumbent Manager 配置
```yaml
incumbent_manager:
  enable: true
  election_timeout: 30s
  heartbeat_interval: 10s
  lease_timeout: 60s

  scheduler:
    enable_priority: true
    balance_shards: true
    max_incumbents_per_node: 5

  monitoring:
    health_check_interval: 30s
    failure_detection_timeout: 90s
    auto_recovery_enabled: true
```

### Incumbent 类型配置
```yaml
incumbent_types:
  scheduler:
    count: 1
    priority: 100
    lease_timeout: 60s
    allowed_nodes: ["master1", "master2", "master3"]

  timestamp_provider:
    count: 1
    priority: 90
    lease_timeout: 30s

  queue_agent:
    count: 3
    priority: 80
    lease_timeout: 45s
```

## 实现原理

### 选举机制
1. **Raft 共识**: 基于 Raft 算法实现选举
2. **租约机制**: 使用租约维持领导者地位
3. **心跳维护**: 定期发送心跳维持租约
4. **故障检测**: 超时触发重新选举

### 调度算法
1. **优先级调度**: 基于优先级分配 Incumbent
2. **负载均衡**: 考虑节点负载分布
3. **亲和性约束**: 满足特定的亲和性要求
4. **故障域隔离**: 避免单点故障

### 故障处理
1. **快速检测**: 基于心跳的快速故障检测
2. **自动转移**: 自动转移到新的领导者
3. **状态恢复**: 恢复服务状态和数据
4. **通知机制**: 通知相关组件状态变化

## 性能优化

### 心跳优化
- **批量心跳**: 批量发送多个心跳
- **压缩传输**: 压缩心跳数据
- **网络优化**: 优化网络传输路径
- **超时调整**: 动态调整心跳超时

### 调度优化
- **缓存**: 缓存调度决策结果
- **预计算**: 预计算调度方案
- **并行处理**: 并行处理多个调度任务
- **增量更新**: 增量更新调度状态

### 存储优化
- **内存存储**: 活跃数据内存存储
- **压缩存储**: 历史数据压缩存储
- **批量写入**: 批量写入减少 I/O
- **异步持久化**: 异步持久化提高性能

## 监控和调试

### 关键指标
- Incumbent 总数和分布
- 选举频率和成功率
- 心跳延迟和丢失率
- 故障转移时间

### 调试命令
```bash
# 查看所有 Incumbent
yt get //sys/incumbents

# 查看 Incumbent 状态
yt get //sys/incumbents/<type>/@status

# 查看选举历史
yt get //sys/incumbent_elections

# 查看 Orchid 监控
yt get //sys/incumbent_manager/orchid
```

### 性能分析
```bash
# 查看心跳统计
yt get //sys/incumbent_manager/@heartbeat_stats

# 查看调度统计
yt get //sys/incumbent_manager/@scheduling_stats

# 查看选举延迟
yt get //sys/incumbent_manager/@election_latency
```

## 故障处理

### 常见问题
1. **选举频繁**: 检查网络延迟和负载
2. **心跳丢失**: 检查网络连接和超时
3. **调度失败**: 检查资源和约束
4. **状态不一致**: 触发重新同步

### 恢复机制
- **自动恢复**: 大部分问题自动恢复
- **手动干预**: 复杂情况手动处理
- **状态重置**: 重置 Incumbent 状态
- **重新选举**: 强制重新选举

## 安全考虑

### 访问控制
- **权限验证**: 严格的权限验证
- **身份认证**: 基于证书的认证
- **授权管理**: 细粒度的授权控制
- **审计日志**: 完整的操作审计

### 通信安全
- **TLS 加密**: 所有通信 TLS 加密
- **消息签名**: 关键消息数字签名
- **防重放**: 防止重放攻击
- **完整性保护**: 保护消息完整性

## 扩展性设计

### 水平扩展
- **多分片支持**: 支持服务的多分片部署
- **分布式选举**: 跨节点的分布式选举
- **负载均衡**: 智能负载分配
- **一致性保证**: 保证分布式一致性

### 垂直扩展
- **批量操作**: 支持批量注册和操作
- **异步处理**: 异步处理非关键操作
- **并发优化**: 提高并发处理能力
- **资源优化**: 优化资源使用

## 最佳实践

### 部署建议
- **高可用**: 至少 3 个节点部署
- **网络优化**: 低延迟网络连接
- **监控告警**: 完善的监控告警
- **备份策略**: 配置备份和恢复

### 运维建议
- **定期检查**: 定期检查服务状态
- **容量规划**: 合理规划资源容量
- **性能调优**: 根据负载调优参数
- **安全更新**: 定期更新安全补丁

## 相关文档
- [Incumbent 设计文档](../../../docs/incumbent-design.md)
- [分布式选举指南](../../../docs/distributed-election.md)
- [高可用部署指南](../../../docs/high-availability.md)