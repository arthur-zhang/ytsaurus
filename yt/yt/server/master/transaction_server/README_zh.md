# Transaction Server 组件

## 概述

Transaction Server 是 YTsaurus 系统中实现分布式事务管理的核心组件。它提供了 ACID 特性的分布式事务支持，包括事务的开始、提交、回滚、嵌套事务、快照隔离等功能。Transaction Server 是保证系统数据一致性和并发控制的基础设施。

## 核心功能

- **事务管理**: 管理事务的完整生命周期
- **ACID 支持**: 提供完整的 ACID 特性
- **嵌套事务**: 支持嵌套和子事务
- **快照隔离**: 实现快照隔离级别
- **并发控制**: 乐观和悲观并发控制
- **死锁检测**: 自动检测和解决死锁

## 关键组件

### Transaction Manager (transaction_manager.h/cpp)
- 核心事务管理器
- 管理所有事务
- 处理事务的协调

### Transaction (transaction.h/cpp)
- 事务对象实现
- 维护事务状态
- 管理锁和资源

### Transaction Supervisor (transaction_supervisor.h/cpp)
- 事务监督器
- 处理两阶段提交
- 协调分布式事务

## 使用方法

```cpp
// 开始事务
auto transaction = transactionManager->StartTransaction();

// 嵌套事务
auto childTransaction = transactionManager->StartTransaction(
    transaction
);

// 提交事务
transactionManager->CommitTransaction(transaction);

// 回滚事务
transactionManager->AbortTransaction(transaction);
```

## 配置参数

```yaml
transaction_server:
  enable: true
  default_timeout: 60s
  max_nested_depth: 10
  enable_deadlock_detection: true
```

## 相关文档
- [事务管理指南](../../../docs/transactions.md)
- [并发控制文档](../../../docs/concurrency-control.md)