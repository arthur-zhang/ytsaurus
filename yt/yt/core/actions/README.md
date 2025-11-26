# Actions 模块

## 模块概述

`yt/yt/core/actions` 模块是 YTsaurus 分布式系统的核心基础设施模块，提供了现代 C++ 异步编程的基本构建块。该模块实现了一套完整且高效的回调和 Future/Promise 机制，为系统中的异步操作、任务调度、取消传播和执行上下文管理提供了统一的解决方案。

该模块的设计灵感来源于现代编程语言中的异步编程模式，结合了 C++ 的类型安全特性和高性能要求，为整个 YTsaurus 系统提供了坚实的并发编程基础。

## 主要功能

### 1. 回调机制 (Callback)
- **TCallback**: 类型安全的函数对象封装器，支持任意签名的回调函数
- **Bind 系统**: 提供强大的参数绑定机制，支持部分参数绑定和柯里化
- **参数包装器**: 包括 `Unretained()`、`Owned()`、`Passed()`、`ConstRef()` 等用于控制参数生命周期
- **内存管理**: 基于引用计数的自动内存管理，支持高效的移动语义

### 2. 异步编程 (Future/Promise)
- **TFuture**: 异步操作的只读句柄，支持订阅、获取和组合操作
- **TPromise**: 异步操作的写入端，用于设置结果或错误
- **类型安全**: 强类型系统，编译时检查类型兼容性
- **错误处理**: 统一的 `TErrorOr<T>` 错误处理机制
- **组合操作**: 支持 `Apply`、`Then`、`Wait` 等链式操作

### 3. 调用器系统 (Invoker)
- **IInvoker**: 统一的回调执行接口，抽象了线程池、事件循环等执行环境
- **IPrioritizedInvoker**: 支持优先级调用的调用器
- **IBoundedConcurrencyInvoker**: 限制并发度的调用器
- **ISuspendableInvoker**: 支持暂停/恢复的调用器
- **调用器池**: 管理多个调用器的集合，支持负载均衡和诊断

### 4. 取消机制 (Cancellation)
- **TCancelableContext**: 可取消的执行上下文，支持取消传播
- **TCancelationToken**: 取消令牌，用于传递取消状态
- **级联取消**: 支持取消操作在相关 Future 和上下文间的传播
- **信号机制**: 基于 Callback 的事件通知系统

### 5. 信号系统 (Signal)
- **事件发布订阅**: 提供类型安全的事件机制
- **宏定义**: 简化信号声明和实现的宏系统
- **多播支持**: 支持多个订阅者监听同一事件

## 文件说明

### 核心接口文件
- **public.h**: 模块的公共接口声明，定义主要的类模板前向声明
- **callback.h/c**: 回调机制的核心实现，提供 TCallback 类和相关功能
- **bind.h**: 参数绑定系统的实现，包含各种参数包装器
- **future.h/c**: Future/Promise 异步编程机制的核心实现
- **invoker.h**: 调用器接口定义，抽象执行环境

### 实现细节文件
- **callback_internal.h/c**: 回调机制的内部实现细节
- **future-inl.h**: Future 模板的内联实现
- **invoker_detail.h/c**: 调用器实现的辅助类和函数
- **invoker_pool.h/c**: 调用器池的实现
- **invoker_util.h/c**: 调用器相关的实用工具函数

### 特殊功能文件
- **cancelable_context.h/c**: 可取消上下文的实现
- **cancelation_token.h/c**: 取消令牌的实现
- **current_invoker.h/c**: 当前调用器的上下文管理
- **codicil_guarded_invoker.h/c**: 带有 codicil 保护的调用器
- **new_with_offloaded_dtor.h/c**: 支持析构函数卸载的内存分配
- **signal.h**: 信号系统的宏定义

### 测试文件
- **unittests/**: 单元测试目录，包含各个组件的测试用例
  - **future_ut.cpp**: Future 功能测试
  - **bind_ut.cpp**: Bind 功能测试
  - **invoker_ut.cpp**: Invoker 功能测试
  - **cancelation_token_ut.cpp**: 取消令牌测试
  - **actions_ut.cpp**: 综合功能测试

## 使用方法

### 基本回调使用
```cpp
#include <yt/yt/core/actions/bind.h>
#include <yt/yt/core/actions/callback.h>

// 定义一个简单的函数
void PrintMessage(const std::string& message) {
    std::cout << message << std::endl;
}

// 创建回调
auto callback = BIND(&PrintMessage, "Hello, YTsaurus!");
callback();  // 执行: Hello, YTsaurus!
```

### Future/Promise 异步编程
```cpp
#include <yt/yt/core/actions/future.h>

// 创建 Promise
auto promise = NewPromise<int>();
auto future = promise.ToFuture();

// 设置回调处理结果
future.Subscribe([](const TErrorOr<int>& result) {
    if (result.IsOK()) {
        std::cout << "Result: " << result.Value() << std::endl;
    } else {
        std::cout << "Error: " << result.GetMessage() << std::endl;
    }
});

// 在其他地方设置结果
promise.Set(42);  // 异步触发回调
```

### 使用调用器
```cpp
#include <yt/yt/core/actions/invoker_util.h>
#include <yt/yt/core/concurrency/action_queue.h>

// 创建 action queue 作为调用器
auto actionQueue = New<TActionQueue>("MyQueue");
auto invoker = actionQueue->GetInvoker();

// 在指定线程中执行回调
invoker->Invoke(BIND([] {
    std::cout << "Running in background thread" << std::endl;
}));
```

### 取消机制使用
```cpp
#include <yt/yt/core/actions/cancelable_context.h>

// 创建可取消上下文
auto context = New<TCancelableContext>();
auto cancelableInvoker = context->CreateInvoker(invoker);

// 长时间运行的任务
auto future = Async([&] {
    // 执行一些工作
    for (int i = 0; i < 1000; ++i) {
        if (context->IsCanceled()) {
            // 检查取消状态
            throw std::runtime_error("Operation cancelled");
        }
        // 执行工作...
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    return 42;
}, cancelableInvoker);

// 需要时取消操作
context->Cancel(TError("Operation cancelled by user"));
```

### 信号系统使用
```cpp
class MyEmitter {
public:
    DECLARE_SIGNAL(void(const std::string&), MessageReceived);

    void SendMessage(const std::string& message) {
        // 触发信号
        MessageReceived_.Fire(message);
    }
};

class MyReceiver {
public:
    void OnMessage(const std::string& message) {
        std::cout << "Received: " << message << std::endl;
    }
};

// 使用示例
MyEmitter emitter;
MyReceiver receiver;

// 订阅信号
emitter.SubscribeMessageReceived(
    BIND(&MyReceiver::OnMessage, Unretained(&receiver))
);

// 发送消息，触发回调
emitter.SendMessage("Hello!");
```

## 依赖关系

### 内部依赖
- **yt/yt/core/misc**: 基础工具和错误处理机制
- **yt/yt/core/threading**: 线程管理相关功能
- **yt/yt/core/memory**: 内存管理工具

### 外部依赖
- **C++20**: 支持概念、协程等现代 C++ 特性
- **Library/cpp/yt/memory**: YT 特定的内存管理组件

## 实现原理

### 回调系统的设计
回调系统基于类型擦除和引用计数实现。`TCallback` 内部存储一个指向 `TBindStateBase` 的指针，该基类封装了目标函数和绑定的参数。通过模板特化在编译时生成类型特定的调用函数，运行时通过函数指针实现类型擦除。

### Future/Promise 实现
Future 和 Promise 共享一个内部状态对象，使用原子操作保证线程安全。Promise 是强引用，Future 是弱引用，当所有 Promise 销毁时，Future 会自动失败并设置取消错误。

### 取消传播机制
取消机制基于观察者模式实现。`TCancelableContext` 维护一个取消标志，注册的上下文和 Future 会订阅取消事件。当上下文被取消时，所有订阅者都会收到取消通知。

### 内存优化
模块使用多种内存优化技术：
- 小对象优化的引用计数
- 移动语义避免不必要的拷贝
- 内联函数减少函数调用开销
- 模板特化优化特定场景

## 设计模式

### 观察者模式
用于信号系统和取消机制的实现，支持一对多的依赖关系。

### 策略模式
调用器接口使用策略模式，不同的调用器实现不同的执行策略。

### 建造者模式
Bind 系统使用建造者模式，通过链式调用构建复杂的回调对象。

### 代理模式
各种包装调用器使用代理模式，在原有调用器基础上添加额外功能。

## 性能特性

- **零拷贝传递**: 支持移动语义，避免不必要的数据拷贝
- **内存高效**: 精心设计的内存布局，减少缓存未命中
- **并发安全**: 使用原子操作和无锁数据结构
- **编译时优化**: 大量使用模板和内联，编译器可充分优化

## 线程安全

- **TFuture/TPromise**: 完全线程安全，支持多线程并发访问
- **TCallback**: 在构造后是线程安全的（const 方法）
- **IInvoker**: 实现依赖，通常支持并发调用 Invoke
- **TCancelableContext**: 线程安全的取消操作

## 最佳实践

1. **使用 BIND 宏**: 总是使用 BIND 而不是手动构造回调
2. **选择合适的参数包装器**: 根据对象生命周期选择 Unretained、Owned 等
3. **错误处理**: 总是检查 Future 的错误状态
4. **取消支持**: 在长时间运行的操作中支持取消
5. **避免阻塞**: 在异步回调中避免阻塞操作

## 常见陷阱

1. **悬空指针**: 错误使用 Unretained 导致的内存安全问题
2. **循环引用**: 回调持有对象指针导致的循环引用
3. **异常安全**: 异常在异步回调中的传播问题
4. **线程亲和性**: 忽略调用器的线程绑定特性

## 调试技巧

1. **启用绑定位置跟踪**: 编译时设置 YT_ENABLE_BIND_LOCATION_TRACKING
2. **使用诊断调用器池**: TDiagnosableInvokerPool 提供性能统计
3. **引用计数跟踪**: 使用 TRefCountedTracker 监控对象生命周期
4. **Future 调试**: 利用 Future 的 ToString 方法获取调试信息

## 扩展点

- **自定义调用器**: 实现特殊的执行策略
- **自定义参数包装器**: 扩展 Bind 系统的参数处理能力
- **Future 组合器**: 实现高级的异步操作组合
- **取消策略**: 自定义取消传播的逻辑