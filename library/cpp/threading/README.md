# Threading 线程和并发库

YTsaurus 高性能并发编程库，提供丰富的线程安全数据结构、同步原语和异步编程工具。

## 📋 项目概述

Threading 库为 YTsaurus 提供了完整的并发编程基础设施，包括阻塞队列、Future/Promise、取消令牌、无锁数据结构等高性能组件，专为高并发、低延迟的分布式系统设计。

### 🎯 核心特性

- **高性能并发**: 无锁数据结构、SPSC/MPSC队列、原子操作优化
- **异步编程**: 完整的 Future/Promise 生态系统
- **取消机制**: 协作式取消令牌系统
- **同步原语**: 阻塞队列、信号量、互斥锁等
- **调度器**: 本地执行器和任务调度
- **无锁结构**: 高性能无锁跳表和队列
- **定时任务**: Cron 风格的定时调度

## 🏗️ 架构设计

### 核心组件结构

```
Threading Library
├── Future/Promise      # 异步编程基础
│   ├── TFuture<>       # 异步结果
│   ├── TPromise<>      # 异步承诺
│   ├── TWaitGroup      # 等待组
│   └── TAsyncSemaphore # 异步信号量
├── Cancellation        # 取消机制
│   ├── TCancellationToken   # 取消令牌
│   └── TCancellationTokenSource # 令牌源
├── BlockingQueue      # 阻塞队列
├── Queues            # 高性能队列
│   ├── MPSC          # 多生产者单消费者
│   ├── MPMC          # 多生产者多消费者
│   └── Unordered     # 无序队列
├── SkipList          # 无锁跳表
├── LocalExecutor     # 本地执行器
├── Cron             # 定时任务
└── MuxEvent         # 多路事件
```

### 组件关系图

```
┌─────────────────┐    ┌─────────────────┐
│  TFuture<T>     │◄───┤  TPromise<T>    │
└─────────┬───────┘    └─────────────────┘
          │
          ▼
┌─────────────────┐    ┌─────────────────┐
│ TWaitGroup      │    │ TAsyncSemaphore │
└─────────────────┘    └─────────────────┘

┌─────────────────┐    ┌─────────────────┐
│TCancellationToken│◄───┤TCancellationTokenSource│
└─────────────────┘    └─────────────────┘

┌─────────────────┐    ┌─────────────────┐
│TBlockingQueue   │    │TLocalExecutor   │
└─────────────────┘    └─────────────────┘
```

## 💻 使用方法

### Future/Promise 异步编程

```cpp
#include <library/cpp/threading/future/future.h>
#include <library/cpp/threading/future/wait/wait.h>

// 基础 Future/Promise
void BasicFutureExample() {
    // 创建 Promise 和 Future
    auto promise = NewPromise<int>();
    auto future = promise.GetFuture();

    // 在另一个线程设置值
    std::thread([&promise]() {
        std::this_thread::sleep_for(std::chrono::seconds(1));
        promise.SetValue(42);
    }).detach();

    // 等待结果
    int result = future.GetValueSync();
    std::cout << "Result: " << result << std::endl; // Result: 42
}

// 异步函数
TFuture<int> ComputeAsync(int x, int y) {
    return Async([x, y]() -> int {
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        return x + y;
    });
}

void AsyncChainExample() {
    // 异步链式操作
    auto future1 = ComputeAsync(10, 20);
    auto future2 = future1.Apply([](int result) -> int {
        return result * 2;
    });

    auto finalResult = future2.GetValueSync();
    std::cout << "Final result: " << finalResult << std::endl; // 60
}

// 多个 Future 并行
void ParallelFuturesExample() {
    std::vector<TFuture<int>> futures;

    // 启动多个异步任务
    for (int i = 0; i < 5; ++i) {
        futures.push_back(Async([i]() -> int {
            std::this_thread::sleep_for(std::chrono::milliseconds(100 * i));
            return i * i;
        }));
    }

    // 等待所有任务完成
    auto allFuture = WaitAll(futures);
    allFuture.WaitSync();

    for (size_t i = 0; i < futures.size(); ++i) {
        std::cout << "Task " << i << " result: " << futures[i].GetValueSync() << std::endl;
    }
}
```

### 取消令牌 (Cancellation Token)

```cpp
#include <library/cpp/threading/cancellation/cancellation_token.h>

// 基础取消操作
void CancellationExample() {
    TCancellationTokenSource source;
    auto token = source.Token();

    // 启动长时间运行的任务
    auto task = std::thread([&token]() {
        for (int i = 0; i < 100; ++i) {
            // 检查取消请求
            if (token.IsCancellationRequested()) {
                std::cout << "Task cancelled!" << std::endl;
                return;
            }

            std::cout << "Working... " << i << std::endl;
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }
    });

    // 3秒后取消任务
    std::this_thread::sleep_for(std::chrono::seconds(3));
    source.Cancel();

    task.join();
}

// 带超时的操作
void TimeoutExample() {
    TCancellationTokenSource source;
    auto token = source.Token();

    // 设置超时时间
    token.SetDeadline(TInstant::Now() + TDuration::Seconds(5));

    try {
        // 可能超时的操作
        while (true) {
            token.ThrowIfTokenCancelled();

            // 执行工作
            DoSomeWork();
        }
    } catch (const TOperationCancelledException& e) {
        std::cout << "Operation cancelled or timed out" << std::endl;
    }
}

// 传递取消令牌到异步函数
TFuture<std::string> DownloadFileAsync(const std::string& url, TCancellationToken token) {
    return Async([url, token]() -> std::string {
        // 模拟文件下载
        for (int progress = 0; progress <= 100; progress += 10) {
            token.ThrowIfCancellationRequested();

            std::cout << "Download progress: " << progress << "%" << std::endl;
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }

        return "File content for: " + url;
    });
}

void CancellationInAsyncExample() {
    TCancellationTokenSource source;
    auto token = source.Token();

    auto downloadFuture = DownloadFileAsync("https://example.com/file", token);

    // 5秒后取消下载
    std::thread([&source]() {
        std::this_thread::sleep_for(std::chrono::seconds(5));
        source.Cancel();
    }).detach();

    try {
        auto content = downloadFuture.GetValueSync();
        std::cout << "Download completed: " << content << std::endl;
    } catch (const TOperationCancelledException& e) {
        std::cout << "Download cancelled" << std::endl;
    }
}
```

### 阻塞队列 (BlockingQueue)

```cpp
#include <library/cpp/threading/blocking_queue/blocking_queue.h>

// 生产者-消费者模式
void ProducerConsumerExample() {
    // 创建容量为10的阻塞队列
    NThreading::TBlockingQueue<int> queue(10);

    // 生产者线程
    std::thread producer([&queue]() {
        for (int i = 0; i < 100; ++i) {
            std::cout << "Producing: " << i << std::endl;

            // 阻塞直到有空间
            bool pushed = queue.Push(i);
            if (!pushed) {
                std::cout << "Failed to push, queue stopped" << std::endl;
                break;
            }

            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }

        queue.Stop(); // 停止队列
    });

    // 消费者线程
    std::thread consumer([&queue]() {
        while (true) {
            // 阻塞直到有元素或队列停止
            auto item = queue.Pop();
            if (!item.Defined()) {
                std::cout << "Queue stopped, consumer exiting" << std::endl;
                break;
            }

            std::cout << "Consuming: " << item.GetRef() << std::endl;
            std::this_thread::sleep_for(std::chrono::milliseconds(20));
        }
    });

    producer.join();
    consumer.join();
}

// 带超时的队列操作
void TimeoutQueueExample() {
    NThreading::TBlockingQueue<std::string> queue(5);

    // 尝试推送（带超时）
    auto pushed = queue.Push("Hello", TDuration::Seconds(1));
    if (pushed) {
        std::cout << "Successfully pushed item" << std::endl;
    } else {
        std::cout << "Push timed out" << std::endl;
    }

    // 尝试弹出（带超时）
    auto item = queue.Pop(TDuration::Seconds(2));
    if (item.Defined()) {
        std::cout << "Popped: " << item.GetRef() << std::endl;
    } else {
        std::cout << "Pop timed out" << std::endl;
    }

    // 批量清空队列
    auto items = queue.Drain();
    std::cout << "Drained " << items.size() << " items" << std::endl;
}
```

### 等待组 (WaitGroup)

```cpp
#include <library/cpp/threading/future/wait/wait_group.h>

void WaitGroupExample() {
    NThreading::TWaitGroup wg;
    std::vector<std::thread> workers;
    std::vector<int> results(10);

    // 启动多个工作线程
    for (int i = 0; i < 10; ++i) {
        wg.Add(1); // 增加计数

        workers.emplace_back([&wg, &results, i]() {
            // 模拟工作
            std::this_thread::sleep_for(std::chrono::milliseconds(100 * (i + 1)));
            results[i] = i * i;

            wg.Finish(); // 完成一个任务
        });
    }

    // 等待所有任务完成
    auto waitFuture = wg.Wait();
    waitFuture.WaitSync();

    std::cout << "All tasks completed!" << std::endl;
    for (int result : results) {
        std::cout << result << " ";
    }
    std::cout << std::endl;

    // 等待所有线程结束
    for (auto& worker : workers) {
        worker.join();
    }
}
```

### 异步信号量 (AsyncSemaphore)

```cpp
#include <library/cpp/threading/future/async_semaphore.h>

void AsyncSemaphoreExample() {
    // 创建最多允许3个并发操作的信号量
    NThreading::TAsyncSemaphore semaphore(3);

    std::vector<TFuture<void>> futures;

    // 启动10个异步任务，但最多3个并发执行
    for (int i = 0; i < 10; ++i) {
        auto future = semaphore.Acquire()
            .Apply([&semaphore, i](auto) -> TFuture<void> {
                // 执行任务
                std::cout << "Task " << i << " started" << std::endl;
                std::this_thread::sleep_for(std::chrono::seconds(1));
                std::cout << "Task " << i << " completed" << std::endl;

                // 释放信号量
                semaphore.Release();
                return MakeFuture();
            });

        futures.push_back(future);
    }

    // 等待所有任务完成
    WaitAll(futures).WaitSync();
    std::cout << "All tasks completed" << std::endl;
}
```

### 本地执行器 (LocalExecutor)

```cpp
#include <library/cpp/threading/local_executor/local_executor.h>

void LocalExecutorExample() {
    // 创建本地执行器（使用TBB）
    NThreading::ILocalExecutor::TParams execParams;
    execParams.PoolSize = 4; // 4个工作线程

    auto executor = NThreading::CreateLocallyExecutor(execParams);

    std::vector<int> data(100);

    // 并行填充数组
    executor->ExecRange([&data](int i) {
        data[i] = i * i;
    }, 0, 100, NThreading::TLocalExecutor::WAIT_COMPLETE);

    // 并行计算总和
    std::atomic<long long> sum(0);
    executor->ExecRange([&data, &sum](int i) {
        sum.fetch_add(data[i]);
    }, 0, 100, NThreading::TLocalExecutor::WAIT_COMPLETE);

    std::cout << "Sum: " << sum.load() << std::endl;
}
```

### Cron 定时任务

```cpp
#include <library/cpp/threading/cron/cron.h>

void CronExample() {
    // 创建Cron调度器
    NThreading::TCron cron;

    // 每分钟执行一次
    cron.Schedule("* * * * *", []() {
        std::cout << "Minutely task: " << TInstant::Now().FormatLocal() << std::endl;
    });

    // 每5秒执行一次
    cron.Schedule("*/5 * * * * *", []() {
        std::cout << "Every 5 seconds task" << std::endl;
    });

    // 运行调度器（在实际应用中应该在单独线程中运行）
    std::thread schedulerThread([&cron]() {
        cron.Start();

        // 运行1分钟
        std::this_thread::sleep_for(std::chrono::minutes(1));

        cron.Stop();
    });

    schedulerThread.join();
}
```

## 🔧 高级特性

### 无锁数据结构

```cpp
#include <library/cpp/threading/skip_list/skiplist.h>
#include <library/cpp/threading/queue/mpsc_intrusive_unordered.h>

// 无锁跳表
void LockFreeSkipListExample() {
    NThreading::TSkipList<int, std::string> skipList;

    // 并发插入
    std::vector<std::thread> writers;
    for (int i = 0; i < 10; ++i) {
        writers.emplace_back([&skipList, i]() {
            for (int j = 0; j < 100; ++j) {
                int key = i * 100 + j;
                skipList.Insert(key, "value_" + std::to_string(key));
            }
        });
    }

    // 并发查找
    std::vector<std::thread> readers;
    for (int i = 0; i < 5; ++i) {
        readers.emplace_back([&skipList]() {
            for (int j = 0; j < 1000; ++j) {
                auto* value = skipList.Find(j);
                if (value) {
                    // 找到值
                }
            }
        });
    }

    // 等待所有线程完成
    for (auto& writer : writers) {
        writer.join();
    }
    for (auto& reader : readers) {
        reader.join();
    }
}

// MPSC队列（多生产者单消费者）
struct TTask {
    int Id;
    std::string Data;
};

void MPSCQueueExample() {
    NThreading::TMPSCIntrusiveUnorderedQueue<TTask> queue;

    // 多个生产者
    std::vector<std::thread> producers;
    for (int i = 0; i < 5; ++i) {
        producers.emplace_back([&queue, i]() {
            for (int j = 0; j < 100; ++j) {
                auto task = std::make_unique<TTask>();
                task->Id = i * 100 + j;
                task->Data = "Task " + std::to_string(task->Id);
                queue.Enqueue(task.release());
            }
        });
    }

    // 单个消费者
    std::thread consumer([&queue]() {
        while (true) {
            auto task = queue.Dequeue();
            if (!task) {
                // 可以添加退出条件
                std::this_thread::sleep_for(std::chrono::milliseconds(1));
                continue;
            }

            std::cout << "Processing task " << task->Id << std::endl;
            delete task;
        }
    });

    for (auto& producer : producers) {
        producer.join();
    }
    consumer.detach(); // 在实际应用中需要适当的退出机制
}
```

### 错误处理和异常

```cpp
void ExceptionHandlingExample() {
    // Future 中的异常处理
    auto future = Async([]() -> int {
        throw std::runtime_error("Something went wrong");
        return 42;
    });

    try {
        int result = future.GetValueSync();
    } catch (const std::exception& e) {
        std::cout << "Exception caught: " << e.what() << std::endl;
    }

    // 处理异常并继续
    auto recoverFuture = future
        .Apply([](int) -> int {
            return 0; // 默认值
        })
        .Catch([](const std::exception& e) -> int {
            std::cout << "Handled exception: " << e.what() << std::endl;
            return -1;
        });

    std::cout << "Recovered result: " << recoverFuture.GetValueSync() << std::endl;
}
```

## 📊 性能优化

### 内存管理优化

```cpp
void MemoryOptimizationExample() {
    // 复用 Promise/Promise 对象
    std::vector<TPromise<int>> promises;
    promises.reserve(1000);

    for (int i = 0; i < 1000; ++i) {
        promises.push_back(NewPromise<int>());
    }

    // 使用移动语义减少拷贝
    std::vector<TFuture<int>> futures;
    for (auto& promise : promises) {
        futures.push_back(promise.GetFuture());
    }
}

// 批量操作优化
void BatchOperationExample() {
    NThreading::TWaitGroup wg;
    std::vector<TFuture<void>> futures;

    // 批量启动任务
    for (int i = 0; i < 1000; ++i) {
        wg.Add(1);
        futures.push_back(Async([&wg, i]() {
            // 执行工作
            DoWork(i);
            wg.Finish();
        }));
    }

    // 批量等待
    auto allDone = WaitAll(futures);
    allDone.WaitSync();
}
```

### 线程池优化

```cpp
void ThreadPoolOptimizationExample() {
    // 合理设置线程池大小
    const size_t cpuCount = std::thread::hardware_concurrency();
    const size_t poolSize = std::max(size_t(4), cpuCount * 2);

    NThreading::ILocalExecutor::TParams params;
    params.PoolSize = poolSize;
    auto executor = NThreading::CreateLocallyExecutor(params);

    // 使用适当的粒度
    executor->ExecRange([](int i) {
        // 适当大小的任务，避免过小的任务粒度
        ProcessChunk(i, 100); // 每次处理100个元素
    }, 0, 100000, NThreading::TLocalExecutor::WAIT_COMPLETE);
}
```

## 🧪 测试和调试

### 并发测试

```cpp
#include <library/cpp/testing/unittest/registar.h>

Y_UNIT_TEST_SUITE(ThreadingTest) {
    Y_UNIT_TEST(FutureBasicTest) {
        auto promise = NewPromise<int>();
        auto future = promise.GetFuture();

        UNIT_ASSERT(!future.HasValue());

        promise.SetValue(42);

        UNIT_ASSERT(future.HasValue());
        UNIT_ASSERT_VALUES_EQUAL(future.GetValueSync(), 42);
    }

    Y_UNIT_TEST(BlockingQueueTest) {
        NThreading::TBlockingQueue<int> queue(2);

        UNIT_ASSERT(queue.Empty());
        UNIT_ASSERT_VALUES_EQUAL(queue.Size(), 0);

        UNIT_ASSERT(queue.Push(1));
        UNIT_ASSERT(queue.Push(2));

        UNIT_ASSERT_VALUES_EQUAL(queue.Size(), 2);

        auto item = queue.Pop();
        UNIT_ASSERT(item.Defined());
        UNIT_ASSERT_VALUES_EQUAL(item.GetRef(), 1);
    }

    Y_UNIT_TEST(CancellationTest) {
        TCancellationTokenSource source;
        auto token = source.Token();

        UNIT_ASSERT(!token.IsCancellationRequested());

        source.Cancel();

        UNIT_ASSERT(token.IsCancellationRequested());
    }
}
```

### 调试技巧

```cpp
// 调试并发问题
void DebugConcurrency() {
    // 使用原子计数器跟踪操作
    std::atomic<int> operationCount(0);

    auto future = Async([&operationCount]() {
        operationCount.fetch_add(1);
        DoSomeWork();
        operationCount.fetch_sub(1);
    });

    future.WaitSync();
    std::cout << "Operations in progress: " << operationCount.load() << std::endl;
}

// 死锁检测
class TDeadlockDetector {
public:
    void AcquireLock(const std::string& lockName) {
        std::lock_guard<std::mutex> guard(Mutex);
        std::cout << "Acquiring lock: " << lockName << std::endl;
        ActiveLocks.push_back(lockName);
    }

    void ReleaseLock(const std::string& lockName) {
        std::lock_guard<std::mutex> guard(Mutex);
        ActiveLocks.erase(
            std::remove(ActiveLocks.begin(), ActiveLocks.end(), lockName),
            ActiveLocks.end());
        std::cout << "Released lock: " << lockName << std::endl;
    }

    void PrintLocks() const {
        std::lock_guard<std::mutex> guard(Mutex);
        std::cout << "Active locks: ";
        for (const auto& lock : ActiveLocks) {
            std::cout << lock << " ";
        }
        std::cout << std::endl;
    }

private:
    mutable std::mutex Mutex;
    std::vector<std::string> ActiveLocks;
};
```

## 📈 最佳实践

### 设计原则

1. **优先使用高级抽象**：使用 Future/Promise 而不是原始线程
2. **合理设置超时**：避免无限等待
3. **使用取消令牌**：支持协作式取消
4. **避免锁竞争**：使用无锁数据结构
5. **批量处理**：减少同步开销

### 性能建议

1. **选择合适的队列类型**：
   - MPSC：多生产者单消费者
   - MPMC：多生产者多消费者
   - BlockingQueue：需要阻塞操作时

2. **异步编程模式**：
   - 使用链式操作减少回调
   - 合理使用并行执行
   - 避免过度序列化

3. **资源管理**：
   - 及时释放 Future 和 Promise
   - 避免内存泄漏
   - 监控线程池大小

### 错误处理建议

1. **Future 错误传播**：确保异常正确传播
2. **取消检查**：在长时间操作中检查取消令牌
3. **超时处理**：设置合理的超时时间
4. **资源清理**：确保在异常情况下正确清理资源

## 🔗 相关模块

- **Memory**: 内存管理工具
- **Atomic**: 原子操作支持
- **Containers**: STL容器扩展
- **TimeProvider**: 时间和定时器
- **Logger**: 并发日志记录

Threading 库为 YTsaurus 提供了完整的并发编程基础设施，支持从简单的线程同步到复杂的异步编排的各种使用场景，是构建高性能分布式系统的核心组件。