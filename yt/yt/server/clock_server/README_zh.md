# Clock Server - 集群时钟服务

## 概述

Clock Server（集群时钟服务）是 YTsaurus 分布式系统中的核心时间服务组件。它为整个集群提供全局一致、单调递增的时间戳服务，确保分布式事务的一致性和事件的有序性。该服务基于分布式共识算法实现高可用性和容错能力。

## 核心功能

### 1. 全局时间戳管理
- **单调递增时间戳** - 保证时间戳严格单调递增
- **分布式一致性** - 确保所有节点看到相同的时间戳序列
- **高精度时钟** - 提供微秒级精度的时间戳
- **时间窗口管理** - 管理时间戳分配窗口

### 2. 事务时间戳分配
- **事务开始时间** - 为分布式事务分配开始时间戳
- **提交时间戳** - 为事务提交确定时间戳
- **冲突检测** - 基于时间戳检测事务冲突
- **MVCC 支持** - 支持多版本并发控制

### 3. 时钟同步
- **NTP 集成** - 与外部时间源同步
- **时钟漂移校正** - 自动校正节点间时钟差异
- **闰秒处理** - 正确处理闰秒情况
- **时钟回退保护** - 防止时钟回退导致的问题

### 4. 高可用性
- **主备切换** - 支持主备自动切换
- **故障恢复** - 快速从故障中恢复
- **数据持久化** - 持久化保存时间戳状态
- **分布式共识** - 基于 Raft 算法实现一致性

## 架构设计

### 核心组件

#### 1. Clock Automaton（时钟自动机）
```cpp
class TClockAutomaton : public TRefCounted
{
public:
    // 状态管理
    void Initialize();
    void Start();
    void Stop();

    // 时间戳操作
    TTimestamp GenerateTimestamp();
    void AdvanceTimestamp(TTimestamp timestamp);
};
```
负责维护时钟状态和处理时间戳生成请求。

#### 2. Hydra Facade（Hydra 门面）
```cpp
class THydraFacade : public TRefCounted
{
public:
    // Hydra 管理
    void InitializeHydra();
    IHydraManagerPtr GetHydraManager();
    IHydraInstancePtr GetHydraInstance();
};
```
提供与 YTsaurus Hydra 分布式一致性框架的集成。

#### 3. Bootstrap（启动器）
```cpp
class TBootstrap : public TRefCounted
{
public:
    TBootstrap(TClusterClockBootstrapConfigPtr config);

    void Run();

    // 组件访问
    IHydraManagerPtr GetHydraManager();
    TClockAutomatonPtr GetAutomaton();
};
```
管理服务的生命周期和组件初始化。

#### 4. Timestamp Manager（时间戳管理器）
- 管理时间戳分配窗口
- 处理批量时间戳请求
- 优化时间戳分配性能

### 队列系统

服务使用多个优先级队列处理不同类型的请求：

```cpp
enum class EAutomatonThreadQueue
{
    Default,         // 默认操作队列
    Periodic,        // 定期任务队列
    Mutation,        // 变更操作队列
    TimestampManager // 时间戳管理队列
};
```

## 实现原理

### 时间戳生成算法

1. **窗口预分配** - 预先分配时间戳窗口
2. **本地分配** - 在窗口内快速分配时间戳
3. **窗口更新** - 耗尽时申请新窗口
4. **持久化** - 定期持久化当前状态

```cpp
// 时间戳生成流程
TTimestamp TClockService::GenerateTimestamp() {
    // 1. 检查本地窗口
    if (localTimestamp < windowEnd) {
        return ++localTimestamp;
    }

    // 2. 申请新窗口
    RequestNewWindow();

    // 3. 返回新时间戳
    return ++localTimestamp;
}
```

### 分布式一致性

基于 Raft 算法实现：

1. **Leader 选举** - 选举主节点处理时间戳请求
2. **日志复制** - 复制状态变更到所有节点
3. **提交确认** - 确保变更被多数节点确认
4. **状态机应用** - 将变更应用到状态机

### 故障恢复

```cpp
// 故障恢复流程
void TClockAutomaton::OnLeaderRecovery() {
    // 1. 加载持久化状态
    LoadPersistedState();

    // 2. 同步集群状态
    SynchronizeClusterState();

    // 3. 恢复时间戳分配
    RestoreTimestampAllocation();

    // 4. 重新开始服务
    StartTimestampService();
}
```

## 配置说明

### 基础配置

```yaml
cluster_clock:
  # 服务监听地址
  listen_addresses:
    - "0.0.0.0:21300"

  # 集群连接
  cluster_connection:
    primary_masters:
      - "master1:9013"
      - "master2:9013"
      - "master3:9013"

  # 时间戳配置
  timestamp:
    window_size: 1000000        # 时间戳窗口大小
    max_batch_size: 1000       # 最大批量大小
    advance_interval: 100ms     # 推进间隔

  # 持久化配置
  persistence:
    snapshot_interval: 1h      # 快照间隔
    wal_path: "/var/lib/ytsaurus/clock/wal"
    snapshot_path: "/var/lib/ytsaurus/clock/snapshots"
```

### 性能调优

```yaml
performance:
  # 线程池配置
  thread_pool_size: 8

  # 缓冲区配置
  buffer_size: 1MB

  # 批处理配置
  batch_timeout: 10ms
  max_batch_count: 1000
```

## 使用方法

### 启动服务

```bash
# 单节点启动
./ytserver-clock --config clock_config.yaml

# 或通过 ytserver-all
./ytserver-all clock --config clock_config.yaml

# 集群部署（需要多个节点）
./ytserver-clock --config clock_config.yaml --cell-id clock-1
```

### 客户端使用

#### C++ 客户端
```cpp
#include <yt/yt/client/timestamp.h>

// 获取当前时间戳
auto timestamp = client->GenerateTimestamp();
std::cout << "Timestamp: " << timestamp << std::endl;

// 批量获取时间戳
auto timestamps = client->GenerateTimestamps(1000);
```

#### Python 客户端
```python
import yt

client = yt.YtClient("127.0.0.1:8000")

# 获取时间戳
timestamp = client.generate_timestamp()
print(f"Timestamp: {timestamp}")

# 事务中使用
with client.Transaction():
    # 事务开始时自动获取时间戳
    client.insert("/path", {"value": 42})
```

### 监控和调试

#### Orchid 接口
```bash
# 查看服务状态
yt get //sys/clock/orchid/

# 查看时间戳统计
yt get //sys/clock/orchid/timestamp/stats

# 查看 Hydra 状态
yt get //sys/clock/orchid/hydra
```

#### 性能指标
```bash
# 时间戳生成速率
yt get //sys/clock/orchid/metrics/timestamps_per_second

# 平均延迟
yt get //sys/clock/orchid/metrics/average_latency

# 错误率
yt get //sys/clock/orchid/metrics/error_rate
```

## 部署建议

### 生产环境

1. **高可用部署**
   - 至少 3 个节点
   - 分布在不同机架
   - 独立的存储设备

2. **网络配置**
   - 低延迟网络
   - 冗余网络路径
   - 专用网络带宽

3. **硬件要求**
   - 高性能 SSD
   - 足够的内存
   - 稳定的时钟源

### 性能优化

1. **批处理优化**
   - 启用批量时间戳分配
   - 调整批处理大小
   - 优化批处理超时

2. **缓存策略**
   - 预分配更大的时间窗口
   - 使用本地缓存
   - 减少网络往返

3. **并发优化**
   - 增加工作线程数
   - 使用异步 I/O
   - 优化队列配置

## 故障处理

### 常见问题

1. **时钟偏差过大**
   - 检查 NTP 配置
   - 调整时钟同步频率
   - 更换更稳定的时钟源

2. **性能瓶颈**
   - 增加时间戳窗口大小
   - 优化批处理配置
   - 扩展到更多节点

3. **主备切换失败**
   - 检查网络连接
   - 验证配置一致性
   - 查看日志定位原因

### 故障恢复

```bash
# 检查服务状态
systemctl status ytserver-clock

# 查看错误日志
tail -f /var/log/ytsaurus/clock_server.log

# 强制切换主节点
yt set //sys/clock/@force_leader_change true
```

## 最佳实践

1. **监控告警**
   - 监控时钟偏差
   - 监控服务可用性
   - 设置性能阈值告警

2. **容量规划**
   - 预估时间戳需求
   - 规划扩展策略
   - 定期评估性能

3. **运维管理**
   - 定期备份配置
   - 测试故障恢复
   - 更新和维护计划

## 相关文档

- [YTsaurus 架构概述](../../../README.md)
- [Hydra 分布式共识](../../../docs/hydra.md)
- [分布式事务文档](../../../docs/transactions.md)
- [时间戳服务 API](../../../docs/timestamp_api.md)

## API 参考

### RPC 服务

```cpp
service IClockService {
    rpc GenerateTimestamp(TGenerateTimestampReq) returns (TGenerateTimestampResp);
    rpc GenerateTimestamps(TGenerateTimestampsReq) returns (TGenerateTimestampsResp);
    rpc GetClockState(TGetClockStateReq) returns (TGetClockStateResp);
    rpc AdvanceTimestamp(TAdvanceTimestampReq) returns (TAdvanceTimestampResp);
}
```

### 配置选项

详见 `config.h` 中的配置结构定义。

## 许可证

本项目采用 Apache License 2.0 许可证。详见 [LICENSE](../../../LICENSE) 文件。