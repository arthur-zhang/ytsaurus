# Node Tracker Server 组件

## 概述

Node Tracker Server 是 YTsaurus 系统中负责跟踪和管理集群中所有节点的组件。它维护节点的状态信息、资源使用情况、网络拓扑等关键数据，是集群资源管理的基础设施。Node Tracker 负责节点的注册、健康检查、故障检测和恢复等功能。

## 核心功能

- **节点注册**: 自动发现和注册新节点
- **健康检查**: 定期检查节点健康状态
- **资源监控**: 跟踪节点资源使用情况
- **故障检测**: 快速检测节点故障
- **拓扑管理**: 维护集群网络拓扑

## 关键组件

### Node Tracker (node_tracker.h/cpp)
- 核心节点跟踪器实现
- 管理所有节点的生命周期
- 处理节点状态更新和事件

### Data Center (data_center.h/cpp)
- 数据中心抽象和实现
- 管理数据中心级别的拓扑

## 使用方法

```cpp
// 注册节点
nodeTracker->RegisterNode(nodeDescriptor);

// 检查节点状态
auto status = nodeTracker->GetNodeStatus(nodeId);

// 获取集群拓扑
auto topology = nodeTracker->GetClusterTopology();
```

## 配置参数

```yaml
node_tracker:
  heartbeat_interval: 10s
  failure_timeout: 60s
  health_check_period: 30s
```

## 相关文档
- [集群管理指南](../../../docs/cluster-management.md)
- [节点管理文档](../../../docs/node-management.md)