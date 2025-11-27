# YTServer All 统一服务器程序

## 概述

YTServer All 是 YTsaurus 分布式系统的统一服务器入口程序，它集成了所有 YTsaurus 组件的可执行文件。通过这一个二进制文件，可以启动 YTsaurus 集群中的任何服务组件。

## 功能特性

### 统一入口
- 单一二进制文件包含所有 YTsaurus 服务
- 根据命令行参数自动识别并启动对应的服务
- 支持所有核心组件的启动

### 支持的服务组件

#### 核心服务
- **master** - Master 服务，负责元数据管理和集群协调
- **clock** - 集群时钟服务，提供全局一致的时间戳
- **node** - 计算节点服务，负责数据存储和任务执行
- **scheduler** - 调度器服务，负责作业调度和资源分配
- **controller-agent** - 控制代理服务，负责作业生命周期管理

#### 代理服务
- **http-proxy** - HTTP 代理服务，提供 REST API 接口
- **proxy/rpc-proxy** - RPC 代理服务，处理客户端 RPC 请求
- **tcp-proxy** - TCP 代理服务
- **cypress-proxy** - Cypress 树形结构代理服务
- **kafka-proxy** - Kafka 集成代理服务

#### 辅助服务
- **job-proxy** - 作业代理服务，在计算节点上执行具体任务
- **exec** - 执行服务
- **tools** - 工具集服务
- **log-tailer** - 日志跟踪服务
- **discovery** - 服务发现服务
- **timestamp-provider** - 时间戳提供者服务

#### 管理服务
- **master-cache** - Master 缓存服务
- **chaos-cache** - 混沌缓存服务
- **cell-balancer/bundle-controller** - Cell 平衡器/捆绑控制器
- **queue-agent** - 队列代理服务
- **tablet-balancer** - Tablet 平衡器服务
- **query-tracker** - 查询跟踪服务
- **replicated-table-tracker** - 复制表跟踪服务
- **multi** - 多守护进程服务

## 使用方法

### 基本用法

```bash
# 启动 Master 服务
./ytserver-all --config master.config

# 或者通过符号链接
ln -s ytserver-all ytserver-master
./ytserver-master --config master.config

# 启动 Node 服务
./ytserver-all --config node.config

# 启动 HTTP 代理
./ytserver-all --config http_proxy.config
```

### 命令行选项

```bash
# 查看帮助
./ytserver-all --help

# 查看版本信息
./ytserver-all --version

# 查看构建信息
./ytserver-all --build
```

### 配置文件

每个服务都需要对应的配置文件，配置文件通常包含：
- 服务监听地址和端口
- 集群连接信息
- 日志配置
- 性能参数
- 安全设置

## 实现原理

### 程序架构

1. **程序映射表** - 维护所有可用服务的名称到启动函数的映射
2. **命令识别** - 根据可执行文件名称或第一个参数识别要启动的服务
3. **动态调用** - 运行时根据识别结果调用对应服务的主函数

### 关键组件

- `TProgramMap` - 程序映射表，存储所有可用服务
- `TProgramMapBuilder` - 映射表构建器，用于注册服务
- `TAllProgram` - 默认程序，处理未知命令和帮助信息

### 代码结构

```cpp
// 核心头文件包含各个服务的程序入口
#include <yt/yt/server/master/cell_master/program.h>
#include <yt/yt/server/clock_server/cluster_clock/program.h>
// ... 其他服务头文件

// 主函数逻辑
int main(int argc, const char** argv) {
    // 参数预处理
    // 尝试运行匹配的服务
    // 失败则显示帮助信息
}
```

## 构建和部署

### 构建要求

- C++20 兼容编译器
- CMake 3.22+
- 所有 YTsaurus 依赖库

### 构建步骤

```bash
# 配置构建
cmake -DCMAKE_BUILD_TYPE=Release .

# 构建
ninja ytserver-all

# 构建产物
# yt/yt/server/all/ytserver-all
```

### 部署方式

1. **单一二进制部署** - 复制 ytserver-all 到目标机器
2. **符号链接部署** - 创建各个服务的符号链接
3. **容器化部署** - 打包到 Docker 镜像中

## 最佳实践

### 生产环境

1. 使用专用的服务用户运行
2. 配置适当的系统限制（ulimit）
3. 启用日志轮转
4. 配置监控和告警
5. 使用 systemd 或其他服务管理器管理进程

### 开发环境

1. 使用调试模式编译
2. 启用详细日志
3. 使用 valgrind 或其他工具检查内存
4. 运行单元测试和集成测试

## 故障排查

### 常见问题

1. **服务无法启动** - 检查配置文件路径和格式
2. **端口占用** - 确认配置的端口未被其他进程占用
3. **权限问题** - 确认运行用户有足够的权限
4. **依赖缺失** - 确认所有动态库都已安装

### 调试方法

```bash
# 启用调试模式
./ytserver-all --verbose

# 查看详细日志
tail -f /var/log/ytsaurus/*.log

# 检查进程状态
ps aux | grep ytserver
```

## 相关文档

- [YTsaurus 架构概述](../../../README.md)
- [Master 服务](../master/README_zh.md)
- [Scheduler 服务](../scheduler/README_zh.md)
- [Node 服务](../node/README_zh.md)
- [配置参考](../../../docs/configuration.md)

## 许可证

本项目采用 Apache License 2.0 许可证。详见 [LICENSE](../../../LICENSE) 文件。