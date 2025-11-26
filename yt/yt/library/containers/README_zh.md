# 容器管理库

## 概述

这个库提供了 Linux 容器的管理和执行功能，支持通过 Porto 和 CRI (Container Runtime Interface) 两种方式管理容器。它用于 YTsaurus 中运行用户作业、隔离资源和监控系统状态。

## 功能特性

### 容器运行时支持

- **Porto 集成**：完整支持 Porto 容器运行时
- **CRI 支持**：支持 Kubernetes CRI 兼容的运行时
- **健康检查**：容器健康状态监控
- **资源跟踪**：实时资源使用监控

### 资源管理

- **CPU 控制**：CPU 限制和保证
- **内存管理**：内存限制和 OOM 处理
- **IO 限制**：磁盘 IO 带宽控制
- **网络管理**：网络隔离和配置

## 文件结构

### 核心组件

- `instance.h/cpp` - 容器实例管理
- `config.h/cpp` - 容器配置
- `helpers.h/cpp` - 辅助工具函数

### Porto 支持

- `porto_executor.h/cpp` - Porto 执行器实现
- `porto_resource_tracker.h/cpp` - 资源跟踪器
- `porto_health_checker.h/cpp` - 健康检查器
- `porto_helpers.h` - Porto 辅助函数

### CRI 支持 (`cri/` 目录)

- `cri_executor.h/cpp` - CRI 执行器
- `cri_api.h/cpp` - CRI API 封装
- `config.h/cpp` - CRI 配置
- `image_cache.h/cpp` - 镜像缓存管理

### Cgroup 支持

- `cgroup.h/cpp` - Cgroup 管理
- `cgroups_new.h/cpp` - 新版 Cgroup 支持
- `container_devices_checker.h/cpp` - 设备访问检查

## 核心接口

### IContainerExecutor

容器执行器接口：

```cpp
class IContainerExecutor {
public:
    // 创建容器
    virtual TFuture<TContainerCreationResult> CreateContainer(
        const TCreateContainerRequest& request) = 0;

    // 执行命令
    virtual TFuture<TContainerExecutionResult> ExecuteContainer(
        const TExecuteContainerRequest& request) = 0;

    // 销毁容器
    virtual TFuture<void> DestroyContainer(
        const TString& containerId) = 0;

    // 获取容器状态
    virtual TFuture<TContainerStatus> GetContainerStatus(
        const TString& containerId) = 0;
};
```

### TContainerInstance

容器实例表示：

```cpp
class TContainerInstance {
public:
    // 获取容器 ID
    const TString& GetId() const;

    // 获取容器统计信息
    TContainerStatistics GetStatistics() const;

    // 更新资源限制
    void UpdateResourceLimits(const TResourceLimits& limits);

    // 停止容器
    TFuture<void> Stop();
};
```

## 使用示例

### 使用 Porto 执行器

```cpp
#include <yt/yt/library/containers/porto_executor.h>

using namespace NYT::NContainers;

// 创建 Porto 执行器
auto portoExecutor = CreatePortoExecutor(TPortoExecutorConfig{
    .PortoPath = "/usr/bin/porto",
    .Timeout = TDuration::Seconds(30)
});

// 创建容器
TCreateContainerRequest createRequest;
createRequest.ContainerId = "my_container";
createRequest.Command = {"/bin/bash", "-c", "echo Hello"};
createRequest.ResourceLimits.CpuLimit = 2.0;
createRequest.ResourceLimits.MemoryLimit = 1_GB;

auto createResult = WaitFor(portoExecutor->CreateContainer(createRequest))
    .ValueOrThrow();

// 执行容器
TExecuteContainerRequest execRequest;
execRequest.ContainerId = createResult.ContainerId;

auto execResult = WaitFor(portoExecutor->ExecuteContainer(execRequest))
    .ValueOrThrow();

// 获取输出
Cout << "Exit code: " << execResult.ExitCode << Endl;
Cout << "Stdout: " << execResult.StdoutOutput << Endl;
```

### 使用 CRI 执行器

```cpp
#include <yt/yt/library/containers/cri/cri_executor.h>

// 创建 CRI 执行器
auto criExecutor = CreateCriExecutor(TCriExecutorConfig{
    .SocketPath = "/var/run/cri.sock",
    .RuntimeEndpoint = "unix:///var/run/containerd/containerd.sock"
});

// 拉取镜像
auto pullResult = WaitFor(criExecutor->PullImage(
    "docker://ubuntu:20.04")).ValueOrThrow();

// 创建并运行容器
TCreateContainerRequest createRequest;
createRequest.ImageId = pullResult.ImageId;
createRequest.Command = {"/bin/echo", "Hello from CRI"};

auto container = WaitFor(criExecutor->CreateContainer(createRequest))
    .ValueOrThrow();
```

### 资源监控

```cpp
// 获取容器统计信息
auto stats = container->GetStatistics();

// CPU 使用率
auto cpuUsage = stats.GetFieldValue(EStatField::CpuUsage);
auto cpuLimit = stats.GetFieldValue(EStatField::CpuLimit);
double cpuUtilization = static_cast<double>(cpuUsage) / cpuLimit;

// 内存使用
auto memoryUsage = stats.GetFieldValue(EStatField::MemoryUsage);
auto memoryLimit = stats.GetFieldValue(EStatField::MemoryLimit);

// IO 统计
auto ioReadBytes = stats.GetFieldValue(EStatField::IOReadByte);
auto ioWriteBytes = stats.GetFieldValue(EStatField::IOWriteByte);
```

## 资源字段

### CPU 字段

- `CpuUsage` - CPU 使用时间
- `CpuLimit` - CPU 限制
- `CpuGuarantee` - CPU 保证
- `CpuThrottled` - CPU 调节次数
- `ThreadCount` - 线程数量

### 内存字段

- `MemoryUsage` - 内存使用量
- `MemoryLimit` - 内存限制
- `MemoryGuarantee` - 内存保证
- `MaxMemoryUsage` - 最大内存使用
- `OomKills` - OOM 杀死次数

### IO 字段

- `IOReadByte` - 读取字节数
- `IOWriteByte` - 写入字节数
- `IOOps` - IO 操作数
- `IOBytesLimit` - IO 带宽限制

## 配置选项

### Porto 配置

```cpp
struct TPortoExecutorConfig {
    TString PortoPath = "/usr/bin/porto";           // Porto 可执行文件路径
    TDuration Timeout = TDuration::Seconds(30);     // 操作超时
    int RetryCount = 3;                             // 重试次数
    bool EnableVerboseLogging = false;             // 详细日志
};
```

### CRI 配置

```cpp
struct TCriExecutorConfig {
    TString SocketPath = "/var/run/cri.sock";       // CRI socket 路径
    TString RuntimeEndpoint;                        // 运行时端点
    TString ImageEndpoint;                          // 镜像服务端点
    TDuration Timeout = TDuration::Minutes(5);      // 操作超时
};
```

## 实现原理

### Porto 交互

- 通过 Unix socket 与 Porto 守护进程通信
- 使用 Porto 命令行接口执行操作
- 解析 Porto 输出获取状态信息

### CRI 交互

- 使用 gRPC 与 CRI 运行时通信
- 实现 CRI 协议的所有必要操作
- 支持镜像管理和容器生命周期

### 资源监控

- 定期读取 cgroup 统计信息
- 计算使用率和趋势
- 触发警报和自动处理

## 错误处理

### 常见错误类型

- `EErrorCode::Timeout` - 操作超时
- `EErrorCode::ResourceNotFound` - 容器不存在
- `EErrorCode::PermissionDenied` - 权限不足
- `EErrorCode::ResourceExhausted` - 资源耗尽
- `EErrorCode::ContainerFailed` - 容器执行失败

### 错误恢复

- 自动重试机制
- 资源清理
- 状态同步
- 降级处理

## 性能优化

### 批量操作

- 批量创建容器
- 批量更新配置
- 批量收集统计

### 缓存机制

- 容器状态缓存
- 镜像缓存
- 配置缓存

### 异步处理

- 非阻塞操作
- 并发执行
- 流水线处理

## 安全考虑

### 隔离机制

- 进程隔离
- 文件系统隔离
- 网络隔离
- 设备访问控制

### 特权控制

- 最小权限原则
- 能力限制
- 安全上下文
- 审计日志

## 依赖项

- Porto 容器运行时（可选）
- CRI 兼容运行时（可选）
- cgroups v1/v2
- Linux 内 namespaces

## 平台支持

- Linux x86_64
- Linux aarch64

## 最佳实践

1. **资源规划**
   - 合理设置资源限制
   - 监控资源使用
   - 预留安全余量

2. **错误处理**
   - 实现重试逻辑
   - 记录详细日志
   - 提供恢复机制

3. **性能优化**
   - 使用批量操作
   - 缓存常用数据
   - 避免频繁查询

## 故障排除

### 常见问题

1. **Porto 连接失败**
   - 检查 Porto 服务状态
   - 验证 socket 权限
   - 确认版本兼容性

2. **资源限制不生效**
   - 检查 cgroup 挂载
   - 验证内核支持
   - 确认权限设置

3. **容器创建失败**
   - 检查镜像可用性
   - 验证配置正确性
   - 查看详细错误日志

### 调试工具

- `portoctl` - Porto 命令行工具
- `crictl` - CRI 调试工具
- `strace` - 系统调用跟踪
- `journalctl` - 系统日志查看