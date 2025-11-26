# YTsaurus Queue Client 模块

## 概述

Queue Client 模块是 YTsaurus 队列系统的客户端接口，提供分布式消息队列功能，支持消息的生产、消费和管理。

## 核心功能

### 1. 队列操作
- **消息生产**: 向队列发送消息
- **消息消费**: 从队列消费消息
- **队列管理**: 队列创建和配置

### 2. 消息处理
- **批量操作**: 批量消息处理
- **事务消息**: 支持事务性消息
- **消息过滤**: 基于条件的消息过滤

## 使用方法

```cpp
#include <yt/yt/client/queue_client/public.h>

// 创建队列客户端
auto client = CreateQueueClient(config);

// 发送消息
client->PushMessage("/queue/path", message);

// 消费消息
auto messages = client->PullMessages("/queue/path", 10);
```

## 依赖项

### 内部依赖
- `yt/yt/core/misc/public.h` - 核心公共定义

## 相关模块

- **Table Client**: 队列数据存储
- **Transaction Client**: 队列事务

## 贡献指南

确保消息传递的可靠性和顺序性。