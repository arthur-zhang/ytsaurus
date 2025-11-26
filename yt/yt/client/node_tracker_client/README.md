# YTsaurus Node Tracker Client 模块

## 概述

Node Tracker Client 模块是 YTsaurus 节点跟踪系统的客户端接口，负责管理和监控集群中的计算节点。该模块提供节点发现、状态监控、资源管理和节点调度等核心功能，是集群管理的重要组成部分。

## 核心功能

### 1. 节点目录管理
- **节点发现**: 自动发现和注册集群节点
- **状态监控**: 实时监控节点健康状态
- **资源跟踪**: 跟踪节点资源使用情况
- **地址解析**: 节点网络地址解析和管理

### 2. 节点状态管理
- **在线状态**: 监控节点在线/离线状态
- **负载监控**: 跟踪节点负载和性能指标
- **健康检查**: 定期执行节点健康检查
- **故障检测**: 快速检测节点故障

## 主要组件

### 1. 节点目录 (node_directory.h/cpp)
```cpp
class TNodeDirectory {
public:
    // 节点管理
    void AddNode(const TNodeDescriptor& descriptor);
    void RemoveNode(const TNodeId& nodeId);
    TNodeDescriptorPtr FindNode(const TNodeId& nodeId);

    // 查询功能
    std::vector<TNodeDescriptorPtr> GetNodesByAddress(const TString& address);
    std::vector<TNodeDescriptorPtr> GetHealthyNodes();
    std::vector<TNodeDescriptorPtr> GetNodesBy Rack(const TString& rack);
};
```

### 2. 辅助函数 (helpers.h/cpp)
```cpp
class TNodeTrackerHelpers {
public:
    // 节点选择策略
    static TNodeDescriptorPtr SelectBestNode(
        const std::vector<TNodeDescriptorPtr>& candidates,
        ENodeSelectionStrategy strategy);

    // 负载评估
    static double EvaluateNodeLoad(const TNodeDescriptor& node);
    static bool IsNodeHealthy(const TNodeDescriptor& node);
};
```

### 3. 节点描述符
```cpp
struct TNodeDescriptor {
    TNodeId Id;
    TString Address;
    TString Rack;
    TString DataCenter;
    ENodeState State;
    TNodeResources Resources;
    TNodeStatistics Statistics;
    TInstant LastHeartbeat;
};
```

## 使用方法

### 1. 基本节点目录使用

```cpp
#include <yt/yt/client/node_tracker_client/public.h>
#include <yt/yt/client/node_tracker_client/node_directory.h>

using namespace NYT::NNodeTrackerClient;

// 创建节点目录
auto nodeDirectory = std::make_unique<TNodeDirectory>();

// 添加节点
TNodeDescriptor node1;
node1.Id = TNodeId::Create();
node1.Address = "node1.ytsaurus.net:9013";
node1.Rack = "rack-a";
node1.DataCenter = "dc-east";
node1.State = ENodeState::Online;

nodeDirectory->AddNode(node1);

// 查找节点
auto foundNode = nodeDirectory->FindNode(node1.Id);
if (foundNode) {
    YT_LOG_INFO("Found node: %v", foundNode->Address);
}

// 获取健康节点
auto healthyNodes = nodeDirectory->GetHealthyNodes();
```

### 2. 智能节点选择

```cpp
// 节点选择策略
class NodeSelector {
public:
    TNodeDescriptorPtr SelectNodeForJob(
        const TJobSpec& jobSpec,
        const TNodeDirectory& nodeDirectory) {

        auto candidates = nodeDirectory.GetHealthyNodes();
        return TNodeTrackerHelpers::SelectBestNode(
            candidates,
            ENodeSelectionStrategy::LeastLoaded);
    }

    std::vector<TNodeDescriptorPtr> SelectNodesForReplication(
        int replicationFactor,
        const TNodeDirectory& nodeDirectory) {

        auto candidates = nodeDirectory.GetHealthyNodes();
        std::vector<TNodeDescriptorPtr> selected;

        for (const auto& candidate : candidates) {
            if (ShouldSelectNode(candidate, selected)) {
                selected.push_back(candidate);
                if (selected.size() >= replicationFactor) {
                    break;
                }
            }
        }

        return selected;
    }

private:
    bool ShouldSelectNode(
        const TNodeDescriptorPtr& node,
        const std::vector<TNodeDescriptorPtr>& alreadySelected) {

        // 避免同机架
        for (const auto& selected : alreadySelected) {
            if (selected->Rack == node->Rack) {
                return false;
            }
        }

        // 检查资源可用性
        return node->Resources.AvailableCpuCores > MinRequiredCpuCores &&
               node->Resources.AvailableMemory > MinRequiredMemory;
    }
};
```

### 3. 节点监控

```cpp
// 节点健康监控
class NodeHealthMonitor {
private:
    TNodeDirectory* nodeDirectory_;
    std::thread monitoringThread_;
    std::atomic<bool> running_;

public:
    void StartMonitoring() {
        running_ = true;
        monitoringThread_ = std::thread(&NodeHealthMonitor::MonitoringLoop, this);
    }

    void StopMonitoring() {
        running_ = false;
        if (monitoringThread_.joinable()) {
            monitoringThread_.join();
        }
    }

private:
    void MonitoringLoop() {
        while (running_) {
            CheckAllNodesHealth();
            TDelay::Sleep(TDuration::Seconds(30));
        }
    }

    void CheckAllNodesHealth() {
        auto nodes = nodeDirectory_->GetAllNodes();

        for (const auto& node : nodes) {
            auto isHealthy = CheckNodeHealth(node);
            if (!isHealthy) {
                MarkNodeUnhealthy(node->Id);
            }
        }
    }

    bool CheckNodeHealth(const TNodeDescriptorPtr& node) {
        try {
            // 执行健康检查
            auto client = CreateClientForNode(node);
            auto startTime = TInstant::Now();

            auto result = WaitFor(client->PingNode())
                .WithTimeout(TDuration::Seconds(5));

            if (result.IsOK()) {
                node->LastHeartbeat = startTime;
                return true;
            }
        } catch (const std::exception& e) {
            YT_LOG_DEBUG("Node health check failed (Node: %v, Error: %v)",
                node->Address, e.what());
        }

        return false;
    }
};
```

### 4. 负载均衡

```cpp
// 负载均衡器
class NodeLoadBalancer {
public:
    TNodeDescriptorPtr SelectLeastLoadedNode(
        const std::vector<TNodeDescriptorPtr>& candidates) {

        TNodeDescriptorPtr bestNode = nullptr;
        double minLoad = std::numeric_limits<double>::max();

        for (const auto& node : candidates) {
            double load = CalculateNodeLoad(node);
            if (load < minLoad && IsNodeSuitable(node)) {
                minLoad = load;
                bestNode = node;
            }
        }

        return bestNode;
    }

    std::vector<TNodeDescriptorPtr> DistributeLoad(
        const std::vector<TJobSpec>& jobs,
        const TNodeDirectory& nodeDirectory) {

        std::vector<TNodeDescriptorPtr> assignments;
        auto availableNodes = nodeDirectory.GetHealthyNodes();

        for (const auto& job : jobs) {
            auto node = SelectBestNodeForJob(job, availableNodes);
            if (node) {
                assignments.push_back(node);
                UpdateNodeLoad(node, job);
            }
        }

        return assignments;
    }

private:
    double CalculateNodeLoad(const TNodeDescriptorPtr& node) {
        // 综合负载计算
        double cpuLoad = static_cast<double>(node->Resources.UsedCpuCores) /
                        node->Resources.TotalCpuCores;
        double memoryLoad = static_cast<double>(node->Resources.UsedMemory) /
                           node->Resources.TotalMemory;
        double diskLoad = static_cast<double>(node->Resources.UsedDiskSpace) /
                         node->Resources.TotalDiskSpace;

        return 0.4 * cpuLoad + 0.3 * memoryLoad + 0.3 * diskLoad;
    }
};
```

## 性能优化

### 1. 缓存机制
- **节点信息缓存**: 缓存节点描述符信息
- **地址解析缓存**: 缓存网络地址解析结果
- **健康状态缓存**: 缓存节点健康检查结果

### 2. 并发优化
- **读写锁**: 支持并发读取的安全更新
- **原子操作**: 使用原子操作保证线程安全
- **无锁数据结构**: 高性能的无锁查询

### 3. 批量操作
- **批量查询**: 批量查询多个节点状态
- **批量更新**: 批量更新节点信息
- **异步处理**: 异步执行耗时操作

## 监控指标

```cpp
struct NodeTrackerMetrics {
    std::atomic<i64> TotalNodes{0};
    std::atomic<i64> OnlineNodes{0};
    std::atomic<i64> OfflineNodes{0};
    std::atomic<i64> FailedHealthChecks{0};
    TDuration AverageHealthCheckTime;
    std::unordered_map<TString, std::atomic<i64>> NodesByRack;
    std::unordered_map<TString, std::atomic<i64>> NodesByDataCenter;
};
```

## 最佳实践

### 1. 节点选择策略

```cpp
enum class ENodeSelectionStrategy {
    RoundRobin,           // 轮询
    LeastLoaded,          // 最少负载
    RackAware,            // 机架感知
    DataCenterAware,      // 数据中心感知
    Random                // 随机选择
};
```

### 2. 故障处理

```cpp
// 节点故障处理
class NodeFailureHandler {
public:
    void HandleNodeFailure(const TNodeId& nodeId) {
        auto node = nodeDirectory_->FindNode(nodeId);
        if (!node) return;

        // 标记节点为不可用
        node->State = ENodeState::Unavailable;

        // 重新调度节点上的作业
        RescheduleNodeJobs(nodeId);

        // 通知监控系统
        AlertMonitoringSystem(node);

        // 尝试恢复节点
        ScheduleNodeRecovery(nodeId);
    }
};
```

## 依赖项

### 内部依赖
- `yt/yt/core/misc/public.h` - 核心公共定义

### 外部依赖
- 网络通信库
- 线程库
- 时间管理库

## 相关模块

- **Scheduler Client**: 作业调度
- **Object Client**: 对象存储
- **Chunk Client**: 分片管理

## 参考文档

- [YTsaurus 集群管理](../../../docs/cluster-management.md)
- [节点监控指南](../../../docs/node-monitoring.md)
- [负载均衡策略](../../../docs/load-balancing.md)

## 贡献指南

在修改此模块时：
1. 确保线程安全的数据结构
2. 优化大规模集群的性能
3. 添加充分的并发测试
4. 考虑网络分区和故障场景
5. 保持向后兼容性