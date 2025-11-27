# Chunk Server 组件

## 概述

Chunk Server 是 YTsaurus 系统中负责管理数据块（Chunk）的核心组件。Chunk 是系统中数据存储的基本单元，通常大小为 64MB-1GB。Chunk Server 负责 Chunk 的生命周期管理、副本分布、数据完整性校验、垃圾回收以及数据迁移等关键功能，确保数据的可靠性和可用性。

## 核心功能

### 1. Chunk 生命周期管理
- **创建和分配**: 管理新 Chunk 的创建和存储节点分配
- **副本管理**: 维护 Chunk 的多个副本，确保冗余度
- **数据恢复**: 自动检测和修复损坏的副本
- **垃圾回收**: 回收不再需要的 Chunk 空间

### 2. 数据完整性
- **校验和验证**: 为每个 Chunk 计算和验证校验和
- **纠删码支持**: 支持多种纠删码算法，提高存储效率
- **健康检查**: 定期检查 Chunk 的健康状态
- **数据修复**: 自动修复损坏或丢失的数据

### 3. 存储优化
- **数据压缩**: 支持多种压缩算法减少存储空间
- **数据合并**: 合并小 Chunk 减少元数据开销
- **智能放置**: 基于负载和地理位置的智能数据放置
- **分层存储**: 支持热、温、冷数据的分层存储

### 4. 分布式协调
- **节点跟踪**: 跟踪所有存储节点的状态
- **负载均衡**: 在节点间均衡分布数据
- **故障检测**: 快速检测和处理节点故障
- **数据迁移**: 根据策略迁移数据

## 关键组件

### Chunk Manager (chunk_manager.h/cpp)
- Chunk Server 的核心管理器，管理所有 Chunk 操作
- 处理 Chunk 的创建、删除、修复和迁移
- 维护 Chunk 的元数据和索引
- 提供 Chunk 查询和管理接口

### Chunk (chunk.h/cpp)
- Chunk 对象的核心实现
- 存储 Chunk 的元数据（大小、校验和、位置等）
- 管理 Chunk 的副本信息
- 支持 Chunk 的导入和导出

### Chunk Placement (chunk_placement.h/cpp)
- 实现 Chunk 的放置策略
- 根据负载、故障域等优化数据分布
- 支持自定义放置约束
- 处理数据的重新平衡

### Chunk Merger (chunk_merger.h/cpp)
- 管理 Chunk 的合并操作
- 优化小 Chunk 的存储效率
- 处理合并任务调度
- 维护合并历史记录

### Chunk Reincarnator (chunk_reincarnator.h/cpp)
- 管理 Chunk 的重生（版本更新）过程
- 处理 Chunk 格式升级
- 管理迁移过程中的一致性
- 支持无缝的数据迁移

## 文件说明

### 核心管理文件
- `chunk_manager.cpp/h`: Chunk 管理器主实现（256KB）
- `chunk.cpp/h`: Chunk 对象核心定义
- `chunk_placement.cpp/h/inl.h`: 数据放置策略实现
- `chunk_merger.cpp/h`: Chunk 合并器实现

### Chunk 生命周期文件
- `chunk_autotomizer.cpp/h`: Chunk 自动回收
- `chunk_reincarnator.cpp/h`: Chunk 重生管理器（87KB）
- `chunk_replacer.cpp/h`: Chunk 替换逻辑
- `chunk_replica_fetcher.cpp/h`: 副本获取器

### 树结构文件
- `chunk_tree.h`: Chunk 树基类
- `chunk_list.cpp/h`: Chunk 列表实现
- `chunk_view.cpp/h`: Chunk 视图实现
- `chunk_owner_base.cpp/h`: Chunk 所有者基类

### 存储相关文件
- `chunk_location.cpp/h/inl.h`: Chunk 存储位置
- `medium_base.cpp/h`: 存储介质基类
- `chunk_replica.cpp/h`: Chunk 副本管理
- `stored_chunk_replica.h`: 存储的副本定义

### 代理和类型处理文件
- `chunk_proxy.cpp/h`: Chunk 代理实现（60KB）
- `chunk_owner_node_proxy.cpp/h`: Chunk 所有者代理（84KB）
- `chunk_owner_type_handler.cpp/h`: 类型处理器（35KB）
- `chunk_list_type_handler.cpp/h`: 列表类型处理器

### 工具和辅助文件
- `job_base.h/cpp`: 作业基类
- `chunk_replication.h`: 复制配置
- `chunk_requisition.h`: Chunk 需求
- `helpers.cpp/h`: 辅助函数

## 使用方法

### 创建 Chunk
```cpp
// 创建新的 Chunk
auto chunk = chunkManager->CreateChunk(
    chunkType,
    erasureCodec,
    mediumId
);

// 分配存储位置
auto locations = chunkPlacement->AllocateLocations(
    chunk,
    replicaCount,
    placementHints
);

// 注册副本
for (const auto& location : locations) {
    chunkManager->RegisterReplica(
        chunk,
        location,
        nodeId
    );
}
```

### 管理 Chunk 副本
```cpp
// 获取 Chunk 副本
auto replicas = chunkManager->GetChunkReplicas(chunkId);

// 检查副本健康状态
for (const auto& replica : replicas) {
    auto health = chunkManager->CheckReplicaHealth(replica);
    if (health != EReplicaHealth::Healthy) {
        chunkManager->ScheduleReplicaRepair(replica);
    }
}

// 添加新副本
chunkManager->AddReplica(
    chunkId,
    targetNodeId,
    targetLocation
);
```

### 合并 Chunk
```cpp
// 创建合并任务
auto mergeTask = chunkMerger->CreateMergeTask(
    sourceChunks,
    targetMedium
);

// 设置合并选项
mergeTask->SetCompressionCodec("lz4");
mergeTask->SetErasureCodec("reed_solomon_6_3");

// 执行合并
auto mergedChunk = chunkMerger->ExecuteMerge(mergeTask);
```

### 数据修复
```cpp
// 检测损坏的 Chunk
auto damagedChunks = chunkManager->ScanForDamage();

// 启动修复任务
for (const auto& chunk : damagedChunks) {
    auto repairTask = chunkManager->CreateRepairTask(chunk);
    repairTask->SetPriority(EPriority::High);
    chunkManager->ScheduleRepair(repairTask);
}
```

## 配置参数

### Chunk Manager 配置
```yaml
chunk_manager:
  enable_chunk_merger: true
  enable_chunk_reincarnator: true
  repair_queue_size_limit: 10000

chunk_placement:
  default_replica_count: 3
  max_replicas_per_rack: 2
  max_replicas_per_data_center: 1
  enable_distributed_placement: true

chunk_merger:
  min_chunk_size: 16MB
  max_chunk_size: 1GB
  merge_threshold: 100
  max_concurrent_merges: 10
```

### 数据完整性配置
```yaml
integrity:
  enable_checksum_verification: true
  checksum_codec: crc32c
  corruption_scan_period: 24h
  auto_repair_enabled: true

erasure_codecs:
  reed_solomon_6_3:
    data_part_count: 6
    parity_part_count: 3
  jerasure_16_4:
    data_part_count: 16
    parity_part_count: 4
```

### 存储介质配置
```yaml
media:
  default:
    lifecycle: chunk
    access_time: hot

  ssd:
    lifecycle: chunk
    access_time: hot
    priority: 10

  hdd:
    lifecycle: chunk
    access_time: warm
    priority: 5

  archive:
    lifecycle: blob
    access_time: cold
    priority: 1
```

## 实现原理

### 放置算法
Chunk Placement 使用多层次的放置策略：

1. **故障域隔离**: 确保副本分布在不同故障域
2. **负载均衡**: 基于节点负载动态调整
3. **数据局部性**: 优化数据访问模式
4. **容量规划**: 预留空间应对未来增长

### 副本管理
- **主动复制**: 预防性创建额外副本
- **被动修复**: 检测到丢失后补充副本
- **优先级调度**: 根据数据重要性调度
- **带宽控制**: 限制修复带宽占用

### 垃圾回收
- **引用计数**: 跟踪 Chunk 的引用关系
- **延迟删除**: 避免误删除正在使用的 Chunk
- **批量回收**: 批量处理提高效率
- **空间回收**: 及时释放不再使用的空间

## 性能优化

### 缓存策略
- **元数据缓存**: 缓存热点 Chunk 元数据
- **位置缓存**: 缓存 Chunk 位置信息
- **预取**: 预取相关 Chunk 信息
- **LRU 淘汰**: 使用 LRU 管理缓存

### 批量操作
- **批量创建**: 批量创建 Chunk 减少开销
- **批量修复**: 合并修复任务
- **批量迁移**: 整理数据减少碎片
- **批量验证**: 批量校验提高效率

### 并发控制
- **读写分离**: 分离读写操作路径
- **细粒度锁**: 减少锁争用
- **无锁数据结构**: 优化热点路径
- **异步处理**: 异步处理非关键操作

## 监控和调试

### 关键指标
- Chunk 总数和大小分布
- 副本分布和健康状态
- 修复任务队列长度
- 存储空间利用率
- 数据读写 QPS

### 调试命令
```bash
# 查看所有 Chunk
yt get //sys/chunks

# 查看特定 Chunk
yt get //sys/chunks/<chunk-id>

# 查看 Chunk 位置
yt get //sys/chunks/<chunk-id>/@stored_replicas

# 查看修复队列
yt get //sys/chunk_repair_queues

# 触发 Chunk 修复
yt set //sys/chunks/<chunk-id>/@force_repair true
```

## 故障处理

### 常见问题
1. **副本丢失**: 检查节点状态和可用空间
2. **数据损坏**: 运行完整性检查
3. **放置失败**: 检查资源和约束
4. **修复慢**: 调整修复任务优先级

### 恢复策略
- **自动恢复**: 大部分问题自动处理
- **手动干预**: 复杂情况手动处理
- **数据重建**: 从备份重建数据
- **紧急修复**: 高优先级快速修复

## 扩展性设计

### 水平扩展
- **分片存储**: 按范围分片管理
- **分布式协调**: 多节点协调管理
- **负载迁移**: 平滑迁移负载
- **一致性保证**: 保证最终一致性

### 垂直扩展
- **内存优化**: 优化内存使用
- **CPU 优化**: 提高 CPU 利用率
- **I/O 优化**: 优化磁盘 I/O
- **网络优化**: 优化网络传输

## 安全考虑

### 数据安全
- **传输加密**: 数据传输加密
- **存储加密**: 可选的存储加密
- **访问控制**: 基于权限的访问
- **审计日志**: 记录所有操作

### 完整性保护
- **数字签名**: 重要数据签名
- **版本控制**: 维护数据版本
- **备份验证**: 定期验证备份
- **防篡改**: 防止恶意篡改

## 相关文档
- [Chunk 存储设计](../../../docs/chunk-storage.md)
- [纠删码指南](../../../docs/erasure-coding.md)
- [数据恢复文档](../../../docs/data-recovery.md)