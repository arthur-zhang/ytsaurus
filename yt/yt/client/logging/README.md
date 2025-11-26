# YTsaurus Logging Client 模块

## 概述

Logging Client 模块是 YTsaurus 的动态日志记录系统，专门用于高性能的结构化日志写入。该模块支持动态表日志写入，提供高吞吐量、低延迟的日志记录功能，适用于大规模系统的日志聚合和分析。

## 核心功能

### 1. 动态表日志写入
- **结构化日志**: 支持复杂结构化数据的日志记录
- **动态表**: 写入动态模式的数据表
- **批量写入**: 高效的批量日志写入
- **异步处理**: 异步日志写入减少延迟

### 2. 配置管理
- **灵活配置**: 支持多种日志配置选项
- **性能调优**: 针对不同场景的优化参数
- **格式控制**: 支持多种日志格式

## 主要组件

### 1. 动态表日志写入器 (dynamic_table_log_writer.h/cpp)
```cpp
class TDynamicTableLogWriter {
public:
    TDynamicTableLogWriter(
        NApi::IClientPtr client,
        const TString& tablePath,
        TDynamicTableLogConfigPtr config);

    void Write(const NYson::TYsonString& logEntry);
    void Flush();
    void Close();
};
```

### 2. 配置系统 (config.h/cpp)
```cpp
struct TDynamicTableLogConfig : public NYTree::TYsonStruct {
    TDuration FlushInterval;        // 刷新间隔
    size_t BatchSize;               // 批量大小
    bool EnableCompression;         // 启用压缩
    int MaxRetries;                 // 最大重试次数
    TDuration WriteTimeout;         // 写入超时
};
```

## 使用方法

### 1. 基本日志写入

```cpp
#include <yt/yt/client/logging/public.h>
#include <yt/yt/client/logging/dynamic_table_log_writer.h>

using namespace NYT::NLogging;

// 创建日志配置
auto config = New<TDynamicTableLogConfig>();
config->FlushInterval = TDuration::Seconds(5);
config->BatchSize = 1000;
config->EnableCompression = true;

// 创建日志写入器
auto writer = std::make_unique<TDynamicTableLogWriter>(
    client,
    "/path/to/log/table",
    config);

// 写入日志
writer->Write(NYson::ConvertToYsonString(TYsonString(R"({
    "timestamp" = 1234567890,
    "level" = "INFO",
    "message" = "Operation completed successfully",
    "operation_id" = "op-123",
    "details" = {
        "duration_ms" = 1500,
        "records_processed" = 1000
    }
})")));

// 刷新和关闭
writer->Flush();
writer->Close();
```

### 2. 高性能批量写入

```cpp
// 高性能日志处理器
class HighPerformanceLogger {
private:
    std::unique_ptr<TDynamicTableLogWriter> writer_;
    std::vector<NYson::TYsonString> batchBuffer_;
    std::mutex bufferMutex_;

public:
    void WriteAsync(const NYson::TYsonString& entry) {
        std::lock_guard<std::mutex> lock(bufferMutex_);
        batchBuffer_.push_back(entry);

        if (batchBuffer_.size() >= BatchThreshold) {
            FlushBatch();
        }
    }

    void FlushBatch() {
        if (batchBuffer_.empty()) return;

        std::vector<NYson::TYsonString> batch;
        std::swap(batch, batchBuffer_);

        for (const auto& entry : batch) {
            writer_->Write(entry);
        }

        writer_->Flush();
    }
};
```

### 3. 错误处理和重试

```cpp
// 带重试的日志写入器
class ResilientLogWriter {
public:
    void WriteWithRetry(const NYson::TYsonString& entry) {
        int attempts = 0;
        while (attempts < MaxRetries) {
            try {
                writer_->Write(entry);
                return;
            } catch (const TErrorException& e) {
                attempts++;
                if (attempts >= MaxRetries) {
                    YT_LOG_ERROR("Failed to write log after %v attempts: %v",
                        MaxRetries, e);
                    return;
                }

                // 指数退避
                auto delay = TDuration::MilliSeconds(100 * (1 << attempts));
                TDelay::Wait(delay);
            }
        }
    }
};
```

## 性能优化

### 1. 内存优化
- **批量缓冲**: 内存中的批量缓冲区
- **压缩**: 实时压缩减少内存占用
- **对象池**: 复用日志对象

### 2. I/O 优化
- **异步写入**: 异步批量写入
- **连接复用**: 复用客户端连接
- **预分配**: 预分配缓冲区

### 3. 并发优化
- **线程安全**: 线程安全的并发写入
- **锁优化**: 最小化锁竞争
- **无锁队列**: 高性能无锁数据结构

## 配置参数详解

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| FlushInterval | TDuration | 5s | 自动刷新间隔 |
| BatchSize | size_t | 1000 | 批量写入大小 |
| EnableCompression | bool | true | 启用压缩 |
| MaxRetries | int | 3 | 最大重试次数 |
| WriteTimeout | TDuration | 30s | 写入超时时间 |
| BufferSize | size_t | 1MB | 缓冲区大小 |
| CompressionCodec | ECompressionCodec | LZ4 | 压缩算法 |

## 最佳实践

### 1. 配置选择指南

```cpp
// 不同场景的推荐配置
class LogConfigFactory {
public:
    static TDynamicTableLogConfigPtr CreateForHighThroughput() {
        auto config = New<TDynamicTableLogConfig>();
        config->FlushInterval = TDuration::Seconds(10);
        config->BatchSize = 5000;
        config->EnableCompression = true;
        return config;
    }

    static TDynamicTableLogConfigPtr CreateForLowLatency() {
        auto config = New<TDynamicTableLogConfig>();
        config->FlushInterval = TDuration::MilliSeconds(100);
        config->BatchSize = 100;
        config->EnableCompression = false;
        return config;
    }

    static TDynamicTableLogConfigPtr CreateForReliability() {
        auto config = New<TDynamicTableLogConfig>();
        config->FlushInterval = TDuration::Seconds(1);
        config->BatchSize = 50;
        config->MaxRetries = 10;
        config->EnableCompression = true;
        return config;
    }
};
```

### 2. 监控指标

```cpp
// 日志写入监控
struct LogWriterMetrics {
    std::atomic<i64> EntriesWritten{0};
    std::atomic<i64> BatchesFlushed{0};
    std::atomic<i64> WriteErrors{0};
    std::atomic<i64> RetriesAttempted{0};
    TDuration AverageWriteTime;
    double CompressionRatio;
    TDuration MaxFlushTime;
};
```

## 依赖项

### 内部依赖
- `yt/yt/core/misc/public.h` - 核心公共定义
- `yt/yt/client/api/public.h` - API 客户端接口

### 外部依赖
- 压缩库
- 线程库
- 时间管理库

## 相关模块

- **API Client**: 表数据操作
- **Formats Client**: 数据格式处理
- **Table Client**: 表结构管理

## 参考文档

- [YTsaurus 日志系统设计](../../../docs/logging-system.md)
- [动态表使用指南](../../../docs/dynamic-tables.md)
- [性能优化最佳实践](../../../docs/performance-optimization.md)

## 贡献指南

在修改此模块时：
1. 确保高性能写入能力
2. 添加充分的并发测试
3. 考虑错误恢复机制
4. 优化内存使用效率
5. 保持配置向后兼容