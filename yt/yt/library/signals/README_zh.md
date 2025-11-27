# Signals 信号处理库

## 项目概述

`NSignals` 是 YTsaurus 中的信号处理库，提供了跨平台的信号注册、处理和管理机制。该库支持信号阻塞、崩溃信号保护、多处理器回调链，并提供了线程安全的信号处理框架，是 YTsaurus 系统稳定性和错误处理的核心组件。

## 核心功能

- **信号注册管理**：统一的信号处理器注册和管理
- **崩溃信号保护**：防止多个崩溃信号处理器同时执行
- **信号阻塞**：进程级别的信号阻塞机制
- **多处理器链**：支持为同一信号注册多个处理器
- **跨平台支持**：兼容 Unix 和 Windows 系统
- **初始化优先级**：支持信号处理的早期初始化

## 主要接口

### TSignalRegistry - 信号注册表

```cpp
#include <yt/yt/library/signals/signal_registry.h>

using namespace NYT::NSignals;

// 获取全局信号注册表实例
auto registry = TSignalRegistry::Get();

// 启用崩溃信号保护
registry->SetEnableCrashSignalProtection(true);

// 设置是否覆盖非默认信号处理器
registry->SetOverrideNonDefaultSignalHandlers(true);

// 设置信号处理器（带自定义标志）
registry->SetupSignal(SIGTERM, SA_RESTART);

// 注册简单回调
registry->PushCallback(SIGTERM, []() {
    Cout << "Received SIGTERM" << Endl;
});

// 注册带信号编号的回调（Unix）
#ifdef _unix_
registry->PushCallback(SIGSEGV, [](int signal) {
    Cout << "Received signal: " << signal << Endl;
});
#endif

// 注册完整信号处理器（Unix）
#ifdef _unix_
registry->PushCallback(SIGSEGV, [](int signal, siginfo_t* info, void* context) {
    Cout << "Signal: " << signal << ", Address: " << info->si_addr << Endl;
});
#endif

// 添加默认信号处理器
registry->PushDefaultSignalHandler(SIGABRT);
```

### 信号阻塞机制

```cpp
#include <yt/yt/library/signals/signal_blocking.h>

using namespace NYT::NSignals;

// 在进程启动时阻塞信号
YT_TRY_BLOCK_SIGNAL_FOR_PROCESS(SIGUSR1, [] (bool ok, int threadCount) {
    if (ok) {
        Cout << "Signal SIGUSR1 blocked successfully" << Endl;
    } else {
        Cout << "Failed to block SIGUSR1, thread count: " << threadCount << Endl;
    }
});

// 运行时阻塞信号
BlockSignal(SIGUSR2);
```

### AllCrashSignals 常量

```cpp
// 使用 AllCrashSignals 处理所有崩溃信号
auto registry = TSignalRegistry::Get();

// 为所有崩溃信号注册处理器
registry->PushCallback(AllCrashSignals, []() {
    Cout << "Crash signal received, performing cleanup..." << Endl;
    cleanupResources();
});

// 为所有崩溃信号设置处理器
registry->SetupSignal(AllCrashSignals, SA_RESTART);
```

## 使用方法

### 基本信号处理

```cpp
#include <yt/yt/library/signals/signal_registry.h>
#include <yt/yt/library/signals/signal_blocking.h>

using namespace NYT::NSignals;

class SignalHandler {
public:
    SignalHandler() {
        setupSignalHandlers();
    }

private:
    void setupSignalHandlers() {
        auto registry = TSignalRegistry::Get();

        // 设置优雅关闭处理器
        registry->PushCallback(SIGTERM, [this]() {
            handleGracefulShutdown();
        });

        registry->PushCallback(SIGINT, [this]() {
            handleInterrupt();
        });

        // 设置崩溃信号处理器
        setupCrashHandlers();

        // 启用崩溃信号保护
        registry->SetEnableCrashSignalProtection(true);
    }

    void setupCrashHandlers() {
        auto registry = TSignalRegistry::Get();

#ifdef _unix_
        // Unix 特定的崩溃信号处理器
        registry->PushCallback(SIGSEGV, [this](int signal, siginfo_t* info, void* context) {
            handleSegmentationFault(signal, info, context);
        });

        registry->PushCallback(SIGABRT, [this](int signal, siginfo_t* info, void* context) {
            handleAbortSignal(signal, info, context);
        });

        registry->PushCallback(SIGFPE, [this](int signal, siginfo_t* info, void* context) {
            handleFloatingPointException(signal, info, context);
        });
#else
        // Windows 特定的处理器
        registry->PushCallback(SIGABRT, [this]() {
            handleAbortSignal();
        });
#endif
    }

    void handleGracefulShutdown() {
        Cout << "Received graceful shutdown signal" << Endl;
        // 执行清理操作
        cleanup();
        std::exit(0);
    }

    void handleInterrupt() {
        Cout << "Received interrupt signal" << Endl;
        // 处理中断信号
    }

#ifdef _unix_
    void handleSegmentationFault(int signal, siginfo_t* info, void* context) {
        Cout << "Segmentation fault at address: " << info->si_addr << Endl;
        // 记录崩溃信息
        logCrashInfo(signal, info, context);
        // 添加默认处理器以终止程序
        TSignalRegistry::Get()->PushDefaultSignalHandler(SIGSEGV);
    }

    void handleAbortSignal(int signal, siginfo_t* info, void* context) {
        Cout << "Abort signal received" << Endl;
        logCrashInfo(signal, info, context);
    }

    void handleFloatingPointException(int signal, siginfo_t* info, void* context) {
        Cout << "Floating point exception" << Endl;
        logCrashInfo(signal, info, context);
    }
#endif
};
```

### 信号阻塞和早期初始化

```cpp
#include <yt/yt/library/signals/signal_blocking.h>

// 在程序启动早期阻塞特定信号
YT_TRY_BLOCK_SIGNAL_FOR_PROCESS(SIGUSR1, [](bool ok, int threadCount) {
    if (!ok) {
        // 处理阻塞失败的情况
        std::cerr << "Warning: Failed to block SIGUSR1" << std::endl;
    }
});

YT_TRY_BLOCK_SIGNAL_FOR_PROCESS(SIGUSR2, [](bool ok, int threadCount) {
    std::cout << "SIGUSR2 blocking result: " << ok
              << ", thread count: " << threadCount << std::endl;
});

class ThreadSafeSignalManager {
public:
    ThreadSafeSignalManager() {
        // 确保信号处理在多线程环境下的安全性
        initializeSignalHandling();
    }

private:
    void initializeSignalHandling() {
        auto registry = TSignalRegistry::Get();

        // 防止覆盖用户自定义的信号处理器
        registry->SetOverrideNonDefaultSignalHandlers(false);

        // 设置信号处理标志
        registry->SetupSignal(SIGUSR1, SA_RESTART);
        registry->SetupSignal(SIGUSR2, SA_RESTART);

        // 注册信号处理器
        registry->PushCallback(SIGUSR1, [this]() {
            handleUserSignal1();
        });

        registry->PushCallback(SIGUSR2, [this]() {
            handleUserSignal2();
        });
    }

    void handleUserSignal1() {
        std::lock_guard<std::mutex> lock(mutex_);
        std::cout << "Handling SIGUSR1" << std::endl;
        // 执行信号1的处理逻辑
    }

    void handleUserSignal2() {
        std::lock_guard<std::mutex> lock(mutex_);
        std::cout << "Handling SIGUSR2" << std::endl;
        // 执行信号2的处理逻辑
    }

    std::mutex mutex_;
};
```

### 复杂信号处理场景

```cpp
#include <yt/yt/library/signals/signal_registry.h>
#include <yt/yt/library/signals/signal_blocking.h>
#include <atomic>
#include <thread>
#include <chrono>

class AdvancedSignalHandler {
public:
    AdvancedSignalHandler()
        : shutdownRequested_(false)
    {
        setupAdvancedSignalHandling();
    }

    void waitForShutdown() {
        while (!shutdownRequested_.load()) {
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }
    }

private:
    void setupAdvancedSignalHandling() {
        auto registry = TSignalRegistry::Get();

        // 设置多级信号处理
        setupGracefulShutdownHandlers(registry);
        setupCrashHandlers(registry);
        setupCustomSignalHandlers(registry);

        // 启用崩溃信号保护
        registry->SetEnableCrashSignalProtection(true);
    }

    void setupGracefulShutdownHandlers(TSignalRegistry* registry) {
        // 第一级：记录关闭请求
        registry->PushCallback(SIGTERM, [this]() {
            std::cout << "Level 1: Shutdown request received" << std::endl;
            shutdownRequested_.store(true);
        });

        // 第二级：执行清理操作
        registry->PushCallback(SIGTERM, [this]() {
            std::cout << "Level 2: Performing cleanup" << std::endl;
            performCleanup();
        });

        // 第三级：添加默认处理器
        registry->PushDefaultSignalHandler(SIGTERM);
    }

    void setupCrashHandlers(TSignalRegistry* registry) {
        // 为所有崩溃信号设置处理器
        registry->PushCallback(AllCrashSignals, [this]() {
            std::cout << "Crash signal detected" << std::endl;
            saveCrashDump();
        });

#ifdef _unix_
        // Unix 特定的详细崩溃处理
        registry->PushCallback(SIGSEGV, [](int signal, siginfo_t* info, void* context) {
            std::cout << "SIGSEGV: Fault at address " << info->si_addr << std::endl;
            std::cout << "Error code: " << info->si_code << std::endl;
        });

        registry->PushCallback(SIGFPE, [](int signal, siginfo_t* info, void* context) {
            std::cout << "SIGFPE: Floating point exception" << std::endl;
            std::cout << "Exception type: " << info->si_code << std::endl;
        });
#endif
    }

    void setupCustomSignalHandlers(TSignalRegistry* registry) {
        // 自定义信号处理
        registry->PushCallback(SIGUSR1, [this]() {
            std::cout << "Custom signal 1: Reloading configuration" << std::endl;
            reloadConfiguration();
        });

        registry->PushCallback(SIGUSR2, [this]() {
            std::cout << "Custom signal 2: Dumping statistics" << std::endl;
            dumpStatistics();
        });
    }

    void performCleanup() {
        std::cout << "Cleaning up resources..." << std::endl;
        // 执行清理操作
    }

    void saveCrashDump() {
        std::cout << "Saving crash dump..." << std::endl;
        // 保存崩溃转储
    }

    void reloadConfiguration() {
        std::cout << "Reloading configuration..." << std::endl;
        // 重新加载配置
    }

    void dumpStatistics() {
        std::cout << "Dumping statistics..." << std::endl;
        // 输出统计信息
    }

    std::atomic<bool> shutdownRequested_;
};
```

## 性能考虑

- **信号处理开销**：信号处理器应该尽可能简短快速
- **阻塞范围**：避免长时间阻塞信号，影响系统响应
- **处理器链**：过长的处理器链可能导致信号处理延迟
- **线程安全**：确保信号处理器中的操作是线程安全的

```cpp
// 性能优化示例
class OptimizedSignalHandler {
public:
    OptimizedSignalHandler() {
        setupOptimizedHandlers();
    }

private:
    void setupOptimizedHandlers() {
        auto registry = TSignalRegistry::Get();

        // 使用异步处理避免信号处理器中的重操作
        registry->PushCallback(SIGUSR1, [this]() {
            // 在信号处理器中只设置标志
            signalFlags_.store(1);
        });

        // 启动后台线程处理
        handlerThread_ = std::thread([this]() {
            processSignals();
        });
    }

    void processSignals() {
        while (running_) {
            int flags = signalFlags_.exchange(0);
            if (flags & 1) {
                handleUserSignal1();
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
    }

    void handleUserSignal1() {
        // 在常规线程中执行重操作
        std::cout << "Processing user signal 1" << std::endl;
    }

    std::atomic<int> signalFlags_{0};
    std::atomic<bool> running_{true};
    std::thread handlerThread_;
};
```

## 最佳实践

1. **早期初始化**：在程序启动早期设置信号处理器
2. **简短处理**：保持信号处理器逻辑简短快速
3. **异步处理**：将复杂操作延迟到常规线程中执行
4. **错误处理**：妥善处理信号处理器中的异常
5. **资源清理**：确保在退出前正确释放资源

```cpp
// 最佳实践示例
class ProductionSignalHandler {
public:
    ProductionSignalHandler() {
        initialize();
    }

    ~ProductionSignalHandler() {
        shutdown();
    }

private:
    void initialize() {
        // 早期初始化信号处理
        setupCrashHandlers();
        setupGracefulShutdownHandlers();
        setupCustomHandlers();

        // 启动处理线程
        startProcessingThread();
    }

    void setupCrashHandlers() {
        auto registry = TSignalRegistry::Get();
        registry->SetEnableCrashSignalProtection(true);

        // 快速崩溃处理
        registry->PushCallback(AllCrashSignals, [this]() {
            // 只做必要的紧急清理
            emergencyCleanup();
        });

        // 然后添加默认处理器
        registry->PushDefaultSignalHandler(AllCrashSignals);
    }

    void setupGracefulShutdownHandlers() {
        auto registry = TSignalRegistry::Get();

        registry->PushCallback(SIGTERM, [this]() {
            // 设置关闭标志，让处理线程处理
            shutdownRequested_.store(true);
        });
    }

    void startProcessingThread() {
        processingThread_ = std::thread([this]() {
            processingLoop();
        });
    }

    void processingLoop() {
        while (!shutdownRequested_.load()) {
            // 处理异步信号事件
            processAsyncSignals();
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }

        // 执行清理
        performCleanup();
    }

    void emergencyCleanup() {
        // 最小化的紧急清理
        saveCriticalState();
    }

    void performCleanup() {
        // 完整的清理操作
        saveState();
        closeConnections();
        releaseResources();
    }

    void shutdown() {
        shutdownRequested_.store(true);
        if (processingThread_.joinable()) {
            processingThread_.join();
        }
    }

    std::atomic<bool> shutdownRequested_{false};
    std::thread processingThread_;
};
```

## 依赖项

- **library/cpp/yt/error**：错误处理支持
- **library/cpp/yt/misc**：通用工具和概念
- **util/system/platform**：平台相关工具
- **signal.h**：标准信号处理接口（Unix）

## 注意事项

- **信号安全**：信号处理器中只能调用信号安全函数
- **重入性**：避免信号处理器中的重入问题
- **平台差异**：注意不同平台的信号处理差异
- **死锁风险**：避免在信号处理器中持有锁
- **异步信号安全**：注意异步信号安全函数的使用

该库为 YTsaurus 提供了强大而安全的信号处理能力，确保系统在各种异常情况下的稳定性和可控性。