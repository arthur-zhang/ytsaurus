# YTsaurus Scheduler Client 模块

## 概述

Scheduler Client 模块是 YTsaurus 作业调度系统的客户端接口，用于提交作业、监控作业状态和管理作业执行。

## 核心功能

### 1. 作业管理
- **作业提交**: 提交各类计算作业
- **作业监控**: 监控作业执行状态
- **作业控制**: 暂停、恢复、中止作业

### 2. 操作管理
- **操作创建**: 创建 MapReduce、Vanilla 等操作
- **状态查询**: 查询操作执行状态
- **结果获取**: 获取操作执行结果

## 使用方法

```cpp
#include <yt/yt/client/scheduler/public.h>

// 创建调度器客户端
auto client = CreateSchedulerClient(config);

// 提交操作
auto operation = client->StartOperation(
    "vanilla",
    BuildYsonNodeFluently()
        .BeginMap()
            .Item("spec").BeginMap()
                .Item("tasks").BeginList()
                    .Item().BeginMap()
                        .Item("job_count").Value(1)
                        .Item("command").Value("echo 'Hello World'")
                    .EndMap()
                .EndList()
            .EndMap()
        .EndMap());
```

## 依赖项

### 内部依赖
- `yt/yt/core/misc/public.h` - 核心公共定义

## 相关模块

- **Job Tracker Client**: 作业跟踪
- **Driver Client**: 命令行驱动

## 贡献指南

确保作业调度的公平性和效率。