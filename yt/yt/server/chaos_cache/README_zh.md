# Chaos Cache - 混沌缓存服务

## 概述

Chaos Cache 是 YTsaurus 分布式系统中的一个专门服务，用于支持混沌工程（Chaos Engineering）实验。该服务提供了一个缓存层，用于存储和管理混沌测试过程中的状态数据、实验配置和结果，帮助开发和运维团队测试和验证系统的容错能力。

## 核心功能

### 1. 混沌实验管理
- **实验配置存储** - 保存混沌实验的配置参数
- **状态跟踪** - 实时跟踪实验的执行状态
- **结果缓存** - 缓存实验结果和指标数据
- **实验历史** - 维护实验的历史记录

### 2. 故障注入支持
- **故障类型管理** - 支持多种故障类型的定义
- **注入策略** - 实现各种故障注入策略
- **影响范围控制** - 精确控制故障的影响范围
- **恢复机制** - 自动或手动的故障恢复

### 3. 数据缓存服务
- **高性能缓存** - 提供低延迟的数据访问
- **数据一致性** - 确保缓存数据的一致性
- **过期策略** - 支持多种数据过期策略
- **内存管理** - 优化内存使用效率

### 4. 监控和指标
- **实时监控** - 监控混沌实验的影响
- **性能指标** - 收集系统性能指标
- **健康检查** - 定期检查服务健康状态
- **告警机制** - 异常情况的自动告警

## 架构设计

### 核心组件

#### 1. Bootstrap 启动器
```cpp
class TBootstrap
{
public:
    TBootstrap(TChaosCacheConfigPtr config, INodePtr configNode);

    void Run();

    // 服务组件管理
    void Initialize();
    void Start();
    void Stop();
};
```
负责服务的初始化、启动和关闭，管理所有子组件的生命周期。

#### 2. Chaos Cache Service
核心服务实现，提供以下接口：
- `PutChaosExperiment()` - 存储实验配置
- `GetChaosExperiment()` - 获取实验信息
- `ListExperiments()` - 列出所有实验
- `UpdateExperimentStatus()` - 更新实验状态

#### 3. Dynamic Config Manager
```cpp
class TDynamicConfigManager
{
public:
    void LoadConfig();
    void OnConfigChanged();
    TChaosCacheDynamicConfigPtr GetConfig();
};
```
动态配置管理器，支持运行时配置更新。

#### 4. Cypress Registrar
负责在 Cypress 中注册服务信息，提供服务发现功能。

### 数据模型

#### 实验配置结构
```yaml
chaos_experiment:
  id: "exp-001"
  name: "NetworkPartitionTest"
  type: "network_partition"
  target:
    nodes: ["node1", "node2"]
    tablets: ["tablet1"]
  parameters:
    duration: "5m"
    severity: "high"
  status: "running"
  created_at: "2024-01-01T00:00:00Z"
  updated_at: "2024-01-01T00:05:00Z"
```

## 配置说明

### 静态配置

```yaml
chaos_cache:
  # 服务监听地址
  listen_addresses:
    - "0.0.0.0:21300"

  # 集群连接
  cluster_connection:
    primary_masters:
      - "master1:9013"

  # 缓存配置
  cache:
    max_size: 1GB
    ttl: 24h
    cleanup_interval: 1h

  # 实验限制
  experiment_limits:
    max_concurrent: 10
    max_duration: 24h
    allowed_types:
      - "network_partition"
      - "process_kill"
      - "disk_failure"
```

### 动态配置

支持运行时更新的配置项：

```yaml
dynamic_config:
  # 调试模式
  debug_mode: false

  # 日志级别
  log_level: "info"

  # 性能调优
  performance:
    batch_size: 100
    flush_interval: 5s
```

## 使用方法

### 启动服务

```bash
# 使用配置文件启动
./ytserver-chaos-cache --config chaos_cache.yaml

# 或通过 ytserver-all
./ytserver-all chaos-cache --config chaos_cache.yaml
```

### API 使用示例

#### 创建混沌实验
```python
import yt

client = yt.YtClient("127.0.0.1:8000")

# 创建网络分区实验
experiment = {
    "type": "network_partition",
    "target": {
        "nodes": ["node1", "node2"]
    },
    "parameters": {
        "duration": "5m",
        "severity": "medium"
    }
}

response = client.create_chaos_experiment(experiment)
print(f"Experiment ID: {response['id']}")
```

#### 查询实验状态
```python
# 获取实验状态
status = client.get_experiment_status("exp-001")
print(f"Status: {status['status']}")

# 列出所有实验
experiments = client.list_experiments()
for exp in experiments:
    print(f"{exp['id']}: {exp['name']} - {exp['status']}")
```

### Orchid 监控

```bash
# 查看服务状态
yt get //sys/chaos_cache/orchid/

# 查看缓存统计
yt get //sys/chaos_cache/orchid/cache/stats

# 查看活跃实验
yt get //sys/chaos_cache/orchid/experiments/active
```

## 实现原理

### 缓存策略

1. **LRU 淘汰** - 使用最近最少使用算法
2. **分级缓存** - 热数据和冷数据分离存储
3. **预取机制** - 预测性加载相关数据
4. **压缩存储** - 压缩存储以节省内存

### 一致性保证

- **最终一致性** - 保证数据的最终一致性
- **版本控制** - 使用版本号管理数据更新
- **冲突解决** - 自动解决数据冲突

### 故障恢复

```cpp
// 故障恢复流程
void TChaosCacheService::HandleFailure(const TError& error) {
    // 1. 记录故障信息
    Logger->LogError(error);

    // 2. 触发告警
    AlertManager->TriggerAlert(error);

    // 3. 执行恢复操作
    if (error.IsRetriable()) {
        RetryManager->ScheduleRetry();
    }

    // 4. 降级服务
    DegradationManager->ApplyDegradation();
}
```

## 监控和告警

### 关键指标

1. **缓存命中率**
   - `cache.hit_rate` - 缓存命中率
   - `cache.miss_rate` - 缓存未命中率

2. **实验统计**
   - `experiments.active` - 活跃实验数
   - `experiments.completed` - 已完成实验数
   - `experiments.failed` - 失败实验数

3. **系统性能**
   - `memory.usage` - 内存使用量
   - `cpu.usage` - CPU 使用率
   - `request.latency` - 请求延迟

### 告警规则

```yaml
alerts:
  - name: "HighFailureRate"
    condition: "failure_rate > 0.1"
    duration: "5m"

  - name: "LowCacheHitRate"
    condition: "cache.hit_rate < 0.8"
    duration: "10m"

  - name: "ServiceDown"
    condition: "service.health == false"
    duration: "1m"
```

## 最佳实践

### 实验设计

1. **渐进式测试** - 从小规模实验开始
2. **金丝雀发布** - 使用金丝雀策略
3. **监控先行** - 确保有完善的监控
4. **回滚准备** - 准备快速回滚方案

### 安全考虑

1. **权限控制** - 严格控制实验权限
2. **范围限制** - 限制实验影响范围
3. **时间窗口** - 设置合理的执行时间
4. **审批流程** - 建立实验审批机制

### 性能优化

1. **批量操作** - 使用批量 API
2. **异步处理** - 非阻塞的异步操作
3. **连接池** - 复用数据库连接
4. **索引优化** - 优化查询索引

## 故障排查

### 常见问题

1. **服务启动失败**
   - 检查配置文件格式
   - 验证端口是否被占用
   - 确认集群连接信息

2. **缓存失效**
   - 检查内存使用情况
   - 验证 TTL 设置
   - 查看错误日志

3. **实验执行失败**
   - 确认目标节点状态
   - 检查权限配置
   - 验证实验参数

### 调试命令

```bash
# 查看详细日志
tail -f /var/log/ytsaurus/chaos_cache.log

# 检查内存使用
yt get //sys/chaos_cache/orchid/memory

# 查看服务状态
yt get //sys/chaos_cache/orchid/health
```

## 相关文档

- [YTsaurus 架构概述](../../../README.md)
- [混沌工程指南](../../../docs/chaos_engineering.md)
- [故障注入文档](../../../docs/fault_injection.md)
- [监控系统文档](../../../docs/monitoring.md)

## API 参考

### RPC 服务接口

```cpp
// 实验管理接口
service IChaosCacheService {
    rpc PutExperiment(TPutExperimentReq) returns (TPutExperimentResp);
    rpc GetExperiment(TGetExperimentReq) returns (TGetExperimentResp);
    rpc ListExperiments(TListExperimentsReq) returns (TListExperimentsResp);
    rpc DeleteExperiment(TDeleteExperimentReq) returns (TDeleteExperimentResp);
    rpc UpdateExperimentStatus(TUpdateExperimentStatusReq) returns (TUpdateExperimentStatusResp);
}

// 缓存管理接口
service ICacheManagementService {
    rpc ClearCache(TClearCacheReq) returns (TClearCacheResp);
    rpc GetCacheStats(TGetCacheStatsReq) returns (TGetCacheStatsResp);
    rpc UpdateCacheConfig(TUpdateCacheConfigReq) returns (TUpdateCacheConfigResp);
}
```

### 配置选项

详见 `config.h` 中的详细配置定义。

## 许可证

本项目采用 Apache License 2.0 许可证。详见 [LICENSE](../../../LICENSE) 文件。