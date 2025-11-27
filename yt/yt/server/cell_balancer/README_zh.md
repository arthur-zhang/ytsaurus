# Cell Balancer - Cell 平衡器服务

## 概述

Cell Balancer 是 YTsaurus 分布式系统中的关键组件，负责管理和平衡集群中的 Tablet Cell。它确保 Tablet Cell 在节点间均匀分布，优化集群资源利用率，并提供自动故障恢复能力。该服务同时包含 Bundle Controller 功能，用于管理 Tablet Cell Bundle。

## 核心功能

### 1. Cell 管理
- **Cell 跟踪** - 监控所有 Tablet Cell 的状态和位置
- **生命周期管理** - 处理 Cell 的创建、迁移和删除
- **故障检测** - 自动检测失效的 Cell 并触发恢复流程
- **停机时间跟踪** - 记录和分析 Cell 的停机历史

### 2. 负载均衡
- **自动平衡** - 基于负载指标自动重新分布 Cell
- **资源优化** - 优化 CPU、内存和网络资源的利用
- **热点缓解** - 识别并缓解资源热点
- **容量规划** - 预测资源需求并提前规划

### 3. Bundle 管理
- **Bundle 调度** - 管理 Tablet Cell Bundle 的生命周期
- **动态扩缩容** - 根据负载自动调整 Bundle 规模
- **版本管理** - 管理 Bundle 的版本升级和回滚
- **配置管理** - 动态更新 Bundle 配置

### 4. Chaos 调度
- **混沌测试支持** - 支持混沌工程实验
- **故障注入** - 可控地注入故障以测试系统韧性
- **恢复验证** - 验证系统在故障后的恢复能力

## 架构设计

### 核心组件

#### 1. Bundle Controller
```cpp
class IBundleController : public TRefCounted
{
    virtual void Start() = 0;
    virtual void ExecuteIteration(bool dryRun) = 0;
    virtual NYTree::IYPathServicePtr CreateOrchidService() = 0;
};
```
负责管理特定的 Tablet Cell Bundle，执行平衡操作和状态维护。

#### 2. Bundle Scheduler
- 实现复杂的调度算法
- 管理待处理的操作队列
- 协调多个 Bundle 之间的资源分配
- 处理优先级和资源约束

#### 3. Cell Tracker
- 实时跟踪 Cell 状态变化
- 维护 Cell 元数据
- 检测异常和故障
- 触发自愈流程

#### 4. Cluster State Provider
- 提供集群全局状态视图
- 聚合节点和 Cell 的指标
- 支持查询和过滤功能

#### 5. Chaos Scheduler
- 管理混沌实验的执行
- 控制故障注入的时机和范围
- 收集和分析实验结果

### 数据流

1. **状态收集** - 从 Master 获取集群状态
2. **分析决策** - 基于策略和算法做出平衡决策
3. **操作执行** - 通过 Master 执行 Cell 迁移等操作
4. **结果反馈** - 收集操作结果并更新状态

## 配置说明

### 主要配置项

```yaml
cell_balancer:
  # 调度周期
  schedule_interval: 30s

  # 平衡阈值
  balance_threshold:
    cpu_usage: 0.8
    memory_usage: 0.85
    tablet_count: 100

  # Bundle 配置
  bundle_controller:
    enabled: true
    dry_run: false

  # 混沌测试配置
  chaos_scheduler:
    enabled: false
    max_failures: 10
```

### 动态配置

Cell Balancer 支持运行时更新配置，无需重启服务：

```bash
# 更新平衡参数
yt set //sys/cell_balancer/@config/balance_threshold/cpu_usage 0.9

# 切换干运行模式
yt set //sys/cell_balancer/@config/bundle_controller/dry_run true
```

## 使用方法

### 启动服务

```bash
# 直接启动
./ytserver-cell-balancer --config cell_balancer.yaml

# 或通过 ytserver-all
./ytserver-all bundle-controller --config cell_balancer.yaml
```

### 监控和调试

#### Orchid 接口

```bash
# 查看整体状态
yt get //sys/cell_balancer/orchid/

# 查看 Bundle 信息
yt get //sys/cell_balancer/orchid/bundles

# 查看调度队列
yt get //sys/cell_balancer/orchid/scheduler/queue
```

#### 日志分析

```bash
# 查看调度日志
grep "Scheduling" /var/log/ytsaurus/cell_balancer.log

# 查看错误日志
grep "ERROR" /var/log/ytsaurus/cell_balancer.log
```

### 手动干预

```bash
# 触发一次平衡操作
yt set //sys/cell_balancer/@force_balance true

# 暂停特定 Bundle
yt set //sys/cell_balancer/orchid/bundles/my_bundle/@paused true

# 添加手动操作
yt insert //sys/cell_balancer/orchid/scheduler/manual_operations "{...}"
```

## 实现原理

### 平衡算法

1. **负载评估** - 计算每个节点的综合负载分数
2. **差异识别** - 找出负载最高和最低的节点
3. **迁移规划** - 选择合适的 Cell 进行迁移
4. **影响评估** - 预估迁移对系统的影响
5. **执行决策** - 选择最优的执行时机

### 策略配置

支持多种平衡策略：

- **贪婪策略** - 总是选择收益最大的操作
- **保守策略** - 优先保证系统稳定性
- **激进策略** - 追求最大程度的平衡
- **自定义策略** - 基于用户定义的规则

### 约束处理

在平衡过程中考虑多种约束：

- 资源容量约束
- 网络带宽约束
- 数据本地性约束
- 亲和性约束
- 反亲和性约束

## 性能优化

### 关键优化点

1. **增量计算** - 只处理变化的部分
2. **并行处理** - 并行执行独立操作
3. **缓存机制** - 缓存频繁查询的数据
4. **批量操作** - 合并多个小操作

### 扩展性设计

- **分片处理** - 将大规模集群划分为多个分片
- **异步执行** - 使用异步模型避免阻塞
- **状态分离** - 分离热数据和冷数据

## 故障处理

### 常见故障场景

1. **Master 连接中断**
   - 自动重连机制
   - 缓存降级策略

2. **配置错误**
   - 配置验证
   - 默认值回退

3. **资源不足**
   - 操作队列管理
   - 优先级调度

4. **数据不一致**
   - 状态校验
   - 自动修复

### 故障恢复

```cpp
// 自动恢复流程示例
void TBundleController::HandleFailure(const TError& error) {
    // 记录故障信息
    // 评估故障影响
    // 制定恢复计划
    // 执行恢复操作
    // 验证恢复结果
}
```

## 最佳实践

### 生产环境建议

1. **资源规划** - 预留足够的系统资源
2. **监控告警** - 设置完善的监控指标
3. **备份策略** - 定期备份关键配置
4. **版本管理** - 使用蓝绿部署策略
5. **容量评估** - 定期评估和调整容量

### 调优建议

1. **调整调度频率** - 根据集群规模调整
2. **优化阈值设置** - 基于实际负载特征
3. **使用干运行模式** - 测试新配置
4. **分批执行操作** - 避免集群抖动

## 相关文档

- [YTsaurus 架构概述](../../../README.md)
- [Tablet 服务文档](../../tablet/README_zh.md)
- [Master 服务](../master/README_zh.md)
- [集群运维指南](../../../docs/operations.md)

## API 参考

### RPC 服务

- `ListBundles()` - 列出所有 Bundle
- `GetBundleInfo()` - 获取 Bundle 详情
- `BalanceBundle()` - 触发 Bundle 平衡
- `CreateBundle()` - 创建新 Bundle
- `UpdateBundle()` - 更新 Bundle 配置

### 配置选项

详见 `config.h` 中的配置结构定义。

## 许可证

本项目采用 Apache License 2.0 许可证。详见 [LICENSE](../../../LICENSE) 文件。