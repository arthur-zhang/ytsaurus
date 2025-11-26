# Porto 容器管理库

## 项目概述

Porto 是 YTsaurus 项目中的容器管理系统客户端库，提供了与 Porto 守护进程通信的接口。Porto 是一个高级容器运行时，支持进程隔离、资源限制、网络配置等功能。

### 核心功能
- **容器创建**：创建和管理容器实例
- **资源管理**：CPU、内存等资源限制和监控
- **进程隔离**：容器间进程隔离和通信
- **网络配置**：容器网络设置和管理
- **状态监控**：容器状态和性能指标监控

## 文件说明

### 核心文件
- **libporto.cpp** - Porto 客户端库主要实现
- **metrics.cpp** - 性能指标收集和报告
- **libporto_ut.cpp** - 单元测试

## 使用示例

### 基础容器操作
```cpp
#include <library/cpp/porto/libporto.h>

void BasicContainerExample() {
    // 连接 Porto 守护进程
    TPortoClient client;
    client.Connect();

    // 创建容器
    TString containerName = "my_container";
    TContainerProperties properties;
    properties.SetCommand("/bin/bash");
    properties.SetRootPath("/path/to/root");

    TError error = client.CreateContainer(containerName, properties);
    if (error) {
        printf("Failed to create container: %s\n", error.GetMessage().c_str());
        return;
    }

    // 启动容器
    error = client.StartContainer(containerName);
    if (error) {
        printf("Failed to start container: %s\n", error.GetMessage().c_str());
        return;
    }

    // 获取容器状态
    TContainerState state;
    client.GetContainerState(containerName, &state);
    printf("Container state: %s\n", state.ToString().c_str());

    // 停止容器
    client.StopContainer(containerName);

    // 删除容器
    client.DestroyContainer(containerName);
}
```

### 资源限制配置
```cpp
void ResourceLimitExample() {
    TPortoClient client;
    client.Connect();

    TString containerName = "limited_container";
    TContainerProperties properties;

    // 设置 CPU 限制
    properties.SetCpuLimit(2.0);  // 2 CPU cores

    // 设置内存限制
    properties.SetMemoryLimit(1024 * 1024 * 1024);  // 1GB

    // 设置网络带宽限制
    properties.SetNetworkLimit(100 * 1024 * 1024);  // 100MB/s

    // 创建并启动容器
    TError error = client.CreateContainer(containerName, properties);
    if (!error) {
        client.StartContainer(containerName);
    }
}
```

### 容器监控
```cpp
void ContainerMonitoringExample() {
    TPortoClient client;
    client.Connect();

    TString containerName = "monitored_container";

    // 获取容器指标
    TContainerMetrics metrics;
    TError error = client.GetContainerMetrics(containerName, &metrics);
    if (!error) {
        printf("CPU usage: %.2f%%\n", metrics.GetCpuUsage());
        printf("Memory usage: %zu bytes\n", metrics.GetMemoryUsage());
        printf("Network I/O: %zu bytes\n", metrics.GetNetworkIo());
    }

    // 获取容器列表
    TVector<TContainerInfo> containers;
    client.ListContainers(&containers);

    for (const auto& container : containers) {
        printf("Container: %s, State: %s\n",
               container.GetName().c_str(),
               container.GetState().ToString().c_str());
    }
}
```

## 实现原理

### 客户端-服务器架构
- **Unix Socket 通信**：通过 Unix Socket 与守护进程通信
- **协议封装**：封装 Porto 协议的消息格式
- **异步处理**：支持异步操作和回调机制
- **错误处理**：统一的错误处理和报告机制

### 资源抽象
- **CPU 资源**：CPU 核心数和时间片限制
- **内存资源**：内存使用量和交换空间限制
- **网络资源**：带宽和网络连接数限制
- **存储资源**：磁盘空间和 I/O 限制

### 进程管理
- **进程隔离**：使用 Linux 命名空间进行隔离
- **权限控制**：容器内进程的权限管理
- **生命周期管理**：完整的容器生命周期控制
- **信号处理**：容器内进程信号处理

## 应用场景

### 微服务部署
- **服务隔离**：不同服务的运行环境隔离
- **资源分配**：按需分配计算资源
- **服务发现**：容器网络和服务发现
- **负载均衡**：容器负载和流量管理

### 开发测试环境
- **环境一致性**：保证开发测试环境一致性
- **快速部署**：快速创建和销毁测试环境
- **资源限制**：限制测试环境的资源使用
- **环境隔离**：避免测试间的相互影响

### CI/CD 流水线
- **构建隔离**：每个构建任务独立环境
- **并行执行**：多个构建任务并行执行
- **资源优化**：优化构建资源的利用率
- **清理自动化**：自动清理构建环境

### 批处理任务
- **任务隔离**：批处理任务的运行隔离
- **资源控制**：控制批处理任务的资源使用
- **任务调度**：基于资源需求的任务调度
- **故障隔离**：任务故障不影响其他任务

## 性能特性

### 启动性能
- **快速启动**：毫秒级的容器启动时间
- **镜像优化**：优化的容器镜像加载
- **进程复用**：复用系统进程和资源
- **预分配优化**：预分配资源减少延迟

### 运行性能
- **低开销**：最小的运行时开销
- **高效调度**：优化的进程调度策略
- **网络性能**：高性能的容器网络
- **存储性能**：高效的容器存储访问

### 资源效率
- **内存共享**：容器间内存共享优化
- **CPU 调度**：智能的 CPU 资源调度
- **网络虚拟化**：高效的网络虚拟化
- **存储分层**：分层的存储策略

## 配置选项

### 容器配置
```cpp
// CPU 配置
properties.SetCpuLimit(4.0);              // CPU 核心数
properties.SetCpuGuarantee(2.0);           // CPU 保证值
properties.SetCpuPeriod(100000);           // CPU 周期

// 内存配置
properties.SetMemoryLimit(2ULL * 1024 * 1024 * 1024);  // 内存限制
properties.SetSwapLimit(1ULL * 1024 * 1024 * 1024);    // 交换空间限制

// 网络配置
properties.SetNetworkIngressLimit(100 * 1024 * 1024);   // 入站带宽限制
properties.SetNetworkEgressLimit(100 * 1024 * 1024);    // 出站带宽限制
```

### 安全配置
```cpp
// 权限配置
properties.SetUid(1000);                   // 用户 ID
properties.SetGid(1000);                   // 组 ID
properties.SetCapabilities("CAP_NET_ADMIN"); // 能力集

// 文件系统配置
properties.SetRootPath("/path/to/root");    // 根目录
properties.SetReadonly(true);               // 只读文件系统
properties.SetTmpfsSize(100 * 1024 * 1024); // 临时文件系统大小
```

## 最佳实践

### 资源管理
- **合理限制**：根据实际需求设置资源限制
- **监控使用**：持续监控资源使用情况
- **动态调整**：根据负载动态调整资源分配
- **资源回收**：及时回收不再使用的资源

### 安全考虑
- **最小权限**：遵循最小权限原则
- **网络安全**：配置适当的网络隔离
- **文件系统安全**：限制文件系统访问权限
- **定期更新**：定期更新容器和系统组件

### 性能优化
- **镜像优化**：优化容器镜像大小和层数
- **资源复用**：复用相同的资源和镜像
- **批量操作**：批量执行容器操作
- **缓存策略**：合理使用缓存机制