# YTsaurus Tablet Client 模块

## 概述

Tablet Client 模块是 YTsaurus Tablet（表分区）系统的客户端接口，提供分布式表分区管理、数据分区操作和 Tablet 节点通信功能。

## 核心功能

### 1. Tablet 管理
- **Tablet 操作**: Tablet 的创建、删除、分割
- **分区管理**: 数据分区管理和调度
- **负载均衡**: Tablet 负载均衡

### 2. 数据操作
- **分区读写**: 特定 Tablet 的数据读写
- **事务支持**: Tablet 级事务操作
- **一致性控制**: 分布式一致性保证

## 使用方法

```cpp
#include <yt/yt/client/tablet_client/public.h>

// 创建 Tablet 客户端
auto client = CreateTabletClient(config);

// 获取 Tablet 信息
auto tabletInfo = client->GetTabletInfo(tabletId);

// 读写 Tablet 数据
auto result = client->ReadTabletRows(tabletId, rowRange);
```

## 依赖项

### 内部依赖
- `yt/yt/core/misc/public.h` - 核心公共定义

## 相关模块

- **Table Client**: 表数据操作
- **Hive Client**: Tablet 协调

## 贡献指南

确保 Tablet 分布的一致性和数据可靠性。