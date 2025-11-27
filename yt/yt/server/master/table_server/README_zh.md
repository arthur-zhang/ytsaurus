# Table Server 组件

## 概述

Table Server 是 YTsaurus 系统中管理表结构（Table）的核心组件。它负责表的元数据管理、Schema 管理、动态表和静态表的管理、数据分布策略等功能。Table Server 构建在 Cypress Server 之上，为上层应用提供了表级别的抽象和管理能力。

## 核心功能

- **表管理**: 管理表的创建、删除和修改
- **Schema 管理**: 管理表的结构定义
- **数据分布**: 管理数据的分布策略
- **统计信息**: 收集和维护表的统计信息
- **索引管理**: 管理表的二级索引

## 关键组件

### Table Manager (table_manager.h/cpp)
- 核心表管理器
- 管理所有表的元数据
- 处理表的生命周期

### Table Node (table_node.h/cpp)
- 表节点实现
- 继承自 Cypress 节点
- 存储表的元数据

### Schema Handler (schema_handler.h/cpp)
- Schema 处理器
- 管理 Schema 的验证和更新

## 使用方法

```cpp
// 创建表
auto tableNode = tableManager->CreateTable(
    path,
    schema,
    options
);

// 设置分布策略
tableNode->SetMountConfig(mountConfig);

// 获取统计信息
auto statistics = tableNode->GetTableStatistics();
```

## 配置参数

```yaml
table_server:
  enable_dynamic_tables: true
  enable_static_tables: true
  max_schema_version: 1000
  statistics_update_period: 60s
```

## 相关文档
- [表设计指南](../../../docs/table-design.md)
- [Schema 管理](../../../docs/schema-management.md)