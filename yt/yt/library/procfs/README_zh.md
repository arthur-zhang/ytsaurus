# ProcFS (进程文件系统)

ProcFS 是 YTsaurus 中用于访问 Linux /proc 文件系统的工具库，提供了读取进程和系统状态信息的功能。

## 概述

ProcFS 库提供以下核心功能：
- 读取进程线程数量
- 访问 /proc 文件系统信息
- 错误处理和平台兼容性
- 简化的 procfs 接口

## 核心功能

### 1. 获取线程数量
```cpp
int GetThreadCount();
```

该函数读取 `/proc/self/status` 文件，返回当前进程的线程数量。

## 错误类型

```cpp
enum class EErrorCode {
    FailedToParseProcFS = 30,    // 解析 procfs 失败
    NoSuchInfoInProcFS = 31,     // procfs 中不存在请求的信息
};
```

## 使用方法

### 基本使用
```cpp
#include <yt/yt/library/procfs/procfs.h>

try {
    int threadCount = NYT::NProcFS::GetThreadCount();
    std::cout << "Current process has " << threadCount << " threads" << std::endl;
} catch (const NYT::TErrorException& e) {
    std::cerr << "Error getting thread count: " << e.GetMessage() << std::endl;
}
```

### 错误处理
```cpp
try {
    int threadCount = GetThreadCount();
    // 使用线程数
} catch (const TErrorException& e) {
    switch (e.GetErrorCode()) {
        case EErrorCode::FailedToParseProcFS:
            std::cerr << "Failed to parse /proc/self/status" << std::endl;
            break;
        case EErrorCode::NoSuchInfoInProcFS:
            std::cerr << "Threads field not found in /proc/self/status" << std::endl;
            break;
        default:
            std::cerr << "Unknown error: " << e.GetMessage() << std::endl;
    }
}
```

## 平台兼容性

该库主要针对 Linux 系统，因为 Linux 提供了 `/proc` 文件系统。在非 Linux 平台上调用会抛出异常。

```cpp
#ifdef _linux_
    // Linux 特定实现
    TFileInput statusFile("/proc/self/status");
    // ...
#else
    THROW_ERROR_EXCEPTION("There is no procfs on this platform");
#endif
```

## 实现细节

### 解析逻辑
1. 打开 `/proc/self/status` 文件
2. 逐行读取文件内容
3. 查找以 "Threads:\t" 开头的行
4. 提取并解析线程数
5. 如果找不到则抛出异常

### 示例 /proc/self/status 输出
```
Name:   myprocess
State:  R (running)
Pid:    1234
PPid:   1
Threads:        5
...
```

## 扩展功能建议

虽然当前实现相对简单，但可以考虑添加以下功能：

### 1. 进程内存信息
```cpp
struct TMemoryInfo {
    i64 VmRSS;      // 物理内存使用
    i64 VmSize;     // 虚拟内存大小
    i64 VmPeak;     // 虚拟内存峰值
};

TMemoryInfo GetMemoryInfo();
```

### 2. CPU 使用率
```cpp
double GetCpuUsage();
```

### 3. 进程状态
```cpp
enum class EProcessState {
    Running,
    Sleeping,
    Waiting,
    Stopped,
    Zombie
};

EProcessState GetProcessState();
```

### 4. 文件描述符使用
```cpp
int GetOpenFileDescriptorCount();
```

## 使用场景

### 1. 监控和诊断
- 实时监控进程线程数
- 检测线程泄漏
- 性能调优

### 2. 资源管理
- 基于线程数的资源分配
- 负载均衡决策
- 限流控制

### 3. 调试和分析
- 运行时诊断
- 问题定位
- 性能分析

## 性能考虑

### 文件读取开销
- 每次调用都会读取 `/proc/self/status` 文件
- 考虑缓存结果如果不需要实时更新
- 批量读取多个指标以减少IO

### 错误处理开销
- 异常处理有额外开销
- 可以考虑使用 `TErrorOr<int>` 返回类型
- 在热路径中预先检查平台支持

## 最佳实践

### 1. 错误处理
```cpp
// 推荐的错误处理方式
auto threadCountOrError = TryGetThreadCount();
if (threadCountOrError.IsOK()) {
    int threadCount = threadCountOrError.Value();
    // 使用线程数
} else {
    // 处理错误
}
```

### 2. 缓存优化
```cpp
class CachedThreadCounter {
public:
    int GetThreadCount(TDuration maxAge = TDuration::Seconds(1)) {
        auto now = TInstant::Now();
        if (!lastUpdate_ || now - *lastUpdate_ > maxAge) {
            cachedCount_ = GetThreadCount();
            lastUpdate_ = now;
        }
        return cachedCount_;
    }

private:
    std::optional<int> cachedCount_;
    std::optional<TInstant> lastUpdate_;
};
```

### 3. 监控集成
```cpp
class ThreadMonitor {
public:
    void UpdateMetrics() {
        try {
            int threadCount = GetThreadCount();
            MonitoringSystem->Gauge("process.threads").Update(threadCount);

            // 检查异常情况
            if (threadCount > threshold_) {
                AlertManager->TriggerAlert("Thread count too high");
            }
        } catch (const std::exception& e) {
            MonitoringSystem->Counter("procfs.errors").Increment();
        }
    }

private:
    int threshold_ = 100;
};
```

## 依赖项

- YTsaurus 错误库 (`library/cpp/yt/error/`)
- 文件流库 (`util/stream/file.h`)

## 注意事项

1. **平台限制**: 仅支持 Linux 系统
2. **权限要求**: 需要读取 `/proc` 文件系统的权限
3. **实时性**: 读取的是调用瞬间的状态
4. **性能影响**: 频繁调用可能影响性能
5. **错误处理**: 必须妥善处理各种异常情况
6. **线程安全**: 函数本身是线程安全的

## 相关文档

- Linux procfs 手册: `man 5 proc`
- `/proc/self/status` 文档
- YTsaurus 错误处理文档