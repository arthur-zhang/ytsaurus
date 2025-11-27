# Scheduler Pool Server 组件

## 概述

Scheduler Pool Server 是 YTsaurus 系统中管理调度池（Scheduler Pool）的组件。调度池用于隔离不同用户或业务的作业，提供资源隔离、优先级管理、配额控制等功能。Scheduler Pool Server 负责创建、配置和管理这些调度池。

## 核心功能

- **池管理**: 创建和管理调度池
- **资源隔离**: 实现调度池间的资源隔离
- **配额控制**: 管理调度池的资源配额
- **优先级调度**: 支持基于优先级的调度
- **公平调度**: 实现公平的资源共享

## 关键组件

### Scheduler Pool (scheduler_pool.h/cpp)
- 调度池的核心实现
- 管理池的配置和状态
- 处理资源分配请求

## 使用方法

```cpp
// 创建调度池
auto pool = schedulerPoolManager->CreatePool(
    poolName,
    config
);

// 设置资源配额
pool->SetResourceQuota(quota);

// 分配资源
auto allocation = pool->AllocateResources(request);
```

## 配置参数

```yaml
scheduler_pools:
  default:
    resource_quota:
      cpu: 100
      memory: 100GB
    priority: 0

  production:
    resource_quota:
      cpu: 1000
      memory: 1TB
    priority: 100
    fair_share: true
```

## 相关文档
- [调度器指南](../../../docs/scheduler-guide.md)
- [资源管理文档](../../../docs/resource-management.md)