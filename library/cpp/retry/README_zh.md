# Retry - 重试机制库

## 项目概述

Retry 库为 YTsaurus 系统提供了灵活且强大的重试机制，支持多种重试策略，包括固定间隔、指数退避、随机抖动等。该库专门用于处理分布式系统中的网络请求、数据库操作、外部服务调用等可能失败的操作，提高系统的容错性和可靠性。

## 核心功能

### 重试策略
- **固定间隔重试**: 每次重试之间使用固定的时间间隔
- **指数退避**: 重试间隔按照指数增长，避免系统过载
- **线性递增**: 重试间隔线性增加
- **随机抖动**: 在固定间隔基础上添加随机性，避免雷群效应
- **混合策略**: 结合多种策略实现最优的重试效果

### 错误分类
- **NoRetry**: 不可重试的错误，立即返回失败
- **ShortRetry**: 短时间重试，适用于临时性错误
- **LongRetry**: 需要等待后重试的错误，适用于服务不可用等场景

## 重要文件说明

### 核心头文件

- **`retry.h/cpp`**: 主要的重试接口和实现，提供 `TRetryOptions` 配置类和通用的重试函数
- **`retry_policy.h/cpp`**: 重试策略接口，定义了 `IRetryPolicy` 抽象基类和相关策略实现
- **`utils.h/cpp`**: 重试工具函数和辅助类

### 配置结构

```cpp
struct TRetryOptions {
    ui32 RetryCount;                          // 最大重试次数
    TDuration SleepDuration;                  // 基础睡眠时间
    TDuration SleepRandomDelta;              // 随机抖动范围
    TDuration SleepIncrement;                // 线性递增值
    TDuration SleepExponentialMultiplier;    // 指数退避乘数
    std::function<void(TDuration)> SleepFunction; // 自定义睡眠函数
};
```

## 使用示例

### 基础用法

```cpp
#include <library/cpp/retry/retry.h>

// 简单的重试操作
bool TryConnectToDatabase() {
    return DoWithRetryOnRetCode([]() {
        return TryDatabaseConnection();
    }, TRetryOptions::Count(3));  // 最多重试3次
}

// 带自定义配置的重试
bool ComplexRetryOperation() {
    TRetryOptions options;
    options.WithCount(5)
           .WithSleep(TDuration::MilliSeconds(100))
           .WithRandomDelta(TDuration::MilliSeconds(50))
           .WithExponentialMultiplier(TDuration::MilliSeconds(200));

    return DoWithRetryOnRetCode([&]() {
        return PerformNetworkRequest();
    }, options);
}
```

### 高级重试策略

```cpp
#include <library/cpp/retry/retry_policy.h>

// 使用自定义重试策略
class CustomRetryPolicy : public IRetryPolicy<const std::exception&> {
public:
    TRetryClassFunction GetRetryClassFunction() const override {
        return [](const std::exception& e) -> ERetryErrorClass {
            // 网络错误短时间重试
            if (dynamic_cast<const NetworkException*>(&e)) {
                return ERetryErrorClass::ShortRetry;
            }

            // 数据库错误长时间重试
            if (dynamic_cast<const DatabaseException*>(&e)) {
                return ERetryErrorClass::LongRetry;
            }

            // 其他错误不重试
            return ERetryErrorClass::NoRetry;
        };
    }

    IRetryState::TPtr CreateRetryState() const override {
        return std::make_unique<CustomRetryState>();
    }
};
```

### 模板化重试

```cpp
// 泛型重试函数
template<typename TResult, typename TException = std::exception>
TResult RetryOperation(std::function<TResult()> operation,
                      TRetryOptions options = TRetryOptions::Default()) {
    auto policy = std::make_shared<ExceptionRetryPolicy<TException>>();

    return DoWithRetry<TResult, TException>(
        std::move(operation),
        std::move(policy),
        options.SleepFunction
    );
}

// 使用示例
auto result = RetryOperation<std::string>([]() {
    return CallExternalAPI();
});
```

## 实现原理

### 重试状态管理
```cpp
class IRetryState {
public:
    virtual ~IRetryState() = default;

    // 计算下次重试的延迟时间
    // 返回空值表示不再重试
    virtual TMaybe<TDuration> GetNextRetryDelay(
        typename TTypeTraits<TArgs>::TFuncParam... args) = 0;
};
```

### 延迟计算公式
总延迟时间计算：
```
TotalDuration = SleepDuration + RandomDelta + (attempt * SleepIncrement) + (2^attempt * SleepExponentialMultiplier)
```

其中：
- `SleepDuration`: 基础延迟时间
- `RandomDelta`: 随机抖动时间
- `SleepIncrement`: 线性递增值（基于重试次数）
- `SleepExponentialMultiplier`: 指数退避乘数

## 应用场景

### 1. 网络请求重试

```cpp
// HTTP 请求重试
TString FetchDataFromAPI(const TString& url) {
    return RetryOperation<TString, NetworkException>([&]() {
        auto response = HttpClient->Get(url);
        if (response.GetStatusCode() >= 500) {
            throw NetworkException("Server error");
        }
        return response.GetContent();
    }, TRetryOptions::Count(3).WithSleep(TDuration::Seconds(1)));
}
```

### 2. 数据库操作重试

```cpp
// 数据库事务重试
bool ExecuteDatabaseTransaction(const TString& sql) {
    TRetryOptions options;
    options.WithCount(5)
           .WithSleep(TDuration::MilliSeconds(100))
           .WithExponentialMultiplier(TDuration::MilliSeconds(200));

    return DoWithRetryOnRetCode([&]() {
        try {
            Database->Execute(sql);
            return true;
        } catch (const DatabaseBusyException&) {
            return false;  // 触发重试
        } catch (const DatabaseException&) {
            return true;   // 不重试
        }
    }, options);
}
```

### 3. 文件操作重试

```cpp
// 文件读取重试
TString ReadFileWithRetry(const TString& path) {
    return RetryOperation<TString, std::runtime_error>([&]() {
        std::ifstream file(path);
        if (!file) {
            throw std::runtime_error("Cannot open file: " + path);
        }

        TString content;
        std::string line;
        while (std::getline(file, line)) {
            content += line + "\n";
        }

        return content;
    }, TRetryOptions::Count(3).WithSleep(TDuration::MilliSeconds(50)));
}
```

### 4. 分布式服务调用

```cpp
// 微服务调用重试
class ServiceClient {
public:
    template<typename TRequest, typename TResponse>
    TResponse CallServiceWithRetry(const TRequest& request) {
        auto retryOptions = TRetryOptions::Count(3)
            .WithSleep(TDuration::MilliSeconds(200))
            .WithRandomDelta(TDuration::MilliSeconds(100))
            .WithExponentialMultiplier(TDuration::MilliSeconds(400));

        return DoWithRetry<TResponse, ServiceException>([&]() {
            return MakeRemoteCall<TRequest, TResponse>(request);
        }, retryOptions);
    }
};
```

### 5. 批量操作重试

```cpp
// 批量操作重试管理器
class BatchRetryManager {
private:
    TQueue<std::function<bool()>> pendingOperations;
    TRetryOptions retryOptions;

public:
    BatchRetryManager(TRetryOptions options) : retryOptions(options) {}

    void AddOperation(std::function<bool()> operation) {
        pendingOperations.push(operation);
    }

    void ProcessAll() {
        while (!pendingOperations.empty()) {
            auto operation = pendingOperations.front();
            pendingOperations.pop();

            bool success = DoWithRetryOnRetCode(operation, retryOptions);
            if (!success) {
                // 记录失败的操作
                LogFailedOperation(operation);
            }
        }
    }
};
```

## 高级特性

### 自定义睡眠函数

```cpp
// 异步睡眠函数
class AsyncRetryManager {
public:
    TFuture<bool> RetryAsync(std::function<bool()> operation) {
        TRetryOptions options;
        options.WithSleepFunction([this](TDuration duration) {
            return AsyncSleep(duration);
        });

        return DoWithRetryAsync(operation, options);
    }

private:
    TFuture<void> AsyncSleep(TDuration duration) {
        auto promise = std::make_shared<TPromise<void>>();

        Scheduler->ScheduleAfter(duration, [promise]() {
            promise->SetValue();
        });

        return promise->GetFuture();
    }
};
```

### 重试监控和统计

```cpp
// 重试统计收集
class RetryStats {
private:
    std::atomic<size_t> totalRetries{0};
    std::atomic<size_t> successfulRetries{0};
    std::atomic<size_t> failedRetries{0};
    TMap<std::string, size_t> operationStats;

public:
    void RecordRetry(const std::string& operation, bool success) {
        totalRetries++;
        operationStats[operation]++;

        if (success) {
            successfulRetries++;
        } else {
            failedRetries++;
        }
    }

    void PrintStats() {
        Cout << "重试统计:" << Endl;
        Cout << "  总重试次数: " << totalRetries << Endl;
        Cout << "  成功重试: " << successfulRetries << Endl;
        Cout << "  失败重试: " << failedRetries << Endl;

        for (const auto& [op, count] : operationStats) {
            Cout << "  " << op << ": " << count << Endl;
        }
    }
};
```

## 最佳实践

### 1. 重试策略选择

```cpp
TRetryOptions GetOptimalRetryOptions(RetryScenario scenario) {
    switch (scenario) {
        case RetryScenario::NetworkRequest:
            return TRetryOptions::Count(3)
                .WithSleep(TDuration::MilliSeconds(100))
                .WithExponentialMultiplier(TDuration::MilliSeconds(200));

        case RetryScenario::DatabaseOperation:
            return TRetryOptions::Count(5)
                .WithSleep(TDuration::MilliSeconds(50))
                .WithRandomDelta(TDuration::MilliSeconds(25));

        case RetryScenario::FileOperation:
            return TRetryOptions::Count(2)
                .WithSleep(TDuration::MilliSeconds(10));

        default:
            return TRetryOptions::Default();
    }
}
```

### 2. 异常处理和重试决策

```cpp
// 智能重试决策
class SmartRetryPolicy : public IRetryPolicy<std::exception> {
public:
    TRetryClassFunction GetRetryClassFunction() const override {
        return [](const std::exception& e) -> ERetryErrorClass {
            // 网络相关错误
            if (const auto* netEx = dynamic_cast<const NetworkException*>(&e)) {
                switch (netEx->GetErrorCode()) {
                    case NetworkError::Timeout:
                    case NetworkError::ConnectionRefused:
                        return ERetryErrorClass::ShortRetry;
                    case NetworkError::ServiceUnavailable:
                        return ERetryErrorClass::LongRetry;
                    default:
                        return ERetryErrorClass::NoRetry;
                }
            }

            // 数据库错误
            if (const auto* dbEx = dynamic_cast<const DatabaseException*>(&e)) {
                switch (dbEx->GetErrorCode()) {
                    case DatabaseError::Deadlock:
                    case DatabaseError::LockTimeout:
                        return ERetryErrorClass::ShortRetry;
                    case DatabaseError::ConnectionLost:
                        return ERetryErrorClass::LongRetry;
                    default:
                        return ERetryErrorClass::NoRetry;
                }
            }

            return ERetryErrorClass::NoRetry;
        };
    }
};
```

### 3. 性能优化

```cpp
// 重试配置缓存
class RetryConfigCache {
private:
    static THashMap<std::string, TRetryOptions> configCache;
    static std::mutex cacheMutex;

public:
    static const TRetryOptions& GetConfig(const std::string& operationType) {
        std::lock_guard<std::mutex> lock(cacheMutex);

        auto it = configCache.find(operationType);
        if (it != configCache.end()) {
            return it->second;
        }

        // 创建并缓存新配置
        TRetryOptions config = LoadConfigFromSettings(operationType);
        configCache[operationType] = config;
        return configCache[operationType];
    }
};
```

## 相关模块

- **network**: 网络通信中的重试机制
- **database**: 数据库操作的重试逻辑
- **testing**: 测试框架中的模拟重试
- **threading**: 多线程环境下的重试同步
- **logging**: 重试操作的日志记录

这个重试库为 YTsaurus 提供了全面的容错能力，确保系统在面对各种临时性故障时能够自动恢复，提高了系统的可靠性和用户体验。