# YTsaurus Hive Client 模块

## 概述

Hive Client 模块是 YTsaurus 分布式事务系统的核心组件，实现了基于 Hydra 的一致性协议。该模块提供了跨多个单元（Cell）的分布式事务支持，包括事务协调、时间戳管理和参与者管理等关键功能。

## 核心功能

### 1. 分布式事务协调
- **事务参与者管理**: 管理跨多个单元的事务参与者
- **事务状态同步**: 确保所有参与者的一致性状态
- **故障恢复**: 处理参与者故障和恢复
- **两阶段提交**: 实现分布式事务的原子性

### 2. 时间戳管理
- **全局时间戳**: 提供全局唯一递增的时间戳
- **时间戳映射**: 维护各单元时间戳的映射关系
- **时钟同步**: 确保跨单元时钟的一致性
- **时间戳查询**: 高效的时间戳查询服务

### 3. 单元管理
- **单元发现**: 自动发现和注册集群单元
- **单元目录**: 维护单元的地址和状态信息
- **负载均衡**: 智能的事务分发和负载均衡
- **健康检查**: 定期检查单元健康状态

## 主要组件

### 1. 事务参与者接口 (ITransactionParticipant)

```cpp
DECLARE_REFCOUNTED_STRUCT(ITransactionParticipant)
```

定义了分布式事务参与者的标准接口：
- **事务注册**: 参与者向事务协调器注册
- **操作执行**: 执行事务的一部分操作
- **状态提交**: 提交或回滚事务操作
- **状态查询**: 查询参与者的事务状态

### 2. 时间戳映射 (TTimestampMap)

```cpp
struct TTimestampMap;
```

维护全局时间戳到各单元本地时间戳的映射：
- **映射关系**: 全局时间戳 → {单元ID → 本地时间戳}
- **压缩存储**: 高效的映射关系存储
- **快速查询**: 基于哈希的快速时间戳查找
- **版本控制**: 支持映射关系的版本管理

### 3. 集群目录 (TClusterDirectory)

```cpp
class TClusterDirectory;
```

管理集群单元的元数据信息：
- **单元地址**: 各单元的网络地址和端口
- **单元类型**: Master、Scheduler、Node 等单元类型
- **配置信息**: 单元的配置参数和选项
- **状态监控**: 单元的运行状态和健康指标

## 错误处理

### 错误代码枚举

```cpp
YT_DEFINE_ERROR_ENUM(
    ((MailboxNotCreatedYet)    (2200))  // 邮箱未创建
    ((ParticipantUnregistered) (2201))  // 参与者未注册
    ((TimeEntryNotFound)       (2202))  // 时间条目未找到
    ((UnknownCell)             (2203))  // 未知单元
);
```

### 错误详解

1. **MailboxNotCreatedYet (2200)**
   - **触发条件**: 尝试访问尚未创建的通信邮箱
   - **常见场景**: 系统启动早期、单元初始化中
   - **处理策略**: 重试或等待系统完全启动

2. **ParticipantUnregistered (2201)**
   - **触发条件**: 事务参与者未在协调器中注册
   - **常见场景**: 参与者故障恢复、网络分区
   - **处理策略**: 重新注册参与者或回滚事务

3. **TimeEntryNotFound (2202)**
   - **触发条件**: 请求的时间戳条目不存在
   - **常见场景**: 时间戳过期、时间戳映射损坏
   - **处理策略**: 重新获取时间戳或重建映射

4. **UnknownCell (2203)**
   - **触发条件**: 请求的单元不存在或不可达
   - **常见场景**: 单元下线、配置错误
   - **处理策略**: 更新集群目录或切换备用单元

## 类型定义

### 核心类型别名

```cpp
// 事务相关
using NTransactionClient::TTransactionId;
using NTransactionClient::NullTransactionId;
using NTransactionClient::TTimestamp;
using NTransactionClient::NullTimestamp;

// 单元相关
using NHydra::TCellId;
using NHydra::NullCellId;

// 时间戳映射
struct TTimestampMap;
```

## 使用方法

### 1. 基本事务参与者使用

```cpp
#include <yt/yt/client/hive/public.h>
#include <yt/yt/client/hive/transaction_participant.h>

using namespace NYT::NHiveClient;

// 创建事务参与者
auto participant = CreateTransactionParticipant(cellId, connection);

// 注册事务
TTransactionId transactionId = TGuid::Create();
participant->RegisterParticipant(transactionId);

// 执行事务操作
participant->PrepareTransaction(transactionId);
participant->CommitTransaction(transactionId);
```

### 2. 时间戳映射使用

```cpp
#include <yt/yt/client/hive/timestamp_map.h>

// 创建时间戳映射
auto timestampMap = std::make_shared<TTimestampMap>();

// 添加映射关系
TTimestamp globalTimestamp = GetCurrentTimestamp();
timestampMap->AddEntry(cellId1, localTimestamp1);
timestampMap->AddEntry(cellId2, localTimestamp2);

// 查询时间戳
auto localTimestamp = timestampMap->Lookup(cellId1, globalTimestamp);
if (localTimestamp) {
    // 使用本地时间戳
    ProcessLocalData(*localTimestamp);
}
```

### 3. 集群目录使用

```cpp
#include <yt/yt/client/hive/cluster_directory.h>

// 创建集群目录
auto clusterDirectory = CreateClusterDirectory();

// 添加单元信息
ClusterCellInfo cellInfo;
cellInfo.CellId = cellId;
cellInfo.Addresses = {"cell1.ytsaurus.net:9013"};
cellInfo.CellType = ECellType::Master;

clusterDirectory->RegisterCell(cellInfo);

// 查询单元
auto foundCell = clusterDirectory->FindCell(cellId);
if (foundCell) {
    // 使用单元信息
    ConnectToCell(*foundCell);
}
```

### 4. 错误处理

```cpp
try {
    participant->CommitTransaction(transactionId);
} catch (const TErrorException& e) {
    switch (e.GetErrorCode()) {
        case NYT::TErrorCode(2201): // ParticipantUnregistered
            // 重新注册参与者
            participant->RegisterParticipant(transactionId);
            participant->CommitTransaction(transactionId);
            break;

        case NYT::TErrorCode(2203): // UnknownCell
            // 更新集群目录
            UpdateClusterDirectory();
            break;

        default:
            // 其他错误处理
            throw;
    }
}
```

## 架构设计

### 1. 分层架构

```
应用层
│
├── Hive Client (本模块)
│   ├── 事务协调器
│   ├── 时间戳管理器
│   └── 参与者管理器
│
├── Transaction Client
│   ├── 事务抽象
│   └── 本地事务管理
│
└── Hydra Client
    ├── Raft 实现
    └── 一致性协议
```

### 2. 通信模式

```cpp
// 参与者通信接口
class ITransactionParticipant {
public:
    // 注册参与者
    virtual TFuture<void> RegisterParticipant(
        const TTransactionId& transactionId) = 0;

    // 准备事务
    virtual TFuture<void> PrepareTransaction(
        const TTransactionId& transactionId) = 0;

    // 提交事务
    virtual TFuture<void> CommitTransaction(
        const TTransactionId& transactionId) = 0;

    // 回滚事务
    virtual TFuture<void> AbortTransaction(
        const TTransactionId& transactionId) = 0;
};
```

### 3. 时间戳同步机制

```cpp
// 全局时间戳获取
class GlobalTimestampProvider {
public:
    TFuture<TTimestamp> GetTimestamp() {
        // 1. 向时间戳服务请求全局时间戳
        auto future = TimestampService->AllocateTimestamp();

        // 2. 记录到时间戳映射
        return future.Apply(BIND([this] (TTimestamp timestamp) {
            UpdateTimestampMap(timestamp);
            return timestamp;
        }));
    }

private:
    void UpdateTimestampMap(TTimestamp timestamp) {
        for (const auto& cell : activeCells_) {
            timestampMap_->AddEntry(cell->GetCellId(), timestamp);
        }
    }
};
```

## 性能优化

### 1. 批量操作

```cpp
// 批量时间戳分配
class BatchTimestampAllocator {
public:
    TFuture<std::vector<TTimestamp>> AllocateBatch(
        int count,
        const std::vector<TCellId>& cells) {

        // 一次性分配多个时间戳
        return TimestampService->AllocateBatch(count)
            .Apply(BIND([this, cells] (const std::vector<TTimestamp>& timestamps) {
                // 批量更新时间戳映射
                UpdateBatchTimestampMap(cells, timestamps);
                return timestamps;
            }));
    }
};
```

### 2. 缓存机制

```cpp
// 单元信息缓存
class CellInfoCache {
private:
    TLRUCache<TCellId, ClusterCellInfo> cache_;
    TDuration ttl_;

public:
    std::optional<ClusterCellInfo> Lookup(const TCellId& cellId) {
        auto entry = cache_.Find(cellId);
        if (entry && TInstant::Now() - entry->LastUpdated < ttl_) {
            return entry->Info;
        }
        return std::nullopt;
    }

    void Update(const TCellId& cellId, const ClusterCellInfo& info) {
        CacheEntry entry{info, TInstant::Now()};
        cache_.Insert(cellId, entry);
    }
};
```

### 3. 连接池

```cpp
// 参与者连接池
class ParticipantConnectionPool {
private:
    std::unordered_map<TCellId, std::queue<ITransactionParticipantPtr>> pools_;
    std::mutex mutex_;

public:
    ITransactionParticipantPtr Acquire(const TCellId& cellId) {
        std::lock_guard<std::mutex> lock(mutex_);
        auto& pool = pools_[cellId];
        if (!pool.empty()) {
            auto participant = pool.front();
            pool.pop();
            return participant;
        }
        return CreateParticipant(cellId);
    }

    void Release(const TCellId& cellId, ITransactionParticipantPtr participant) {
        std::lock_guard<std::mutex> lock(mutex_);
        pools_[cellId].push(participant);
    }
};
```

## 监控和诊断

### 1. 关键指标

```cpp
struct HiveClientMetrics {
    // 事务指标
    std::atomic<i64> TotalTransactions{0};
    std::atomic<i64> SuccessfulTransactions{0};
    std::atomic<i64> FailedTransactions{0};
    TDuration AverageTransactionDuration;

    // 时间戳指标
    std::atomic<i64> TimestampRequests{0};
    TDuration AverageTimestampLatency;
    std::atomic<i64> TimestampMapEntries{0};

    // 单元指标
    std::unordered_map<TCellId, CellMetrics> CellMetrics;

    // 错误统计
    std::unordered_map<int, std::atomic<i64>> ErrorCounts;
};

struct CellMetrics {
    std::atomic<i64> RequestCount{0};
    std::atomic<i64> ErrorCount{0};
    TDuration AverageResponseTime;
    TInstant LastSuccessfulRequest;
    bool IsHealthy;
};
```

### 2. 日志记录

```cpp
// 结构化日志
class HiveLogger {
public:
    void LogTransactionStart(
        const TTransactionId& transactionId,
        const std::vector<TCellId>& participants) {

        YT_LOG_INFO("Distributed transaction started (TransactionId: %v, Participants: [%v])",
            transactionId, JoinStrings(participants, ", "));
    }

    void LogTimestampAllocation(
        TTimestamp timestamp,
        const std::vector<TCellId>& cells) {

        YT_LOG_DEBUG("Timestamp allocated (Timestamp: %v, Cells: [%v])",
            timestamp, JoinStrings(cells, ", "));
    }

    void LogParticipantError(
        const TCellId& cellId,
        const TTransactionId& transactionId,
        const TError& error) {

        YT_LOG_WARNING("Participant error (CellId: %v, TransactionId: %v, Error: %v)",
            cellId, transactionId, error);
    }
};
```

## 最佳实践

### 1. 事务设计

```cpp
// 分布式事务最佳实践
class DistributedTransactionBestPractices {
public:
    // 保持事务简短
    TFuture<void> ExecuteShortTransaction() {
        auto transaction = CreateDistributedTransaction();

        // 避免长时间持有锁
        return transaction->Execute([] {
            return PerformQuickOperation();
        });
    }

    // 处理部分失败
    TFuture<void> HandlePartialFailures() {
        return transaction->Execute([] {
            try {
                return CriticalOperation();
            } catch (const TPartialFailureException& e) {
                // 补偿事务
                return CompensationTransaction();
            }
        });
    }
};
```

### 2. 错误恢复策略

```cpp
// 智能重试机制
class IntelligentRetryStrategy {
public:
    template<typename T>
    TFuture<T> ExecuteWithRetry(
        std::function<TFuture<T>()> operation,
        const TTransactionId& transactionId) {

        return RetryOperation(operation, MaxRetries)
            .Apply(BIND([this, transactionId] (const TErrorOr<T>& result) {
                if (!result.IsOK()) {
                    // 分析错误类型
                    AnalyzeAndRecover(result.GetError(), transactionId);
                }
                return result;
            }));
    }

private:
    void AnalyzeAndRecover(const TError& error, const TTransactionId& transactionId) {
        switch (error.GetErrorCode()) {
            case NYT::TErrorCode(2201): // ParticipantUnregistered
                ReRegisterParticipant(transactionId);
                break;
            case NYT::TErrorCode(2203): // UnknownCell
                UpdateClusterDirectory();
                break;
            default:
                // 记录错误用于分析
                LogErrorForAnalysis(error, transactionId);
        }
    }
};
```

## 依赖项

### 内部依赖
- `yt/yt/client/hydra/public.h` - Hydra 一致性协议
- `yt/yt/client/transaction_client/public.h` - 事务客户端
- `yt/yt/core/misc/public.h` - 核心公共定义

### 外部依赖
- 网络通信库
- 时间管理库
- 并发库
- 序列化库

## 扩展性

### 1. 自定义事务策略

```cpp
// 事务策略接口
class ITransactionStrategy {
public:
    virtual TFuture<void> ExecuteDistributedTransaction(
        const std::vector<ITransactionParticipantPtr>& participants,
        const TTransactionRequest& request) = 0;
};

// 实现自定义策略
class CustomTransactionStrategy : public ITransactionStrategy {
public:
    TFuture<void> ExecuteDistributedTransaction(
        const std::vector<ITransactionParticipantPtr>& participants,
        const TTransactionRequest& request) override {

        // 自定义事务执行逻辑
        return ImplementCustomTransaction(participants, request);
    }
};
```

### 2. 插件架构

```cpp
// Hive 客户端插件
class IHiveClientPlugin {
public:
    virtual std::string GetName() const = 0;
    virtual void Initialize(const NYTree::IMapNodePtr& config) = 0;
    virtual ITransactionParticipantPtr CreateParticipant(
        const TCellId& cellId) = 0;
};
```

## 版本兼容性

- **协议兼容性**: 支持多版本的事务协议
- **API 兼容性**: 保持向后兼容的接口
- **数据兼容性**: 支持时间戳映射的版本迁移

## 相关模块

- **Transaction Client**: 本地事务管理
- **Hydra Client**: 一致性协议实现
- **Object Client**: 对象存储接口
- **Table Client**: 表数据操作

## 参考文档

- [YTsaurus 分布式事务系统](../../../docs/distributed-transactions.md)
- [Hydra 一致性协议](../../../docs/hydra-protocol.md)
- [时间戳管理机制](../../../docs/timestamp-management.md)
- [故障恢复策略](../../../docs/failure-recovery.md)

## 贡献指南

在修改此模块时：
1. 确保分布式事务的正确性
2. 添加充分的集成测试
3. 考虑网络分区和故障场景
4. 保证时间戳的一致性
5. 添加详细的监控指标
6. 维护向后兼容性