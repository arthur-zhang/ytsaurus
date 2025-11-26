# YTsaurus Chunk 客户端

## 概述

`chunk_client` 目录提供了 YTsaurus Chunk 存储系统的客户端接口。Chunk 是 YTsaurus 中数据存储的基本单元，该模块负责处理 Chunk 的读取、写入、复制和管理等核心功能。

## 核心功能

### Chunk 管理
- **Chunk 元数据**: 管理 Chunk 的元数据信息和统计
- **Chunk 副本**: 处理 Chunk 的多副本管理和位置信息
- **Chunk 定位**: 高效定位和访问 Chunk 数据
- **Chunk 配置**: 管理 Chunk 相关的各种配置参数

### 数据读写
- **块读取**: 高效的 Chunk 块读取操作
- **块写入**: 支持并行的 Chunk 块写入
- **读取限制**: 灵活的读取范围和限制控制
- **数据验证**: 完整的数据校验和验证机制

### 配置和优化
- **获取配置**: Chunk 获取和定位的配置管理
- **获取器配置**: 数据获取器的详细配置选项
- **性能调优**: 针对不同场景的性能优化配置

## 主要文件说明

### 公共接口定义
- `public.h/.cpp`: 公共类型定义和错误码
  - Proto 消息类型前向声明
  - Chunk 客户端错误码定义（700-728）
  - 公共类型和常量定义

### Chunk 副本管理
- `chunk_replica.h/.cpp`: Chunk 副本管理核心
  - `TChunkReplica`: Chunk 副本信息结构
  - 副本状态管理和位置跟踪
  - 副本选择和负载均衡逻辑

### 配置管理
- `config.h/.cpp`: Chunk 客户端配置
  - `TFetchChunkSpecConfig`: Chunk 获取配置
  - `TFetcherConfig`: 数据获取器配置
  - 各种性能和超时参数配置

### 数据读取
- `read_limit.h/.cpp`: 读取限制控制
  - `TReadLimit`: 读取范围定义
  - 精确的读取控制机制
  - 支持多种读取模式

### 数据统计
- `data_statistics.h/.cpp`: 数据统计信息
  - `TDataStatistics`: 数据统计结构
  - 各种数据量和性能指标

### 基础读写接口
- `reader_base.h`: 读取器基础接口
- `writer_base.h`: 写入器基础接口
- `ready_event_reader_base.h/.cpp`: 异步读取器基础

### 辅助工具
- `helpers.h/.cpp`: 辅助函数和工具
- `private.h`: 私有定义和常量

## 错误码定义

### Chunk 客户端错误码（700-728）
- `700` - AllTargetNodesFailed: 所有目标节点失败
- `701` - SendBlocksFailed: 发送块失败
- `702` - NoSuchSession: 会话不存在
- `703` - SessionAlreadyExists: 会话已存在
- `704` - ChunkAlreadyExists: Chunk 已存在
- `705` - WindowError: 窗口错误
- `706` - BlockContentMismatch: 块内容不匹配
- `707` - NoSuchBlock: 块不存在
- `708` - NoSuchChunk: Chunk 不存在
- `710` - NoLocationAvailable: 无可用位置
- `711` - IOError: I/O 错误
- `712` - MasterCommunicationFailed: Master 通信失败
- `713` - NoSuchChunkTree: Chunk 树不存在
- `714` - MasterNotConnected: Master 未连接
- `716` - ChunkUnavailable: Chunk 不可用
- `717` - NoSuchChunkList: Chunk 列表不存在
- `718` - WriteThrottlingActive: 写入限流激活
- `719` - NoSuchMedium: 介质不存在
- `720` - OptimisticLockFailure: 乐观锁失败
- `721` - InvalidBlockChecksum: 块校验和无效
- `722` - MalformedReadRequest: 格式错误的读取请求
- `724` - MissingExtension: 缺少扩展
- `725` - ReaderThrottlingFailed: 读取器限流失败
- `726` - ReaderTimeout: 读取器超时
- `727` - NoSuchChunkView: Chunk 视图不存在
- `728` - IncorrectChunkFileChecksum: Chunk 文件校验和不正确

## 核心数据结构

### Chunk 副本信息
```cpp
struct TChunkReplica {
    NNodeTrackerClient::TNodeId NodeId;       // 节点 ID
    NNodeTrackerClient::TNodeDescriptorPtr NodeDescriptor; // 节点描述符
    NChunkClient::TPeerIndex PeerIndex;      // 对等节点索引
    bool Active;                             // 是否活跃
    TLegacyHints LegacyHints;                // 传统提示
};
```

### 读取限制
```cpp
struct TReadLimit {
    std::optional<i64> RowIndex;             // 行索引限制
    std::optional<NTableClient::TLegacyKey> Key; // 键限制
    std::optional<NTableClient::TLegacyKey> Offset; // 偏移量限制
};
```

### 数据统计
```cpp
struct TDataStatistics {
    i64 ChunkCount;                          // Chunk 数量
    i64 UncompressedDataSize;                // 未压缩数据大小
    i64 CompressedDataSize;                  // 压缩数据大小
    i64 DataWeight;                          // 数据权重
    i64 RowCount;                            // 行数
    i64 ValueCount;                          // 值数量
};
```

## 使用示例

### Chunk 副本操作
```cpp
#include <yt/yt/client/chunk_client/chunk_replica.h>

using namespace NYT::NChunkClient;

// 创建 Chunk 副本
TChunkReplica replica;
replica.NodeId = nodeId;
replica.Active = true;
replica.PeerIndex = 0;

// 副本比较和排序
if (replica1 < replica2) {
    // 处理副本比较逻辑
}
```

### 配置管理
```cpp
#include <yt/yt/client/chunk_client/config.h>

// 创建获取配置
auto fetchConfig = New<TFetchChunkSpecConfig>();
fetchConfig->MaxChunksPerFetch = 1000;
fetchConfig->MaxChunksPerLocateRequest = 100;

// 创建获取器配置
auto fetcherConfig = New<TFetcherConfig>();
fetcherConfig->NodeRpcTimeout = TDuration::Seconds(30);
fetcherConfig->NodeBanDuration = TDuration::Minutes(5);
fetcherConfig->BackoffTime = TDuration::MilliSeconds(100);
```

### 读取限制
```cpp
#include <yt/yt/client/chunk_client/read_limit.h>

// 创建读取限制
TReadLimit readLimit;
readLimit.RowIndex = 1000;  // 读取前 1000 行
readLimit.Key = /* 起始键 */;

// 创建上界限制
TReadLimit upperLimit;
upperLimit.RowIndex = 2000; // 读取到第 2000 行
```

### 数据统计
```cpp
#include <yt/yt/client/chunk_client/data_statistics.h>

// 创建数据统计
TDataStatistics stats;
stats.ChunkCount = 10;
stats.UncompressedDataSize = 1024 * 1024;  // 1MB
stats.CompressedDataSize = 256 * 1024;     // 256KB
stats.RowCount = 50000;
stats.DataWeight = 800 * 1024;             // 800KB
```

## 配置选项

### 获取配置参数
- **MaxChunksPerFetch**: 每次获取的最大 Chunk 数量
- **MaxChunksPerLocateRequest**: 每次定位请求的最大 Chunk 数量
- **NodeRpcTimeout**: 节点 RPC 超时时间
- **NodeBanDuration**: 节点被禁止访问的时间
- **BackoffTime**: 重试退避时间
- **NodeDirectorySynchronizationTimeout**: 节点目录同步超时

### 性能优化配置
- **MaxChunksPerNodeFetch**: 每个节点每次获取的最大 Chunk 数
- **Concurrency**: 并发操作级别
- **BufferSizes**: 各种缓冲区大小设置
- **Timeouts**: 各种操作超时设置

## 性能优化

### 读取优化
- **批量读取**: 批量获取多个 Chunk
- **预读取**: 智能预取下一个需要的数据
- **压缩传输**: 使用压缩减少网络传输
- **并行读取**: 多个 Chunk 并行读取

### 写入优化
- **并行写入**: 多节点并行写入
- **批量化**: 批量化写入操作
- **流水线**: 写入流水线处理
- **去重**: 避免重复写入相同数据

### 网络优化
- **连接复用**: 复用网络连接
- **负载均衡**: 智能选择最优节点
- **故障转移**: 自动处理节点故障
- **超时控制**: 合理的超时设置

## 监控和诊断

### 性能指标
- **读取吞吐量**: 监控数据读取速度
- **写入吞吐量**: 监控数据写入速度
- **延迟统计**: 监控操作延迟
- **错误率**: 监控错误发生频率

### 诊断工具
- **Chunk 状态查询**: 查询 Chunk 状态和位置
- **副本信息**: 查看副本分布和状态
- **性能分析**: 分析性能瓶颈
- **错误追踪**: 追踪和分析错误

## 最佳实践

### 读取操作
1. **批量读取**: 尽可能批量读取多个 Chunk
2. **合理限制**: 设置合适的读取限制范围
3. **并行处理**: 利用并行读取提高性能
4. **缓存利用**: 充分利用客户端缓存

### 写入操作
1. **批量化**: 使用批量写入减少开销
2. **副本配置**: 合理配置副本数量和分布
3. **压缩选择**: 根据数据特点选择压缩算法
4. **错误处理**: 完善的写入错误处理

### 运维管理
1. **监控告警**: 设置关键指标监控
2. **容量规划**: 根据数据增长规划存储容量
3. **性能调优**: 根据使用模式调优配置
4. **故障恢复**: 制定故障恢复预案

## 注意事项

1. **网络分区**: 正确处理网络分区情况
2. **数据一致性**: 理解 Chunk 的一致性保证
3. **资源限制**: 注意系统的资源限制
4. **并发控制**: 合理控制并发操作数量
5. **错误恢复**: 实现合适的错误恢复策略

## 扩展性

该模块设计支持：
- **新的存储介质**: 支持新的存储介质类型
- **新的压缩算法**: 支持新的压缩算法
- **新的网络协议**: 支持新的网络传输协议
- **插件化架构**: 支持插件化扩展

## 相关模块

该模块与以下模块紧密相关：
- `node_tracker_client`: 节点跟踪客户端
- `table_client`: 表客户端
- `object_client`: 对象客户端
- `rpc`: RPC 通信模块
- `core`: 核心库模块