# YTsaurus Chaos 客户端

## 概述

`chaos_client` 目录提供了 YTsaurus Chaos 复制功能的客户端接口。Chaos 是 YTsaurus 的多集群数据复制解决方案，支持跨集群的异步数据复制，为多活架构和灾难恢复提供基础支持。

## 核心功能

### 复制卡片管理
- **复制卡片**: 定义跨集群复制规则的配置对象
- **副本管理**: 管理源集群和目标集群的副本配置
- **复制进度**: 跟踪数据复制的进度状态
- **复制纪元**: 管理复制配置的版本控制

### 缓存系统
- **复制卡片缓存**: 高效缓存复制卡片信息
- **缓存更新**: 自动更新和失效机制
- **缓存配置**: 灵活的缓存配置选项
- **性能优化**: 减少网络请求和提高响应速度

### 序列化支持
- **持久化**: 支持复制卡片信息的序列化和反序列化
- **版本兼容**: 支持不同版本间的数据兼容
- **网络传输**: 高效的网络数据传输格式
- **存储格式**: 优化的存储格式

## 主要文件说明

### 公共接口定义
- `public.h`: 公共类型定义和错误码
  - 类型别名定义（TReplicationCardId、TChaosObjectId 等）
  - 错误码枚举定义
  - 结构体前向声明

### 复制卡片核心
- `replication_card.h/.cpp`: 复制卡片核心实现
  - `TReplicationCard`: 复制卡片主要数据结构
  - `TReplicaInfo`: 副本信息管理
  - `TReplicationProgress`: 复制进度跟踪
  - `TReplicaHistoryItem`: 副本历史记录

### 缓存管理
- `replication_card_cache.h/.cpp`: 复制卡片缓存实现
  - `IReplicationCardCache`: 缓存接口定义
  - 高效的缓存查询和更新机制

### 配置管理
- `config.h/.cpp`: 配置定义
  - `TChaosCacheChannelConfig`: 缓存通道配置
  - `TReplicationCardCacheConfig`: 复制卡片缓存配置
  - `TReplicationCardCacheDynamicConfig`: 动态配置支持

### 序列化支持
- `replication_card_serialization.h/.cpp`: 序列化实现
  - 高效的数据序列化和反序列化
  - 版本兼容性支持

### 辅助工具
- `helpers.h/.cpp`: 辅助函数和工具

## 核心数据结构

### 复制卡片 (TReplicationCard)
```cpp
struct TReplicationCard : public TRefCounted {
    THashMap<TReplicaId, TReplicaInfo> Replicas;           // 副本映射
    std::vector<NObjectClient::TCellId> CoordinatorCellIds; // 协调器 Cell ID
    TReplicationEra Era;                                   // 复制纪元
    NTableClient::TTableId TableId;                       // 表 ID
    NYPath::TYPath TablePath;                             // 表路径
    std::string TableClusterName;                         // 表集群名称
    NTransactionClient::TTimestamp CurrentTimestamp;      // 当前时间戳
    NTabletClient::TReplicatedTableOptionsPtr ReplicatedTableOptions; // 复制表选项
    TReplicationCardCollocationId ReplicationCardCollocationId; // 共置 ID
};
```

### 副本信息 (TReplicaInfo)
```cpp
struct TReplicaInfo {
    std::string ClusterName;                              // 集群名称
    NYPath::TYPath ReplicaPath;                           // 副本路径
    NTabletClient::ETableReplicaContentType ContentType;  // 内容类型
    NTabletClient::ETableReplicaMode Mode;                // 复制模式
    NTabletClient::ETableReplicaState State;              // 副本状态
    TReplicationProgress ReplicationProgress;             // 复制进度
    std::vector<TReplicaHistoryItem> History;             // 历史记录
    bool EnableReplicatedTableTracker;                    // 是否启用表跟踪器
};
```

### 复制进度 (TReplicationProgress)
```cpp
struct TReplicationProgress {
    struct TSegment {
        NTableClient::TUnversionedOwningRow LowerKey;    // 段起始键
        NTransactionClient::TTimestamp Timestamp;        // 时间戳
    };

    std::vector<TSegment> Segments;                      // 复制段列表
    NTableClient::TUnversionedOwningRow UpperKey;        // 段结束键
};
```

## 错误码定义

### Chaos 客户端错误码
- `3200` - ReplicationCardNotKnown: 复制卡片未知
- `3201` - ReplicationCardMigrated: 复制卡片已迁移
- `3202` - ChaosCellSuspended: Chaos Cell 已暂停
- `3203` - ReplicationCollocationNotKnown: 复制共置未知
- `3204` - ReplicationCollocationIsMigrating: 复制共置正在迁移
- `3205` - ChaosLeaseNotKnown: Chaos 租约未知
- `3206` - ShortcutNotFound: 快捷方式未找到
- `3207` - ShortcutHasDifferentEra: 快捷方式纪元不匹配
- `3208` - ShortcutRevoked: 快捷方式已撤销

## 使用示例

### 复制卡片操作
```cpp
#include <yt/yt/client/chaos_client/replication_card.h>

using namespace NYT::NChaosClient;

// 创建复制卡片
auto replicationCard = New<TReplicationCard>();
replicationCard->Era = 0;
replicationCard->TableId = /* 表 ID */;

// 添加副本
TReplicaInfo replicaInfo;
replicaInfo.ClusterName = "target_cluster";
replicaInfo.ReplicaPath = "/path/to/replica";
replicaInfo.Mode = NTabletClient::ETableReplicaMode::Sync;

// 查找副本
auto* replica = replicationCard->FindReplica(replicaId);
```

### 缓存配置
```cpp
#include <yt/yt/client/chaos_client/config.h>

// 创建缓存配置
auto cacheConfig = New<TReplicationCardCacheConfig>();
cacheConfig->EnableWatching = true;
cacheConfig->ExpireAfterSuccessfulUpdateTime = TDuration::Minutes(5);
cacheConfig->ExpireAfterFailedUpdateTime = TDuration::Seconds(30);

// 创建动态配置
auto dynamicConfig = New<TReplicationCardCacheDynamicConfig>();
dynamicConfig->EnableWatching = false;

// 应用动态配置
auto updatedConfig = cacheConfig->ApplyDynamic(dynamicConfig);
```

### 错误处理
```cpp
#include <yt/yt/client/chaos_client/public.h>

try {
    // 执行 Chaos 操作
} catch (const NYT::NChaosClient::TErrorException& e) {
    switch (e.GetCode()) {
        case NYT::NChaos::EErrorCode::ReplicationCardNotKnown:
            // 处理复制卡片未知错误
            break;
        case NYT::NChaos::EErrorCode::ChaosCellSuspended:
            // 处理 Chaos Cell 暂停错误
            break;
        default:
            // 处理其他错误
            break;
    }
}
```

## 配置选项

### 缓存配置
- **EnableWatching**: 启用复制卡片监听更新
- **ExpireAfterSuccessfulUpdateTime**: 成功更新后的过期时间
- **ExpireAfterFailedUpdateTime**: 失败更新后的过期时间
- **RefreshTime**: 刷新时间间隔
- **BatchSize**: 批量更新大小

### 通道配置
- **RetryAttempts**: 重试次数
- **RetryBackoff**: 重试退避策略
- **LoadBalancing**: 负载均衡配置

## 性能优化

### 缓存策略
- **智能过期**: 基于使用模式的智能缓存过期
- **预加载**: 预加载常用的复制卡片
- **批量更新**: 批量更新缓存以提高效率
- **内存管理**: 高效的内存使用和回收

### 网络优化
- **连接复用**: 复用网络连接
- **压缩传输**: 支持数据压缩
- **异步操作**: 异步网络操作
- **负载均衡**: 智能的负载分配

## 监控和诊断

### 性能指标
- **缓存命中率**: 监控缓存效果
- **响应时间**: 监控操作响应时间
- **错误率**: 监控操作错误率
- **网络流量**: 监控网络使用情况

### 诊断工具
- **调试信息**: 详细的调试日志
- **状态查询**: 查询缓存和复制状态
- **错误追踪**: 完整的错误追踪信息
- **性能分析**: 性能瓶颈分析

## 最佳实践

### 配置管理
1. **合理缓存**: 根据业务特点设置合适的缓存参数
2. **监控更新**: 密切监控复制卡片更新
3. **错误处理**: 实现完善的错误处理机制
4. **性能调优**: 根据性能指标调优配置

### 运维管理
1. **监控告警**: 设置关键指标的监控告警
2. **日志管理**: 完善的日志记录和分析
3. **备份恢复**: 定期备份复制配置
4. **容量规划**: 根据增长趋势规划容量

### 开发建议
1. **异常安全**: 确保异常情况下的资源清理
2. **异步处理**: 使用异步操作提高性能
3. **错误重试**: 实现合理的错误重试策略
4. **测试覆盖**: 确保充分的测试覆盖

## 注意事项

1. **版本兼容**: 注意客户端和服务端版本兼容性
2. **网络分区**: 正确处理网络分区情况
3. **数据一致性**: 理解复制的一致性保证
4. **性能影响**: 复制对源集群性能的影响
5. **故障恢复**: 制定故障恢复策略

## 扩展性

该模块设计支持：
- **新的复制模式**: 支持新的复制模式扩展
- **自定义缓存策略**: 支持自定义缓存策略
- **监控集成**: 与外部监控系统集成
- **插件化架构**: 支持插件化扩展

## 相关模块

该模块与以下模块紧密相关：
- `table_client`: 表客户端，提供表操作接口
- `tablet_client`: Tablet 客户端，管理 Tablet 操作
- `transaction_client`: 事务客户端，提供事务支持
- `object_client`: 对象客户端，管理对象 ID
- `hydra`: Hydra 模块，提供分布式一致性支持