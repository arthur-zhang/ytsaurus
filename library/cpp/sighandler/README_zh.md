# SignalHandler - 信号处理器库

## 项目概述

SignalHandler 库为 YTsaurus 系统提供了跨平台的信号处理机制，支持异步信号处理、优雅关闭、资源清理等关键功能。该库确保应用程序能够正确响应系统信号，实现服务的优雅关闭和状态保存。

## 核心功能

### 异步信号处理
- **非阻塞信号捕获**: 避免信号处理过程中的死锁问题
- **信号队列管理**: 支持多个信号的排队处理
- **线程安全**: 确保信号处理在多线程环境下的安全性
- **回调机制**: 灵活的信号处理回调注册

### 支持的信号类型
- **SIGTERM**: 终止信号，实现优雅关闭
- **SIGINT**: 中断信号（Ctrl+C）
- **SIGUSR1/SIGUSR2**: 用户自定义信号
- **SIGHUP**: 重新加载配置信号
- **SIGPIPE**: 管道破裂信号处理

## 重要文件说明

- **`async_signals_handler.h/cpp`**: 异步信号处理器的核心实现
- **`CMakeLists.txt`**: 跨平台构建配置

## 使用示例

### 基础用法

```cpp
#include <library/cpp/sighandler/async_signals_handler.h>

class Application {
public:
    void Run() {
        // 注册信号处理器
        auto handler = CreateAsyncSignalsHandler();

        handler->RegisterSignalHandler(SIGTERM, [this]() {
            Cout << "收到终止信号，开始优雅关闭..." << Endl;
            Shutdown();
        });

        handler->RegisterSignalHandler(SIGINT, [this]() {
            Cout << "收到中断信号" << Endl;
            Shutdown();
        });

        handler->RegisterSignalHandler(SIGHUP, [this]() {
            Cout << "重新加载配置" << Endl;
            ReloadConfiguration();
        });

        // 启动应用
        while (running_) {
            // 应用主循环
            DoWork();
            Sleep(TDuration::MilliSeconds(100));
        }
    }

private:
    void Shutdown() {
        running_ = false;
        // 执行清理工作
        CleanupResources();
    }

    void ReloadConfiguration() {
        // 重新加载配置文件
        config_.Load("config.yaml");
    }

    bool running_ = true;
    Config config_;
};
```

## 应用场景

### 1. 优雅关闭服务

```cpp
class WebServer {
public:
    void Start() {
        // 启动服务器
        server_.Start(port_);

        // 注册信号处理器
        auto signalHandler = CreateAsyncSignalsHandler();
        signalHandler->RegisterSignalHandler(SIGTERM, [this]() {
            Cout << "开始优雅关闭 Web 服务器..." << Endl;
            GracefulShutdown();
        });

        // 等待关闭信号
        shutdownEvent_.Wait();
    }

private:
    void GracefulShutdown() {
        // 停止接受新连接
        server_.StopAccepting();

        // 等待现有连接完成
        server_.WaitForConnections(TDuration::Seconds(30));

        // 释放资源
        server_.Shutdown();

        // 通知主线程退出
        shutdownEvent_.Signal();
    }

    HttpServer server_;
    TEvent shutdownEvent_;
    int port_ = 8080;
};
```

### 2. 配置热重载

```cpp
class ConfigurableService {
public:
    void Run() {
        LoadConfiguration();

        auto signalHandler = CreateAsyncSignalsHandler();
        signalHandler->RegisterSignalHandler(SIGHUP, [this]() {
            try {
                ReloadConfiguration();
                Cout << "配置重载成功" << Endl;
            } catch (const std::exception& e) {
                Cerr << "配置重载失败: " << e.what() << Endl;
            }
        });

        // 服务主循环
        while (running_) {
            ProcessRequests();
            Sleep(TDuration::MilliSeconds(10));
        }
    }

private:
    void ReloadConfiguration() {
        // 备份当前配置
        Config backup = config_;

        try {
            // 加载新配置
            config_.Load(configPath_);

            // 验证配置有效性
            ValidateConfiguration();

            // 应用新配置
            ApplyConfiguration();

        } catch (const std::exception& e) {
            // 恢复备份配置
            config_ = backup;
            throw;
        }
    }

    bool running_ = true;
    Config config_;
    TString configPath_ = "service.yaml";
};
```

### 3. 资源清理和状态保存

```cpp
class DatabaseService {
public:
    void Start() {
        InitializeDatabase();
        StartBackgroundTasks();

        auto signalHandler = CreateAsyncSignalsHandler();
        signalHandler->RegisterSignalHandler(SIGTERM, [this]() {
            Cout << "清理数据库服务资源..." << Endl;
            CleanupAndSaveState();
        });

        signalHandler->RegisterSignalHandler(SIGUSR1, [this]() {
            Cout << "手动保存状态" << Endl;
            SaveCurrentState();
        });

        // 服务运行...
        WaitForShutdown();
    }

private:
    void CleanupAndSaveState() {
        try {
            // 停止接受新请求
            StopAcceptingRequests();

            // 等待正在处理的事务完成
            WaitForPendingTransactions();

            // 保存内存状态到磁盘
            SaveCurrentState();

            // 关闭数据库连接
            database_->Close();

            // 通知系统可以安全退出
            NotifyShutdownComplete();

        } catch (const std::exception& e) {
            Cerr << "清理过程中发生错误: " << e.what() << Endl;
        }
    }

    void SaveCurrentState() {
        // 保存关键状态到持久化存储
        StateSnapshot snapshot;
        snapshot.timestamp = TInstant::Now();
        snapshot.activeTransactions = GetActiveTransactionCount();
        snapshot.memoryUsage = GetMemoryUsage();

        serializer_.Save(snapshot, "state.snap");
    }

    std::unique_ptr<Database> database_;
    StateSerializer serializer_;
};
```

## 实现原理

### 异步信号处理架构

```cpp
class AsyncSignalsHandler {
private:
    // 信号处理管道
    int signalPipe_[2];

    // 处理线程
    std::thread handlerThread_;

    // 信号回调映射
    THashMap<int, std::vector<std::function<void()>>> callbacks_;

public:
    void RegisterSignalHandler(int signal, std::function<void()> callback) {
        callbacks_[signal].push_back(callback);

        // 注册系统信号处理器
        struct sigaction sa;
        sa.sa_handler = &AsyncSignalsHandler::StaticSignalHandler;
        sigemptyset(&sa.sa_mask);
        sa.sa_flags = SA_RESTART;
        sigaction(signal, &sa, nullptr);
    }

private:
    static void StaticSignalHandler(int signal) {
        // 将信号写入管道，避免在信号处理器中执行复杂操作
        char sig = static_cast<char>(signal);
        write(GetInstance().signalPipe_[1], &sig, 1);
    }

    void SignalProcessingLoop() {
        while (running_) {
            char sig;
            if (read(signalPipe_[0], &sig, 1) == 1) {
                // 在安全的环境中执行回调
                ProcessSignal(static_cast<int>(sig));
            }
        }
    }
};
```

## 最佳实践

### 1. 信号处理器设计原则

- **快速执行**: 信号处理器应该尽快完成
- **异步处理**: 使用管道或事件机制异步处理信号
- **资源清理**: 确保所有资源都被正确释放
- **状态保存**: 在关闭前保存关键状态信息

### 2. 线程安全考虑

```cpp
class ThreadSafeSignalHandler {
private:
    std::mutex callbackMutex_;
    THashMap<int, std::vector<std::function<void()>>> callbacks_;

public:
    void RegisterCallback(int signal, std::function<void()> callback) {
        std::lock_guard<std::mutex> lock(callbackMutex_);
        callbacks_[signal].push_back(std::move(callback));
    }

    void ProcessSignal(int signal) {
        std::lock_guard<std::mutex> lock(callbackMutex_);

        auto it = callbacks_.find(signal);
        if (it != callbacks_.end()) {
            for (const auto& callback : it->second) {
                try {
                    callback();
                } catch (const std::exception& e) {
                    // 记录异常但不中断处理
                    Cerr << "信号处理回调异常: " << e.what() << Endl;
                }
            }
        }
    }
};
```

## 相关模块

- **threading**: 线程管理和同步
- **filesystem**: 文件系统操作（用于状态保存）
- **logging**: 日志记录（用于信号处理日志）
- **time_provider**: 时间获取（用于状态时间戳）

SignalHandler 库确保 YTsaurus 服务能够在各种系统信号下正确响应，实现优雅关闭和状态管理，是系统稳定运行的重要保障。