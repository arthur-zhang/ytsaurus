# YTsaurus Election 模块

## 概述

Election 模块为 YTsaurus 分布式系统提供了选举机制的核心类型定义和错误处理。该模块实现了基于 Raft 一致性算法的领导者选举，支持多节点环境下的分布式协调和一致性保证。

## 核心功能

### 1. 选举类型定义
- **TEpochId**: 选举周期标识符
- **TPeerPriority**: 节点优先级
- **TCellId**: 单元标识符
- **EPeerState**: 节点状态枚举

### 2. 错误处理
专门为选举过程定义的错误代码，用于处理各种异常情况。

### 3. 节点状态管理
定义了选举过程中节点的各种状态及其转换规则。

## 主要组件详解

### 类型定义

```cpp
// 选举周期标识符，用于标识不同的选举周期
using TEpochId = TGuid;

// 节点优先级，第一个分量为主优先级，第二个分量为次优先级
using TPeerPriority = std::pair<i64, i64>;

// 无效节点ID常量
constexpr int InvalidPeerId = -1;

// 分布式单元标识符
using TCellId = TGuid;
extern const TCellId NullCellId;  // 空单元ID常量
```

### 错误代码枚举

```cpp
YT_DEFINE_ERROR_ENUM(
    ((InvalidState)  (800))  // 无效状态
    ((InvalidLeader) (801))  // 无效领导者
    ((InvalidEpoch)  (802))  // 无效选举周期
);
```

#### 错误详解

1. **InvalidState (800) - 无效状态**
   - **触发条件**: 节点处于不支持当前操作的状态
   - **常见场景**:
     - 在非领导者状态下尝试执行领导者操作
     - 状态转换不合法
     - 系统初始化未完成
   - **处理策略**: 检查节点状态，等待正确的状态或重新初始化

2. **InvalidLeader (801) - 无效领导者**
   - **触发条件**: 遇到无效的领导者信息
   - **常见场景**:
     - 领导者失去领导地位
     - 网络分区导致多个领导者
     - 领导者ID格式错误
   - **处理策略**: 重新发起选举，验证领导者合法性

3. **InvalidEpoch (802) - 无效选举周期**
   - **触发条件**: 选举周期ID不匹配或过期
   - **常见场景**:
     - 收到过期的选举消息
     - 网络延迟导致周期不同步
     - 节点重启导致周期重置
   - **处理策略**: 重新同步选举周期，忽略过期消息

### 节点状态枚举

```cpp
DEFINE_ENUM(EPeerState,
    (Stopped)   // 已停止
    (Voting)    // 投票中
    (Leading)   // 领导中
    (Following) // 跟随中
);
```

#### 状态详解

1. **Stopped - 已停止**
   - **描述**: 节点已停止参与选举
   - **原因**:
     - 系统关闭
     - 配置错误
     - 人工干预
   - **转换**: 可转换为 Voting 状态

2. **Voting - 投票中**
   - **描述**: 节点正在参与投票过程
   - **活动**:
     - 接收候选人请求
     - 进行投票决策
     - 监控领导者状态
   - **转换**: 可转换为 Leading 或 Following

3. **Leading - 领导中**
   - **描述**: 节点已成为当前领导者
   - **责任**:
     - 处理客户端请求
     - 维护日志一致性
     - 协调跟随者
   - **转换**: 可转换为 Following 或 Stopped

4. **Following - 跟随中**
   - **描述**: 节点正在跟随当前领导者
   - **活动**:
     - 复制领导者日志
     - 响应领导者心跳
     - 准备接管领导权
   - **转换**: 可转换为 Leading 或 Voting

## 选举算法流程

### 1. 选举启动
```cpp
// 节点启动选举时的典型逻辑
if (CurrentState == EPeerState::Stopped) {
    CurrentState = EPeerState::Voting;
    TEpochId newEpoch = GenerateNewEpochId();
    StartElection(newEpoch);
}
```

### 2. 领导者选举
```cpp
// 成为领导者的条件检查
bool CanBecomeLeader(const TPeerPriority& myPriority,
                    const std::vector<TPeerPriority>& candidates) {
    return std::all_of(candidates.begin(), candidates.end(),
        [myPriority](const TPeerPriority& other) {
            return myPriority > other;
        });
}
```

### 3. 状态转换验证
```cpp
// 安全的状态转换
bool IsValidStateTransition(EPeerState from, EPeerState to) {
    switch (from) {
        case EPeerState::Stopped:
            return to == EPeerState::Voting;
        case EPeerState::Voting:
            return to == EPeerState::Leading ||
                   to == EPeerState::Following ||
                   to == EPeerState::Stopped;
        case EPeerState::Leading:
        case EPeerState::Following:
            return to == EPeerState::Voting || to == EPeerState::Stopped;
        default:
            return false;
    }
}
```

## 使用方法

### 1. 基本类型使用

```cpp
#include <yt/yt/client/election/public.h>

using namespace NYT::NElection;

// 创建选举周期ID
TEpochId epochId = TGuid::Create();

// 设置节点优先级
TPeerPriority myPriority = std::make_pair(100, 50);  // 主优先级100，次优先级50

// 检查节点ID
int peerId = (currentPeerId != InvalidPeerId) ? currentPeerId : -1;
```

### 2. 状态管理

```cpp
class ElectionPeer {
private:
    EPeerState currentState_ = EPeerState::Stopped;
    TEpochId currentEpoch_ = NullEpochId;

public:
    void TransitionToState(EPeerState newState) {
        if (!IsValidStateTransition(currentState_, newState)) {
            throw TErrorException(NYT::TErrorCode(800))
                << "Invalid state transition from " << currentState_
                << " to " << newState;
        }
        currentState_ = newState;
    }

    EPeerState GetCurrentState() const {
        return currentState_;
    }
};
```

### 3. 错误处理

```cpp
try {
    // 执行选举相关操作
    PerformElectionAction();
} catch (const TErrorException& e) {
    switch (e.GetErrorCode()) {
        case NYT::TErrorCode(800):  // InvalidState
            HandleInvalidState(e);
            break;
        case NYT::TErrorCode(801):  // InvalidLeader
            HandleInvalidLeader(e);
            break;
        case NYT::TErrorCode(802):  // InvalidEpoch
            HandleInvalidEpoch(e);
            break;
        default:
            HandleGenericError(e);
            break;
    }
}
```

## 架构设计

### 1. 设计原则
- **一致性保证**: 基于Raft算法的强一致性
- **容错性**: 支持节点故障和网络分区
- **可扩展性**: 支持动态添加和移除节点
- **高性能**: 最小化选举延迟和消息开销

### 2. 状态机模型
```
Stopped -> Voting -> {Leading, Following}
    ^          |          |
    |          v          v
   (restart)  <---------(election timeout)
```

### 3. 优先级机制
- **主优先级**: 基于节点配置和性能
- **次优先级**: 用于打破平局
- **动态调整**: 支持运行时优先级调整

## 性能优化

### 1. 快速选举
- **预投票机制**: 减少无效选举
- **心跳优化**: 降低网络开销
- **批量操作**: 提高选举效率

### 2. 负载均衡
- **领导者转移**: 负载均衡时主动转移领导权
- **区域感知**: 考虑网络拓扑的优先级设置
- **故障预测**: 提前预防节点故障

### 3. 监控指标
```cpp
// 关键性能指标
struct ElectionMetrics {
    i64 ElectionCount;        // 选举次数
    TDuration ElectionTime;   // 平均选举时间
    i64 LeaderChanges;        // 领导者变更次数
    double SuccessRate;       // 选举成功率
    TDuration StateDurations[4]; // 各状态持续时间
};
```

## 最佳实践

### 1. 配置建议
```cpp
// 推荐的选举配置
struct ElectionConfig {
    TDuration ElectionTimeout = TDuration::Seconds(5);      // 选举超时
    TDuration HeartbeatInterval = TDuration::MilliSeconds(500); // 心跳间隔
    int MaxElectionRetries = 3;                             // 最大重试次数
    TDuration LeaderLeaseTimeout = TDuration::Seconds(10);   // 领导者租约
};
```

### 2. 错误处理策略
```cpp
// 渐进式错误处理
void HandleElectionError(const TError& error) {
    if (error.GetErrorCode() == NYT::TErrorCode(801)) { // InvalidLeader
        // 立即重新选举
        ScheduleImmediateElection();
    } else if (error.GetErrorCode() == NYT::TErrorCode(802)) { // InvalidEpoch
        // 延迟重试，避免频繁选举
        ScheduleDelayedElection(TDuration::Seconds(1));
    } else {
        // 通用错误处理
        HandleGenericElectionError(error);
    }
}
```

### 3. 监控和诊断
```cpp
// 详细的日志记录
YT_LOG_INFO("Election state changed (PeerId: %v, OldState: %v, NewState: %v, Epoch: %v)",
    peerId, oldState, newState, epochId);

YT_LOG_WARNING("Election error (PeerId: %v, Error: %v, CurrentState: %v)",
    peerId, error, currentState);
```

## 依赖项

### 内部依赖
- `yt/yt/core/misc/error_code.h` - 错误代码定义
- `library/cpp/yt/misc/enum.h` - 枚举支持
- `library/cpp/yt/misc/guid.h` - GUID 支持
- `library/cpp/yt/string/guid.h` - GUID 字符串转换

### 外部依赖
- 标准库 C++ 运行时
- 系统级原子操作支持
- 网络通信库

## 测试和验证

### 1. 单元测试
- 状态转换测试
- 错误处理测试
- 优先级比较测试

### 2. 集成测试
- 多节点选举测试
- 网络分区测试
- 节点故障测试

### 3. 性能测试
- 选举延迟测试
- 大规模集群测试
- 高负载场景测试

## 扩展指南

### 1. 添加新状态
```cpp
// 在枚举中添加新状态
DEFINE_ENUM(EPeerState,
    (Stopped)
    (Voting)
    (Leading)
    (Following)
    (Recovering)  // 新增恢复状态
);
```

### 2. 扩展错误代码
```cpp
// 添加新的错误类型
YT_DEFINE_ERROR_ENUM(
    ((InvalidState)  (800))
    ((InvalidLeader) (801))
    ((InvalidEpoch)  (802))
    ((NetworkPartition) (803))  // 新增网络分区错误
);
```

## 相关模块

- **Tablet Client**: 使用选举机制进行主副本选举
- **Hydra**: 分布式一致性引擎
- **Scheduler**: 作业调度器的选举
- **Clock Server**: 集群时间同步

## 版本兼容性

- **向后兼容**: 现有错误代码和状态保持稳定
- **扩展性**: 新增状态和错误码向后兼容
- **协议兼容**: 选举协议版本兼容

## 参考文档

- [Raft 一致性算法文档](../../../docs/raft-algorithm.md)
- [分布式选举设计](../../../docs/distributed-election.md)
- [YTsaurus 架构指南](../../../docs/architecture.md)
- [错误处理最佳实践](../../../docs/error-handling.md)

## 贡献指南

在修改此模块时：
1. 保持错误代码的连续性
2. 更新状态转换图
3. 添加充分的测试用例
4. 考虑向后兼容性
5. 更新相关文档