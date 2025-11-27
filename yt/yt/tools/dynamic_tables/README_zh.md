# dynamic_tables - 动态表工作负载均衡器

## 项目描述

`dynamic_tables` 是 YTsaurus 系统中用于动态表工作负载均衡的工具集。该工具主要用于监控、分析和优化 YTsaurus 动态表中 tablet 的分布，通过智能算法实现负载均衡，提高系统性能。

该工具集包含以下主要组件：
- **balancer** - 实时负载均衡器
- **simulator** - 负载均衡模拟器
- **lib** - 核心算法库
- **plotter** - 数据可视化工具

## 功能特性

### 负载均衡功能
- **实时监控**：持续监控动态表的负载状况
- **智能调度**：基于多种算法的 tablet 迁移决策
- **可视化分析**：生成负载分布图表
- **模拟测试**：支持负载均衡策略的模拟验证

### 算法支持
- **Simple 算法**：简单的贪心算法，平衡指定指标
- **Static Greedy 算法**：静态贪心策略
- **Realtime 算法**：实时响应式均衡算法
- **可扩展架构**：支持自定义均衡算法

## 文件结构

```
dynamic_tables/
├── tablet_workload_balancer/
│   ├── balancer/              # 实时负载均衡器
│   │   └── __main__.py       # 均衡器主程序
│   ├── simulator/            # 负载均衡模拟器
│   │   └── __main__.py       # 模拟器主程序
│   ├── plotter/             # 数据可视化工具
│   └── lib/                 # 核心库
│       ├── algorithms/       # 均衡算法实现
│       │   ├── base.py      # 算法基类
│       │   ├── simple.py    # 简单算法
│       │   ├── static_greedy.py  # 静态贪心算法
│       │   ├── realtime.py  # 实时算法
│       │   └── utils.py     # 工具函数
│       ├── fields.py        # 字段定义
│       ├── load.py          # 数据加载模块
│       ├── plot.py          # 绘图模块
│       └── models.py        # 数据模型
└── ya.make                   # 构建配置
```

## 使用方法

### 1. 实时负载均衡器

```bash
# 一次性均衡
python -m yt.yt.tools.dynamic_tables.tablet_workload_balancer.balancer \
    --one-shot \
    --directory //sys/tables \
    --config '{"opt_field":"cpu_usage","plot_field":"cpu_usage"}' \
    --algorithm simple

# 周期性均衡
python -m yt.yt.tools.dynamic_tables.tablet_workload_balancer.balancer \
    --period 300 \
    --directory //sys/tables \
    --config '{"opt_field":"cpu_usage"}' \
    --algorithm simple \
    --dry-run
```

### 2. 负载均衡模拟器

```bash
# 运行模拟
python -m yt.yt.tools.dynamic_tables.tablet_workload_balancer.simulator \
    --stat stat.json \
    --cells cells.json \
    --algorithm simple \
    --config '{"opt_field":"cpu_usage","plot_field":"cpu_usage"}' \
    --plot-directory ./plots

# 生成所有字段的均衡方案
python -m yt.yt.tools.dynamic_tables.tablet_workload_balancer.simulator \
    --stat stat.json \
    --cells cells.json \
    --by-all-fields
```

## 实现原理

### 核心架构

1. **数据收集**：从 YTsaurus 集群收集 tablet 负载统计数据
2. **状态建模**：将 tablet、cell、node 之间的关系建模为图结构
3. **算法决策**：基于选定的均衡算法计算最优 tablet 分布
4. **动作执行**：执行 tablet 迁移操作
5. **结果验证**：验证均衡效果并生成报告

### 均衡算法

#### Simple 算法
- 找出负载最高和最低的 cell
- 将最高负载 cell 中负载最大的 tablet 移动到最低负载的 cell
- 适用于简单的负载均衡场景

#### Static Greedy 算法
- 基于全局信息进行静态优化
- 计算使总体负载方差最小的 tablet 分布
- 适用于可预测的负载模式

#### Realtime 算法
- 响应实时负载变化
- 考虑迁移成本和收益
- 适用于动态变化的环境

## 命令行参数说明

### Balancer 参数

- `--directory`：要均衡的表目录路径
- `--tables`：指定要均衡的表列表（可选）
- `--period`：均衡周期（秒）
- `--one-shot`：执行一次性均衡
- `--algorithm`：均衡算法类型
- `--config`：算法配置（YSON 格式）
- `--dry-run`：仅模拟，不执行实际操作
- `--plot-directory`：图表输出目录
- `--legend`：在图表中显示图例
- `--percentiles`：指定要显示的百分位数

### Simulator 参数

- `--stat`：统计数据文件路径
- `--cells`：cell 布局文件路径
- `--offset`：历史统计数据偏移量
- `--algorithm`：模拟算法类型
- `--config`：算法配置
- `--plot-directory`：图表输出目录
- `--by-all-fields`：为所有字段生成均衡方案
- `--list-fragment-format`：使用 list fragment 格式的 YSON 文件

## 使用示例

### 基础使用示例

```bash
# 1. 一次性均衡 CPU 负载
python -m yt.yt.tools.dynamic_tables.tablet_workload_balancer.balancer \
    --one-shot \
    --directory //sys/tables \
    --config '{"opt_field":"cpu_usage"}' \
    --algorithm simple

# 2. 基于 CPU 使用率进行均衡，但绘制内存使用率图表
python -m yt.yt.tools.dynamic_tables.tablet_workload_balancer.balancer \
    --one-shot \
    --directory //sys/tables \
    --config '{"opt_field":"cpu_usage","plot_field":"memory_usage"}' \
    --algorithm simple

# 3. 干运行模式，仅输出将要执行的动作
python -m yt.yt.tools.dynamic_tables.tablet_workload_balancer.balancer \
    --one-shot \
    --directory //sys/tables \
    --config '{"opt_field":"cpu_usage"}' \
    --algorithm simple \
    --dry-run
```

### 高级使用示例

```bash
# 周期性均衡，每 5 分钟执行一次
python -m yt.yt.tools.dynamic_tables.tablet_workload_balancer.balancer \
    --period 300 \
    --directory //sys/tables \
    --config '{"opt_field":"cpu_usage"}' \
    --algorithm realtime \
    --plot-directory /tmp/balancer_plots \
    --legend \
    --percentiles "[50,95,99]"

# 模拟历史数据
python -m yt.yt.tools.dynamic_tables.tablet_workload_balancer.simulator \
    --stat historical_stats.json \
    --cells cell_layouts.json \
    --algorithm static_greedy \
    --config '{"opt_field":"disk_read_rate","plot_field":"disk_write_rate"}' \
    --plot-directory ./simulation_results
```

## 依赖项

### Python 库依赖
- `yt`：YTsaurus Python 客户端
- `matplotlib`：数据可视化
- `numpy`：数值计算
- `argparse`：命令行参数解析

### YTsaurus 集群依赖
- YTsaurus 集群访问权限
- 相关表的读取权限
- Tablet cell 的管理权限（如需实际执行迁移）

## 相关概念

### Tablet
动态表的水平分片单元，每个 tablet 负责表的一部分数据范围。

### Tablet Cell
运行 tablet 的计算资源单元，一个 cell 可以运行多个 tablet。

### 负载指标
用于衡量 tablet 负载的各种指标：
- `cpu_usage`：CPU 使用率
- `memory_usage`：内存使用量
- `disk_read_rate`：磁盘读取速率
- `disk_write_rate`：磁盘写入速率
- `network_in_rate`：网络入站速率
- `network_out_rate`：网络出站速率

## 最佳实践

### 配置建议
1. **指标选择**：根据实际业务场景选择合适的优化指标
2. **周期设置**：均衡周期不宜过短，避免频繁迁移影响性能
3. **干运行**：生产环境使用前建议先用 `--dry-run` 模式测试
4. **监控**：定期检查生成的图表，评估均衡效果

### 性能优化
1. **批量操作**：尽量批量执行 tablet 迁移，减少系统开销
2. **迁移成本**：考虑 tablet 迁移的成本，避免不必要的小幅度优化
3. **阈值设置**：设置合理的负载差异阈值，避免过度均衡

### 故障处理
1. **异常恢复**：均衡过程中的异常不会影响集群正常运行
2. **状态验证**：均衡后验证 tablet 状态和集群健康度
3. **回滚策略**：保留原始配置，支持快速回滚

## 注意事项

1. **权限要求**：执行实际均衡需要对 tablet cell 的管理权限
2. **性能影响**：tablet 迁移会暂时影响相关表的性能
3. **数据一致性**：均衡过程中确保数据一致性不受影响
4. **集群版本**：确保工具版本与 YTsaurus 集群版本兼容
5. **资源消耗**：实时监控会消耗一定的计算资源，合理规划监控频率