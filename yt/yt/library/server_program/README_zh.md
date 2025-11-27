# Server Program Library (服务器程序库)

## 项目概述 (Overview)

Server Program Library 是 YTsaurus 分布式系统的核心服务器程序框架，为构建高性能、可靠的服务器应用程序提供了统一的基础架构。该库封装了服务器程序的通用功能，包括配置管理、服务定位、生命周期管理、监控集成等关键组件，是所有 YTsaurus 服务器组件的基础框架。

该库设计为模块化和可扩展的架构，支持多种服务器类型的开发，包括 Master、Scheduler、Node、RPC Proxy 等核心服务。

## 核心功能 (Core Features)

### 基础服务器程序框架
- **TServerProgramBase**: 服务器程序基础类，提供通用功能和服务集成
- **TServerProgram<TConfig, TDynamicConfig>**: 模板化服务器程序类，支持静态和动态配置
- **生命周期管理**: 完整的服务启动、运行和关闭流程管理
- **线程管理**: 主线程命名和管理功能

### 配置管理系统
- **统一配置接口**: 基于 Yson 的配置序列化和反序列化
- **动态配置重载**: 运行时配置更新，无需重启服务
- **配置验证**: 自动配置参数验证和类型检查
- **分层配置**: 静态配置与动态配置分离管理

### 服务定位和依赖注入
- **Fusion 服务定位器**: 基于 Fusion 框架的服务定位机制
- **服务目录管理**: 统一的服务注册和发现
- **依赖注入**: 自动化依赖解析和注入

### 系统集成功能
- **内存锁定**: 内存页面锁定，防止内存交换
- **容器化支持**: Porto 容器资源跟踪和管理
- **核心转储**: 自动化核心转储生成和管理
- **性能监控**: Solomon 指标导出和性能分析
- **磁盘管理**: 热插拔磁盘管理支持

## 主要接口 (Main Interfaces)

### 服务器程序基础类

```cpp
#include <yt/yt/library/server_program/server_program.h>

class TMyServerProgram
    : public TServerProgram<TMyServerConfig, TMyServerDynamicConfig>
{
public:
    TMyServerProgram()
    {
        // 设置主线程名称
        SetMainThreadName("MyServerMain");
    }

protected:
    void DoStart() override
    {
        // 服务器启动逻辑
        auto serviceLocator = GetServiceLocator();
        auto serviceDirectory = GetServiceDirectory();

        // 初始化服务
        InitializeServices();

        // 启动服务器
        StartServer();

        // 永久运行（或直到收到停止信号）
        SleepForever();
    }

    void ValidateOpts() override
    {
        // 验证命令行选项
        TServerProgram::ValidateOpts();
        // 自定义验证逻辑
    }

    void TweakConfig() override
    {
        // 配置微调
        TServerProgram::TweakConfig();
        // 自定义配置调整
    }
};

int main(int argc, char** argv)
{
    TMyServerProgram program;
    return program.Run(argc, argv);
}
```

### 配置结构定义

```cpp
struct TMyServerConfig
    : public TServerProgramConfig
{
    // 自定义配置参数
    TString ListenAddress;
    int ListenPort = 9000;
    TDuration RpcTimeout = TDuration::Seconds(30);

    REGISTER_YSON_STRUCT(TMyServerConfig);

    static void Register(TRegistrar registrar)
    {
        TServerProgramConfig::Register(registrar);

        registrar.Parameter("listen_address", &TThis::ListenAddress)
            .Default("0.0.0.0");
        registrar.Parameter("listen_port", &TThis::ListenPort)
            .Default(9000);
        registrar.Parameter("rpc_timeout", &TThis::RpcTimeout)
            .Default(TDuration::Seconds(30));
    }
};

struct TMyServerDynamicConfig
    : public TYsonStruct
{
    std::optional<int> MaxConcurrentRequests;
    std::optional<TDuration> RequestTimeout;

    REGISTER_YSON_STRUCT(TMyServerDynamicConfig);

    static void Register(TRegistrar registrar)
    {
        registrar.Parameter("max_concurrent_requests", &TThis::MaxConcurrentRequests);
        registrar.Parameter("request_timeout", &TThis::RequestTimeout);
    }
};
```

### 配置使用示例

```cpp
void TMyServerProgram::DoStart()
{
    // 获取配置
    const auto& config = GetConfig();
    const auto& dynamicConfig = GetDynamicConfig();

    // 使用配置参数
    TString address = config->ListenAddress;
    int port = config->ListenPort;

    // 动态配置处理
    if (dynamicConfig->MaxConcurrentRequests) {
        SetMaxConcurrentRequests(*dynamicConfig->MaxConcurrentRequests);
    }

    // 配置服务器
    ConfigureServer(address, port, config->RpcTimeout);
}
```

## 使用方法 (Usage)

### 基本使用步骤

1. **包含头文件**
```cpp
#include <yt/yt/library/server_program/server_program.h>
```

2. **定义配置结构**
```cpp
// 继承 TServerProgramConfig 和 TYsonStruct
struct TMyConfig : public TServerProgramConfig { ... };
struct TMyDynamicConfig : public NYTree::TYsonStruct { ... };
```

3. **实现服务器程序类**
```cpp
class TMyProgram : public TServerProgram<TMyConfig, TMyDynamicConfig>
{
protected:
    void DoStart() override;
};
```

4. **配置服务集成**
```cpp
void TMyProgram::DoStart()
{
    auto serviceLocator = GetServiceLocator();
    // 注册和配置服务
}
```

5. **实现主函数**
```cpp
int main(int argc, char** argv)
{
    return TMyProgram().Run(argc, argv);
}
```

### 高级功能使用

#### 自定义服务定位器集成
```cpp
void TMyProgram::DoStart()
{
    auto serviceLocator = GetServiceLocator();

    // 注册自定义服务
    serviceLocator->RegisterService("my_service",
        NYT::New<TMyService>(config->MyServiceConfig));

    // 获取服务目录
    auto serviceDirectory = GetServiceDirectory();
    serviceDirectory->RegisterService("http_server", httpServer_);
}
```

#### 配置验证和微调
```cpp
void TMyProgram::ValidateOpts()
{
    TServerProgram::ValidateOpts();

    // 验证自定义选项
    if (config->ListenPort < 1024 && getuid() != 0) {
        THROW_ERROR_EXCEPTION("需要 root 权限绑定特权端口");
    }
}

void TMyProgram::TweakConfig()
{
    TServerProgram::TweakConfig();

    // 根据系统资源调整配置
    auto systemInfo = GetSystemInfo();
    if (systemInfo.AvailableMemory < 1_GB) {
        config->MaxConcurrentRequests =
            std::min(config->MaxConcurrentRequests, 100);
    }
}
```

## 性能考虑 (Performance Considerations)

### 内存管理优化
- **内存锁定**: 使用 `mlock()` 锁定关键内存页面，防止性能关键代码被交换
- **内存监控**: 集成内存使用监控和告警机制
- **堆大小限制**: 通过 TCMalloc 集成控制堆内存使用

### 启动性能
- **并发初始化**: 支持服务并发初始化，减少启动时间
- **延迟初始化**: 非关键服务延迟初始化，加快启动速度
- **缓存优化**: 配置解析和服务定位结果缓存

### 运行时性能
- **零拷贝配置**: 配置更新使用零拷贝机制
- **异步操作**: 所有 I/O 操作异步化，避免阻塞
- **内存池**: 使用预分配内存池减少动态分配开销

## 最佳实践 (Best Practices)

### 配置管理
1. **分层配置设计**: 静态配置和动态配置分离
2. **配置验证**: 实现完整的配置参数验证
3. **默认值设置**: 为所有配置参数提供合理默认值
4. **向后兼容**: 保持配置格式向后兼容性

### 服务设计
1. **依赖注入**: 使用服务定位器实现松耦合
2. **生命周期管理**: 正确实现服务的启动和停止序列
3. **错误处理**: 实现优雅的错误处理和恢复机制
4. **资源清理**: 确保所有资源正确释放

### 监控集成
1. **指标导出**: 集成 Solomon 监控指标
2. **健康检查**: 实现服务健康检查端点
3. **性能分析**: 启用性能分析和采样
4. **日志记录**: 使用结构化日志记录关键事件

### 部署运维
1. **容器化**: 支持 Porto 容器部署
2. **核心转储**: 配置自动化核心转储分析
3. **服务发现**: 集成服务注册和发现机制
4. **滚动升级**: 支持零停机滚动升级

## 依赖项 (Dependencies)

### 核心依赖
- **yt/yt/core/ytree**: Yson 结构和配置系统
- **yt/yt/library/fusion**: 服务定位和依赖注入框架
- **yt/yt/library/program**: 程序基础框架
- **yt/yt/library/containers**: 容器化支持
- **yt/yt/library/disk_manager**: 磁盘管理功能

### 系统依赖
- **Porto**: 容器运行时（可选）
- **TCMalloc**: 高性能内存分配器
- **CoreDump**: 核心转储工具
- **PerfTools**: 性能分析工具

### 监控依赖
- **yt/yt/library/profiling**: 性能监控框架
- **Solomon Exporter**: 监控指标导出器
- **Perf Event Profiler**: 性能事件分析器

## 注意事项 (Important Notes)

### 线程安全
- **主线程设置**: `SetMainThreadName()` 必须在构造函数中调用
- **服务并发**: 服务定位器是线程安全的，但服务实例本身需要确保线程安全
- **配置更新**: 动态配置更新是原子性的，但应用配置变化时需要注意并发

### 资源管理
- **内存锁定**: 内存锁定需要足够的权限和可用内存
- **文件描述符**: 注意文件描述符数量限制
- **端口绑定**: 特权端口需要 root 权限

### 配置注意
- **配置验证**: 总是验证配置参数的有效性
- **默认配置**: 确保默认配置在所有环境下都能工作
- **动态重载**: 不是所有配置都支持动态重载

### 错误处理
- **异常安全**: 使用 RAII 和异常安全的编程模式
- **资源清理**: 在析构函数中正确清理资源
- **优雅关闭**: 实现优雅的服务关闭流程

### 调试支持
- **核心转储**: 确保核心转储配置正确
- **符号信息**: 发布版本保留必要的调试符号
- **日志级别**: 支持运行时日志级别调整

该库为 YTsaurus 服务器程序提供了统一、可靠的基础框架，正确使用可以大大简化服务器应用的开发和部署。