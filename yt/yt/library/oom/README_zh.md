# OOM (内存不足监控)

## 项目概述

OOM 模块提供了内存不足（Out of Memory）监控和保护机制。该模块通过系统监控和早期预警，帮助系统在内存耗尽前采取保护措施，生成内存转储用于故障分析。

## 核心功能

### 内存监控
- **内存限制检查**: 监控系统内存使用情况
- **早期预警**: 在内存即将耗尽时发出警告
- **自动保护**: 触发保护机制避免系统崩溃
- **内存转储**: 生成详细的内存状态转储文件

### 看门狗机制
- **主动监控**: 持续监控内存使用状态
- **阈值检测**: 基于配置的内存阈值检测
- **动作触发**: 在检测到问题时执行预定义动作

## 主要接口

### 配置结构

```cpp
struct TOomWatchdogOptions
{
    std::optional<i64> MemoryLimit;     // 内存限制（字节）
    TString HeapDumpPath = "oom.pb.gz"; // 内存转储文件路径
};
```

### 主要函数

```cpp
// 启用早期 OOM 看门狗
void EnableEarlyOomWatchdog(TOomWatchdogOptions options);
```

## 使用方法

### 基本使用示例

```cpp
#include <yt/yt/library/oom/oom.h>

using namespace NYT;

void SetupOomMonitoring() {
    // 配置 OOM 看门狗
    TOomWatchdogOptions options;
    options.MemoryLimit = 8ULL * 1024 * 1024 * 1024;  // 8GB
    options.HeapDumpPath = "/var/log/ytsaurus/oom_dump.pb.gz";

    // 启用看门狗
    EnableEarlyOomWatchdog(options);

    Cout << "OOM monitoring enabled" << Endl;
}
```

### 应用程序集成示例

```cpp
class ApplicationWithOomProtection {
public:
    ApplicationWithOomProtection() {
        SetupOomProtection();
    }

    void Run() {
        try {
            // 主应用逻辑
            ProcessLargeDataset();
        } catch (const std::bad_alloc& e) {
            HandleMemoryExhaustion(e);
        }
    }

private:
    void SetupOomProtection() {
        TOomWatchdogOptions options;
        options.MemoryLimit = GetMemoryLimit();
        options.HeapDumpPath = GetHeapDumpPath();

        EnableEarlyOomWatchdog(options);
    }

    i64 GetMemoryLimit() {
        // 根据系统配置或环境变量确定内存限制
        const char* limitEnv = std::getenv("MEMORY_LIMIT_MB");
        if (limitEnv) {
            return std::stoll(limitEnv) * 1024 * 1024;
        }
        return 4ULL * 1024 * 1024 * 1024;  // 默认4GB
    }

    TString GetHeapDumpPath() {
        const char* dumpPath = std::getenv("OOM_DUMP_PATH");
        return dumpPath ? dumpPath : "/tmp/oom_dump.pb.gz";
    }

    void ProcessLargeDataset() {
        // 处理大型数据集的应用逻辑
        for (int i = 0; i < 1000000; ++i) {
            auto data = AllocateMemoryChunk();
            ProcessDataChunk(data);
        }
    }

    void HandleMemoryExhaustion(const std::bad_alloc& e) {
        // 处理内存耗尽情况
        Cerr << "Memory exhausted: " << e.what() << Endl;

        // 执行清理操作
        CleanupResources();

        // 记录错误信息
        LogCriticalError("Memory allocation failed", e.what());

        throw;
    }
};
```

## 配置说明

### 内存限制设置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| MemoryLimit | std::optional<i64> | std::nullopt | 内存限制（字节），未设置则使用系统默认 |
| HeapDumpPath | TString | "oom.pb.gz" | 内存转储文件路径 |

### 环境变量配置

```bash
# 设置内存限制（MB）
export MEMORY_LIMIT_MB=8192

# 设置转储文件路径
export OOM_DUMP_PATH=/var/log/ytsaurus/oom_dump.pb.gz

# 启用详细日志
export OOM_DEBUG_LOG=1
```

## 最佳实践

### 1. 渐进式内存管理

```cpp
class MemoryAwareApplication {
public:
    void InitializeWithMemoryProtection() {
        // 获取系统内存信息
        auto totalMemory = GetTotalSystemMemory();
        auto availableMemory = GetAvailableMemory();

        // 设置合理的内存限制
        auto memoryLimit = static_cast<i64>(availableMemory * 0.8);  // 使用80%可用内存

        TOomWatchdogOptions options;
        options.MemoryLimit = memoryLimit;
        options.HeapDumpPath = GenerateDumpPath();

        EnableEarlyOomWatchdog(options);
    }

private:
    i64 GetTotalSystemMemory() {
        // 获取系统总内存
        std::ifstream meminfo("/proc/meminfo");
        std::string line;
        while (std::getline(meminfo, line)) {
            if (line.substr(0, 9) == "MemTotal:") {
                std::istringstream iss(line);
                std::string label, value, unit;
                iss >> label >> value >> unit;
                return std::stoll(value) * 1024;  // 转换为字节
            }
        }
        return 0;
    }

    i64 GetAvailableMemory() {
        // 获取可用内存
        std::ifstream meminfo("/proc/meminfo");
        std::string line;
        while (std::getline(meminfo, line)) {
            if (line.substr(0, 13) == "MemAvailable:") {
                std::istringstream iss(line);
                std::string label, value, unit;
                iss >> label >> value >> unit;
                return std::stoll(value) * 1024;
            }
        }
        return 0;
    }

    TString GenerateDumpPath() {
        auto timestamp = TInstant::Now().ToString();
        return "/var/log/ytsaurus/oom_dump_" + timestamp + ".pb.gz";
    }
};
```

### 2. 内存泄漏预防

```cpp
class MemoryLeakPrevention {
private:
    std::vector<std::unique_ptr<char[]>> allocations_;
    std::atomic<size_t> totalAllocated_{0};

public:
    void* AllocateWithTracking(size_t size) {
        auto buffer = std::make_unique<char[]>(size);
        auto* ptr = buffer.get();

        allocations_.push_back(std::move(buffer));
        totalAllocated_ += size;

        // 检查内存使用是否过高
        if (totalAllocated_ > MaxMemoryUsage()) {
            TriggerMemoryCleanup();
        }

        return ptr;
    }

    void TriggerMemoryCleanup() {
        Cout << "Memory usage too high, triggering cleanup" << Endl;

        // 清理一些旧的分配
        if (allocations_.size() > 1000) {
            allocations_.erase(allocations_.begin(), allocations_.begin() + 500);
        }

        // 强制垃圾回收（如果适用）
        PerformGarbageCollection();
    }

private:
    size_t MaxMemoryUsage() {
        return 100ULL * 1024 * 1024;  // 100MB
    }

    void PerformGarbageCollection() {
        // 实现特定的垃圾回收逻辑
    }
};
```

## 依赖项

- **System Headers**: 系统内存管理相关头文件
- **Standard Library**: STL 容器和文件操作

## 注意事项

### 1. 系统影响
- OOM 监控会有一定的性能开销
- 内存转储可能占用大量磁盘空间
- 频繁的内存检查可能影响应用性能

### 2. 配置建议
- 合理设置内存限制，避免过于保守或宽松
- 确保转储文件路径有足够的存储空间
- 在生产环境中充分测试 OOM 保护机制

### 3. 故障处理
- 定期检查和分析内存转储文件
- 监控系统内存使用趋势
- 建立内存问题的响应和恢复流程

### 4. 安全考虑
- 内存转储文件可能包含敏感信息
- 合理设置转储文件的访问权限
- 考虑转储文件的加密存储