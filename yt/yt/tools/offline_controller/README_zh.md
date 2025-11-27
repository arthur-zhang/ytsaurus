# offline_controller - 离线控制器工具

## 项目描述

`offline_controller` 是 YTsaurus 系统的离线操作控制器工具，用于在离线模式下执行和管理 YTsaurus 操作。该工具模拟调度器和控制代理的功能，支持离线环境下的数据处理和任务执行。

## 功能特性

- **离线操作**：在离线环境下执行 YTsaurus 操作
- **调度模拟**：模拟 YTsaurus 调度器的功能
- **操作管理**：管理和监控操作的生命周期
- **资源管理**：处理计算资源的分配和调度
- **错误处理**：提供完善的错误处理和恢复机制

## 文件说明

- `main.cpp` - 主程序实现，包含操作控制逻辑
- `CMakeLists.txt` - CMake 构建配置文件（支持多平台）
- `ya.make` - YaTool 构建系统配置文件

## 使用方法

### 编译
```bash
# 使用 CMake 构建
cmake --build . --target offline_controller

# 或使用 ya 工具构建
ya make offline_controller
```

### 运行
```bash
./offline_controller [options] <operation-spec>
```

## 实现原理

该工具基于 YTsaurus 的控制器代理架构实现：

1. **操作初始化**：加载操作配置和规范
2. **资源分配**：模拟资源分配和调度决策
3. **任务执行**：执行具体的计算任务
4. **状态管理**：跟踪操作和任务的状态
5. **结果聚合**：收集和聚合执行结果

## 核心组件

- **TControllerAgent**：控制器代理实现
- **TOperationController**：操作控制器
- **TExecNodeDescriptor**：执行节点描述符
- **TChunkReader**：数据块读取器

## 使用示例

```bash
# 基本离线操作
./offline_controller --config operation_config.yson operation_spec.yson

# 带调试信息的执行
./offline_controller --verbose --debug --config config.yson spec.yson

# 指定工作目录
./offline_controller --work-dir /tmp/offline_work operation.yson
```

## 依赖项

### 核心依赖
- `yt/yt/server/controller_agent/` - 控制器代理库
- `yt/yt/server/lib/scheduler/` - 调度器库
- `yt/yt/client/api/` - YTsaurus 客户端 API
- `yt/yt/library/coredumper/` - 核心转储工具

### 系统依赖
- C++20 编译器
- CMake 3.22+
- YTsaurus 核心库

## 相关概念

### Controller Agent
YTsaurus 中的操作控制组件，负责管理和协调 MapReduce 等操作的执行。

### Operation
YTsaurus 中的数据处理任务，包括 MapReduce、Sort、Merge 等操作类型。

### Scheduler
调度器，负责将任务分配到可用的计算节点上执行。

## 最佳实践

1. **配置优化**：根据工作负载调整资源配置
2. **监控管理**：密切监控操作执行状态
3. **错误恢复**：配置适当的错误处理和重试策略
4. **资源规划**：合理规划计算资源使用

## 注意事项

- 离线模式需要预先准备所有必要的数据和配置
- 确保有足够的本地存储空间
- 生产环境使用前进行充分测试
- 定期备份重要的操作配置和结果