# Time Provider - 时间提供者

时间提供者库为 YTsaurus 系统提供统一的时间服务接口，支持确定性测试和高精度单调时间。

## 🎯 核心功能

### 时间提供者接口

```cpp
#include <library/cpp/time_provider/time_provider.h>

// 标准时间提供者接口
class ITimeProvider: public TThrRefBase {
public:
    virtual TInstant Now() = 0;
};

// 创建默认时间提供者（使用系统时间）
TIntrusivePtr<ITimeProvider> provider = CreateDefaultTimeProvider();
TInstant currentTime = provider->Now();

// 创建确定性时间提供者（用于测试）
TIntrusivePtr<ITimeProvider> deterministic = CreateDeterministicTimeProvider(12345);
```

### 单调时间 (Monotonic Time)

单调时间提供了不受系统时钟调整影响的时间测量，适用于超时、延迟计算等场景。

```cpp
#include <library/cpp/time_provider/monotonic.h>

using namespace NMonotonic;

// 获取当前单调时间（微秒精度）
ui64 microseconds = GetMonotonicMicroSeconds();

// 单调时间类（类似 TInstant）
TMonotonic now = TMonotonic::Now();

// 时间计算
TMonotonic future = now + TDuration::Seconds(30);
TMonotonic deadline = TMonotonic::Minutes(5);

// 时间差计算
TDuration elapsed = now - startTime;

// 时间比较
if (deadline <= TMonotonic::Now()) {
    cout << "超时了！" << endl;
}
```

#### 单调时间特性

- **不受系统时间调整影响**: 即使系统时间被修改，单调时间仍然稳定递增
- **包含系统休眠时间**: 在 Linux 上使用 `CLOCK_BOOTTIME`，系统休眠期间的时间也会被计算
- **微秒精度**: 提供高精度的时间测量
- **跨平台兼容**: 在不同操作系统上提供一致的接口

## 🚀 使用场景

### 1. 超时和延迟计算

```cpp
// 设置操作超时
TMonotonic timeout = TMonotonic::Now() + TMonotonic::Seconds(30);

while (!operationComplete) {
    if (TMonotonic::Now() > timeout) {
        throw yexception() << "操作超时";
    }
    // 执行操作...
    Sleep(TDuration::MilliSeconds(100));
}
```

### 2. 性能测量

```cpp
// 测量代码执行时间
TMonotonic start = TMonotonic::Now();

// 执行需要测量的代码
ProcessLargeDataSet();

TMonotonic end = TMonotonic::Now();
TDuration elapsed = end - start;

cout << "处理耗时: " << elapsed.MilliSeconds() << " 毫秒" << endl;
```

### 3. 速率限制

```cpp
// 简单的速率限制器
class RateLimiter {
    TMonotonic lastReset = TMonotonic::Zero();
    int remainingTokens = 0;
    const int maxTokens;
    const TMonotonic refillInterval;

public:
    RateLimiter(int tokensPerSecond)
        : maxTokens(tokensPerSecond)
        , refillInterval(TMonotonic::Seconds(1) / tokensPerSecond) {}

    bool TryAcquire() {
        TMonotonic now = TMonotonic::Now();

        if (remainingTokens == 0 || now - lastReset > refillInterval) {
            remainingTokens = maxTokens;
            lastReset = now;
        }

        if (remainingTokens > 0) {
            remainingTokens--;
            return true;
        }
        return false;
    }
};
```

### 4. 心跳和健康检查

```cpp
// 心跳监控
class HeartbeatMonitor {
    TMonotonic lastHeartbeat = TMonotonic::Zero();
    TMonotonic timeout = TMonotonic::Seconds(60);

public:
    void RecordHeartbeat() {
        lastHeartbeat = TMonotonic::Now();
    }

    bool IsAlive() const {
        return TMonotonic::Now() - lastHeartbeat < timeout;
    }
};
```

## ⚡ 性能特性

### 高精度计时
- **微秒级精度**: 时间测量精度达到微秒级别
- **低延迟调用**: `TMonotonic::Now()` 调用开销极小
- **缓存友好**: 时间数据结构设计考虑 CPU 缓存局部性

### 跨平台优化
- **Linux**: 使用 `clock_gettime(CLOCK_BOOTTIME)` 获得最佳性能
- **macOS**: 使用 `mach_absolute_time()` 高精度计数器
- **Windows**: 使用 `QueryPerformanceCounter()` 高精度计时

## 🔗 相关模块

- **threading**: 线程同步和等待
- **malloc**: 内存管理中的超时控制
- **netliba**: 网络通信中的超时处理
- **testing**: 测试框架中的时间模拟

## 📈 最佳实践

### 1. 选择合适的时间类型

```cpp
// 系统时间：需要显示给用户的时间
TInstant systemTime = TInstant::Now();
cout << "当前时间: " << systemTime.ToString() << endl;

// 单调时间：用于内部计算和超时
TMonotonic deadline = TMonotonic::Now() + TMonotonic::Seconds(30);

// 注意：不要将两者混合使用
// TDuration duration = systemTime - deadline;  // 错误！
```

### 2. 避免时间比较陷阱

```cpp
// 正确的时间比较方式
TMonotonic deadline = TMonotonic::Now() + TMonotonic::Seconds(10);

// 错误：可能会错过截止时间
while (deadline > TMonotonic::Now()) { /* ... */ }

// 正确：使用差值比较
while ((deadline - TMonotonic::Now()).MicroSeconds() > 0) { /* ... */ }
```

### 3. 测试中的时间控制

```cpp
// 测试代码中使用确定性时间
class TestService {
    TIntrusivePtr<ITimeProvider> timeProvider;

public:
    TestService(TIntrusivePtr<ITimeProvider> provider)
        : timeProvider(provider) {}

    bool IsExpired() {
        return timeProvider->Now() > expiry;
    }
};

// 生产代码
auto service = TestService(CreateDefaultTimeProvider());

// 测试代码
auto testService = TestService(CreateDeterministicTimeProvider(1000));
```

时间提供者库为 YTsaurus 提供了可靠的时间抽象，支持从高精度性能测量到确定性测试的各种时间处理需求。