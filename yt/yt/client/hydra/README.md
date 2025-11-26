# YTsaurus Hydra Client 模块

## 概述

Hydra Client 模块是 YTsaurus 分布式一致性系统的客户端接口，基于 Raft 算法实现强一致性保证。该模块提供了分布式状态机复制、领导者选举、日志复制和快照管理等核心功能，是 YTsaurus 分布式架构的基础组件。

## 核心功能

### 1. Raft 一致性协议
- **领导者选举**: 基于投票的领导者选举机制
- **日志复制**: 确保操作在所有副本上一致执行
- **安全性保证**: 防止脑裂和状态不一致
- **成员变更**: 安全的集群成员动态变更

### 2. 状态管理
- **状态机**: 分布式状态机的抽象和实现
- **版本控制**: 操作和状态的版本管理
- **快照**: 定期状态快照以加快恢复速度
- **变更日志**: 持久化的操作日志

### 3. 故障恢复
- **自动故障转移**: 领导者故障时自动选举新领导者
- **日志恢复**: 从日志中恢复状态
- **快照恢复**: 从快照快速恢复状态
- **数据完整性**: 确保恢复后的数据一致性

## 主要组件

### 1. 节点状态枚举 (EPeerState)

```cpp
DEFINE_ENUM(EPeerState,
    ((None)                (0))  // 无状态
    ((Stopped)             (1))  // 已停止
    ((Elections)           (2))  // 选举中
    ((FollowerRecovery)    (3))  // 跟随者恢复中
    ((Following)           (4))  // 跟随中
    ((LeaderRecovery)      (5))  // 领导者恢复中
    ((Leading)             (6))  // 领导中
);
```

#### 状态转换说明

1. **None → Stopped**: 系统初始化
2. **Stopped → Elections**: 开始选举过程
3. **Elections → Following**: 成为跟随者
4. **Elections → Leading**: 成为领导者
5. **Following → LeaderRecovery**: 领导者故障后的恢复
6. **Leading → Stopped**: 正常关闭或故障

### 2. 错误代码枚举

```cpp
YT_DEFINE_ERROR_ENUM(
    ((NoSuchSnapshot)              (600))  // 快照不存在
    ((NoSuchChangelog)             (601))  // 变更日志不存在
    ((InvalidEpoch)                (602))  // 无效选举周期
    ((InvalidVersion)              (603))  // 无效版本
    ((OutOfOrderMutations)         (609))  // 变更顺序错误
    ((InvalidSnapshotVersion)      (610))  // 无效快照版本
    ((ReadOnlySnapshotBuilt)       (611))  // 只读快照已构建
    ((ReadOnlySnapshotBuildFailed) (612))  // 只读快照构建失败
    ((BrokenChangelog)             (613))  // 变更日志损坏
    ((ChangelogIOError)            (614))  // 变更日志 IO 错误
    ((InvalidChangelogState)       (615))  // 无效变更日志状态
    ((ReadOnly)                    (616))  // 只读模式
    ((RestartAfterRecovery)        (617))  // 恢复后重启
);
```

### 3. 节点类型枚举 (EPeerKind)

```cpp
DEFINE_ENUM(EPeerKind,
    ((Leader)           (0))  // 领导者
    ((Follower)         (1))  // 跟随者
    ((LeaderOrFollower) (2))  // 领导者或跟随者
);
```

### 4. 核心类型定义

```cpp
// 修订版本号
YT_DEFINE_STRONG_TYPEDEF(TRevision, ui64);
constexpr auto NullRevision = TRevision();

// 前向声明
struct TVersion;
struct TReachableState;
struct TElectionPriority;

// 从 Election 模块继承的类型
using NElection::TCellId;
using NElection::NullCellId;
using NElection::InvalidPeerId;
using NElection::TPeerPriority;
using NElection::TEpochId;
```

## 使用方法

### 1. 基本状态查询

```cpp
#include <yt/yt/client/hydra/public.h>

using namespace NYT::NHydra;

// 检查节点状态
if (peerState == EPeerState::Leading) {
    // 当前节点是领导者，可以处理写请求
    HandleWriteRequests();
} else if (peerState == EPeerState::Following) {
    // 当前节点是跟随者，只能处理读请求
    HandleReadOnlyRequests();
} else if (peerState == EPeerState::Elections) {
    // 正在进行选举，建议等待
    WaitForElectionCompletion();
}
```

### 2. 错误处理

```cpp
try {
    // 执行 Hydra 操作
    ExecuteHydraOperation();
} catch (const TErrorException& e) {
    switch (e.GetErrorCode()) {
        case NYT::TErrorCode(600): // NoSuchSnapshot
            HandleMissingSnapshot();
            break;

        case NYT::TErrorCode(614): // ChangelogIOError
            HandleChangelogIOError();
            break;

        case NYT::TErrorCode(616): // ReadOnly
            HandleReadOnlyMode();
            break;

        default:
            // 通用错误处理
            HandleGenericError(e);
            break;
    }
}
```

### 3. 版本管理

```cpp
// 检查版本兼容性
bool IsVersionCompatible(const TVersion& requiredVersion, const TVersion& currentVersion) {
    return currentVersion >= requiredVersion;
}

// 处理版本升级
void HandleVersionUpgrade(const TVersion& newVersion) {
    if (IsVersionCompatible(newVersion, GetCurrentVersion())) {
        // 执行升级逻辑
        PerformUpgrade(newVersion);
    } else {
        throw TErrorException(NYT::TErrorCode(603)) // InvalidVersion
            << "Cannot upgrade from version " << GetCurrentVersion()
            << " to " << newVersion;
    }
}
```

## 架构设计

### 1. Raft 核心组件

```cpp
// Raft 节点抽象
class IRaftPeer {
public:
    virtual EPeerState GetState() const = 0;
    virtual TEpochId GetCurrentEpoch() const = 0;
    virtual TRevision GetCurrentRevision() const = 0;

    virtual TFuture<void> AppendMutation(const TMutation& mutation) = 0;
    virtual TFuture<TSnapshot> CreateSnapshot() = 0;
    virtual TFuture<void> InstallSnapshot(const TSnapshot& snapshot) = 0;
};
```

### 2. 状态机接口

```cpp
// 分布式状态机接口
class IStateMachine {
public:
    virtual TFuture<void> Apply(const TMutation& mutation) = 0;
    virtual TFuture<TSnapshot> CreateSnapshot() = 0;
    virtual TFuture<void> LoadSnapshot(const TSnapshot& snapshot) = 0;
    virtual TVersion GetCurrentVersion() const = 0;
};
```

### 3. 持久化存储

```cpp
// 持久化存储接口
class IPersistentStorage {
public:
    virtual TFuture<void> AppendChangelogRecord(const TChangelogRecord& record) = 0;
    virtual TFuture<std::vector<TChangelogRecord>> ReadChangelog(TRevision from, TRevision to) = 0;
    virtual TFuture<void> StoreSnapshot(const TSnapshot& snapshot) = 0;
    virtual TFuture<TSnapshot> LoadSnapshot(TVersion version) = 0;
};
```

## 性能优化

### 1. 批量操作

```cpp
// 批量变更提交
class BatchMutationSubmitter {
public:
    TFuture<void> SubmitBatch(const std::vector<TMutation>& mutations) {
        // 1. 验证批量操作
        ValidateBatch(mutations);

        // 2. 创建批量变更
        auto batchMutation = CreateBatchMutation(mutations);

        // 3. 提交到 Raft 日志
        return raftPeer_->AppendMutation(batchMutation);
    }

private:
    void ValidateBatch(const std::vector<TMutation>& mutations) {
        // 检查操作的合法性
        for (const auto& mutation : mutations) {
            ValidateMutation(mutation);
        }
    }
};
```

### 2. 快照优化

```cpp
// 增量快照
class IncrementalSnapshotManager {
public:
    TFuture<TSnapshot> CreateIncrementalSnapshot() {
        return currentStateMachine_->GetCurrentVersion()
            .Apply(BIND([this] (TVersion currentVersion) {
                // 1. 检查是否有基础快照
                auto baseSnapshot = GetBaseSnapshot();
                if (!baseSnapshot) {
                    return CreateFullSnapshot();
                }

                // 2. 创建增量快照
                return CreateIncrementalFromBase(baseSnapshot, currentVersion);
            }));
    }

private:
    TFuture<TSnapshot> CreateIncrementalFromBase(
        const TSnapshot& baseSnapshot,
        TVersion targetVersion) {

        // 应用从基础版本到目标版本的变更
        return ApplyIncrementalChanges(baseSnapshot, targetVersion);
    }
};
```

### 3. 并发控制

```cpp
// 读写分离
class ReadWriteController {
public:
    TFuture<TReadResult> ExecuteRead(const TReadRequest& request) {
        if (peerState_ == EPeerState::Leading) {
            // 领导者可以直接处理读请求
            return HandleReadLocally(request);
        } else {
            // 跟随者可能需要从领导者读取
            return ForwardToLeader(request);
        }
    }

    TFuture<TWriteResult> ExecuteWrite(const TWriteRequest& request) {
        if (peerState_ == EPeerState::Leading) {
            // 只有领导者可以处理写请求
            return HandleWriteLocally(request);
        } else {
            // 跟随者转发写请求到领导者
            return ForwardToLeader(request);
        }
    }
};
```

## 监控和诊断

### 1. 关键指标

```cpp
struct HydraMetrics {
    // Raft 指标
    std::atomic<i64> MutationsApplied{0};
    std::atomic<i64> SnapshotsCreated{0};
    TDuration AverageApplyLatency;
    TDuration AverageElectionTime;

    // 状态指标
    EPeerState CurrentState;
    TEpochId CurrentEpoch;
    TRevision CurrentRevision;

    // 网络指标
    std::atomic<i64> MessagesSent{0};
    std::atomic<i64> MessagesReceived{0};
    std::unordered_map<TPeerId, TDuration> PeerLatencies;

    // 存储指标
    i64 ChangelogSize;
    i64 SnapshotSize;
    TDuration LastSnapshotTime;
};
```

### 2. 健康检查

```cpp
// Raft 节点健康检查
class RaftHealthChecker {
public:
    bool IsHealthy() const {
        return CheckState() &&
               CheckConnectivity() &&
               CheckStorage() &&
               CheckProgress();
    }

private:
    bool CheckState() const {
        return currentState_ == EPeerState::Leading ||
               currentState_ == EPeerState::Following;
    }

    bool CheckConnectivity() const {
        // 检查与其他节点的连接
        for (const auto& [peerId, connection] : peerConnections_) {
            if (!connection->IsConnected()) {
                return false;
            }
        }
        return true;
    }

    bool CheckStorage() const {
        // 检查存储系统健康状态
        return storage_->IsHealthy();
    }

    bool CheckProgress() const {
        // 检查是否有进展（应用最新变更）
        auto now = TInstant::Now();
        return (now - lastMutationApplied_) < MaxStallTime;
    }
};
```

## 最佳实践

### 1. 配置调优

```cpp
// Raft 配置优化
struct OptimizedRaftConfig {
    // 选举超时（根据网络延迟调整）
    TDuration ElectionTimeout = TDuration::Seconds(5);

    // 心跳间隔
    TDuration HeartbeatInterval = TDuration::MilliSeconds(500);

    // 快照间隔
    int SnapshotInterval = 10000;  // 每 10000 个变更创建快照

    // 变更日志保留
    int ChangelogToKeep = 5;  // 保留最近 5 个快照的变更日志

    // 并发限制
    int MaxConcurrentMutations = 100;

    // 缓冲区大小
    size_t MaxMutationSize = 1_MB;
};
```

### 2. 故障处理

```cpp
// 故障恢复策略
class FailureRecoveryStrategy {
public:
    void HandlePeerFailure(const TPeerId& failedPeer) {
        // 1. 从集群中移除失败的节点
        RemovePeerFromCluster(failedPeer);

        // 2. 重新配置 Raft 集群
        ReconfigureCluster();

        // 3. 通知监控系统
        AlertMonitoringSystem(failedPeer);
    }

    void HandleStorageFailure(const TError& error) {
        if (error.GetErrorCode() == NYT::TErrorCode(614)) { // ChangelogIOError
            // 尝试修复存储
            AttemptStorageRepair();

            // 如果修复失败，切换到只读模式
            if (!storage_->IsHealthy()) {
                TransitionToReadOnly();
            }
        }
    }
};
```

## 依赖项

### 内部依赖
- `yt/yt/client/election/public.h` - 选举系统接口
- `yt/yt/core/misc/public.h` - 核心公共定义
- `yt/yt/core/rpc/public.h` - RPC 通信框架

### 外部依赖
- 网络通信库
- 持久化存储库
- 序列化库
- 时间管理库

## 版本兼容性

- **协议兼容性**: 支持多版本 Raft 协议
- **状态兼容性**: 支持状态机的版本迁移
- **存储兼容性**: 支持快照和日志的格式升级

## 扩展性

### 1. 自定义状态机

```cpp
// 自定义状态机接口
class ICustomStateMachine : public IStateMachine {
public:
    // 扩展的状态机操作
    virtual TFuture<CustomResult> ExecuteCustomOperation(
        const CustomRequest& request) = 0;
};
```

### 2. 插件架构

```cpp
// Raft 插件接口
class IRaftPlugin {
public:
    virtual std::string GetName() const = 0;
    virtual void Initialize(const NYTree::IMapNodePtr& config) = 0;
    virtual TFuture<void> OnLeaderElected() = 0;
    virtual TFuture<void> OnBecomeFollower() = 0;
};
```

## 相关模块

- **Election Client**: 领导者选举系统
- **Transaction Client**: 分布式事务
- **Hive Client**: 分布式协调
- **RPC Client**: 网络通信层

## 参考文档

- [Raft 一致性算法详解](../../../docs/raft-algorithm.md)
- [YTsaurus 分布式架构](../../../docs/distributed-architecture.md)
- [故障恢复和一致性](../../../docs/fault-tolerance.md)
- [性能优化指南](../../../docs/raft-performance.md)

## 贡献指南

在修改此模块时：
1. 严格遵守 Raft 协议规范
2. 充分测试故障场景
3. 验证一致性和安全性
4. 添加详细的监控指标
5. 保持向后兼容性
6. 考虑网络分区和时钟偏差