# Chaos Server 组件

## 概述

Chaos Server 是 YTsaurus 系统中负责管理混沌复制（Chaos Replication）的核心组件。它提供了跨数据中心、跨集群的异步数据复制能力，支持多主复制、双向复制、环形复制等复杂的复制拓扑。Chaos Replication 允许在不同 YTsaurus 集群之间建立复制关系，实现数据的地理分布和灾难恢复。

## 核心功能

### 1. 跨集群复制
- **异步复制**: 支持异步数据复制，不影响本地写入性能
- **多拓扑支持**: 支持星形、环形、网状等多种复制拓扑
- **冲突解决**: 提供多种冲突解决策略
- **复制延迟监控**: 实时监控复制延迟和进度

### 2. 复制卡管理
- **Replication Card**: 核心的复制元数据结构
- **动态配置**: 支持在线修改复制配置
- **版本控制**: 维护复制配置的版本历史
- **生命周期管理**: 完整的复制卡生命周期管理

### 3. 异构集群支持
- **Alien Cell**: 管理外部集群的 Cell 对象
- **集群注册**: 维护外部集群的注册信息
- **认证授权**: 跨集群的安全认证
- **协议兼容**: 支持不同版本的集群互操作

### 4. 混沌复制表
- **复制表节点**: 特殊的 Cypress 节点类型
- **Schema 管理**: 维护复制表的 Schema
- **队列模式**: 支持队列生产者/消费者模式
- **路由配置**: 配置数据路由策略

## 关键组件

### Chaos Manager (chaos_manager.h/cpp)
- Chaos Server 的核心管理器
- 负责所有复制操作的协调
- 管理复制卡的创建、更新和删除
- 处理跨集群的通信和同步

### Alien Cell (alien_cell.h/cpp)
- 代表外部集群的 Cell 对象
- 管理与外部集群的连接
- 缓存外部集群的元数据
- 处理外部集群的状态变化

### Alien Cell Synchronizer (alien_cell_synchronizer.h/cpp)
- 同步 Alien Cell 的状态
- 定期从外部集群拉取更新
- 处理连接断开和重连
- 优化同步频率和批量大小

### Chaos Replicated Table (chaos_replicated_table_node.h/cpp)
- 混沌复制表的 Cypress 节点实现
- 管理表的复制配置
- 提供 CRUD 操作接口
- 支持事务性操作

### Chaos Cell Bundle (chaos_cell_bundle.h/cpp)
- Chaos Cell 的集合管理
- 提供 Cell 的资源隔离
- 支持动态扩缩容
- 管理负载均衡策略

## 文件说明

### 核心管理文件
- `chaos_manager.cpp/h`: Chaos Manager 主实现
- `alien_cell.cpp/h`: 外部 Cell 管理
- `alien_cell_synchronizer.cpp/h`: 外部 Cell 同步器
- `alien_cluster_registry.cpp/h`: 外部集群注册表

### Cell 管理文件
- `chaos_cell.cpp/h`: Chaos Cell 实现
- `chaos_cell_bundle.cpp/h`: Cell Bundle 管理
- `chaos_cell_proxy.cpp/h`: Cell 代理接口
- `chaos_service.cpp/h`: Chaos RPC 服务

### 表管理文件
- `chaos_replicated_table_node.cpp/h`: 复制表节点
- `chaos_replicated_table_node_proxy.cpp/h`: 表节点代理
- `chaos_replicated_table_node_type_handler.cpp/h`: 表类型处理器

### 类型处理文件
- `chaos_cell_bundle_type_handler.cpp/h`: Bundle 类型处理器
- `chaos_cell_type_handler.cpp/h`: Cell 类型处理器

### 配置和工具文件
- `config.cpp/h`: Chaos Server 配置
- `helpers.cpp/h`: 辅助函数
- `public.h`: 公共接口定义
- `private.h`: 私有定义

## 使用方法

### 创建复制卡
```cpp
// 创建新的复制卡
auto replicationCard = chaosManager->CreateReplicationCard(
    tableId,
    options
);

// 添加复制项
replicationCard->AddReplica(
    clusterName,
    tableName,
    mode,
    options
);
```

### 创建混沌复制表
```cpp
// 在 Cypress 中创建复制表
auto tableNode = CreateChaosReplicatedTable(
    "/path/to/table",
    chaosCellBundleId,
    schema
);

// 配置复制规则
auto replicationCardId = tableNode->GetReplicationCardId();
chaosManager->ConfigureReplication(replicationCardId, config);
```

### 管理外部集群
```cpp
// 注册外部集群
auto alienCluster = chaosManager->RegisterAlienCluster(
    clusterName,
    connectionConfig
);

// 创建 Alien Cell
auto alienCell = chaosManager->CreateAlienCell(
    alienCluster,
    cellId
);
```

### 监控复制状态
```cpp
// 获取复制状态
auto status = chaosManager->GetReplicationStatus(replicationCardId);

// 检查复制延迟
for (const auto& replica : status.GetReplicas()) {
    std::cout << "Replica: " << replica.GetClusterName()
              << ", Lag: " << replica.GetReplicationLag() << std::endl;
}
```

## 配置参数

### Chaos Server 配置
```yaml
chaos_manager:
  enable: true
  sync_period: 30s
  max_concurrent_syncs: 10
  sync_timeout: 60s

replication:
  default_mode: async
  conflict_resolution: last_writer_wins
  max_replication_lag: 1h
```

### Alien Cluster 配置
```yaml
alien_clusters:
  cluster_a:
    connection:
      addresses:
        - host: master1.cluster-a.com
          port: 9000
      authentication:
        token: "secure_token"
    sync_options:
      period: 60s
      batch_size: 1000
```

### 复制表配置
```yaml
chaos_replicated_table:
  replication_card:
    replicas:
      - cluster_name: primary
        table_path: "/path/to/table"
        mode: sync
      - cluster_name: secondary
        table_path: "/path/to/replica"
        mode: async
        lag_threshold: 10min
  options:
    enable_data_validation: true
    compression_codec: lz4
```

## 实现原理

### 复制协议
Chaos Server 使用基于日志的异步复制协议：

1. **变更捕获**: 从源表捕获数据变更
2. **事件序列化**: 将变更序列化为复制事件
3. **可靠传输**: 通过 RPC 可靠传输到目标集群
4. **冲突检测**: 检测并发修改冲突
5. **应用变更**: 在目标集群应用变更

### 冲突解决策略
- **Last Writer Wins**: 基于时间戳的最后写入者获胜
- **First Writer Wins**: 第一个写入者获胜
- **Custom Resolver**: 自定义冲突解决逻辑
- **Manual Resolution**: 人工介入解决

### 一致性保证
- **最终一致性**: 保证最终数据一致
- **因果一致性**: 保证操作因果序
- **单调读**: 保证读操作单调性
- **单调写**: 保证写操作单调性

## 性能优化

### 批量处理
- **批量变更**: 合并多个变更事件
- **批量传输**: 网络传输批量优化
- **批量应用**: 批量应用远程变更

### 缓存策略
- **元数据缓存**: 缓存外部集群元数据
- **连接池**: 复用网络连接
- **预取**: 主动预取常用数据

### 并行处理
- **并行复制**: 多个复制任务并行
- **流水线处理**: 流水线式数据处理
- **异步 I/O**: 非阻塞 I/O 操作

## 监控和调试

### 关键指标
- 复制延迟和吞吐量
- 冲突数量和类型
- 外部集群连接状态
- 复制卡数量和分布

### 调试命令
```bash
# 查看所有复制卡
yt get //sys/chaos_replication_cards

# 查看特定复制状态
yt get //sys/chaos_replication_cards/<card-id>/@status

# 查看外部集群
yt get //sys/alien_clusters

# 强制触发同步
yt set //sys/alien_clusters/<cluster>/@force_sync true
```

## 故障处理

### 常见问题
1. **连接超时**: 检查网络连通性
2. **认证失败**: 验证凭证配置
3. **Schema 不匹配**: 确保表结构兼容
4. **复制延迟**: 调整批处理参数

### 恢复机制
- **自动重试**: 临时故障自动重试
- **断点续传**: 从断点继续复制
- **数据校验**: 复制完成后校验数据

## 安全考虑

### 认证和授权
- **Token 认证**: 使用安全 Token 认证
- **TLS 加密**: 网络传输 TLS 加密
- **权限控制**: 细粒度的权限控制
- **审计日志**: 记录所有操作日志

### 数据安全
- **传输加密**: 端到端数据加密
- **存储加密**: 可选的存储加密
- **访问控制**: 基于角色的访问控制

## 相关文档
- [Chaos Replication 设计](../../../docs/chaos-replication.md)
- [跨集群复制指南](../../../docs/cross-cluster.md)
- [故障恢复文档](../../../docs/chaos-recovery.md)