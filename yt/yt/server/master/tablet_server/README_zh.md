# Tablet Server 组件

## 概述

Tablet Server 是 YTsaurus 系统中管理 Tablet（表分片）的核心组件。Tablet 是动态表的分片单元，Tablet Server 负责 Tablet 的创建、分布、负载均衡、故障恢复等功能。它是实现 OLTP 场景下高性能数据存储和查询的基础设施。

## 核心功能

- **Tablet 管理**: 管理 Tablet 的生命周期
- **分片策略**: 实现表的分片策略
- **负载均衡**: 在 Tablet Cell 间分配 Tablet
- **故障恢复**: 处理 Tablet 的故障恢复
- **数据迁移**: 管理数据的在线迁移

## 关键组件

### Tablet Manager (tablet_manager.h/cpp)
- 核心 Tablet 管理器
- 管理所有 Tablet
- 处理 Tablet 的调度

### Tablet (tablet.h/cpp)
- Tablet 对象实现
- 存储 Tablet 元数据
- 管理 Tablet 状态

### Tablet Cell (tablet_cell.h/cpp)
- Tablet Cell 管理
- 管理 Tablet Cell 的生命周期

## 使用方法

```cpp
// 创建 Tablet
auto tablet = tabletManager->CreateTablet(
    table,
    pivotKeys,
    cellBundle
);

// 分配 Tablet 到 Cell
tabletManager->AssignTablet(
    tablet,
    tabletCell
);

// 重新平衡
tabletManager->RebalanceTablets(cellBundle);
```

## 配置参数

```yaml
tablet_server:
  enable: true
  default_tablet_cell_count: 3
  rebalance_period: 60s
  health_check_timeout: 30s
```

## 相关文档
- [Tablet 架构设计](../../../docs/tablet-architecture.md)
- [动态表指南](../../../docs/dynamic-tables.md)