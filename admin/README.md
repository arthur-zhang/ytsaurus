# Admin 管理工具

本目录包含 YTsaurus 系统的管理和运维工具。

## 目录结构

- **dashboard_generator/** - 仪表盘生成器
  - 用于生成系统监控仪表盘的工具

- **dashboards/** - 监控仪表盘
  - 预配置的系统监控仪表盘模板
  - 包含各种系统指标的展示面板

- **snapshot_processing/** - 快照处理工具
  - 处理系统快照数据的工具集
  - 支持快照的创建、分析和恢复操作

- **timbertruck/** - 日志处理工具
  - 日志收集和处理系统
  - 支持大规模日志数据的聚合和分析

- **ya.make** - 构建配置文件
  - YaTool 构建系统的配置文件
  - 定义了各组件的依赖关系和构建规则

## 功能特性

### 仪表盘管理
- 自动生成监控仪表盘
- 支持自定义指标展示
- 实时数据可视化

### 快照处理
- 系统状态快照创建
- 快照数据分析
- 快照恢复功能

### 日志管理
- 分布式日志收集
- 日志数据处理
- 日志查询和分析

## 使用方法

### 构建组件
```bash
# 使用 ya make 构建系统
ya make admin

# 或使用 cmake 构建
cmake --build . --target admin_tools
```

### 运行仪表盘生成器
```bash
./dashboard_generator/bin/dashboard_generator --config config.yaml
```

### 处理快照
```bash
./snapshot_processing/bin/snapshot_processor --snapshot-path /path/to/snapshot
```

## 依赖项

- YTsaurus 核心库
- YaTool/CMake 构建系统
- 监控系统组件
- 日志处理库

## 实现原理

本模块采用模块化设计，各个工具相对独立：

1. **仪表盘生成器**：基于配置文件动态生成监控面板
2. **快照处理器**：读取和分析系统快照数据
3. **日志处理**：使用流式处理方式处理大规模日志数据

所有工具都遵循 YTsaurus 的统一接口规范，便于集成和扩展。