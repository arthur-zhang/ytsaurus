# 栈回溯内省库

## 概述

这个库提供了运行时线程和 Fiber 的内省功能，允许检查系统中所有线程和协程的当前状态。它对于调试、性能分析和系统监控非常有用。

## 功能特性

### 线程内省
- 获取所有线程的当前状态
- 捕获线程的调用栈
- 获取线程名称和 ID
- 追踪 Trace 信息

### Fiber 内省
- 检查所有 Fiber 的状态
- 显示 Fiber 等待信息
- 捕获 Fiber 调用栈
- 关联 Fiber 和执行线程

### HTTP 接口
- 提供 HTTP 接口查看内省信息
- 支持 JSON 格式输出
- 实时状态查询

## 文件说明

### 核心文件

- `introspect.h` - 主要接口定义，包含数据结构和函数声明
- `introspect.cpp` - 通用实现
- `introspect_linux.cpp` - Linux 平台特定实现
- `introspect_dummy.cpp` - 空实现（用于不支持的平台）

### 私有文件

- `private.h` - 内部使用的私有定义
- `public.h` - 公共接口定义

### HTTP 服务

- `http/handler.h` - HTTP 处理器接口
- `http/handler.cpp` - HTTP 处理器实现

### 测试文件

- `unittests/` - 单元测试目录

## 核心数据结构

### TThreadIntrospectionInfo

线程内省信息结构：

```cpp
struct TThreadIntrospectionInfo {
    NThreading::TThreadId ThreadId;        // 线程 ID
    NConcurrency::TFiberId FiberId;        // 当前 Fiber ID
    TString ThreadName;                    // 线程名称
    NTracing::TTraceId TraceId;            // Trace ID
    std::string TraceLoggingTag;           // Trace 日志标签
    std::vector<const void*> Backtrace;    // 调用栈
};
```

### TFiberIntrospectionInfo

Fiber 内省信息结构：

```cpp
struct TFiberIntrospectionInfo {
    NConcurrency::EFiberState State;       // Fiber 状态
    NConcurrency::TFiberId FiberId;        // Fiber ID
    TInstant WaitingSince;                 // 开始等待时间
    NThreading::TThreadId ThreadId;        // 执行线程 ID
    TString ThreadName;                    // 执行线程名称
    NTracing::TTraceId TraceId;            // Trace ID
    std::string TraceLoggingTag;           // Trace 日志标签
    std::vector<const void*> Backtrace;    // 调用栈
};
```

## 核心接口

### 线程内省

```cpp
// 获取所有线程的内省信息
std::vector<TThreadIntrospectionInfo> IntrospectThreads();

// 格式化线程信息
TString FormatIntrospectionInfos(
    const std::vector<TThreadIntrospectionInfo>& infos);
```

### Fiber 内省

```cpp
// 获取所有 Fiber 的内省信息
std::vector<TFiberIntrospectionInfo> IntrospectFibers();

// 格式化 Fiber 信息
TString FormatIntrospectionInfos(
    const std::vector<TFiberIntrospectionInfo>& infos);
```

## 使用示例

### 基本使用

```cpp
#include <yt/yt/library/backtrace_introspector/public.h>

using namespace NYT::NBacktraceIntrospector;

// 获取所有线程信息
auto threadInfos = IntrospectThreads();
for (const auto& info : threadInfos) {
    Cout << "Thread " << info.ThreadName
         << " ID: " << info.ThreadId
         << " Fiber: " << info.FiberId
         << Endl;
}

// 获取所有 Fiber 信息
auto fiberInfos = IntrospectFibers();
for (const auto& info : fiberInfos) {
    Cout << "Fiber " << info.FiberId
         << " State: " << ToString(info.State)
         << " Thread: " << info.ThreadName
         << Endl;
}
```

### HTTP 集成

```cpp
// 创建 HTTP 处理器
auto handler = CreateIntrospectionHandler();

// 注册到 HTTP 服务器
httpServer->AddHandler("/introspect/threads", handler);
httpServer->AddHandler("/introspect/fibers", handler);
```

## 实现原理

### 平台特定实现

- **Linux**：使用 `libunwind` 或系统调用获取调用栈
- **其他平台**：提供空实现以避免编译错误

### 性能考虑

- 内省操作是同步的，会短暂暂停目标线程
- 调用栈深度有限制，避免无限递归
- 缓存线程名称以提高性能

### 线程安全

- 使用信号处理机制安全地暂停线程
- 避免死锁和竞态条件
- 最小化临界区时间

## 输出格式

### 线程信息输出示例

```
Thread: MainThread (ID: 140234567890)
  Fiber: 1001
  Trace: 12345678-1234-1234-1234-123456789abc
  Backtrace:
    0x00007ffff7a6d432: main
    0x00007ffff7a6d567: __libc_start_main
```

### Fiber 信息输出示例

```
Fiber: 1001
  State: Running
  Thread: WorkerThread-1 (ID: 140234567891)
  Trace: 87654321-4321-4321-4321-cba987654321
  Waiting since: Invalid instant
  Backtrace:
    0x0000555555556789: ProcessRequest
    0x0000555555556890: HandleConnection
```

## HTTP API

### 获取线程信息

```
GET /introspect/threads
```

响应格式：
```json
{
  "threads": [
    {
      "thread_id": "140234567890",
      "fiber_id": "1001",
      "thread_name": "MainThread",
      "trace_id": "12345678-1234-1234-1234-123456789abc",
      "backtrace": ["0x00007ffff7a6d432", "0x00007ffff7a6d567"]
    }
  ]
}
```

### 获取 Fiber 信息

```
GET /introspect/fibers
```

响应格式：
```json
{
  "fibers": [
    {
      "state": "Running",
      "fiber_id": "1001",
      "waiting_since": null,
      "thread_id": "140234567891",
      "thread_name": "WorkerThread-1",
      "trace_id": "87654321-4321-4321-4321-cba987654321",
      "backtrace": ["0x0000555555556789", "0x0000555555556890"]
    }
  ]
}
```

## 性能影响

- 内省操作会短暂暂停所有线程
- 调用栈捕获可能有性能开销
- 建议在调试和监控时使用，避免在生产环境频繁调用

## 安全考虑

- 内省功能可能暴露敏感信息
- 建议限制访问权限
- 在生产环境中考虑禁用或限制

## 依赖项

- YTsaurus 核心库
- libunwind（Linux 平台）
- 系统调用接口

## 平台支持

- **Linux x86_64**：完整支持
- **Linux aarch64**：完整支持
- **macOS**：有限支持
- **其他平台**：空实现

## 调试技巧

1. **死锁检测**：使用内省检查哪些线程持有锁
2. **性能分析**：分析 Fiber 的等待时间
3. **状态监控**：实时监控系统运行状态
4. **问题诊断**：获取异常发生时的调用栈

## 注意事项

1. 内省操作是同步的，可能影响实时性
2. 调用栈信息依赖于符号信息
3. 在 Release 构建中可能需要额外的调试信息
4. 避免在信号处理程序中调用内省功能