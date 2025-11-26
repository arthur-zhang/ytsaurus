# YTsaurus Query Tracker Client 模块

## 概述

Query Tracker Client 模块是 YTsaurus 查询跟踪系统的客户端接口，用于查询执行状态监控、结果收集和查询管理。

## 核心功能

### 1. 查询跟踪
- **查询监控**: 监控查询执行状态
- **结果收集**: 查询结果收集
- **进度报告**: 查询执行进度报告

### 2. 查询管理
- **查询取消**: 取消正在执行的查询
- **查询列表**: 获取查询列表
- **历史查询**: 查询历史记录

## 使用方法

```cpp
#include <yt/yt/client/query_tracker_client/public.h>

// 创建查询跟踪客户端
auto client = CreateQueryTrackerClient(config);

// 跟踪查询
auto queryId = client->StartQuery("SELECT * FROM `/table`");
auto status = client->GetQueryStatus(queryId);
auto results = client->GetQueryResults(queryId);
```

## 依赖项

### 内部依赖
- `yt/yt/core/misc/public.h` - 核心公共定义

## 相关模块

- **Query Client**: 查询执行
- **Scheduler Client**: 查询调度

## 贡献指南

确保查询状态同步的准确性和实时性。