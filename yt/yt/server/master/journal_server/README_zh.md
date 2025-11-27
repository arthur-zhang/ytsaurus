# Journal Server 组件

## 概述

Journal Server 是 YTsaurus 系统中负责管理日志对象（Journal）的组件。Journal 是一种特殊的对象，用于存储顺序追加的日志数据，支持高效的追加写入和范围读取。Journal Server 基于 Chunk Server 实现，将日志数据存储在 Chunk 中，提供了分布式、持久化、高可用的日志存储服务。

## 核心功能

### 1. 日志存储
- **追加写入**: 支持高效的顺序追加写入
- **分布式存储**: 日志数据分布存储在多个节点
- **持久化保证**: 通过多副本保证数据持久化
- **批量写入**: 支持批量写入提高性能

### 2. 日志管理
- **创建和删除**: 管理 Journal 的生命周期
- **统计信息**: 维护 Journal 的统计信息
- **封存操作**: 支持日志封存只读
- **截断操作**: 支持从尾部截断日志

### 3. 数据访问
- **顺序读取**: 高效的顺序数据读取
- **范围查询**: 支持按行号范围读取
- **随机访问**: 支持随机位置访问
- **流式处理**: 支持流式处理大日志

### 4. 性能优化
- **压缩支持**: 支持数据压缩减少存储
- **缓存机制**: 智能缓存热点数据
- **预取策略**: 预取后续数据
- **批量操作**: 批量读写优化

## 关键组件

### Journal Manager (journal_manager.h/cpp)
- Journal Server 的核心管理器（8KB）
- 管理 Journal 的所有操作
- 处理日志的创建、封存、截断等
- 维护日志的统计信息

### Journal Node (journal_node.h/cpp)
- Journal 节点的实现
- 继承自 ChunkOwnerBase 管理数据
- 维护日志的元数据信息
- 实现日志的基本操作

### Journal Node Proxy (journal_node_proxy.h/cpp)
- Journal 节点的代理实现（11KB）
- 提供 RPC 接口供客户端访问
- 处理日志操作请求
- 实现访问控制和安全检查

### Journal Node Type Handler (journal_node_type_handler.h/cpp)
- Journal 节点的类型处理器（10KB）
- 管理 Journal Node 的生命周期
- 处理节点的创建、删除和修改
- 提供类型特定的操作接口

## 文件说明

### 核心实现文件
- `journal_manager.cpp/h`: Journal 管理器主实现
- `journal_node.cpp/h`: Journal 节点核心实现
- `journal_node_proxy.cpp/h`: Journal 节点代理
- `journal_node_type_handler.cpp/h`: Journal 节点类型处理器

### 配置和定义文件
- `config.h`: 配置管理
- `public.h/cpp`: 公共接口定义
- `private.h`: 私有定义和常量

## 使用方法

### 创建 Journal
```cpp
// 创建 Journal 节点
auto journalNode = journalManager->CreateJournal(
    parentPath,
    journalName,
    transaction
);

// 设置 Journal 属性
journalNode->SetRowCount(0);
journalNode->SetSealed(false);

// 提交创建
transactionManager->CommitTransaction(transaction);
```

### 追加数据
```cpp
// 获取 Journal
auto journalNode = cypressManager->ResolvePath(
    "/path/to/journal"
);

// 追加数据（通常通过客户端 API）
auto chunkId = journalNode->GetChunkId(chunkIndex);
chunkWriter->WriteData(data);
```

### 读取日志
```cpp
// 获取 Journal Chunk 列表
auto chunks = journalNode->GetChunks();

// 按范围读取
i64 startRow = 100;
i64 endRow = 200;

for (const auto& chunk : chunks) {
    auto data = chunkReader->ReadRange(startRow, endRow);
    // 处理数据
}
```

### 封存和截断
```cpp
// 封存 Journal
journalManager->SealJournal(journalNode);

// 截断日志（保留前 N 行）
i64 rowCount = 1000;
journalManager->TruncateJournal(
    journalNode,
    rowCount
);
```

## 配置参数

### Journal Server 配置
```yaml
journal_server:
  enable_compression: true
  default_compression_codec: "lz4"
  chunk_size: 64MB
  max_row_count_per_chunk: 1000000

write:
  batch_size: 1000
  flush_interval: 1s
  sync_enabled: true

read:
  enable_prefetch: true
  prefetch_window: 2
  cache_size: 100MB
```

### 性能优化配置
```yaml
performance:
  enable_caching: true
  cache_size: 1GB
  batch_read_size: 1000
  async_operations: true

compression:
  enabled_codecs:
    - "none"
    - "lz4"
    - "zstd"
  default_level: 3
  compress_on_write: true
```

## 实现原理

### 数据组织
1. **Chunk 切分**: 按行数或大小切分 Chunk
2. **顺序存储**: 数据按写入顺序存储
3. **元数据索引**: 维护行号到 Chunk 的映射
4. **统计信息**: 实时更新统计信息

### 写入流程
1. **数据缓冲**: 缓冲写入数据
2. **批量提交**: 批量提交到 Chunk
3. **元数据更新**: 更新元数据信息
4. **持久化**: 持久化到多个副本

### 读取流程
1. **元数据查询**: 查询目标 Chunk
2. **并行读取**: 并行读取多个 Chunk
3. **数据组装**: 按顺序组装数据
4. **流式返回**: 流式返回给客户端

### 封存机制
1. **停止写入**: 停止接受新的写入
2. **数据验证**: 验证已写入数据
3. **统计更新**: 更新最终统计信息
4. **状态变更**: 变更为只读状态

## 性能优化

### 写入优化
- **批量写入**: 批量提交提高效率
- **压缩**: 实时压缩减少存储
- **并行处理**: 并行处理多个写入
- **缓冲策略**: 智能缓冲策略

### 读取优化
- **预取**: 预取后续数据
- **缓存**: 缓存热点数据
- **并行读取**: 并行读取多个 Chunk
- **压缩传输**: 网络传输压缩

### 存储优化
- **压缩**: 数据压缩减少空间
- **去重**: 重复数据去重
- **分层存储**: 热温冷数据分层
- **垃圾回收**: 及时清理无用数据

## 监控和调试

### 关键指标
- Journal 总数和大小
- 写入 QPS 和延迟
- 读取 QPS 和延迟
- 压缩率和存储效率

### 调试命令
```bash
# 查看 Journal 信息
yt get //path/to/journal

# 查看 Journal 统计
yt get //path/to/journal/@row_count
yt get //path/to/journal/@compressed_data_size

# 查看 Chunk 信息
yt get //path/to/journal/@chunk_ids

# 读取日志
yt read-journal //path/to/journal --from-row 100 --to-row 200
```

### 性能分析
```bash
# 查看写入统计
yt get //sys/journal_server/@write_stats

# 查看读取统计
yt get //sys/journal_server/@read_stats

# 查看压缩统计
yt get //sys/journal_server/@compression_stats
```

## 故障处理

### 常见问题
1. **写入失败**: 检查存储空间和权限
2. **读取慢**: 检查网络和缓存
3. **数据损坏**: 运行完整性检查
4. **封存失败**: 检查数据完整性

### 恢复机制
- **自动重试**: 临时故障自动重试
- **数据修复**: 自动修复损坏数据
- **备份恢复**: 从备份恢复数据
- **重建索引**: 重建损坏的索引

## 安全考虑

### 数据安全
- **访问控制**: 基于权限的访问控制
- **传输加密**: HTTPS/TLS 传输加密
- **存储加密**: 可选的存储加密
- **完整性保护**: 校验和保护数据完整性

### 运行时安全
- **输入验证**: 严格的输入验证
- **资源限制**: 防止资源耗尽
- **审计日志**: 记录所有操作
- **权限最小化**: 最小权限原则

## 最佳实践

### 使用建议
- **合理大小**: 控制 Journal 大小
- **定期封存**: 定期封存旧日志
- **压缩策略**: 对文本数据启用压缩
- **监控告警**: 设置合理的监控告警

### 性能建议
- **批量操作**: 使用批量写入
- **异步处理**: 异步处理非关键操作
- **缓存策略**: 合理设置缓存
- **分区策略**: 大日志按时间分区

## 应用场景

### 日志收集
- **应用日志**: 存储应用运行日志
- **审计日志**: 存储操作审计日志
- **事件流**: 存储事件流数据
- **监控数据**: 存储监控时序数据

### 消息队列
- **发布订阅**: 作为消息队列后端
- **事件溯源**: 存储领域事件
- **变更日志**: 存储数据变更日志
- **流处理**: 流处理中间结果

## 相关文档
- [Journal 设计文档](../../../docs/journal-design.md)
- [日志存储指南](../../../docs/log-storage.md)
- [流处理文档](../../../docs/stream-processing.md)