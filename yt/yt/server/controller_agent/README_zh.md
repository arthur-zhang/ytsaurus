# Controller Agent - 控制代理服务

## 概述

Controller Agent 是 YTsaurus 分布式计算框架中的核心组件，负责管理和控制 MapReduce、Merge、Erase 等操作的执行。它作为 Scheduler 的代理，承担具体的作业控制逻辑，包括任务调度、资源管理、错误处理等，实现了操作控制与调度决策的分离。

## 核心功能

### 1. 操作控制
- **操作生命周期管理** - 从初始化到完成的全程管理
- **任务调度** - 将操作分解为具体任务并调度执行
- **资源协调** - 协调作业所需的计算和存储资源
- **进度跟踪** - 实时跟踪操作执行进度

### 2. 作业管理
- **MapReduce 控制** - 管理 MapReduce 作业的执行流程
- **Merge 操作** - 控制数据合并操作
- **Erase 操作** - 管理数据擦除操作
- **Sort 操作** - 处理数据排序作业

### 3. 数据流管理
- **Chunk 管理** - 管理数据块的分布和处理
- **数据本地性** - 优化数据访问的本地性
- **中间结果处理** - 处理作业的中间数据
- **输出管理** - 管理作业的输出结果

### 4. 错误处理和恢复
- **错误检测** - 检测任务执行中的错误
- **自动重试** - 对失败的任务进行自动重试
- **故障恢复** - 从节点故障中恢复
- **异常处理** - 处理各种异常情况

## 架构设计

### 核心组件

#### 1. Controller Agent 主控制器
```cpp
class TControllerAgent : public TRefCounted
{
public:
    TControllerAgent(TControllerAgentConfigPtr config,
                     NYTree::INodePtr configNode,
                     TBootstrap* bootstrap);

    void Initialize();

    // 服务接口
    NYTree::IYPathServicePtr CreateOrchidService();
    IInvokerPtr GetControllerThreadPoolInvoker();
};
```
负责整个服务的初始化和协调各个组件。

#### 2. 操作控制器（Operation Controller）
```cpp
class IOperationController : public TRefCounted
{
public:
    // 操作控制
    virtual void Initialize() = 0;
    virtual void Prepare() = 0;
    virtual void Commit() = 0;
    virtual void Abort() = 0;

    // 状态查询
    virtual EControllerState GetState() const = 0;
    virtual TOperationProgress GetProgress() const = 0;
};
```
定义了操作控制的通用接口，具体操作类型有相应的实现。

#### 3. Chunk 列表池
```cpp
class TChunkListPool
{
public:
    // Chunk 列表管理
    TChunkListPtr Acquire();
    void Release(TChunkListPtr chunkList);

    // 池管理
    void SetCapacity(size_t capacity);
    size_t GetSize() const;
};
```
管理 Chunk 列表的分配和回收，优化内存使用。

#### 4. 输入统计收集器
```cpp
class TInputStatisticsCollector
{
public:
    // 统计收集
    void AddChunk(const TChunkSpec& chunk);
    TInputStreamStatistics GetStatistics() const;

    // 重置和合并
    void Reset();
    void Merge(const TInputStatisticsCollector& other);
};
```
收集作业的输入数据统计信息。

#### 5. 中间数据清理器
```cpp
class TIntermediateChunkScraper
{
public:
    // 清理任务
    void ScheduleCleanup(const std::vector<TChunkId>& chunks);
    void ProcessCleanupQueue();

    // 状态管理
    bool IsCleanupPending(TChunkId chunkId) const;
};
```
负责清理作业执行过程中产生的临时数据。

### 线程模型

Controller Agent 使用多线程模型处理不同类型的任务：

1. **控制线程池** - 处理操作控制逻辑
2. **Chunk 刮除线程池** - 处理数据块清理任务
3. **I/O 线程池** - 处理网络 I/O 操作
4. **回调线程** - 处理异步回调

## 实现原理

### 操作执行流程

1. **初始化阶段**
   ```cpp
   void TControllerAgent::Initialize() {
       // 1. 创建服务实例
       CreateServices();

       // 2. 启动线程池
       StartThreadPools();

       // 3. 初始化组件
       InitializeComponents();

       // 4. 注册服务
       RegisterServices();
   }
   ```

2. **操作准备阶段**
   ```cpp
   void TMapOperationController::Prepare() {
       // 1. 分析输入数据
       AnalyzeInputData();

       // 2. 计算数据分布
       CalculateDataDistribution();

       // 3. 创建任务计划
       CreateTaskPlan();

       // 4. 分配资源
       AllocateResources();
   }
   ```

3. **执行阶段**
   ```cpp
   void TControllerAgent::OnTaskCompleted(const TTaskSummary& summary) {
       // 1. 更新进度
       UpdateProgress(summary);

       // 2. 调度新任务
       ScheduleMoreTasks();

       // 3. 处理错误
       if (summary.Error) {
           HandleError(summary.Error);
       }
   }
   ```

### 任务调度策略

1. **数据本地性优先** - 优先在数据所在节点执行任务
2. **负载均衡** - 避免某些节点过载
3. **资源约束** - 考虑节点的资源限制
4. **依赖关系** - 处理任务间的依赖

### 错误处理机制

```cpp
void TControllerAgent::HandleTaskError(const TTaskId& taskId, const TError& error) {
    // 1. 分析错误类型
    auto errorType = ClassifyError(error);

    // 2. 决定处理策略
    switch (errorType) {
        case EErrorType::Transient:
            ScheduleRetry(taskId);
            break;
        case EErrorType::NodeFailure:
            RescheduleTask(taskId);
            break;
        case EErrorType::Permanent:
            FailOperation(error);
            break;
    }

    // 3. 更新统计
    UpdateErrorStatistics(error);
}
```

## 配置说明

### 主配置文件

```yaml
controller_agent:
  # 基本配置
  listen_port: 21300

  # Scheduler 连接
  scheduler:
    addresses:
      - "scheduler1:9010"
      - "scheduler2:9010"

  # 线程池配置
  thread_pools:
    controller_thread_pool_size: 8
    chunk_scraper_heavy_thread_pool_size: 4
    io_thread_pool_size: 16

  # 资源限制
  resource_limits:
    max_operation_count: 1000
    max_concurrent_job_count: 10000
    max_memory_per_operation: 1TB

  # 重试策略
  retry_policy:
    max_retry_count: 10
    initial_backoff: 1s
    max_backoff: 1m
```

### 操作特定配置

```yaml
operations:
  map_reduce:
    max_io_errors: 100
    chunk_scraper_period: 5s

  merge:
    merge_job_io_error_count_limit: 50
    max_chunk_count_per_job: 1000

  erase:
    max_nodes_per_erase: 100
    node_requisition_timeout: 5m
```

## 使用方法

### 启动服务

```bash
# 直接启动
./ytserver-controller-agent --config controller_agent.yaml

# 或通过 ytserver-all
./ytserver-all controller-agent --config controller_agent.yaml
```

### 监控接口

#### Orchid 监控
```bash
# 查看整体状态
yt get //sys/controller_agents/*/orchid/

# 查看正在运行的操作
yt get //sys/controller_agents/*/orchid/operations

# 查看性能指标
yt get //sys/controller_agents/*/orchid/performance_counters
```

#### 操作状态查询
```cpp
// 获取操作详情
auto operation = GetOperation(operationId);
auto progress = operation->GetProgress();
auto statistics = operation->GetStatistics();

// 获取任务列表
auto tasks = operation->GetTasks();
for (const auto& task : tasks) {
    std::cout << "Task " << task.Id << ": " << task.State << std::endl;
}
```

### 调试工具

```bash
# 查看操作日志
yt get //sys/controller_agents/*/orchid/operations/{operation_id}/stderr

# 查看任务分布
yt get //sys/controller_agents/*/orchid/operations/{operation_id}/task_distribution

# 强制完成操作
yt set //sys/controller_agents/*/orchid/operations/{operation_id}/@force_completed true
```

## 性能优化

### 关键优化点

1. **批量处理**
   - 批量调度任务
   - 批量收集统计
   - 批量更新状态

2. **缓存策略**
   - 缓存 Chunk 元数据
   - 缓存节点状态
   - 缓存操作配置

3. **并发控制**
   - 合理设置线程池大小
   - 使用无锁数据结构
   - 优化锁粒度

4. **资源管理**
   - 及时释放资源
   - 使用对象池
   - 预分配内存

### 调优参数

```yaml
performance_tuning:
  # 批处理大小
  task_schedule_batch_size: 100
  statistics_collection_batch_size: 50

  # 缓存大小
  chunk_metadata_cache_size: 100000
  node_state_cache_size: 1000

  # 超时设置
  operation_timeout: 24h
  task_timeout: 1h
  heartbeat_timeout: 30s
```

## 故障处理

### 常见故障场景

1. **内存不足**
   - 症状：OOM 错误
   - 处理：调整内存限制，优化内存使用

2. **任务超时**
   - 症状：大量任务超时
   - 处理：调整超时配置，检查网络

3. **节点故障**
   - 症状：任务失败率上升
   - 处理：自动重试，隔离故障节点

4. **Scheduler 连接中断**
   - 症状：无法调度新任务
   - 处理：自动重连，缓存任务

### 故障恢复

```cpp
void TControllerAgent::RecoverFromFailure() {
    // 1. 保存当前状态
    SaveState();

    // 2. 停止新任务调度
    StopScheduling();

    // 3. 等待运行任务完成
    WaitForRunningTasks();

    // 4. 恢复连接
    Reconnect();

    // 5. 恢复调度
    ResumeScheduling();
}
```

## 最佳实践

### 部署建议

1. **资源规划**
   - CPU：8 核心以上
   - 内存：32GB 以上
   - 磁盘：SSD 用于临时存储

2. **高可用部署**
   - 部署多个实例
   - 使用负载均衡
   - 配置健康检查

3. **监控告警**
   - 监控关键指标
   - 设置合理阈值
   - 配置自动恢复

### 运维管理

1. **日志管理**
   - 配置日志轮转
   - 分级日志输出
   - 集中日志收集

2. **配置管理**
   - 使用版本控制
   - 动态配置更新
   - 配置验证

3. **性能调优**
   - 定期性能分析
   - 调整线程池大小
   - 优化批处理参数

## 相关文档

- [YTsaurus 架构概述](../../../README.md)
- [Scheduler 服务](../scheduler/README_zh.md)
- [MapReduce 指南](../../../docs/mapreduce.md)
- [操作 API 参考](../../../docs/operation_api.md)

## API 参考

### RPC 服务

```cpp
service IControllerAgentService {
    rpc RegisterOperation(TRegisterOperationReq) returns (TRegisterOperationResp);
    rpc UpdateOperationProgress(TUpdateOperationProgressReq) returns (TUpdateOperationProgressResp);
    rpc AbortOperation(TAbortOperationReq) returns (TAbortOperationResp);
    rpc CompleteOperation(TCompleteOperationReq) returns (TCompleteOperationResp);
}

service IControllerAgent {
    rpc Heartbeat(THeartbeatReq) returns (THeartbeatResp);
    rpc ScheduleJob(TScheduleJobReq) returns (TScheduleJobResp);
    rpc OnJobCompleted(TOnJobCompletedReq) returns (TOnJobCompletedResp);
}
```

### 配置选项

详见 `config.h` 中的详细配置定义。

## 许可证

本项目采用 Apache License 2.0 许可证。详见 [LICENSE](../../../LICENSE) 文件。