# Sequoia Server 组件

## 概述

Sequoia Server 是 YTsaurus 系统中实现多 Master Cell 协调的组件。它负责协调多个 Master Cell 之间的数据一致性、负载均衡、故障转移等功能，是构建大规模高可用集群的关键组件。

## 核心功能

- **多 Cell 协调**: 协调多个 Master Cell 的工作
- **数据一致性**: 保证跨 Cell 的数据一致性
- **负载均衡**: 在 Cell 间分配负载
- **故障转移**: 处理 Cell 级别的故障转移
- **元数据同步**: 同步 Cell 间的元数据

## 关键组件

### Sequoia Manager (sequoia_manager.h/cpp)
- 核心协调管理器
- 处理 Cell 间的协调
- 维护全局一致性

### Sequoia Cell (sequoia_cell.h/cpp)
- Sequoia Cell 抽象
- 管理 Cell 的状态

## 使用方法

```cpp
// 创建 Sequoia 配置
auto config = New<TSequoiaConfig>();
config->SetCellIds(cellIds);
config->SetReplicationFactor(3);

// 初始化 Sequoia Manager
auto sequoiaManager = CreateSequoiaManager(
    bootstrap,
    config
);

// 启动协调
sequoiaManager->Start();
```

## 配置参数

```yaml
sequoia_server:
  enable: true
  coordination_timeout: 30s
  replication_factor: 3
  sync_period: 10s
```

## 相关文档
- [多 Master 架构](../../../docs/multi-master.md)
- [Sequoia 设计文档](../../../docs/sequoia-design.md)