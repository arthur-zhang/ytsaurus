# Node Tracker Client - 节点跟踪客户端

本模块提供 YTsaurus 集群中节点信息的跟踪和管理功能，包括节点目录、节点描述符、资源统计等核心组件。

## 核心组件

### 1. 节点描述符 (TNodeDescriptor)

`TNodeDescriptor` 类提供了节点的完整网络和位置信息：

```cpp
class TNodeDescriptor {
    // 地址映射：网络 -> host:port
    TAddressMap Addresses_;

    // 位置信息
    std::optional<std::string> Host_;        // 主机名
    std::optional<std::string> Rack_;        // 机架
    std::optional<std::string> DataCenter_; // 数据中心
    std::vector<std::string> Tags_;         // 标签

    // 最后在线时间（不持久化）
    mutable TCopyableAtomic<TCpuInstant> LastSeenTime_;
};
```

主要功能：
- `GetDefaultAddress()` - 获取默认地址
- `GetAddressOrThrow()` - 根据网络偏好获取地址
- `FindAddress()` - 查找指定网络的地址
- `UpdateLastSeenTime()` - 更新最后在线时间

### 2. 节点目录 (TNodeDirectory)

`TNodeDirectory` 是线程安全的节点信息缓存和管理器：

- 维护集群中所有节点的信息
- 支持并发读写访问
- 提供节点查找和过滤功能
- 支持增量更新

### 3. 地址管理

#### 地址类型 (EAddressType)
```cpp
enum EAddressType {
    InternalRpc,     // 内部 RPC 通信
    SkynetHttp,      // Skynet HTTP 服务
    MonitoringHttp,  // 监控 HTTP 服务
};
```

#### 地址映射
- `TAddressMap`：网络到地址的映射
- `TNodeAddressMap`：地址类型到网络地址的映射
- `TNetworkPreferenceList`：网络偏好列表

### 4. 节点标识

```cpp
using TNodeId = ui32;
constexpr TNodeId MaxRealNodeId = (1 << 24) - 128 - 1;  // 最大实际节点ID
constexpr TNodeId InvalidNodeId = 0;                    // 无效节点ID
constexpr TNodeId OffshoreNodeId = (1 << 24) - 1;        // 离岸节点ID

using TChunkLocationIndex = ui32;  // Chunk 位置索引
using THostId = TObjectId;         // 主机ID
using TRackId = TObjectId;         // 机架ID
using TDataCenterId = TObjectId;   // 数据中心ID
```

### 5. 错误处理

```cpp
DEFINE_ERROR_ENUM(
    (NoSuchNode,        1600),  // 节点不存在
    (InvalidState,      1601),  // 无效状态
    (NoSuchNetwork,     1602),  // 网络不存在
    (NoSuchRack,        1603),  // 机架不存在
    (NoSuchDataCenter,  1604),  // 数据中心不存在
);
```

## 使用示例

### 创建节点描述符
```cpp
#include <yt/yt/client/node_tracker_client/node_directory.h>

// 使用默认地址创建
auto descriptor1 = TNodeDescriptor("node1.yandex.net");

// 使用完整信息创建
TAddressMap addresses = {
    {"default", "node1.yandex.net:9012"},
    {"internal", "10.0.0.1:9012"},
    {"external", "185.12.34.56:9012"}
};

auto descriptor2 = TNodeDescriptor(
    addresses,
    "node1-host",        // host
    "rack-1",            // rack
    "dc-west",           // data center
    {"ssd", "fast"}      // tags
);

// 获取地址
auto defaultAddr = descriptor2.GetDefaultAddress();
auto internalAddr = descriptor2.GetAddressOrThrow({"internal", "default"});

// 更新最后在线时间
descriptor2.UpdateLastSeenTime(TInstant::Now());
```

### 节点目录操作
```cpp
#include <yt/yt/client/node_tracker_client/public.h>

// 创建节点目录
auto nodeDirectory = New<TNodeDirectory>();

// 添加节点
nodeDirectory->AddDescriptor(nodeId1, descriptor1);
nodeDirectory->AddDescriptor(nodeId2, descriptor2);

// 查找节点
auto descriptor = nodeDirectory->FindDescriptor(nodeId1);
if (descriptor) {
    // 使用节点信息
    std::cout << "Node address: " << descriptor->GetDefaultAddress() << std::endl;
}

// 根据地址查找节点ID
auto nodeId = nodeDirectory->GetNodeId(descriptor1.GetDefaultAddress());

// 获取所有节点描述符
auto allDescriptors = nodeDirectory->GetAllDescriptors();
```

### 地址辅助函数
```cpp
#include <yt/yt/client/node_tracker_client/helpers.h>

// 获取集群节点路径
auto nodesPath = GetClusterNodesPath();        // //sys/cluster_nodes
auto execNodesPath = GetExecNodesPath();       // //sys/exec_nodes

// 地址查找
auto defaultAddr = FindDefaultAddress(addresses);
auto addr = GetAddressOrThrow(addresses, {"internal", "default"});
```

## 设计原理

### 线程安全设计
1. **读写锁**：使用读写自旋锁保护节点目录
2. **原子操作**：最后在线时间使用原子操作
3. **不可变性**：节点描述符创建后不可变

### 网络优先级
1. **网络偏好**：支持指定网络访问优先级
2. **地址解析**：智能选择最佳网络地址
3. **回退机制**：网络不可用时的回退策略

### 性能优化
1. **缓存机制**：节点信息缓存减少 RPC 调用
2. **增量更新**：只更新变化的节点信息
3. **批量操作**：支持批量添加和更新节点

## 依赖项

- `yt/yt/client/chunk_client/chunk_replica.h` - Chunk 副本信息
- `yt/yt/core/actions/future.h` - 异步操作支持
- `yt/yt/core/rpc/helpers.h` - RPC 辅助功能
- `yt/yt/core/yson/public.h` - YSON 序列化
- `yt/yt/core/misc/property.h` - 属性系统
- `yt/yt/core/ypath/public.h` - YPath 操作
- `library/cpp/yt/threading/rw_spin_lock.h` - 读写自旋锁

## 注意事项

1. **节点ID范围**：实际节点ID必须在 [1, MaxRealNodeId] 范围内
2. **网络配置**：确保网络配置正确，地址可达
3. **并发访问**：节点目录是线程安全的，可并发使用
4. **持久化**：最后在线时间不会被持久化
5. **地址格式**：地址必须是完整的 host:port 格式

## 相关模块

- `yt/yt/client/chunk_client` - Chunk 客户端（使用节点信息进行数据定位）
- `yt/yt/core/rpc` - RPC 通信（使用节点地址进行连接）
- `yt/yt/server/node_tracker_server` - 节点跟踪服务端实现