# Concurrency 模块

## 模块概述

`yt/yt/core/concurrency` 模块是 YTsaurus 分布式系统的并发编程核心库，提供了完整的协程、线程池、异步编程和资源调度解决方案。该模块实现了高性能的用户态协程系统，支持细粒度的并发控制、公平共享调度和异步 I/O 操作，为整个 YTsaurus 系统提供高效的并发执行基础设施。

## 主要功能

### 1. 协程系统 (Fiber)
- **用户态协程**: 轻量级协程实现，避免系统线程开销
- **协程调度**: 协作式调度器，支持优先级和公平共享
- **栈管理**: 可配置大小的执行栈，支持 Small/Large/Huge 三种规格
- **上下文切换**: 高效的协程上下文切换机制

### 2. 线程池管理
- **通用线程池**: 可配置大小的线程池
- **公平共享线程池**: 支持公平共享调度的线程池
- **两级公平共享**: 高级的多层次公平共享调度
- **轮询器线程池**: 专门用于 I/O 轮询的线程池

### 3. 异步执行器
- **周期执行器**: 定期执行任务的执行器
- **重试执行器**: 支持自动重试的周期执行器
- **调度执行器**: 支持复杂调度的执行器
- **量化执行器**: 支持资源量化的执行器

### 4. 同步原语
- **异步信号量**: 支持异步等待的信号量
- **性能分析信号量**: 带性能监控的信号量
- **非阻塞队列**: 高性能的并发队列
- **异步流管道**: 用于异步数据传输的管道

### 5. 流量控制
- **吞吐量限制器**: 限制操作吞吐量的组件
- **可配置限制器**: 支持动态配置的限制器
- **相对限制器**: 基于相对比率的限制器
- **预取限制器**: 支持数据预取的限制器

### 6. 异步 I/O
- **异步输入流**: 支持异步读取的输入流
- **异步输出流**: 支持异步写入的输出流
- **零拷贝流**: 优化的零拷贝异步流
- **可刷新流**: 支持刷新操作的异步输出流

## 核心文件说明

### 协程系统
- **fiber.h**: 协程核心接口和类型定义
- **fiber_manager.h**: 协程管理器实现
- **execution_stack.h**: 执行栈管理
- **context_switch.h**: 上下文切换实现

### 线程池
- **thread_pool.h**: 通用线程池接口
- **fair_share_action_queue.h**: 公平共享动作队列
- **thread_pool_poller.h**: 轮询器线程池

### 执行器
- **periodic_executor.h**: 周期执行器
- **scheduled_executor.h**: 调度执行器
- **quantized_executor.h**: 量化执行器

### 同步原语
- **async_semaphore.h**: 异步信号量
- **nonblocking_queue.h**: 非阻塞队列
- **async_stream_pipe.h**: 异步流管道

## 使用示例

### 基本协程使用
```cpp
#include <yt/yt/core/concurrency/fiber.h>
#include <yt/yt/core/concurrency/scheduler_api.h>

using namespace NYT::NConcurrency;

// 在协程中运行
void MyAsyncFunction() {
    // 协程上下文中的异步操作
    WaitFor(AsyncOperation()).GetValue();

    // 让出控制权
    Yield();
}

// 启动协程
auto future = BIND(MyAsyncFunction).AsyncVia(GetSyncInvoker()).Run();
```

### 使用线程池
```cpp
#include <yt/yt/core/concurrency/thread_pool.h>

// 创建线程池
auto threadPool = CreateThreadPool(4, "MyThreadPool");

// 异步执行任务
auto future = BIND([=] {
    // 在线程池中执行的工作
    return DoWork();
}).AsyncVia(threadPool->GetInvoker()).Run();

// 等待结果
auto result = WaitFor(future).ValueOrThrow();
```

### 使用异步信号量
```cpp
#include <yt/yt/core/concurrency/async_semaphore.h>

// 创建信号量
auto semaphore = New<TAsyncSemaphore>(10);

// 获取信号量
auto acquiredFuture = semaphore->Acquire();
auto lease = WaitFor(acquiredFuture).Value();

// 使用资源
DoWork();

// 释放信号量
lease.Release();
```

### 使用周期执行器
```cpp
#include <yt/yt/core/concurrency/periodic_executor.h>

// 创建周期执行器
auto executor = New<TPeriodicExecutor>(
    GetSyncInvoker(),
    BIND([] { DoPeriodicWork(); }),
    TDuration::Seconds(1));

// 启动执行器
executor->Start();
```

## 配置选项

### 协程管理器配置
- **DefaultMaxIdleFibers**: 默认最大空闲协程数 (5000)
- **DefaultFiberStackPoolSize**: 默认栈池大小 (1000)

### 执行栈类型
- **Small**: 256KB (默认)
- **Large**: 8MB
- **Huge**: 64MB

## 依赖关系

- **yt/yt/core/actions**: 异步编程基础设施
- **yt/yt/core/misc**: 基础工具和错误处理
- **yt/yt/core/logging**: 日志记录功能

## 性能特性

- **低延迟**: 协程切换延迟在微秒级别
- **高吞吐**: 支持每秒数百万次协程切换
- **内存效率**: 协程栈内存按需分配和复用
- **可扩展**: 支持数万个并发协程

## 最佳实践

1. **协程使用**: 优先使用协程而非线程进行并发编程
2. **资源管理**: 使用 RAII 和智能指针管理资源
3. **错误处理**: 在协程中正确处理异常和错误
4. **性能调优**: 根据场景选择合适的执行栈大小
5. **监控指标**: 监控协程数量、执行时间等指标