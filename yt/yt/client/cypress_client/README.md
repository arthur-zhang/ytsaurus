# YTsaurus Cypress Client 模块

## 概述

Cypress Client 模块是 YTsaurus 分布式文件系统的客户端接口，提供了对 Cypress 元数据树的核心操作支持。Cypress 是 YTsaurus 的统一命名空间和元数据管理系统，类似于传统文件系统的目录结构，但功能更为强大。

## 核心功能

### 1. 对象标识系统
提供各种对象的唯一标识符定义：
- **TNodeId**: 节点标识符
- **TLockId**: 锁标识符
- **TCypressShardId**: Cypress 分片标识符
- **TVersionedNodeId**: 版本化节点标识符

### 2. 锁管理机制
定义了完整的锁类型和状态系统，支持并发访问控制。

### 3. 错误分类
提供专门的错误代码，用于锁冲突和事务管理相关的错误处理。

## 主要组件详解

### 对象标识符类型

```cpp
using TNodeId = TObjectId;              // 节点ID
using TLockId = TObjectId;              // 锁ID
using TCypressShardId = TObjectId;      // 分片ID
using TVersionedNodeId = TVersionedObjectId;  // 版本化节点ID

extern const TLockId NullLockId;        // 空锁ID常量
```

### 锁模式 (ELockMode)

定义了四种锁模式，按强度递增排序：

#### None (0) - 无锁
- 不对资源进行任何锁定
- 允许并发读写操作
- 适用于读一致性要求不高的场景

#### Snapshot (1) - 快照锁
- 提供读取时的一致性快照
- 防止在读取期间数据被修改
- 适用于一致性读取操作

#### Shared (2) - 共享锁
- 允许多个事务同时读取
- 阻止写操作
- 适用于多读无写的场景

#### Exclusive (3) - 排他锁
- 独占访问权限
- 阻止所有其他读写操作
- 适用于写操作和结构变更

### 锁状态 (ELockState)

#### Pending (0) - 等待状态
- 锁请求已提交但尚未获得
- 可能存在锁冲突需要等待
- 系统会自动处理锁获取

#### Acquired (1) - 已获取状态
- 锁已成功获得
- 可以进行相应的操作
- 会在事务结束时自动释放

## 锁冲突处理

### 错误类型定义

```cpp
YT_DEFINE_ERROR_ENUM(
    ((SameTransactionLockConflict)         (400))  // 同事务内锁冲突
    ((DescendantTransactionLockConflict)   (401))  // 子事务锁冲突
    ((ConcurrentTransactionLockConflict)   (402))  // 并发事务锁冲突
    ((PendingLockConflict)                 (403))  // 等待锁冲突
    ((LockDestroyed)                       (404))  // 锁已被销毁
    ((TooManyLocksOnTransaction)           (405))  // 事务锁数量超限
);
```

### 冲突解决策略

1. **同事务锁冲突** (SameTransactionLockConflict)
   - 同一事务内尝试获取不兼容的锁
   - 解决方案：重新设计事务逻辑或使用嵌套事务

2. **子事务锁冲突** (DescendantTransactionLockConflict)
   - 父子事务之间的锁冲突
   - 解决方案：调整事务层次结构

3. **并发事务锁冲突** (ConcurrentTransactionLockConflict)
   - 不同事务之间的锁冲突
   - 解决方案：重试、调整锁模式或事务顺序

4. **等待锁冲突** (PendingLockConflict)
   - 锁等待超时或中断
   - 解决方案：增加超时时间或优化锁获取顺序

## 使用方法

### 1. 基本类型使用

```cpp
#include <yt/yt/client/cypress_client/public.h>

using namespace NYT::NCypressClient;

// 创建节点ID
TNodeId nodeId = GetObjectId(nodePath);

// 设置锁模式
ELockMode lockMode = ELockMode::Shared;
```

### 2. 锁操作示例

```cpp
// 请求共享锁
auto lockRequest = TLockRequest()
    .Path("/path/to/resource")
    .Mode(ELockMode::Shared)
    .TransactionId(transactionId);

// 检查锁状态
if (lockState == ELockState::Pending) {
    // 处理等待状态
    WaitForLockAcquisition(lockRequest);
}
```

### 3. 错误处理

```cpp
try {
    // 执行需要锁的操作
    LockResource(path, ELockMode::Exclusive);
} catch (const TSameTransactionLockConflict& e) {
    // 处理同事务锁冲突
    HandleSameTransactionLockConflict(e);
} catch (const TConcurrentTransactionLockConflict& e) {
    // 处理并发事务锁冲突
    HandleConcurrentLockConflict(e);
}
```

## 架构设计

### 1. 分层设计
- **Object Client 层**: 基础对象管理
- **Cypress Client 层**: Cypress 特定功能
- **API 层**: 高级操作接口

### 2. 类型安全
- 使用强类型枚举避免魔法数字
- 类型别名提高代码可读性
- 编译时类型检查

### 3. 扩展性
- 枚举设计便于添加新的锁类型和状态
- 错误代码系统可扩展
- 向后兼容的 API 设计

## 性能优化

### 1. 内存效率
- 使用固定大小的整数类型
- 避免动态内存分配
- 零拷贝设计原则

### 2. 锁获取优化
- 快速路径优化常见场景
- 锁升级机制减少重试
- 异步锁获取减少阻塞

### 3. 缓存机制
- 锁信息缓存减少 RPC 调用
- 预取策略提高命中率

## 监控和诊断

### 关键指标
- 锁获取延迟
- 锁冲突频率
- 事务锁数量
- 锁等待时间

### 诊断工具
```cpp
// 锁状态查询
auto lockInfo = GetLockInfo(lockId);
YT_LOG_INFO("Lock status (LockId: %v, State: %v, Mode: %v)",
    lockId, lockInfo.State, lockInfo.Mode);

// 冲突分析
auto conflicts = AnalyzeLockConflicts(transactionId);
for (const auto& conflict : conflicts) {
    YT_LOG_WARNING("Lock conflict detected: %v", conflict);
}
```

## 最佳实践

### 1. 锁使用原则
- **最小锁范围**: 尽可能缩小锁定的资源范围
- **最短锁时间**: 快速完成操作后及时释放锁
- **合理锁强度**: 根据需要选择合适的锁模式

### 2. 事务设计
- **短事务**: 保持事务简短高效
- **一致顺序**: 按固定顺序获取锁避免死锁
- **错误处理**: 完善的异常处理和重试机制

### 3. 性能调优
- **批量操作**: 减少锁获取次数
- **异步处理**: 使用异步锁获取
- **监控预警**: 设置合理的性能阈值

## 依赖项

### 内部依赖
- `yt/yt/client/object_client/public.h` - 对象客户端接口
- `yt/yt/core/misc/public.h` - 核心公共定义

### 外部依赖
- 标准库 C++ 运行时
- 系统级原子操作支持

## 扩展指南

### 添加新锁模式
1. 在 `ELockMode` 枚举中添加新值
2. 更新兼容性矩阵
3. 实现相应的获取逻辑
4. 添加测试用例

### 错误代码扩展
1. 定义新的错误类型
2. 实现错误处理逻辑
3. 更新错误映射表
4. 文档化错误场景

## 相关模块

- **Object Client**: 基础对象管理
- **Transaction Client**: 事务管理
- **Table Client**: 表数据操作
- **API**: 高级操作接口

## 版本兼容性

该模块保持严格的向后兼容性：
- 现有枚举值保持不变
- 新功能通过扩展实现
- API 稳定性保证

## 参考文档

- [YTsaurus Cypress 系统设计](../../../docs/cypress.md)
- [分布式锁管理文档](../../../docs/locks.md)
- [事务系统指南](../../../docs/transactions.md)
- [错误处理最佳实践](../../../docs/error-handling.md)

## 贡献指南

在修改此模块时：
1. 保持 API 向后兼容
2. 添加充分的测试覆盖
3. 更新相关文档
4. 考虑性能影响