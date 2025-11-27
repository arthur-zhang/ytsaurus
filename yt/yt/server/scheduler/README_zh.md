# YTsaurus Scheduler 服务

## 概述

YTsaurus Scheduler 是集群的核心调度服务，负责作业的调度、资源管理和作业生命周期控制。作为 YTsaurus 分布式计算的大脑，Scheduler 实现了复杂的调度算法，支持多种作业类型，提供高效的资源利用率和作业执行性能。

Scheduler 采用模块化架构设计，支持可插拔的调度策略，能够适应不同类型的计算负载。它与 Master 和 Node 紧密协作，确保作业在合适的资源上高效执行。

## 核心功能

### 1. 作业调度

#### 多种作业类型支持
- **MapReduce 作业**：经典的 MapReduce 计算模型
- **Vanilla 作业**：自定义用户程序执行
- **Reduce 作业**：数据聚合和计算
- **Merge 作业**：数据合并和整理
- **Sort 作业**：大规模数据排序
- **Remote Copy 作业**：跨集群数据复制

#### 调度策略
- **Fair Scheduling**：公平调度，确保用户间的公平性
- **Capacity Scheduling**：容量调度，保证资源容量
- **FIFO Scheduling**：先进先出调度
- **Priority Scheduling**：基于优先级的调度
- **Resource-aware Scheduling**：资源感知调度

#### 作业生命周期管理
```cpp
enum class EOperationState {
    None,           // 未初始化
    Starting,       // 启动中
    WaitingForAgent,// 等待 Controller Agent
    Running,        // 运行中
    Completing,     // 完成中
    Completed,      // 已完成
    Failed,         // 失败
    Aborting,       // 中止中
    Aborted,        // 已中止
};
```

### 2. 资源管理

#### 资源模型
- **CPU 资源**：CPU 核心数和调度策略
- **内存资源**：内存使用和限制
- **磁盘资源**：临时磁盘空间
- **网络资源**：网络带宽使用
- **GPU 资源**：GPU 卡和内存管理

#### 资源分配策略
- **Bin Packing**：装箱算法优化资源利用率
- **Spread Algorithm**：分散算法提高容错性
- **Locality-aware Scheduling**：数据本地性优化
- **Preemption**：作业抢占机制
- **Resource Reclaiming**：资源回收

#### 节点管理
- **节点注册和心跳**：维护节点状态信息
- **资源统计**：实时监控节点资源使用
- **健康检查**：节点健康状态监控
- **故障恢复**：处理节点故障和恢复

### 3. 作业控制

#### Controller Agent 管理
- **Agent 选择**：智能选择 Controller Agent
- **负载均衡**：在多个 Agent 间均衡负载
- **故障转移**：Agent 故障时的自动切换
- **版本管理**：Agent 版本兼容性管理

#### 作业执行控制
- **作业启动**：启动和初始化作业
- **进度监控**：实时监控作业执行进度
- **作业暂停和恢复**：支持作业的暂停和恢复
- **作业中止**：强制中止异常作业

#### 动态配置
- **运行时配置更新**：支持配置热更新
- **调度策略调整**：动态调整调度参数
- **资源限制修改**：运行时修改资源限制

### 4. 监控和统计

#### 性能监控
- **调度延迟**：作业调度延迟监控
- **资源利用率**：集群资源使用统计
- **作业吞吐量**：作业完成率统计
- **队列状态**：作业队列状态监控

#### 历史数据
- **作业历史**：作业执行历史记录
- **调度决策**：调度决策日志
- **资源使用历史**：资源使用趋势
- **性能指标**：历史性能指标

## 架构设计

### 核心组件

#### 1. Scheduler 主模块
```
scheduler/
├── scheduler.cpp              # 调度器主类
├── node_manager.cpp           # 节点管理器
├── operation_controller.cpp   # 作业控制器
├── master_connector.cpp       # Master 连接器
└── operations_cleaner.cpp     # 作业清理器
```

#### 2. 作业管理模块
```
operation/
├── operation.cpp              # 作业类
├── operation_controller.cpp   # 作业控制器
├── operation_controller_impl.cpp # 作业控制器实现
└── operation_alert_event.cpp   # 作业告警事件
```

#### 3. Controller Agent 模块
```
controller_agent/
├── controller_agent.cpp       # Controller Agent 类
├── controller_agent_tracker.cpp # Agent 跟踪器
└── controller_agent_service.cpp  # Agent 服务
```

#### 4. 调度策略模块
```
strategy/
├── scheduler_strategy.cpp     # 调度策略基类
├── fair_share_strategy.cpp    # 公平分享策略
├── fifo_strategy.cpp          # FIFO 策略
└── pool_strategy.cpp          # 池化策略
```

### 调度流程

#### 1. 作业提交流程
```
User → RPC Proxy → Master → Scheduler
  ↓        ↓          ↓        ↓
1.提交  2.验证权限  3.创建作业 4.调度决策
  ↓        ↓          ↓        ↓
10.响应  9.更新状态  8.启动作业 5.分配节点
                         ↓        ↓
                     7.分配资源  6.准备环境
```

#### 2. 调度决策流程
```
作业队列 → 资源匹配 → 节点选择 → 作业分配
    ↓           ↓          ↓         ↓
1.获取作业   2.检查资源   3.数据本地性 4.最终决策
    ↓           ↓          ↓         ↓
8.更新状态   7.记录决策   6.评估代价 5.排序
```

#### 3. 资源管理流程
```
节点注册 → 资源发现 → 分配决策 → 监控调整
   ↓          ↓          ↓         ↓
1.心跳检测 2.资源统计 3.匹配算法 4.动态调整
   ↓          ↓          ↓         ↓
8.状态同步 7.回收资源 6.执行分配 5.预留资源
```

### 数据结构

#### 1. 节点描述符
```cpp
struct TExecNodeDescriptor {
    TString Address;                  // 节点地址
    i32 CpuCount;                    // CPU 核心数
    i64 MemoryLimit;                 // 内存限制
    i64 DiskSpaceLimit;              // 磁盘空间限制
    bool Online;                     // 在线状态
    std::vector<TMediumDescriptor> Mediums; // 存储介质描述
};
```

#### 2. 作业描述符
```cpp
struct TOperationDescriptor {
    TOperationId Id;                 // 作业 ID
    EOperationType Type;             // 作业类型
    EOperationState State;           // 作业状态
    i64 StartTime;                   // 开始时间
    TUser Resources;                 // 资源需求
    TUser Spec;                      // 作业规格
};
```

#### 3. 资源分配
```cpp
struct TAllocation {
    TAllocationId Id;               // 分配 ID
    TOperationId OperationId;       // 所属作业 ID
    TNodeId NodeId;                 // 分配到的节点
    TJobResources Resources;        // 分配的资源
    EAllocationState State;         // 分配状态
};
```

## 配置说明

### 主配置文件

#### 基础配置
```yaml
scheduler:
  # 服务标识
  scheduler_id: "scheduler-001"

  # 监听地址
  rpc_port: 9015
  monitoring_port: 9016
  http_port: 9017

  # 集群连接
  master_connection:
    primary_master: "master1.ytsaurus.local:9013"
    secondary_masters:
      - "master2.ytsaurus.local:9013"
      - "master3.ytsaurus.local:9013"
```

#### 调度策略配置
```yaml
scheduler_strategy:
  # 默认策略
  default_strategy: "fair_share"

  # Fair Share 策略
  fair_share_strategy:
    fair_share_update_period: 1000
    fair_share_starvation_timeout: 60000
    pool_weight_update_period: 5000

  # FIFO 策略
  fifo_strategy:
    enable_fifo: true
    fifo_order_by_start_time: true

  # 资源限制
  resource_limits:
    max_concurrent_operations: 1000
    max_operation_memory_ratio: 0.8
    max_operation_cpu_ratio: 0.9
```

#### 节点管理配置
```yaml
node_manager:
  # 节点心跳配置
  node_heartbeat_timeout: 30000
  node_offline_timeout: 180000

  # 资源统计
  enable_resource_statistics: true
  resource_statistics_update_period: 5000

  # 节点过滤
  node_filter:
    exclude_offline_nodes: true
    exclude_full_nodes: true
    exclude_banned_nodes: true
```

#### Controller Agent 配置
```yaml
controller_agent:
  # Agent 连接池
  connection_pool_size: 10
  connection_timeout: 10000

  # 负载均衡
  enable_load_balancing: true
  max_operations_per_agent: 50

  # 故障转移
  enable_failover: true
  failover_timeout: 30000
```

### 动态配置

```yaml
dynamic_config:
  # 配置更新间隔
  update_period: 5000

  # 配置路径
  config_path: "//sys/scheduler/config"

  # 验证配置
  validate_config: true
```

## 使用方法

### 编译和部署

1. **编译 Scheduler 服务**
```bash
# 构建完整服务
ninja ytserver-all

# 或单独构建
ninja ytserver-scheduler
```

2. **准备配置文件**
```bash
# 创建配置目录
mkdir -p /etc/ytsaurus

# 复制示例配置
cp config/ytserver-scheduler.yaml /etc/ytsaurus/

# 编辑配置
vim /etc/ytsaurus/ytserver-scheduler.yaml
```

3. **启动服务**
```bash
# 前台启动
./yt/yt/server/all/ytserver-all \
  --config /etc/ytsaurus/ytserver-scheduler.yaml \
  --scheduler-id scheduler-001

# 后台启动
nohup ./yt/yt/server/all/ytserver-all \
  --config /etc/ytsaurus/ytserver-scheduler.yaml \
  --scheduler-id scheduler-001 \
  > /var/log/ytsaurus/scheduler.log 2>&1 &
```

### 集群注册

1. **注册 Scheduler**
```bash
# 创建 Scheduler 节点
yt create map_node //sys/schedulers/scheduler-001

# 设置 Scheduler 地址
yt set //sys/schedulers/scheduler-001/@address "scheduler1.ytsaurus.local"

# 设置监听端口
yt set //sys/schedulers/scheduler-001/@rpc_port 9015
```

2. **配置调度池**
```bash
# 创建默认调度池
yt create document //sys/scheduler/pools/default
yt set //sys/s/scheduler/pools/default/@fair_share_weight 1.0

# 创建用户池
yt create document //sys/scheduler/pools/users
yt set //sys/s/scheduler/pools/users/@fair_share_weight 10.0
yt set //sys/s/scheduler/pools/users/@parent_pool "default"
```

### 作业操作

#### 1. 提交作业
```bash
# MapReduce 作业
yt map \
  --mapper cat \
  --reduce cat \
  --src <input_table> \
  --dst <output_table> \
  --spec "{pool='users'}"

# Vanilla 作业
yt run-vanilla \
  --command "echo 'Hello World'" \
  --spec "{pool='users',memory_limit=1GB}"
```

#### 2. 管理作业
```bash
# 列出作业
yt list operations

# 查看作业状态
yt get <operation_id>/@state

# 中止作业
yt abort-operation <operation_id>

# 暂停作业
yt suspend-operation <operation_id>

# 恢复作业
yt resume-operation <operation_id>
```

#### 3. 监控调度
```bash
# 查看调度统计
yt get //sys/scheduler/@statistics

# 查看节点状态
yt get //sys/scheduler/@nodes

# 查看作业队列
yt get //sys/scheduler/@operations
```

## 实现原理

### 调度算法

#### 1. Fair Share 算法
```cpp
class TFairShareStrategy {
    double CalculateFairShare(const TPool& pool) {
        // 计算池的公平分享值
        double resourceWeight = pool.ResourceWeight;
        double demandWeight = pool.DemandWeight;
        double fairShare = resourceWeight / demandWeight;
        return fairShare;
    }

    void UpdatePoolWeights() {
        // 更新所有池的权重
        for (auto& pool : Pools_) {
            pool.FairShare = CalculateFairShare(pool);
        }
    }
};
```

#### 2. 资源匹配算法
```cpp
bool TNodeManager::MatchResources(
    const TJobResources& required,
    const TJobResources& available) const {

    return required.Cpu() <= available.Cpu() &&
           required.Memory() <= available.Memory() &&
           required.Disk() <= available.Disk();
}
```

#### 3. 数据本地性优化
```cpp
class TLocalityScoreCalculator {
    double CalculateScore(
        const TOperation& operation,
        const TExecNodeDescriptor& node) {

        double localityScore = 0.0;

        // 计算数据本地性得分
        for (const auto& inputData : operation.InputData) {
            if (HasLocalReplica(inputData, node)) {
                localityScore += inputData.Size;
            }
        }

        return localityScore / operation.TotalInputSize;
    }
};
```

### 资源管理机制

#### 1. 资源抽象
```cpp
struct TJobResources {
    double Cpu_ = 0.0;            // CPU 核心数
    i64 Memory_ = 0;              // 内存字节数
    i64 Disk_ = 0;                // 磁盘空间
    int Gpu_ = 0;                 // GPU 数量

    TJobResources& operator+=(const TJobResources& other);
    TJobResources& operator-=(const TJobResources& other);
    bool operator<=(const TJobResources& other) const;
};
```

#### 2. 资源分配
```cpp
class TResourceAllocator {
    TAllocationId AllocateResources(
        const TOperationId& operationId,
        const TJobResources& resources,
        const std::vector<TNodeId>& candidateNodes) {

        // 1. 过滤可用节点
        auto availableNodes = FilterAvailableNodes(candidateNodes);

        // 2. 计算节点得分
        auto scoredNodes = ScoreNodes(availableNodes, operationId);

        // 3. 选择最佳节点
        auto bestNode = SelectBestNode(scoredNodes);

        // 4. 分配资源
        return CreateAllocation(operationId, resources, bestNode);
    }
};
```

#### 3. 抢占机制
```cpp
class TPreemptor {
    void PreemptResources(
        const TOperationId& preemptorOperation,
        const TJobResources& requiredResources) {

        // 1. 找到可抢占的作业
        auto preemptableOperations = FindPreemptableOperations(preemptorOperation);

        // 2. 按优先级排序
        SortByPriority(preemptableOperations);

        // 3. 逐个抢占直到满足资源需求
        for (const auto& operation : preemptableOperations) {
            if (ReleaseEnoughResources(operation, requiredResources)) {
                break;
            }
        }
    }
};
```

### 作业生命周期

#### 1. 作业启动流程
```cpp
void TOperationController::StartOperation() {
    // 1. 验证作业规格
    ValidateOperationSpec();

    // 2. 初始化作业环境
    InitializeOperation();

    // 3. 分配初始资源
    AllocateInitialResources();

    // 4. 启动作业
    LaunchJobs();

    // 5. 更新状态
    UpdateOperationState(EOperationState::Running);
}
```

#### 2. 作业监控
```cpp
void TOperationController::MonitorOperation() {
    while (Operation_->State == EOperationState::Running) {
        // 1. 收集作业状态
        auto jobStates = CollectJobStates();

        // 2. 更新进度
        UpdateProgress(jobStates);

        // 3. 检查异常
        CheckForAnomalies(jobStates);

        // 4. 动态调整
        AdjustResources(jobStates);

        // 5. 等待下一次检查
        Sleep(MonitoringInterval);
    }
}
```

#### 3. 作业完成
```cpp
void TOperationController::CompleteOperation() {
    // 1. 停止所有作业
    StopAllJobs();

    // 2. 清理资源
    ReleaseResources();

    // 3. 收集结果
    CollectResults();

    // 4. 更新元数据
    UpdateOperationMetadata();

    // 5. 通知完成
    NotifyOperationCompleted();
}
```

## 性能优化

### 调度性能优化

#### 1. 批处理优化
```yaml
batch_optimization:
  # 批量调度
  enable_batch_scheduling: true
  max_batch_size: 100
  batch_timeout: "10ms"

  # 预调度
  enable_prescheduling: true
  preschedule_window: 1000
```

#### 2. 缓存优化
```yaml
cache_optimization:
  # 节点信息缓存
  node_info_cache:
    ttl: 5000
    max_size: 10000

  # 作业信息缓存
  operation_cache:
    ttl: 10000
    max_size: 1000
```

#### 3. 并行化
```yaml
parallelization:
  # 并行调度线程数
  scheduler_thread_count: 8

  # 并行监控线程数
  monitor_thread_count: 4

  # 异步处理
  enable_async_processing: true
```

### 资源利用率优化

#### 1. 资源碎片整理
```yaml
defragmentation:
  # 启用碎片整理
  enable_defragmentation: true

  # 整理阈值
  fragmentation_threshold: 0.7

  # 整理间隔
  defragmentation_period: 300000
```

#### 2. 负载均衡
```yaml
load_balancing:
  # 启用负载均衡
  enable_load_balancing: true

  # 负载均衡策略
  strategy: "resource_aware"

  # 平衡阈值
  imbalance_threshold: 0.2
```

#### 3. 数据本地性
```yaml
locality:
  # 启用数据本地性优化
  enable_locality_optimization: true

  # 本地性权重
  locality_weight: 0.8

  # 远程数据权重
  remote_data_weight: 0.2
```

## 监控调试

### 关键监控指标

#### 调度器状态
```bash
# 调度器健康状态
yt get //sys/schedulers/scheduler-001/@health

# 调度统计
yt get //sys/schedulers/scheduler-001/@statistics

# 作业队列状态
yt get //sys/schedulers/scheduler-001/@operations
```

#### 性能指标
```bash
# 调度延迟
yt get //sys/schedulers/scheduler-001/@scheduler_latency

# 资源利用率
yt get //sys/schedulers/scheduler-001/@resource_utilization

# 作业吞吐量
yt get //sys/schedulers/scheduler-001/@job_throughput

# 节点数量
yt get //sys/schedulers/scheduler-001/@node_count
```

#### 作业指标
```bash
# 活跃作业数
yt get //sys/schedulers/scheduler-001/@active_operation_count

# 排队作业数
yt get //sys/schedulers/scheduler-001/@queued_operation_count

# 完成作业数
yt get //sys/schedulers/scheduler-001/@completed_operation_count

# 失败作业数
yt get //sys/schedulers/scheduler-001/@failed_operation_count
```

### 调试工具

#### 1. Orchid 监控
```bash
# 访问 Scheduler Orchid
curl http://localhost:9016/orchid

# 查看调度策略
curl http://localhost:9016/orchid/scheduler/strategy

# 查看节点状态
curl http://localhost:9016/orchid/scheduler/nodes

# 查看作业状态
curl http://localhost:9016/orchid/scheduler/operations
```

#### 2. 性能分析
```bash
# CPU 使用情况
top -p $(pgrep ytserver)

# 内存使用情况
cat /proc/$(pgrep ytserver)/status

# 线程状态
ps -T -p $(pgrep ytserver)

# 网络连接
netstat -an | grep 9015
```

#### 3. 日志分析
```bash
# 查看实时日志
tail -f /var/log/ytsaurus/scheduler.log

# 搜索调度日志
grep "SCHEDULER" /var/log/ytsaurus/scheduler.log

# 搜索错误日志
grep "ERROR" /var/log/ytsaurus/scheduler.log

# 分析性能日志
grep "PERFORMANCE" /var/log/ytsaurus/scheduler.log
```

#### 4. 作业调试
```bash
# 查看作业详情
yt get <operation_id>/@

# 查看作业日志
yt list <operation_id>/jobs

# 查看作业事件
yt read <operation_id>/events

# 查看作业规格
yt get <operation_id>/@spec
```

## 故障处理

### 常见故障及解决方案

#### 1. 调度器无法启动
```bash
# 现象：服务启动失败
# 解决方案：

# 1. 检查配置文件
./ytserver-all --config config.yaml --dry-run

# 2. 检查端口占用
netstat -tlnp | grep 9015

# 3. 检查 Master 连接
telnet master1.ytsaurus.local 9013

# 4. 查看详细日志
tail -f /var/log/ytsaurus/scheduler.log
```

#### 2. 作业调度缓慢
```bash
# 现象：作业调度延迟过高
# 解决方案：

# 1. 检查资源使用
yt get //sys/scheduler/@resource_utilization

# 2. 检查节点状态
yt get //sys/scheduler/@nodes

# 3. 调整调度参数
# 修改调度策略配置

# 4. 重启调度器
systemctl restart ytserver-scheduler
```

#### 3. 作业频繁失败
```bash
# 现象：作业执行失败率高
# 解决方案：

# 1. 检查节点健康
yt get //sys/cluster_nodes/@health

# 2. 检查资源配额
yt get //sys/scheduler/@resource_limits

# 3. 查看作业错误
yt get <operation_id>/@error

# 4. 调整作业规格
# 修改作业内存、CPU 配置
```

#### 4. Controller Agent 故障
```bash
# 现象：Controller Agent 不可用
# 解决方案：

# 1. 检查 Agent 状态
yt get //sys/controller_agents/@health

# 2. 重启 Agent
systemctl restart ytserver-controller-agent

# 3. 检查网络连接
telnet agent-host 9014

# 4. 查看连接池状态
curl http://localhost:9016/orchid/controller_agents
```

### 数据恢复

#### 1. 作业状态恢复
```bash
# 如果调度器重启，作业状态会自动恢复
# 检查恢复状态：

yt list //sys/scheduler/operations

# 如有异常，手动修复：
yt set <operation_id>/@state "running"
```

#### 2. 资源分配恢复
```bash
# 清理异常分配：
yt list //sys/scheduler/allocations

# 删除无效分配：
yt remove //sys/scheduler/allocations/<allocation_id>
```

#### 3. 集群状态恢复
```bash
# 检查集群整体状态：
yt get //sys/@cluster_state

# 如有状态不一致，触发状态同步：
yt set //sys/@trigger_state_sync true
```

## 最佳实践

### 部署建议

#### 1. 硬件配置
- **CPU**：至少 16 核，推荐 32 核以上
- **内存**：至少 32GB，推荐 64GB 以上
- **存储**：SSD 存储，至少 100GB
- **网络**：千兆网卡，推荐万兆

#### 2. 高可用部署
```yaml
# 多调度器部署
schedulers:
  - id: "scheduler-001"
    address: "scheduler1.ytsaurus.local:9015"
  - id: "scheduler-002"
    address: "scheduler2.ytsaurus.local:9015"
  - id: "scheduler-003"
    address: "scheduler3.ytsaurus.local:9015"
```

#### 3. 网络配置
```yaml
network:
  # 绑定到多网卡
  bind_addresses:
    - "10.0.1.100"
    - "10.0.2.100"

  # 启用 TLS
  enable_tls: true

  # 连接池配置
  connection_pool_size: 100
```

### 运维建议

#### 1. 监控告警
```yaml
alerts:
  - name: "scheduler_down"
    condition: "up == 0"
    severity: "critical"

  - name: "high_queue_length"
    condition: "queue_length > 1000"
    severity: "warning"

  - name: "low_resource_utilization"
    condition: "resource_utilization < 0.5"
    severity: "info"
```

#### 2. 性能调优
```yaml
performance:
  # 调度线程数
  scheduler_thread_count: 8

  # 监控线程数
  monitor_thread_count: 4

  # 批处理配置
  batch_size: 50
  batch_timeout: "5ms"
```

#### 3. 定期维护
- 定期清理完成的作业历史
- 监控和优化调度参数
- 定期备份调度器配置
- 测试故障恢复流程

### 调度策略优化

#### 1. 池配置建议
```yaml
pools:
  # 根池
  root:
    fair_share_weight: 1.0

  # 生产环境池
  production:
    parent_pool: "root"
    fair_share_weight: 100.0
    max_running_operations: 500

  # 开发测试池
  development:
    parent_pool: "root"
    fair_share_weight: 10.0
    max_running_operations: 50
```

#### 2. 资源配额
```yaml
quotas:
  # 默认用户配额
  default_user:
    memory_limit: "100GB"
    cpu_limit: 50
    operation_count_limit: 100

  # VIP 用户配额
  vip_user:
    memory_limit: "1TB"
    cpu_limit: 500
    operation_count_limit: 1000
```

## 相关文档

- [YTsaurus 架构概述](../../README.md)
- [Master 服务文档](../master/README_zh.md)
- [Node 服务文档](../node/README_zh.md)
- [作业调度设计](../../../docs/scheduling.md)
- [资源管理系统](../../../docs/resource_management.md)
- [Controller Agent 文档](../controller_agent/README_zh.md)
- [作业类型指南](../../../docs/job_types.md)
- [性能调优手册](../../../docs/performance.md)