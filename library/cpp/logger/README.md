# Logger 日志系统

YTsaurus 高性能分布式日志系统，提供结构化、线程安全的日志记录功能。

## 📋 项目概述

Logger 是 YTsaurus 的核心日志组件，专为大规模分布式系统设计，支持高性能日志记录、多后端输出、日志轮转、异步写入等企业级功能。

### 🎯 核心特性

- **高性能**: 支持异步写入、批量刷新、零拷贝优化
- **线程安全**: 全面的多线程支持，无竞争条件
- **灵活后端**: 支持文件、控制台、网络、组合等多种输出后端
- **日志轮转**: 自动日志文件轮转和压缩
- **优先级过滤**: 7级日志优先级系统
- **结构化日志**: 支持自定义格式化和元数据
- **动态配置**: 运行时日志级别和输出配置
- **容错机制**: 日志文件自动重连和恢复

## 🏗️ 架构设计

### 核心组件

```
Logger System
├── TLog              # 主要日志接口
├── TLogBackend       # 后端接口抽象
│   ├── TFileLogBackend      # 文件后端
│   ├── TRotatingFileBackend # 轮转文件后端
│   ├── TCompositeLogBackend # 组合后端
│   ├── TNullLogBackend      # 空后端
│   └── TThreadedLogBackend  # 异步后端
├── TLogElement       # 流式日志元素
├── TLogRecord        # 日志记录结构
├── TLogPriority      # 日志优先级
└── TLogFilter        # 日志过滤器
```

### 优先级系统

```cpp
enum ELogPriority {
    LOG_EMERG,    // 紧急：系统不可用
    LOG_ALERT,    // 警报：必须立即行动
    LOG_CRIT,     // 关键：严重错误
    LOG_ERR,      // 错误：错误条件
    LOG_WARNING,  // 警告：警告条件
    LOG_NOTICE,   // 通知：正常但重要的信息
    LOG_INFO,     // 信息：一般信息
    LOG_DEBUG,    // 调试：调试信息
    LOG_TRACE,    // 追踪：详细追踪信息
    LOG_MAX_PRIORITY
};
```

## 💻 使用方法

### 基础使用

```cpp
#include <library/cpp/logger/all.h>

// 创建基础日志器
TLog logger;

// 写入不同级别的日志
logger.Write(TLOG_INFO, "Application started");
logger.Write(TLOG_ERR, "Failed to connect to server");
logger.Write(TLOG_DEBUG, "Processing request with ID: 12345");

// 使用流式接口
logger << TLOG_INFO << "User " << userId << " logged in from " << ip;
```

### 文件日志器

```cpp
#include <library/cpp/logger/all.h>

// 创建文件日志器
TLog fileLogger("app.log", TLOG_INFO);

// 创建带线程安全的文件日志器
auto backend = CreateLogBackend("app.log", TLOG_INFO, true);
TLog threadedLogger(std::move(backend));

// 写入日志
fileLogger << TLOG_INFO << "Server started on port " << 8080;
threadedLogger << TLOG_ERR << "Database connection failed";
```

### 轮转日志器

```cpp
#include <library/cpp/logger/all.h>

// 创建轮转文件后端
auto rotatingBackend = THolder(new TRotatingFileBackend(
    "app.log",           // 基础文件名
    100 * 1024 * 1024,   // 100MB 轮转大小
    10                   // 保留10个文件
));

TLog rotatingLogger(std::move(rotatingBackend));

// 写入日志（自动轮转）
for (int i = 0; i < 100000; ++i) {
    rotatingLogger << TLOG_INFO << "Log entry " << i;
}
```

### 组合日志器

```cpp
#include <library/cpp/logger/all.h>

// 创建多个后端
auto fileBackend = CreateLogBackend("app.log", TLOG_INFO);
auto consoleBackend = CreateLogBackend("/dev/stderr", TLOG_WARNING);

// 创建组合后端
std::vector<TLogBackend*> backends = {fileBackend.Get(), consoleBackend.Get()};
auto compositeBackend = THolder(new TCompositeLogBackend(backends));

TLog multiLogger(std::move(compositeBackend));

// 同时输出到文件和控制台
multiLogger << TLOG_ERR << "Critical error occurred";
```

### 自定义格式化

```cpp
#include <library/cpp/logger/all.h>

TLog logger("app.log");

// 设置自定义格式化器
logger.SetFormatter([](ELogPriority priority, TStringBuf message) {
    TStringBuilder formatted;
    auto now = TInstant::Now();
    formatted << "[" << now.FormatLocal("%Y-%m-%d %H:%M:%S.%f") << "] ";

    switch (priority) {
        case TLOG_ERR:    formatted << "[ERROR] "; break;
        case TLOG_WARNING: formatted << "[WARN]  "; break;
        case TLOG_INFO:   formatted << "[INFO]  "; break;
        case TLOG_DEBUG:  formatted << "[DEBUG] "; break;
        default:          formatted << "[TRACE] "; break;
    }

    // 添加线程ID
    formatted << "[TID:" << TThread::CurrentThreadId() << "] ";
    formatted << message;
    return formatted;
});

// 使用自定义格式
logger << TLOG_INFO << "Custom formatted message";
```

### 高性能异步日志

```cpp
#include <library/cpp/logger/all.h>

// 创建异步后端（带队列）
auto asyncBackend = CreateOwningThreadedLogBackend(
    "app.log",           // 文件名
    10000               // 队列大小
);

TLog asyncLogger(std::move(asyncBackend));

// 设置过滤级别
asyncLogger.SetDefaultPriority(TLOG_INFO);

// 高性能写入（异步）
for (int i = 0; i < 1000000; ++i) {
    asyncLogger << TLOG_INFO << "High performance logging " << i;
}

// 检查队列大小
size_t queueSize = asyncLogger.BackEndQueueSize();
Cout << "Async queue size: " << queueSize << Endl;
```

### 带过滤器的日志器

```cpp
#include <library/cpp/logger/all.h>

// 创建基于优先级的过滤器
class TPriorityFilter: public TLogFilter {
public:
    TPriorityFilter(ELogPriority minLevel): MinLevel(minLevel) {}

    bool Accept(ELogPriority priority) const override {
        return priority >= MinLevel;
    }

private:
    ELogPriority MinLevel;
};

// 创建过滤后端
auto fileBackend = CreateLogBackend("app.log");
auto filterBackend = THolder(new TFilteredLogBackend(
    std::move(fileBackend),
    THolder(new TPriorityFilter(TLOG_WARNING))
));

TLog filterLogger(std::move(filterBackend));

// 只有 WARNING 及以上级别会被记录
filterLogger << TLOG_DEBUG << "This won't be logged";
filterLogger << TLOG_INFO << "This won't be logged";
filterLogger << TLOG_WARNING << "This will be logged";
filterLogger << TLOG_ERR << "This will be logged";
```

### 带上下文的日志器

```cpp
#include <library/cpp/logger/all.h>

class TContextLogger {
public:
    TContextLogger(TLog baseLogger, TString requestId)
        : BaseLogger(baseLogger), RequestId(requestId)
    {
        BaseLogger.SetFormatter([this](ELogPriority priority, TStringBuf message) {
            return TStringBuilder() << "[req:" << RequestId << "] " << message;
        });
    }

    template <typename T>
    auto operator<<(const T& data) const {
        return BaseLogger << data;
    }

private:
    TLog BaseLogger;
    TString RequestId;
};

// 使用上下文日志器
TLog baseLogger("app.log");
TContextLogger requestLogger(baseLogger, "req-12345");

requestLogger << TLOG_INFO << "Processing request started";
requestLogger << TLOG_ERR << "Request processing failed";
```

## 🔧 配置选项

### 日志级别配置

```cpp
// 运行时修改日志级别
logger.SetDefaultPriority(TLOG_DEBUG);

// 获取当前过滤级别
ELogPriority currentLevel = logger.FiltrationLevel();

// 检查是否为空日志器
if (logger.IsNullLog()) {
    // 处理空日志器情况
}
```

### 重配日志后端

```cpp
// 重置后端（非线程安全）
auto newBackend = CreateLogBackend("new_app.log");
logger.ResetBackend(std::move(newBackend));

// 释放当前后端
auto oldBackend = logger.ReleaseBackend();

// 重新打开日志文件
logger.ReopenLog();           // 带刷新
logger.ReopenLogNoFlush();    // 不刷新
```

### 后端队列配置

```cpp
// 检查异步队列大小
size_t queueSize = logger.BackEndQueueSize();

// 创建指定队列大小的异步后端
auto backend = CreateFilteredOwningThreadedLogBackend(
    "app.log",
    TLOG_INFO,
    50000    // 队列大小
);
```

## 📊 性能优化

### 异步写入优化

```cpp
// 使用异步后端提高性能
auto asyncBackend = CreateOwningThreadedLogBackend("high_volume.log", 100000);
TLog perfLogger(std::move(asyncBackend));

// 批量写入优化
for (int i = 0; i < batch_size; ++i) {
    perfLogger << TLOG_INFO << "Batch entry " << i;
}

// 避免频繁的级别检查
const ELogPriority currentPriority = TLOG_INFO;
for (auto& item : large_collection) {
    perfLogger.Write(currentPriority, FormatEntry(item));
}
```

### 内存优化

```cpp
// 复用日志器实例
TLog& GetLogger() {
    static TLog logger("optimized.log", TLOG_INFO);
    return logger;
}

// 使用StringBuilder减少字符串拷贝
TStringBuilder logMessage;
logMessage << "Complex message with " << multiple << " parts";
logger.Write(TLOG_INFO, logMessage);
```

### 缓存优化

```cpp
// 预格式化常用消息
static const TString START_MSG = "=== Application Started ===";
static const TString STOP_MSG = "=== Application Stopped ===";

logger.Write(TLOG_INFO, START_MSG);
```

## 🔍 错误处理和监控

### 日志健康检查

```cpp
// 检查日志系统状态
bool IsLoggerHealthy(const TLog& logger) {
    if (logger.IsNullLog()) {
        return false;
    }

    // 检查队列大小
    if (logger.BackEndQueueSize() > 100000) {
        return false;
    }

    return true;
}

// 定期健康检查
void CheckLoggerHealth(const TLog& logger) {
    if (!IsLoggerHealthy(logger)) {
        std::cerr << "Logger health check failed!" << std::endl;
        // 采取恢复措施
        logger.ReopenLog();
    }
}
```

### 错误恢复

```cpp
// 带重试机制的日志写入
void SafeLog(TLog& logger, ELogPriority priority, const TString& message) {
    static const int MAX_RETRIES = 3;
    int attempts = 0;

    while (attempts < MAX_RETRIES) {
        try {
            logger.Write(priority, message);
            break;
        } catch (const std::exception& e) {
            ++attempts;
            if (attempts == MAX_RETRIES) {
                std::cerr << "Failed to log after " << MAX_RETRIES
                         << " attempts: " << e.what() << std::endl;
                break;
            }

            // 尝试重新打开日志文件
            logger.ReopenLog();
            Sleep(TDuration::MilliSeconds(100));
        }
    }
}
```

## 🧪 测试和调试

### 单元测试

```cpp
#include <library/cpp/testing/unittest/registar.h>
#include <library/cpp/logger/all.h>

Y_UNIT_TEST_SUITE(LoggerTest) {
    Y_UNIT_TEST(BasicLogging) {
        TLog logger;

        // 测试基本写入
        logger.Write(TLOG_INFO, "Test message");
        UNIT_ASSERT(logger.IsNotNullLog());
    }

    Y_UNIT_TEST(PriorityFiltering) {
        auto backend = CreateLogBackend("test.log", TLOG_WARNING);
        TLog logger(std::move(backend));

        // 测试优先级过滤
        ELogPriority filterLevel = logger.FiltrationLevel();
        UNIT_ASSERT_VALUES_EQUAL(filterLevel, TLOG_WARNING);
    }

    Y_UNIT_TEST(CustomFormatting) {
        TLog logger;
        bool formatterCalled = false;

        logger.SetFormatter([&formatterCalled](ELogPriority priority, TStringBuf msg) {
            formatterCalled = true;
            return TString(msg);
        });

        logger << TLOG_INFO << "Test";
        UNIT_ASSERT(formatterCalled);
    }
}
```

### 调试技巧

```cpp
// 开发环境调试宏
#ifdef DBG
    #define DBG_LOG(logger, priority, msg) \
        logger << priority << "[DEBUG] " << msg << " (" << __FILE__ << ":" << __LINE__ << ")"
#else
    #define DBG_LOG(logger, priority, msg)
#endif

// 使用调试日志
DBG_LOG(logger, TLOG_DEBUG, "Debug information");

// 性能监控
class TPerformanceLogger {
public:
    TPerformanceLogger(TLog logger, TString operation)
        : Logger(logger), Operation(operation), Start(TInstant::Now())
    {}

    ~TPerformanceLogger() {
        auto duration = TInstant::Now() - Start;
        Logger << TLOG_INFO << "Operation '" << Operation
               << "' completed in " << duration.MilliSeconds() << "ms";
    }

private:
    TLog Logger;
    TString Operation;
    TInstant Start;
};

// 使用性能监控
{
    TPerformanceLogger perf(logger, "DataProcessing");
    // 执行数据处理
    ProcessData();
} // 自动记录执行时间
```

## 📈 最佳实践

### 生产环境建议

1. **日志级别管理**
   ```cpp
   // 生产环境使用适当的日志级别
   #ifdef NDEBUG
       TLog prodLogger("production.log", TLOG_INFO);
   #else
       TLog devLogger("debug.log", TLOG_DEBUG);
   #endif
   ```

2. **异步写入**
   ```cpp
   // 高吞吐量场景使用异步后端
   auto asyncBackend = CreateOwningThreadedLogBackend("high_volume.log", 100000);
   ```

3. **日志轮转**
   ```cpp
   // 配置自动轮转防止日志文件过大
   auto rotatingBackend = THolder(new TRotatingFileBackend(
       "app.log", 500 * 1024 * 1024, 20));  // 500MB, 保留20个文件
   ```

4. **结构化日志**
   ```cpp
   // 使用结构化格式便于解析
   logger.SetFormatter([](ELogPriority p, TStringBuf msg) {
       return JsonBuilder()
           .BeginObject()
               .Item("timestamp").Value(TInstant::Now().IsoStringLocal())
               .Item("level").Value(ToString(p))
               .Item("message").Value(msg)
               .Item("thread_id").Value(TThread::CurrentThreadId())
           .EndObject();
   });
   ```

### 性能建议

1. 避免在热路径中进行复杂的字符串格式化
2. 使用异步后端处理高并发场景
3. 合理设置日志级别，避免记录过多调试信息
4. 定期检查日志队列大小，防止内存溢出
5. 使用日志轮转管理磁盘空间

### 安全建议

1. 避免在日志中记录敏感信息（密码、密钥等）
2. 实施日志访问控制
3. 定期清理过期日志文件
4. 监控日志文件大小和磁盘使用情况

## 🔗 相关模块

- **Threading**: 提供线程安全支持
- **FileSystem**: 日志文件操作
- **JSON**: 结构化日志格式支持
- **TimeProvider**: 时间戳生成
- **Memory**: 内存管理和优化

Logger 日志系统为 YTsaurus 提供了企业级的日志记录能力，支持从简单的文件日志到复杂的分布式日志聚合的各种使用场景。