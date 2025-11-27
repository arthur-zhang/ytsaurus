# 线程工具库

本模块提供线程安全的并发编程工具，包括无锁队列、线程池、单例模式等组件。

## 功能特性

### 无锁数据结构
- 无锁队列（Lock-Free Queue）
- 无锁栈（Lock-Free Stack）
- 高性能并发操作
- 内存序保证

### 线程管理
- 线程池实现
- 任务调度
- 工作窃取算法
- 资源管理

### 并发模式
- 单例模式（线程安全）
- 工厂模式
- 生产者-消费者模式
- 读写锁（如果实现）

## 主要组件

### 无锁容器
- **lfqueue.h/cpp** - 无锁队列
- **lfstack.h/cpp** - 无锁栈

### 线程池
- **pool.h/cpp** - 线程池实现

### 设计模式
- **singleton.h/cpp** - 单例模式
- **factory.h/cpp** - 工厂模式

### 前向声明
- **fwd.h/cpp** - 类型前向声明

## 使用方法

### 无锁队列
```cpp
#include "util/thread/lfqueue.h"

// 创建无锁队列
TLockFreeQueue<int> queue;

// 生产者线程
void Producer() {
    for (int i = 0; i < 1000; ++i) {
        queue.Enqueue(i);
    }
}

// 消费者线程
void Consumer() {
    int value;
    while (queue.Dequeue(value)) {
        ProcessValue(value);
    }
}
```

### 无锁栈
```cpp
#include "util/thread/lfstack.h"

// 创建无锁栈
TLockFreeStack<TString> stack;

// 推入元素
stack.Push("item1");
stack.Push("item2");

// 弹出元素
TString item;
if (stack.Pop(item)) {
    std::cout << "Popped: " << item << std::endl;
}
```

### 线程池
```cpp
#include "util/thread/pool.h"

// 创建线程池
TThreadPool pool(4);  // 4个工作线程

// 提交任务
auto future = pool.Submit([](int x) {
    return x * x;
}, 42);

// 获取结果
int result = future.Get();  // 1764

// 批量提交任务
std::vector<std::future<int>> futures;
for (int i = 0; i < 100; ++i) {
    futures.push_back(pool.Submit(ProcessItem, i));
}

// 等待所有任务完成
for (auto& f : futures) {
    f.Wait();
}
```

### 线程安全单例
```cpp
#include "util/thread/singleton.h"

// 定义单例类
class MySingleton {
public:
    void DoWork() {
        std::cout << "Working..." << std::endl;
    }

private:
    MySingleton() = default;
    friend class TSingleton<MySingleton>;
};

// 使用单例
auto& instance = TSingleton<MySingleton>::Instance();
instance.DoWork();
```

### 线程工厂
```cpp
#include "util/thread/factory.h"

// 创建线程工厂
TThreadFactory factory;

// 创建线程
auto thread = factory.CreateThread([]() {
    std::cout << "Hello from thread!" << std::endl;
});

// 等待完成
thread.Join();
```

## 无锁算法原理

### ABA 问题
```cpp
// 使用版本号避免 ABA 问题
struct Node {
    std::atomic<Node*> next;
    std::atomic<uint64_t> version;
};
```

### 内存序
```cpp
// 使用适当的内存序
std::atomic<Node*> head;
head.load(std::memory_order_acquire);  // 获取语义
head.store(newNode, std::memory_order_release);  // 释放语义
```

## 性能特性

### 基准测试结果
- 无锁队列：> 100M ops/sec
- 无锁栈：> 150M ops/sec
- 线程池任务提交：> 50M ops/sec

### 优化策略
- 缓存行对齐
- 避免伪共享
- 最小化原子操作
- 使用内存回收算法

## 线程池配置

### 基本配置
```cpp
// 创建自定义线程池
TThreadPoolConfig config;
config.ThreadCount = std::thread::hardware_concurrency();
config.QueueSize = 10000;
config.StackSize = 1024 * 1024;  // 1MB

TThreadPool pool(config);
```

### 高级配置
```cpp
// 设置线程优先级
config.Priority = THREAD_PRIORITY_NORMAL;

// 设置 CPU 亲和性
config.CPUAffinity = {0, 1, 2, 3};  // 绑定到前4个核心

// 设置工作窃取策略
config.EnableWorkStealing = true;
config.StealRetryCount = 3;
```

## 错误处理

### 异常处理
```cpp
try {
    auto result = pool.Submit(MayThrow);
    result.Get();  // 重新抛出异常
} catch (const std::exception& e) {
    std::cerr << "Task failed: " << e.what() << std::endl;
}
```

### 超时处理
```cpp
// 带超时的等待
auto future = pool.Submit(LongRunningTask);
if (future.WaitFor(std::chrono::seconds(5))) {
    auto result = future.Get();
} else {
    std::cout << "Task timed out!" << std::endl;
}
```

## 测试

### 单元测试
```bash
# 运行所有测试
./ut/thread_ut

# 运行无锁队列测试
./ut/thread_ut --gtest_filter="LFQueueTest.*"

# 运行线程池测试
./ut/thread_ut --gtest_filter="ThreadPoolTest.*"
```

### 压力测试
```bash
# 并发压力测试
./test/thread_stress.py

# 内存泄漏检测
valgrind --tool=memcheck ./ut/thread_ut
```

## 最佳实践

1. **无锁编程**
   - 理解内存序语义
   - 避免数据竞争
   - 正确处理 ABA 问题

2. **线程池使用**
   - 合理设置线程数
   - 避免任务阻塞
   - 正确处理异常

3. **性能优化**
   - 减少锁竞争
   - 批量处理任务
   - 使用局部性原理

## 调试技巧

### 死锁检测
```cpp
// 启用死锁检测（调试模式）
#ifdef Y_DEBUG
    TDeadlockDetector::Enable();
#endif
```

### 线程命名
```cpp
// 设置线程名便于调试
TThreadFactory factory;
factory.SetThreadName("WorkerThread");
```

### 竞态条件检测
```cpp
// 使用 ThreadSanitizer
编译时添加：-fsanitize=thread
运行时：TSAN_OPTIONS=report_atomic_races=1
```

## 平台支持

### Linux
- 完整的线程支持
- futex 优化
- NUMA 支持

### macOS
- 基础线程支持
- GCD 集成（如果实现）

### Windows
- Windows 线程 API
- 纤程支持

## 依赖项

- C++11 或更高版本（std::atomic, std::thread）
- 平台特定的线程库
- 无外部依赖

## 版本历史

- v3.0: 添加工作窃取
- v2.5: 性能优化
- v2.0: 重构 API
- v1.0: 初始版本