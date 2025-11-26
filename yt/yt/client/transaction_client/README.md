# YTsaurus Transaction Client 模块

## 概述

Transaction Client 模块是 YTsaurus 分布式事务系统的客户端接口，提供 ACID 事务的完整支持。该模块实现了多版本并发控制（MVCC）、乐观并发控制、分布式两阶段提交等核心事务功能。

## 核心功能

### 1. 事务管理
- **事务创建**: 创建和管理事务对象
- **事务提交**: 原子性提交事务
- **事务回滚**: 回滚未提交的事务
- **嵌套事务**: 支持嵌套事务

### 2. 并发控制
- **快照隔离**: MVCC 快照隔离
- **锁机制**: 精细的锁管理
- **冲突检测**: 自动冲突检测和解决
- **死锁检测**: 死锁检测和解除

### 3. 时间戳管理
- **全局时间戳**: 全局唯一时间戳
- **事务时间戳**: 事务开始和提交时间戳
- **版本控制**: 多版本数据管理

## 使用方法

```cpp
#include <yt/yt/client/transaction_client/public.h>

using namespace NYT::NTransactionClient;

// 开始事务
auto client = CreateClient(config);
auto transaction = client->StartTransaction(ETransactionType::Master);

// 在事务中执行操作
transaction->CreateNode("/path/to/node", EObjectType::MapNode);

// 提交事务
transaction->Commit();

// 或者回滚
transaction->Abort();
```

## 事务类型

```cpp
DEFINE_ENUM(ETransactionType,
    (Master)      // 主事务（写事务）
    (Timestamp)   // 时间戳事务（只读事务）
    (Prerequisited) // 前置条件事务
);
```

## 依赖项

### 内部依赖
- `yt/yt/core/misc/public.h` - 核心公共定义

### 外部依赖
- 标准库 C++ 运行时

## 相关模块

- **Table Client**: 表事务操作
- **Cypress Client**: Cypress 事务

## 贡献指南

在修改此模块时：
1. 确保 ACID 特性的正确实现
2. 优化事务性能
3. 添加充分的并发测试
4. 保持向后兼容性