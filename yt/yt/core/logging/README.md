# Logging 模块

## 模块概述

`yt/yt/core/logging` 模块是 YTsaurus 分布式系统的日志记录核心库，提供了完整的高性能日志记录、格式化、输出和管理功能。该模块支持多级别日志、结构化日志、异步写入和日志轮转等功能，为 YTsaurus 系统的运行监控、问题诊断和性能分析提供强大的日志基础设施。

## 主要功能

### 1. 日志记录
- **多级别日志**: 支持 TRACE、DEBUG、INFO、WARNING、ERROR 等多个日志级别
- **结构化日志**: 支持键值对的结构化日志格式
- **异步日志**: 非阻塞的异步日志写入
- **批量输出**: 批量日志输出提高性能

### 2. 日志格式化
- **自定义格式**: 支持自定义日志格式模板
- **时间戳**: 高精度的时间戳记录
- **线程信息**: 线程 ID 和协程 ID 记录
- **堆栈跟踪**: 可选的调用堆栈信息

### 3. 日志管理
- **日志轮转**: 基于大小和时间的日志轮转
- **压缩归档**: 历史日志的压缩和归档
- **远程日志**: 支持远程日志收集
- **日志过滤**: 基于模式的日志过滤

### 4. 性能优化
- **内存池**: 日志缓冲区的内存池管理
- **零拷贝**: 避免不必要的字符串拷贝
- **批量写入**: 批量写入减少 I/O 开销
- **异步处理**: 后台线程处理日志写入

## 文件说明

### 核心文件
- **log.h**: 核心日志接口和宏定义
- **log_manager.h**: 日志管理器实现
- **log_writer.h**: 日志写入器接口
- **formatter.h**: 日志格式化器

### 实现文件
- **file_log_writer.h**: 文件日志写入器
- **console_log_writer.h**: 控制台日志写入器
- **structed_log.h**: 结构化日志支持
- **log_system.h**: 日志系统初始化

## 使用示例

### 基本日志记录
```cpp
#include <yt/yt/core/logging/log.h>

using namespace NYT::NLogging;

// 获取日志器
const auto& Logger = DataLogger;

// 记录不同级别的日志
TRACE(Logger, "Detailed trace information");
DEBUG(Logger, "Debug information");
INFO(Logger, "Normal information: %s", message);
WARNING(Logger, "Warning: %s", warningMessage);
ERROR(Logger, "Error occurred: %v", error);

// 结构化日志
StructuredInfo(Logger, "Request processed")
    .Item("request_id").Value(requestId)
    .Item("duration_ms").Value(duration.MilliSeconds())
    .Item("status").Value("success");
```

### 自定义日志配置
```cpp
#include <yt/yt/core/logging/config.h>

// 创建日志配置
auto config = New<TLogManagerConfig>();
config->MinLevel = ELogLevel::Info;
config->Rules.push_back(New<TRuleConfig>());

// 添加文件写入器
auto fileWriter = New<TFileLogWriterConfig>();
fileWriter->FileName = "ytserver.log";
fileWriter->RotationPolicy = New<TRotationPolicyConfig>();
fileWriter->RotationPolicy->SizeLimit = 100_MB;

config->Writers.push_back(fileWriter);

// 应用配置
LogManager->Configure(config);
```

### 自定义日志写入器
```cpp
#include <yt/yt/core/logging/log_writer.h>

class CustomLogWriter : public ILogWriter {
public:
    void Write(const std::vector<TLogEvent>& events) override {
        for (const auto& event : events) {
            // 自定义日志处理逻辑
            ProcessLogEvent(event);
        }
    }

    void Flush() override {
        // 刷新缓冲区
    }
};
```

## 配置选项

### 日志级别
- **TRACE**: 最详细的跟踪信息
- **DEBUG**: 调试信息
- **INFO**: 一般信息
- **WARNING**: 警告信息
- **ERROR**: 错误信息
- **FATAL**: 致命错误

### 轮转策略
- **基于大小**: 文件达到指定大小时轮转
- **基于时间**: 按时间间隔轮转
- **混合策略**: 同时考虑大小和时间

### 格式化选项
- **时间格式**: 时间戳的显示格式
- **消息格式**: 日志消息的格式模板
- **字段选择**: 显示哪些字段信息

## 性能特性

- **高吞吐**: 支持每秒数百万条日志记录
- **低延迟**: 异步写入减少延迟影响
- **内存高效**: 优化内存使用和分配
- **CPU 高效**: 最小化 CPU 开销

## 依赖关系

- **yt/yt/core/misc**: 基础工具和格式化
- **yt/yt/core/actions**: 异步操作支持
- **yt/yt/core/concurrency**: 线程和协程支持

## 最佳实践

1. **合理级别**: 选择合适的日志级别避免过度日志
2. **结构化**: 使用结构化日志便于分析和查询
3. **上下文**: 在日志中包含足够的上下文信息
4. **性能**: 在性能关键路径谨慎使用高频率日志
5. **监控**: 监控日志系统的性能和存储使用

## 监控和调试

### 性能指标
- **日志吞吐**: 每秒记录的日志数量
- **写入延迟**: 日志写入的延迟时间
- **缓冲区使用**: 日志缓冲区使用情况
- **磁盘使用**: 日志文件磁盘使用量

### 调试工具
- **日志分析**: 日志文件分析工具
- **实时查看**: 实时日志查看命令
- **错误统计**: 日志错误统计和告警
- **性能分析**: 日志系统性能分析