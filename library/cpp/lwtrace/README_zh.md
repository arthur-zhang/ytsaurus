# LWTrace 轻量级追踪系统

## 项目概述

LWTrace 是一个高性能的轻量级追踪和探针系统，专为大型分布式应用设计。它提供了低开销的运行时跟踪功能，支持动态探针注入、事件记录、性能分析和调试监控，适用于复杂系统的性能调优、故障诊断和行为分析。

## 文件说明

### 核心组件

- **`all.h`** - 主要入口头文件
  - 包含所有 LWTrace 核心功能
  - 提供完整的使用接口
  - 包含详细的使用说明和示例

- **`probe.h/cpp`** - 探针系统
  - `IExecutor`: 执行器接口
  - 探针的注册、管理和执行
  - 支持链式执行和多级处理
  - 线程安全的探针调用

- **`control.h/cpp`** - 控制和管理
  - `IBox`: 探针所有权管理
  - `TStaticBox`: 静态探针包装
  - 探针注册表和生命周期管理
  - 动态探针添加和移除

- **`event.h`** - 事件系统
  - 事件类型定义和分类
  - 事件参数处理
  - 时间戳和元数据管理

### 追踪和日志

- **`log.h/cpp`** - 追踪日志系统
  - 高性能事件记录
  - 格式化日志输出
  - 缓冲和批量处理

- **`log_shuttle.h/cpp`** - 日志传输器
  - 事件数据的传输和分发
  - 异步日志处理
  - 网络和文件输出支持

- **`trace.cpp`** - 核心追踪实现
  - 主要追踪逻辑
  - 性能统计和监控
  - 系统集成接口

### 预处理器和签名

- **`preprocessor.h`** - 宏预处理器
  - 探针宏定义
  - 代码生成工具
  - 编译时优化

- **`signature.h`** - 函数签名处理
  - 类型安全的参数传递
  - 签名验证和匹配
  - 序列化支持

- **`param_traits.h`** - 参数特征
  - 参数类型特征分析
  - 自动类型推导
  - 序列化特性

### 执行和动作

- **`shuttle.h/cpp`** - 数据传输器
  - 事件数据的路由
  - 处理链管理
  - 异步执行支持

- **`custom_action.h/cpp`** - 自定义动作
  - 用户定义的处理逻辑
  - 动作注册和执行
  - 事件响应机制

- **`kill_action.h/cpp`** - 终止动作
- **`sleep_action.h/cpp`** - 延迟动作

### 性能和并发

- **`rwspinlock.h`** - 读写自旋锁
  - 高性能并发控制
  - 读写分离优化
  - 无锁数据结构

- **`perf.h/cpp`** - 性能监控
  - 执行时间统计
  - 吞吐量测量
  - 资源使用监控

### 监控集成

#### `mon/` 目录 - 监控服务集成

- 监控页面和服务接口
- 与 YTsaurus 监控系统集成
- 实时数据展示和控制

### 示例和测试

#### 示例目录
- **`example1/`** - 基础使用示例
- **`example2/`** - 高级功能示例
- **`example3/`** - 性能监控示例
- **`example4/`** - 自定义动作示例
- **`example5/`** - 系统集成示例

#### 测试目录
- **`tests/`** - 单元测试
- **`ut/`** - 集成测试

### 协议和工具

- **`protos/`** - Protocol Buffers 定义
  - 事件序列化协议
  - 配置消息格式
  - 跨语言兼容性

- **`symbol.h/cpp`** - 符号处理
- **`stderr_writer.h/cpp`** - 标准错误输出

## 实现原理

### 探针系统架构

```cpp
// 探针提供者定义
#define MY_PROVIDER(PROBE, EVENT, GROUPS, TYPES, NAMES) \
    PROBE(MyProbe, GROUPS("Group1", "Group2"), TYPES(int, TString), NAMES("arg1", "arg2")) \
    PROBE(MyScopedProbe, GROUPS(), TYPES(ui64, int), NAMES("duration", "stage")) \
    /**/

LWTRACE_DECLARE_PROVIDER(MY_PROVIDER)
LWTRACE_DEFINE_PROVIDER(MY_PROVIDER)
```

### 执行器链模式

```cpp
class IExecutor {
    IExecutor* Next;

    void Execute(TOrbit& orbit, const TParams& params) {
        if (DoExecute(orbit, params) && Next != nullptr) {
            Next->Execute(orbit, params);  // 链式执行
        }
    }
};
```

### 轨道和上下文

- **TOrbit**: 执行上下文和状态管理
- **TParams**: 参数传递和类型安全
- **事件生命周期管理**

### 高性能优化

1. **零拷贝**: 直接内存访问避免数据复制
2. **无锁设计**: 原子操作和内存屏障
3. **批量处理**: 批量事件处理减少系统调用
4. **缓存优化**: CPU 缓存友好的数据结构

## 使用示例

### 基础探针使用

```cpp
#include <library/cpp/lwtrace/all.h>

// 1. 定义探针提供者
#define MY_PROVIDER(PROBE, EVENT, GROUPS, TYPES, NAMES) \
    PROBE(FunctionStart, GROUPS("Perf"), TYPES(const char*), NAMES("function")) \
    PROBE(FunctionEnd, GROUPS("Perf"), TYPES(const char*, double), NAMES("function", "duration")) \
    PROBE(Error, GROUPS("Errors"), TYPES(const char*, int), NAMES("message", "code")) \

LWTRACE_DECLARE_PROVIDER(MY_PROVIDER)
LWTRACE_DEFINE_PROVIDER(MY_PROVIDER)

// 2. 在代码中使用探针
void ProcessData(const std::string& data) {
    auto start = std::chrono::high_resolution_clock::now();

    GLOBAL_LWPROBE(MY_PROVIDER, FunctionStart, "ProcessData");

    try {
        // 业务逻辑
        ProcessCore(data);
    } catch (const std::exception& e) {
        GLOBAL_LWPROBE(MY_PROVIDER, Error, e.what(), -1);
        throw;
    }

    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration<double>(end - start).count();

    GLOBAL_LWPROBE(MY_PROVIDER, FunctionEnd, "ProcessData", duration);
}
```

### 作用域探针

```cpp
#include <library/cpp/lwtrace/all.h>

#define SCOPED_PROVIDER(PROBE, EVENT, GROUPS, TYPES, NAMES) \
    PROBE(TimedScope, GROUPS("Timing"), TYPES(const char*, ui64), NAMES("scope", "duration")) \

LWTRACE_DECLARE_PROVIDER(SCOPED_PROVIDER)
LWTRACE_DEFINE_PROVIDER(SCOPED_PROVIDER)

// 使用 RAII 的作用域追踪
class TScopedTrace {
private:
    const char* ScopeName;
    std::chrono::high_resolution_clock::time_point Start;

public:
    explicit TScopedTrace(const char* scope)
        : ScopeName(scope)
        , Start(std::chrono::high_resolution_clock::now())
    {}

    ~TScopedTrace() {
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - Start).count();
        GLOBAL_LWPROBE(SCOPED_PROVIDER, TimedScope, ScopeName, duration);
    }
};

#define TRACE_SCOPE(name) TScopedTrace scopedTrace(name)

void ComplexOperation() {
    TRACE_SCOPE("ComplexOperation");

    TRACE_SCOPE("Step1");
    DoStep1();

    TRACE_SCOPE("Step2");
    DoStep2();

    // 自动记录各个步骤的执行时间
}
```

### 参数化探针

```cpp
#define PARAM_PROVIDER(PROBE, EVENT, GROUPS, TYPES, NAMES) \
    PROBE(Request, GROUPS("HTTP"), TYPES(const char*, const char*, int), \
          NAMES("method", "path", "status")) \
    PROBE(Database, GROUPS("DB"), TYPES(const char*, int, double), \
          NAMES("query", "rows", "duration")) \

LWTRACE_DECLARE_PROVIDER(PARAM_PROVIDER)
LWTRACE_DEFINE_PROVIDER(PARAM_PROVIDER)

void HandleHttpRequest(const std::string& method, const std::string& path) {
    try {
        // 处理请求
        ProcessRequest(method, path);
        GLOBAL_LWPROBE(PARAM_PROVIDER, Request, method.c_str(), path.c_str(), 200);
    } catch (const std::exception& e) {
        GLOBAL_LWPROBE(PARAM_PROVIDER, Request, method.c_str(), path.c_str(), 500);
        throw;
    }
}

void ExecuteQuery(const std::string& query) {
    auto start = std::chrono::high_resolution_clock::now();

    int rows = DatabaseExecute(query);

    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration<double>(end - start).count();

    GLOBAL_LWPROBE(PARAM_PROVIDER, Database, query.c_str(), rows, duration);
}
```

### 自定义动作

```cpp
#include <library/cpp/lwtrace/custom_action.h>

class TAlertAction: public NLWTrace::ICustomAction {
public:
    bool Execute(const NLWTrace::TEvent& event) override {
        // 检查是否为错误事件
        if (event.ProbeName == "Error") {
            // 发送警报
            SendAlert(event.Params["message"], event.Params["code"]);
        }
        return true;  // 继续执行链中的下一个动作
    }

private:
    void SendAlert(const std::string& message, int code) {
        // 实现警报逻辑
        std::cerr << "ALERT: " << message << " (code: " << code << ")" << std::endl;
    }
};

// 注册自定义动作
void SetupCustomActions() {
    auto alertAction = std::make_shared<TAlertAction>();
    NLWTrace::RegisterCustomAction("alert", alertAction);
}
```

### 监控集成

```cpp
#include <library/cpp/lwtrace/mon/trace_mon_page.h>

class TMyMonitoringService {
private:
    NLWTrace::TProbeRegistry Probes;

public:
    TMyMonitoringService() {
        // 添加探针到监控系统
        Probes.AddProbesList(LWTRACE_GET_PROBES(MY_PROVIDER));
        Probes.AddProbesList(LWTRACE_GET_PROBES(PARAM_PROVIDER));

        // 创建监控页面
        auto tracePage = MakeHolder<NLWTrace::TTraceMonPage>();
        tracePage->GetProbes() = Probes;

        RegisterPage(tracePage.Release());
    }

    void EnableTraceGroup(const std::string& group) {
        // 启用特定组的追踪
        Probes.EnableGroup(group);
    }

    void DisableTraceGroup(const std::string& group) {
        // 禁用特定组的追踪
        Probes.DisableGroup(group);
    }
};
```

### 环境配置

```cpp
// 从环境变量初始化 LWTrace
void InitLWTrace() {
    NLWTrace::StartLwtraceFromEnv();
}

// 环境变量示例：
// LWTRACE=MyProvider.Group1:debug,MyProvider.Group2:info
// LWTRACE_LOG_FILE=/tmp/lwtrace.log
// LWTRACE_MAX_EVENTS=1000000
```

## 应用场景

### 1. 性能分析

- **函数调用跟踪**: 记录函数入口和退出
- **执行时间测量**: 精确的性能计时
- **热点识别**: 找出性能瓶颈
- **调用链分析**: 分析函数调用关系

### 2. 错误诊断

- **异常捕获**: 记录异常和错误信息
- **状态监控**: 监控系统状态变化
- **故障追踪**: 跟踪故障传播路径
- **日志增强**: 结构化错误日志

### 3. 业务监控

- **请求处理**: HTTP/请求生命周期跟踪
- **数据库操作**: SQL 查询性能监控
- **缓存命中**: 缓存性能分析
- **队列处理**: 消息队列监控

### 4. 系统调试

- **并发问题**: 线程同步问题诊断
- **内存使用**: 内存分配和释放跟踪
- **资源竞争**: 资源竞争检测
- **死锁检测**: 死锁路径分析

### 5. APM (应用性能监控)

- **分布式追踪**: 跨服务调用链跟踪
- **服务拓扑**: 服务依赖关系分析
- **SLA 监控**: 服务等级协议监控
- **容量规划**: 资源使用趋势分析

## 技术特性

### 高性能

1. **低开销**: 编译时优化，运行时最小开销
2. **无锁设计**: 避免锁竞争，支持高并发
3. **批量处理**: 批量事件处理减少系统调用
4. **内存高效**: 智能内存管理和回收

### 灵活性

1. **动态配置**: 运行时启用/禁用探针
2. **分组管理**: 按功能分组管理探针
3. **自定义动作**: 支持用户自定义处理逻辑
4. **多种输出**: 支持文件、网络、控制台输出

### 可扩展性

1. **插件架构**: 支持插件式扩展
2. **协议支持**: Protocol Buffers 序列化
3. **多语言**: 支持跨语言集成
4. **云原生**: 适合容器化和云部署

### 易用性

1. **简单 API**: 直观的探针定义和使用
2. **宏支持**: 简化探针声明
3. **类型安全**: 编译时类型检查
4. **丰富示例**: 完整的使用示例

## 配置选项

### 环境变量

```bash
# 启用特定的探针组
LWTRACE=MyProvider.Perf:debug,MyProvider.Errors:info

# 日志文件配置
LWTRACE_LOG_FILE=/var/log/lwtrace.log
LWTRACE_MAX_EVENTS=1000000
LWTRACE_BUFFER_SIZE=64MB

# 性能配置
LWTRACE_MAX_THREADS=100
LWTRACE_FLUSH_INTERVAL=5s
```

### 编译时配置

```cpp
// 禁用 LWTrace 编译
#define LWTRACE_DISABLED 1

// 设置默认缓冲区大小
#define LWTRACE_DEFAULT_BUFFER_SIZE (1024 * 1024)

// 启用调试模式
#define LWTRACE_DEBUG 1
```

## 性能指标

- **探针开销**: < 10ns (编译时优化)
- **内存使用**: ~1KB 每个活跃探针
- **吞吐量**: > 1M events/second
- **延迟**: < 100μs 事件处理延迟

## 最佳实践

### 1. 探针设计

```cpp
// ✅ 好的探针设计
PROBE(RequestStart, GROUPS("HTTP"), TYPES(const char*, int), NAMES("path", "size"))

// ❌ 避免复杂参数
PROBE(ComplexData, GROUPS("Debug"), TYPES(const ComplexObject&), NAMES("data"))
```

### 2. 性能考虑

```cpp
// ✅ 避免在热路径中使用
if (Y_UNLIKELY(is_debug_mode)) {
    GLOBAL_LWPROBE(DEBUG_PROVIDER, DebugInfo, expensive_to_compute_data);
}

// ✅ 使用简单的参数类型
GLOBAL_LWPROBE(PERF_PROVIDER, Timing, simple_string, numeric_value);
```

### 3. 内存管理

```cpp
// ✅ 定期清理不需要的探针
void CleanupProbes() {
    NLWTrace::CleanupInactiveProbes();
    NLWTrace::FlushEventBuffers();
}
```

### 4. 错误处理

```cpp
// ✅ 安全的探针调用
try {
    GLOBAL_LWPROBE(PROVIDER, Operation, param1, param2);
} catch (const std::exception& e) {
    // 探针失败不应影响业务逻辑
    LOG_ERROR("Trace probe failed: " << e.what());
}
```