# Safe Assert 安全断言库

## 项目概述

`NSafeAssert` 是 YTsaurus 中的安全断言库，提供了一种增强的断言机制，能够在断言失败时生成详细的诊断信息，包括堆栈跟踪、核心转储和自定义注释。该库支持异步核心转储生成，防止资源耗尽，并提供了灵活的配置选项。

## 核心功能

- **增强断言**：比标准断言提供更丰富的错误信息
- **堆栈跟踪**：自动捕获详细的调用堆栈信息
- **核心转储**：异步生成核心转储文件用于后续分析
- **资源控制**：使用信号量控制并发核心转储数量
- **自定义注释**：支持添加自定义诊断信息
- **异常安全**：提供异常形式的断言失败处理

## 主要接口

### TAssertionFailedException - 断言失败异常

```cpp
#include <yt/yt/library/safe_assert/safe_assert.h>

using namespace NYT;

try {
    // 可能触发断言的代码
} catch (const TAssertionFailedException& ex) {
    // 处理断言失败异常
    Cout << "Assertion failed: " << ex.GetExpression() << Endl;
    Cout << "Stack trace: " << ex.GetStackTrace() << Endl;

    if (ex.GetCorePath()) {
        Cout << "Core dump: " << *ex.GetCorePath() << Endl;
    }
}
```

### CreateSafeAssertionGuard - 创建安全断言保护

```cpp
#include <yt/yt/library/safe_assert/safe_assert.h>

using namespace NYT;
using namespace NConcurrency;
using namespace NCoreDump;

// 创建安全断言保护
auto guard = CreateSafeAssertionGuard(
    coreDumper,           // 核心转储器
    coreSemaphore,        // 异步信号量
    {"Custom note 1", "Custom note 2"}  // 核心注释
);

// 在保护作用域内使用
{
    // 断言将使用上面创建的保护
    // 失败时会生成核心转储和堆栈跟踪
}

// guard 析构时自动清理
```

## 使用方法

### 基本安全断言

```cpp
#include <yt/yt/library/safe_assert/safe_assert.h>

using namespace NYT;

void criticalOperation() {
    // 创建安全断言保护
    auto coreDumper = CreateCoreDumper();
    auto coreSemaphore = New<TAsyncSemaphore>(5);  // 最多5个并发核心转储

    auto guard = CreateSafeAssertionGuard(
        coreDumper,
        coreSemaphore,
        {"Critical operation failed"}
    );

    // 关键断言
    int* ptr = nullptr;
    SAFE_ASSERT(ptr != nullptr, "Pointer cannot be null in critical operation");

    // 或者使用异常版本
    SAFE_ASSERT_THROW(ptr != nullptr, "Pointer cannot be null");
}
```

### 高级配置示例

```cpp
#include <yt/yt/library/safe_assert/safe_assert.h>
#include <yt/yt/library/coredumper/coredumper.h>
#include <yt/yt/core/concurrency/async_semaphore.h>

using namespace NYT;
using namespace NConcurrency;
using namespace NCoreDump;

class SafeAssertManager {
public:
    SafeAssertManager() {
        initialize();
    }

    void executeWithSafeAssert(std::function<void()> operation) {
        auto guard = createGuard();

        try {
            operation();
        } catch (const TAssertionFailedException& ex) {
            handleAssertionFailure(ex);
        }
    }

private:
    void initialize() {
        // 创建核心转储器
        coreDumper_ = CreateCoreDumper();

        // 创建资源控制信号量
        coreSemaphore_ = New<TAsyncSemaphore>(
            MaxConcurrentCoreDumps,  // 限制并发核心转储数
            "SafeAssertCoreSemaphore"
        );
    }

    std::any createGuard() {
        return CreateSafeAssertionGuard(
            coreDumper_,
            coreSemaphore_,
            {
                "Service: " + serviceName_,
                "Version: " + version_,
                "Timestamp: " + ToString(TInstant::Now())
            }
        );
    }

    void handleAssertionFailure(const TAssertionFailedException& ex) {
        YT_LOG_ERROR(ex, "Safe assertion failed");

        // 记录详细信息
        auto error = TError("Safe assertion failed")
            << TErrorAttribute("expression", ex.GetExpression())
            << TErrorAttribute("stack_trace", ex.GetStackTrace());

        if (ex.GetCorePath()) {
            error <<= TErrorAttribute("core_path", *ex.GetCorePath());
        }

        // 发送错误报告
        reportError(error);
    }

    ICoreDumperPtr coreDumper_;
    TAsyncSemaphorePtr coreSemaphore_;
    TString serviceName_ = "MyService";
    TString version_ = "1.0.0";
    static constexpr int MaxConcurrentCoreDumps = 3;
};
```

### 条件性安全断言

```cpp
#include <yt/yt/library/safe_assert/safe_assert.h>

class SafeAssertHelper {
public:
    static void validateInput(const std::vector<int>& data) {
        // 只在调试模式或特定条件下启用
        #ifdef YT_DEBUG
            auto guard = createDebugGuard();
        #endif

        // 输入验证
        SAFE_ASSERT(!data.empty(), "Input data cannot be empty");

        if (data.size() > 1000) {
            SAFE_ASSERT_THROW(false, "Input data too large: " << data.size());
        }

        // 数据完整性检查
        for (size_t i = 0; i < data.size(); ++i) {
            SAFE_ASSERT(data[i] >= 0, "Negative value at index " << i);
        }
    }

private:
    #ifdef YT_DEBUG
    static std::any createDebugGuard() {
        static auto coreDumper = CreateCoreDumper();
        static auto coreSemaphore = New<TAsyncSemaphore>(1);

        return CreateSafeAssertionGuard(
            coreDumper,
            coreSemaphore,
            {"Debug mode validation"}
        );
    }
    #endif
};
```

## 性能考虑

- **资源控制**：使用信号量限制并发核心转储，防止系统资源耗尽
- **异步处理**：核心转储生成是异步的，不会阻塞主执行流程
- **内存开销**：堆栈跟踪收集有一定开销，可按需启用
- **存储空间**：核心转储文件可能很大，需要足够的磁盘空间

```cpp
// 性能优化示例
class OptimizedSafeAssert {
public:
    OptimizedSafeAssert(bool enableFullDiagnostics = true)
        : enableFullDiagnostics_(enableFullDiagnostics)
    { }

    template<typename T>
    void validate(const T& value, const TString& context) {
        if (enableFullDiagnostics_) {
            // 完整诊断模式
            auto guard = createFullGuard(context);
            SAFE_ASSERT(isValid(value), "Validation failed: " << context);
        } else {
            // 轻量级模式
            SAFE_ASSERT(isValid(value), "Validation failed: " << context);
        }
    }

private:
    std::any createFullGuard(const TString& context) {
        return CreateSafeAssertionGuard(
            coreDumper_,
            coreSemaphore_,
            {
                "Context: " + context,
                "Timestamp: " + ToString(TInstant::Now()),
                "Thread: " + ToString(GetCurrentThreadId())
            }
        );
    }

    bool enableFullDiagnostics_;
    ICoreDumperPtr coreDumper_ = CreateCoreDumper();
    TAsyncSemaphorePtr coreSemaphore_ = New<TAsyncSemaphore>(2);
};
```

## 最佳实践

1. **合理使用**：只在关键路径和可能失败的断言处使用
2. **资源控制**：设置合适的并发核心转储限制
3. **错误处理**：妥善捕获和处理断言失败异常
4. **日志记录**：将断言失败信息记录到日志系统
5. **配置管理**：支持运行时启用/禁用安全断言

```cpp
// 最佳实践示例
class ProductionSafeAssert {
public:
    ProductionSafeAssert(const TSafeAssertConfig& config)
        : config_(config)
    {
        initialize();
    }

    void criticalSection(std::function<void()> operation) {
        if (!config_.Enabled) {
            operation();
            return;
        }

        auto guard = createGuard();

        try {
            operation();
        } catch (const TAssertionFailedException& ex) {
            handleCriticalFailure(ex);
            throw;  // 重新抛出异常
        }
    }

private:
    void initialize() {
        if (config_.Enabled) {
            coreDumper_ = CreateCoreDumper();
            coreSemaphore_ = New<TAsyncSemaphore>(config_.MaxConcurrentCoreDumps);
        }
    }

    std::any createGuard() {
        if (!config_.Enabled) {
            return std::any();
        }

        return CreateSafeAssertionGuard(
            coreDumper_,
            coreSemaphore_,
            config_.CoreNotes
        );
    }

    void handleCriticalFailure(const TAssertionFailedException& ex) {
        YT_LOG_CRITICAL(ex, "Critical safe assertion failed");

        // 发送告警
        sendAlert(ex);

        // 记录到监控系统
        reportToMonitoring(ex);
    }

    TSafeAssertConfig config_;
    ICoreDumperPtr coreDumper_;
    TAsyncSemaphorePtr coreSemaphore_;
};
```

## 依赖项

- **yt/yt/library/coredumper**：核心转储生成库
- **yt/yt/core/concurrency**：并发控制和异步操作支持
- **yt/yt/core/misc**：通用工具和基础设施
- **library/cpp/yt/memory**：内存管理工具
- **util/system**：系统级工具和平台支持

## 注意事项

- **线程安全**：每个线程需要创建独立的安全断言保护
- **资源限制**：注意磁盘空间和核心转储文件的管理
- **性能影响**：在性能敏感的代码路径中谨慎使用
- **异常安全**：确保异常传播不会造成资源泄漏
- **平台差异**：不同平台的核心转储支持可能有差异

该库为 YTsaurus 提供了强大的调试和诊断能力，特别适用于生产环境中难以复现的问题分析和系统健康监控。