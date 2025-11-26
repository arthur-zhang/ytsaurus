# Coroutine 协程库

## 项目描述

Coroutine 库是 YTsaurus 中的高性能协程实现，提供用户态轻量级线程支持。该库实现了完整的协程调度器、事件循环、同步原语和网络 I/O 支持，使开发者能够以同步的方式编写异步代码，同时获得极高的并发性能。

通过栈式协程的实现，该库在保持编程简单性的同时，提供了比传统线程模型更高效的并发处理能力，特别适合 I/O 密集型和高并发场景。

## 核心特性

### 🚀 高性能调度
- **用户态调度**: 避免内核态切换开销
- **协作式调度**: 协程主动让出执行权
- **无锁设计**: 高效的协程间通信
- **优先级支持**: 支持协程优先级调度

### ⚡ 异步 I/O
- **非阻塞 I/O**: 基于 epoll/kqueue 的异步 I/O
- **事件驱动**: 高效的事件循环机制
- **网络优化**: 专门优化的网络操作
- **超时控制**: 精确的超时和定时器支持

### 🔧 同步原语
- **协程事件**: 协程间事件通知机制
- **等待队列**: 支持条件等待和通知
- **互斥锁**: 协程安全的互斥锁实现
- **条件变量**: 协程条件变量支持

### 💾 内存管理
- **栈分配**: 可配置的协程栈大小
- **池化管理**: 高效的协程对象池
- **垃圾回收**: 自动回收完成的协程资源
- **内存优化**: 最小化内存占用

## 架构设计

### 1. 核心组件

#### 协程执行器 (TContExecutor)
```cpp
class TContExecutor {
public:
    // 协程管理
    TCont* Create(NCoro::TTrampoline::TFunc func, const char* name, size_t stackSize);
    void Schedule(TCont* cont);
    void Execute();

    // 调度控制
    void Yield();
    void Exit();
    TCont* Running() const;

    // I/O 和事件
    void Poll();
    void Sleep(TDuration timeout);
    void WaitI();
};
```

#### 协程对象 (TCont)
```cpp
class TCont {
public:
    // 基本操作
    void Yield() noexcept;
    void ReScheduleAndSwitch() noexcept;

    // 睡眠和等待
    int SleepD(TInstant deadline) noexcept;
    int SleepT(TDuration timeout) noexcept;
    int WaitI();

    // 状态查询
    TContExecutor* Executor() noexcept;
    const char* Name() const noexcept;
    void PrintMe(IOutputStream& out) const noexcept;
};
```

#### 事件系统 (TContEvent)
```cpp
class TContEvent {
public:
    TContEvent(TCont* current) noexcept;

    // 等待操作
    int WaitD(TInstant deadline);
    int WaitT(TDuration timeout);
    int WaitI();

    // 唤醒操作
    void Wake() noexcept;
    TCont* Cont() noexcept;
    int Status() const noexcept;
};
```

#### 等待队列 (TContWaitQueue)
```cpp
class TContWaitQueue {
public:
    // 等待操作
    int WaitD(TCont* current, TInstant deadline);
    int WaitT(TCont* current, TDuration timeout);
    int WaitI(TCont* current);

    // 通知操作
    void Signal() noexcept;
    void BroadCast() noexcept;
    void BroadCast(size_t number) noexcept;
};
```

### 2. 网络支持

#### 网络连接 (TContSocket)
```cpp
class TContSocket {
public:
    // 连接操作
    int Connect(const TContSocketAddress& addr);
    int Accept();
    int Bind(const TContSocketAddress& addr);
    int Listen(int backlog);

    // I/O 操作
    int Send(const void* data, size_t len, int flags = 0);
    int Recv(void* data, size_t len, int flags = 0);

    // 异步操作
    int Poll(int events, TDuration timeout);
};
```

#### 套接字池 (TSocketPool)
```cpp
class TSocketPool {
public:
    // 连接管理
    TContSocket* Connect(const TString& host, int port);
    void Release(TContSocket* socket);

    // 连接池操作
    void SetMaxConnections(size_t max);
    void SetKeepAlive(bool enable);
    size_t ActiveConnections() const;
};
```

### 3. 同步原语

#### 协程互斥锁
```cpp
class TContMutex {
public:
    void Lock();
    void Unlock();
    bool TryLock();

    // RAII 支持
    class TGuard {
    public:
        TGuard(TContMutex& mutex);
        ~TGuard();
    };
};
```

#### 协程条件变量
```cpp
class TContCondVar {
public:
    void Wait(TContMutex& mutex);
    bool Wait(TContMutex& mutex, TDuration timeout);
    void NotifyOne();
    void NotifyAll();
};
```

## 使用示例

### 1. 基本协程使用
```cpp
#include <library/cpp/coroutine/engine/impl.h>

void SimpleCoroutineExample() {
    // 创建协程执行器
    TContExecutor executor;

    // 创建协程函数
    auto task1 = [&](TCont* current) {
        for (int i = 0; i < 5; ++i) {
            Cout << "Task 1: " << i << Endl;
            current->SleepT(TDuration::Seconds(1));
        }
    };

    auto task2 = [&](TCont* current) {
        for (int i = 0; i < 3; ++i) {
            Cout << "Task 2: " << i << Endl;
            current->SleepT(TDuration::Seconds(2));
        }
    };

    // 创建并启动协程
    TCont* cont1 = executor.Create(task1, "Task1", 64 * 1024);
    TCont* cont2 = executor.Create(task2, "Task2", 64 * 1024);

    executor.Schedule(cont1);
    executor.Schedule(cont2);

    // 运行事件循环
    executor.Execute();
}
```

### 2. 网络服务器示例
```cpp
#include <library/cpp/coroutine/engine/network.h>

class SimpleEchoServer {
private:
    TContExecutor executor_;
    int port_;

    void HandleConnection(TCont* current, TContSocket socket) {
        char buffer[1024];

        while (true) {
            int len = socket.Recv(buffer, sizeof(buffer) - 1);
            if (len <= 0) break;

            buffer[len] = '\0';
            Cout << "Received: " << buffer << Endl;

            // Echo back
            socket.Send(buffer, len);
        }
    }

    void AcceptConnections(TCont* current) {
        TContSocket listenSocket;
        listenSocket.Bind(TContSocketAddress("0.0.0.0", port_));
        listenSocket.Listen(128);

        while (true) {
            TContSocket clientSocket = listenSocket.Accept();

            // 为每个连接创建处理协程
            auto handler = [this, clientSocket](TCont* cont) mutable {
                HandleConnection(cont, clientSocket);
            };

            TCont* handlerCont = executor_.Create(handler, "Handler", 64 * 1024);
            executor_.Schedule(handlerCont);
        }
    }

public:
    SimpleEchoServer(int port) : port_(port) {}

    void Start() {
        auto acceptor = [this](TCont* current) {
            AcceptConnections(current);
        };

        TCont* acceptorCont = executor_.Create(acceptor, "Acceptor", 64 * 1024);
        executor_.Schedule(acceptorCont);

        Cout << "Echo server started on port " << port_ << Endl;
        executor_.Execute();
    }
};
```

### 3. 生产者-消费者模式
```cpp
#include <library/cpp/coroutine/engine/events.h>

template <typename T>
class CoroutineChannel {
private:
    TContWaitQueue waitReaders_;
    TContWaitQueue waitWriters_;
    TVector<T> buffer_;
    size_t capacity_;
    TContMutex mutex_;

public:
    CoroutineChannel(size_t capacity) : capacity_(capacity) {}

    void Put(T item, TCont* current) {
        TContMutex::TGuard guard(mutex_);

        // 等待缓冲区有空间
        while (buffer_.size() >= capacity_) {
            guard.Unlock();
            waitWriters_.WaitI(current);
            guard.Lock();
        }

        buffer_.push_back(item);

        // 通知等待的读者
        if (!waitReaders_.Empty()) {
            waitReaders_.Signal();
        }
    }

    T Get(TCont* current) {
        TContMutex::TGuard guard(mutex_);

        // 等待缓冲区有数据
        while (buffer_.empty()) {
            guard.Unlock();
            waitReaders_.WaitI(current);
            guard.Lock();
        }

        T item = buffer_.front();
        buffer_.erase(buffer_.begin());

        // 通知等待的写者
        if (!waitWriters_.Empty()) {
            waitWriters_.Signal();
        }

        return item;
    }
};

void ProducerConsumerExample() {
    TContExecutor executor;
    CoroutineChannel<int> channel(5);

    // 生产者协程
    auto producer = [&](TCont* current) {
        for (int i = 0; i < 20; ++i) {
            Cout << "Producing: " << i << Endl;
            channel.Put(i, current);
            current->SleepT(TDuration::MilliSeconds(100));
        }
    };

    // 消费者协程
    auto consumer = [&](TCont* current) {
        for (int i = 0; i < 20; ++i) {
            int item = channel.Get(current);
            Cout << "Consuming: " << item << Endl;
            current->SleepT(TDuration::MilliSeconds(200));
        }
    };

    TCont* prodCont = executor.Create(producer, "Producer", 64 * 1024);
    TCont* consCont = executor.Create(consumer, "Consumer", 64 * 1024);

    executor.Schedule(prodCont);
    executor.Schedule(consCont);
    executor.Execute();
}
```

### 4. 并发任务处理
```cpp
#include <library/cpp/coroutine/engine/cont_poller.h>

class AsyncTaskProcessor {
private:
    TContExecutor executor_;
    TVector<TCont*> tasks_;
    TContWaitQueue completionQueue_;
    std::atomic<size_t> completedTasks_{0};

    struct TaskResult {
        bool success;
        TString error;
        TString result;
    };

    void ProcessUrl(TCont* current, const TString& url) {
        TaskResult result;

        try {
            // 模拟网络请求
            current->SleepT(TDuration::MilliSeconds(rand() % 1000));

            result.success = true;
            result.result = "Data from " + url;
        } catch (const std::exception& e) {
            result.success = false;
            result.error = e.what();
        }

        // 通知完成
        completedTasks_++;
        completionQueue_.Signal();
    }

public:
    void AddTask(const TString& url) {
        auto task = [this, url](TCont* cont) {
            ProcessUrl(cont, url);
        };

        TCont* taskCont = executor_.Create(task, ("Task_" + url).data(), 64 * 1024);
        tasks_.push_back(taskCont);
        executor_.Schedule(taskCont);
    }

    void RunAll() {
        size_t totalTasks = tasks_.size();

        // 等待所有任务完成
        auto waiter = [&](TCont* current) {
            while (completedTasks_ < totalTasks) {
                completionQueue_.WaitI(current);
            }
        };

        TCont* waiterCont = executor_.Create(waiter, "Waiter", 64 * 1024);
        executor_.Schedule(waiterCont);

        Cout << "Processing " << totalTasks << " tasks..." << Endl;
        executor_.Execute();

        Cout << "All " << completedTasks_ << " tasks completed" << Endl;
    }
};
```

### 5. 定时器和超时处理
```cpp
#include <library/cpp/coroutine/engine/custom_time.h>

class TimerService {
private:
    TContExecutor executor_;
    TContWaitQueue timerQueue_;

    void TimerWorker(TCont* current) {
        while (true) {
            // 等待下一个定时器事件
            TInstant nextTime = GetNextTimerTime();
            if (nextTime == TInstant::Max()) {
                timerQueue_.WaitI(current);
            } else {
                timerQueue_.WaitD(current, nextTime);
            }

            // 处理到期的定时器
            ProcessExpiredTimers();
        }
    }

public:
    void Start() {
        auto worker = [this](TCont* cont) {
            TimerWorker(cont);
        };

        TCont* timerCont = executor_.Create(worker, "TimerWorker", 64 * 1024);
        executor_.Schedule(timerCont);
    }

    // 设置一次性定时器
    void SetTimeout(TDuration timeout, std::function<void()> callback) {
        TInstant deadline = TInstant::Now() + timeout;
        AddTimer(deadline, callback);
        timerQueue_.Signal();
    }

    // 设置周期性定时器
    void SetInterval(TDuration interval, std::function<void()> callback) {
        auto periodicCallback = [this, interval, callback]() {
            callback();
            SetTimeout(interval, callback); // 重新设置
        };

        SetTimeout(interval, periodicCallback);
    }
};
```

## 性能特性

### 调度性能
- **上下文切换**: ~100-500ns（远小于线程切换）
- **内存开销**: 每个协程 64KB 栈（可配置）
- **创建开销**: ~1-5μs（远小于线程创建）
- **并发数量**: 支持数百万并发协程

### 网络性能
- **连接数**: 支持数百万并发连接
- **延迟**: 亚毫秒级网络延迟
- **吞吐量**: 高吞吐量网络处理
- **效率**: 高 CPU 利用率

## 应用场景

### 1. 网络服务器
```cpp
class WebServer {
public:
    WebServer(int port) : port_(port) {}

    void Start() {
        // 启动接受连接的协程
        auto acceptor = [this](TCont* current) {
            AcceptConnections(current);
        };

        TCont* acceptorCont = executor_.Create(acceptor, "Acceptor", 64 * 1024);
        executor_.Schedule(acceptorCont);
        executor_.Execute();
    }

private:
    void AcceptConnections(TCont* current);
    void HandleRequest(TCont* current, TContSocket socket);

    TContExecutor executor_;
    int port_;
};
```

### 2. 数据库连接池
```cpp
class AsyncConnectionPool {
private:
    struct Connection {
        TContSocket socket;
        bool inUse = false;
    };

    TVector<Connection> connections_;
    TContWaitQueue waitQueue_;
    TContExecutor executor_;

public:
    std::shared_ptr<Connection> Acquire(TCont* current) {
        // 查找可用连接
        for (auto& conn : connections_) {
            if (!conn.inUse) {
                conn.inUse = true;
                return std::shared_ptr<Connection>(&conn, [this](Connection* c) {
                    c->inUse = false;
                    if (!waitQueue_.Empty()) {
                        waitQueue_.Signal();
                    }
                });
            }
        }

        // 等待连接可用
        waitQueue_.WaitI(current);
        return Acquire(current);
    }
};
```

### 3. 流处理管道
```cpp
class DataProcessor {
private:
    CoroutineChannel<Data> inputChannel_;
    CoroutineChannel<ProcessedData> outputChannel_;
    TContExecutor executor_;

    void ProcessData(TCont* current) {
        while (true) {
            Data data = inputChannel_.Get(current);
            ProcessedData result = Process(data);
            outputChannel_.Put(result, current);
        }
    }

public:
    DataProcessor(size_t bufferSize)
        : inputChannel_(bufferSize), outputChannel_(bufferSize) {}

    void StartProcessing() {
        auto processor = [this](TCont* cont) {
            ProcessData(cont);
        };

        TCont* processorCont = executor_.Create(processor, "Processor", 64 * 1024);
        executor_.Schedule(processorCont);
    }

    void Input(const Data& data) {
        inputChannel_.Put(data, executor_.Running());
    }

    ProcessedData Output() {
        return outputChannel_.Get(executor_.Running());
    }
};
```

## 最佳实践

### 1. 协程生命周期管理
```cpp
// 使用 RAII 管理协程资源
class ScopedCoroutine {
private:
    TContExecutor* executor_;
    TCont* coroutine_;

public:
    ScopedCoroutine(TContExecutor* executor,
                   std::function<void(TCont*)> func,
                   const char* name, size_t stackSize)
        : executor_(executor) {
        coroutine_ = executor_->Create(func, name, stackSize);
        executor_->Schedule(coroutine_);
    }

    ~ScopedCoroutine() {
        if (coroutine_) {
            // 等待协程完成
            while (coroutine_->IsRunning()) {
                executor_->Yield();
            }
        }
    }

    // 禁止拷贝
    ScopedCoroutine(const ScopedCoroutine&) = delete;
    ScopedCoroutine& operator=(const ScopedCoroutine&) = delete;
};
```

### 2. 错误处理和恢复
```cpp
// 协程错误处理
class SafeCoroutine {
public:
    template<typename Func>
    static void SafeExecute(TCont* current, Func func) {
        try {
            func(current);
        } catch (const std::exception& e) {
            // 记录错误
            LogError(current->Name(), e.what());

            // 可选的恢复策略
            if (ShouldRetry(e)) {
                current->SleepT(TDuration::Seconds(1));
                SafeExecute(current, func);
            }
        } catch (...) {
            LogError(current->Name(), "Unknown error");
        }
    }
};
```

### 3. 资源清理
```cpp
// 自动资源清理
template<typename T>
class ResourceGuard {
private:
    T resource_;
    std::function<void(T)> cleanup_;

public:
    ResourceGuard(T resource, std::function<void(T)> cleanup)
        : resource_(resource), cleanup_(cleanup) {}

    ~ResourceGuard() {
        if (cleanup_) {
            cleanup_(resource_);
        }
    }

    T Get() const { return resource_; }
};

// 使用示例
void HandleConnection(TCont* current, TContSocket socket) {
    ResourceGuard<TContSocket> guard(socket, [](TContSocket& sock) {
        sock.Close();
    });

    // 使用 socket...
    // 自动关闭连接
}
```

## 调试和监控

### 协程状态监控
```cpp
class CoroutineMonitor {
private:
    struct CoroutineInfo {
        TString name;
        TInstant startTime;
        size_t stackUsage;
        bool isRunning;
    };

    THashMap<TCont*, CoroutineInfo> coroutines_;

public:
    void RegisterCoroutine(TCont* cont, const TString& name) {
        coroutines_[cont] = {
            name,
            TInstant::Now(),
            0,
            false
        };
    }

    void PrintStatus() {
        Cout << "=== Coroutine Status ===" << Endl;
        for (const auto& [cont, info] : coroutines_) {
            Cout << "Name: " << info.name
                 << ", Runtime: " << (TInstant::Now() - infoStartTime)
                 << ", Stack: " << info.stackUsage << " bytes" << Endl;
        }
    }

    void UnregisterCoroutine(TCont* cont) {
        coroutines_.erase(cont);
    }
};
```

## 限制和注意事项

### 使用限制
- **栈大小限制**: 协程栈大小固定，需要合理设置
- **阻塞操作**: 避免在协程中使用阻塞系统调用
- **CPU 密集型任务**: 不适合纯 CPU 密集型任务

### 最佳实践建议
- **合理设置栈大小**: 根据需求设置合适的栈大小
- **避免长时间阻塞**: 及时让出执行权
- **错误处理**: 妥善处理协程中的异常

## 总结

Coroutine 协程库为 YTsaurus 系统提供了高性能的用户态并发支持。通过轻量级协程的设计和完善的调度机制，该库使开发者能够以同步的思维编写高效的异步代码。

其优秀的性能表现、丰富的功能和易用的接口，使其成为构建高并发网络服务、异步任务处理和实时数据处理的理想选择。通过合理利用协程的特性，可以显著提升应用程序的并发能力和响应性能。