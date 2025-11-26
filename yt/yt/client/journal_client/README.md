# YTsaurus Journal Client 模块

## 概述

Journal Client 模块是 YTsaurus 日志系统的客户端接口，提供高效的日志读取功能。该模块专门针对结构化日志数据的读取进行了优化，支持复制延迟控制和流式数据处理。

## 核心功能

### 1. 日志读取
- **分块读取器**: 高效的日志分块读取
- **流式处理**: 支持大容量日志的流式读取
- **压缩支持**: 自动处理压缩的日志数据
- **并行读取**: 多线程并行读取提高性能

### 2. 复制延迟控制
- **延迟限制**: 控制允许的最大复制延迟
- **一致性保证**: 确保读取的数据一致性
- **同步策略**: 可配置的数据同步策略

### 3. 配置管理
- **读取器配置**: 灵活的读取器参数配置
- **性能调优**: 针对不同场景的优化配置

## 主要组件

### 1. 分块读取器配置 (TChunkReaderConfig)

```cpp
DECLARE_REFCOUNTED_STRUCT(TChunkReaderConfig)
```

提供了日志分块读取的详细配置选项：
- **缓冲区大小**: 读取缓冲区的大小配置
- **并发度**: 并行读取的线程数
- **预取策略**: 数据预取和缓存策略
- **压缩处理**: 压缩数据的处理方式

### 2. 复制延迟控制

```cpp
constexpr i64 DefaultReplicaLagLimit = 32768;
```

定义了默认的复制延迟限制：
- **默认值**: 32768 (条目数)
- **用途**: 控制读取器允许的最大复制延迟
- **配置**: 可通过配置文件调整

## 使用方法

### 1. 基本日志读取

```cpp
#include <yt/yt/client/journal_client/public.h>

using namespace NYT::NJournalClient;

// 创建日志读取器配置
auto readerConfig = New<TChunkReaderConfig>();
readerConfig->BufferSize = 1_MB;
readerConfig->Concurrency = 4;

// 创建日志读取器
auto reader = CreateJournalReader(journalPath, readerConfig);

// 读取日志数据
while (reader->HasMoreData()) {
    auto chunk = reader->ReadNextChunk();
    ProcessLogChunk(chunk);
}
```

### 2. 复制延迟控制

```cpp
// 配置复制延迟限制
auto readerConfig = New<TChunkReaderConfig>();
readerConfig->ReplicaLagLimit = 16384;  // 更严格的延迟限制

// 创建延迟感知的读取器
auto reader = CreateLagAwareJournalReader(journalPath, readerConfig);

// 监控复制延迟
reader->OnReplicaLagExceeded.Subscribe([] (i64 currentLag) {
    YT_LOG_WARNING("Journal replica lag exceeded (CurrentLag: %v)", currentLag);
});
```

### 3. 流式日志处理

```cpp
// 流式处理大量日志
class StreamingLogProcessor {
public:
    void ProcessJournal(const TString& journalPath) {
        auto readerConfig = CreateOptimizedReaderConfig();
        auto reader = CreateJournalReader(journalPath, readerConfig);

        // 异步流式处理
        ProcessAsync(reader)
            .Subscribe([] (const TError& error) {
                if (!error.IsOK()) {
                    YT_LOG_ERROR("Log processing failed: %v", error);
                }
            });
    }

private:
    TFuture<void> ProcessAsync(IJournalReaderPtr reader) {
        return AsyncYield()
            .Apply(BIND([this, reader] {
                return ProcessBatch(reader);
            }))
            .Apply(BIND([this, reader] (bool hasMore) {
                return hasMore ? ProcessAsync(reader) : VoidFuture;
            }));
    }

    TFuture<bool> ProcessBatch(IJournalReaderPtr reader) {
        std::vector<TLogEntry> batch;
        while (reader->HasMoreData() && batch.size() < BatchSize) {
            batch.push_back(reader->ReadNextEntry());
        }

        return ProcessBatchAsync(batch)
            .Apply(BIND([batch] (const TError&) {
                return !batch.empty();
            }));
    }
};
```

### 4. 性能优化配置

```cpp
// 高性能读取配置
TChunkReaderConfigPtr CreateHighPerformanceReaderConfig() {
    auto config = New<TChunkReaderConfig>();

    // 大缓冲区提高吞吐量
    config->BufferSize = 8_MB;

    // 高并发读取
    config->Concurrency = std::thread::hardware_concurrency();

    // 激进预取
    config->PrefetchStrategy = EPrefetchStrategy::Aggressive;

    // 内存映射读取
    config->UseMemoryMapping = true;

    // 压缩处理优化
    config->CompressionHandling = ECompressionHandling::ParallelDecompression;

    return config;
}
```

## 性能优化

### 1. 内存管理

```cpp
// 内存优化的日志读取器
class MemoryOptimizedJournalReader {
private:
    TLRUCache<TChunkId, TDecompressedChunk> chunkCache_;
    std::unique_ptr<char[]> readBuffer_;
    size_t bufferSize_;

public:
    TDecompressedChunk ReadChunkOptimized(const TChunkId& chunkId) {
        // 1. 检查缓存
        auto cachedChunk = chunkCache_.Find(chunkId);
        if (cachedChunk) {
            return *cachedChunk;
        }

        // 2. 读取原始数据
        auto rawData = ReadRawChunk(chunkId);

        // 3. 解压缩到缓冲区
        auto decompressedData = DecompressToBuffer(rawData);

        // 4. 缓存结果
        chunkCache_.Insert(chunkId, decompressedData);

        return decompressedData;
    }
};
```

### 2. 并行处理

```cpp
// 并行日志读取器
class ParallelJournalReader {
private:
    TThreadPoolPtr threadPool_;
    std::vector<IJournalReaderPtr> readers_;

public:
    TFuture<std::vector<TLogEntry>> ReadParallel(
        const std::vector<TString>& journalPaths) {

        std::vector<TFuture<std::vector<TLogEntry>>> futures;

        for (const auto& path : journalPaths) {
            auto future = BIND([this, path] {
                return ReadSingleJournal(path);
            }).AsyncVia(threadPool_->GetInvoker()).Run();

            futures.push_back(future);
        }

        return AllSucceeded(std::move(futures))
            .Apply(BIND([] (const std::vector<std::vector<TLogEntry>>& results) {
                std::vector<TLogEntry> merged;
                for (const auto& batch : results) {
                    merged.insert(merged.end(), batch.begin(), batch.end());
                }
                return merged;
            }));
    }
};
```

### 3. 压缩优化

```cpp
// 智能压缩处理
class CompressionAwareReader {
public:
    TDecompressedData ReadWithCompression(const TChunkId& chunkId) {
        auto chunkMetadata = GetChunkMetadata(chunkId);

        switch (chunkMetadata->CompressionCodec()) {
            case ECompressionCodec::None:
                return ReadUncompressed(chunkId);

            case ECompressionCodec::Lz4:
                return ReadWithLz4Decompression(chunkId);

            case ECompressionCodec::Zstd:
                return ReadWithZstdDecompression(chunkId);

            default:
                // 使用通用解压缩
                return ReadWithGenericDecompression(chunkId);
        }
    }

private:
    TDecompressedData ReadWithLz4Decompression(const TChunkId& chunkId) {
        // LZ4 优化的解压缩路径
        auto compressedData = ReadCompressedData(chunkId);
        auto decompressedSize = LZ4GetDecompressedSize(compressedData);

        std::vector<char> decompressedData(decompressedSize);
        auto resultSize = LZ4_decompress_safe(
            compressedData.Data(),
            decompressedData.data(),
            compressedData.Size(),
            decompressedSize);

        YCHECK(resultSize == decompressedSize);
        return TDecompressedData(std::move(decompressedData));
    }
};
```

## 监控和诊断

### 1. 关键指标

```cpp
struct JournalReaderMetrics {
    // 性能指标
    std::atomic<i64> ChunksRead{0};
    std::atomic<i64> BytesRead{0};
    std::atomic<i64> EntriesRead{0};
    TDuration AverageReadTime;
    double ThroughputMBps;

    // 缓存指标
    std::atomic<i64> CacheHits{0};
    std::atomic<i64> CacheMisses{0};
    double CacheHitRate;

    // 压缩指标
    std::atomic<i64> CompressedChunksRead{0};
    double CompressionRatio;
    TDuration AverageDecompressionTime;

    // 复制延迟指标
    std::atomic<i64> ReplicaLagExceeded{0};
    TDuration MaxReplicaLag;
};
```

### 2. 健康检查

```cpp
// 日志读取器健康检查
class JournalReaderHealthChecker {
public:
    bool IsHealthy(const IJournalReaderPtr& reader) {
        return CheckReadPerformance(reader) &&
               CheckMemoryUsage(reader) &&
               CheckReplicaLag(reader);
    }

private:
    bool CheckReadPerformance(const IJournalReaderPtr& reader) {
        auto now = TInstant::Now();
        if (now - lastSuccessfulRead_ > MaxReadStallTime) {
            return false;
        }

        auto metrics = reader->GetMetrics();
        return metrics.ThroughputMBps > MinThroughputThreshold;
    }

    bool CheckReplicaLag(const IJournalReaderPtr& reader) {
        auto currentLag = reader->GetCurrentReplicaLag();
        return currentLag <= DefaultReplicaLagLimit;
    }
};
```

## 最佳实践

### 1. 配置优化

```cpp
// 场景特定的配置
class JournalReaderConfigFactory {
public:
    static TChunkReaderConfigPtr CreateForRealTimeProcessing() {
        auto config = New<TChunkReaderConfig>();
        config->BufferSize = 256_KB;
        config->Concurrency = 2;
        config->ReplicaLagLimit = 1024;  // 更严格的延迟要求
        config->PrefetchStrategy = EPrefetchStrategy::Conservative;
        return config;
    }

    static TChunkReaderConfigPtr CreateForBatchProcessing() {
        auto config = New<TChunkReaderConfig>();
        config->BufferSize = 8_MB;
        config->Concurrency = std::thread::hardware_concurrency();
        config->ReplicaLagLimit = 65536;  // 宽松的延迟要求
        config->PrefetchStrategy = EPrefetchStrategy::Aggressive;
        return config;
    }

    static TChunkReaderConfigPtr CreateForDebugging() {
        auto config = New<TChunkReaderConfig>();
        config->BufferSize = 64_KB;
        config->Concurrency = 1;  // 单线程便于调试
        config->EnableDetailedLogging = true;
        config->ValidateChecksums = true;
        return config;
    }
};
```

### 2. 错误处理

```cpp
// 健壮的错误处理
class ResilientJournalReader {
private:
    IJournalReaderPtr reader_;
    int maxRetries_;

public:
    TFuture<TLogChunk> ReadWithRetry() {
        return ReadWithRetryInternal(0);
    }

private:
    TFuture<TLogChunk> ReadWithRetryInternal(int attempt) {
        return reader_->ReadNextChunk()
            .Apply(BIND([this, attempt] (const TErrorOr<TLogChunk>& result) {
                if (result.IsOK()) {
                    return MakeFuture(result.Value());
                }

                if (attempt < maxRetries_ && IsRetriableError(result.GetError())) {
                    auto delay = TDuration::MilliSeconds(100 * (1 << attempt));
                    return TDelayedExecutor::MakeDelayed(delay)
                        .Apply(BIND([this, attempt] {
                            return ReadWithRetryInternal(attempt + 1);
                        }));
                }

                return MakeFuture<TLogChunk>(result.GetError());
            }));
    }

    bool IsRetriableError(const TError& error) {
        return error.FindMatching(NYT::NRpc::EErrorCode::Timeout) ||
               error.FindMatching(NYT::NRpc::EErrorCode::TransportError);
    }
};
```

## 依赖项

### 内部依赖
- `yt/yt/core/misc/public.h` - 核心公共定义

### 外部依赖
- 压缩库 (LZ4, Zstd)
- 线程库
- 文件系统接口

## 扩展性

### 1. 自定义读取器

```cpp
// 自定义日志读取器接口
class ICustomJournalReader {
public:
    virtual TFuture<TLogChunk> ReadNextChunk() = 0;
    virtual bool HasMoreData() const = 0;
    virtual TJournalReaderMetrics GetMetrics() const = 0;
};
```

### 2. 插件架构

```cpp
// 压缩处理插件
class ICompressionHandlerPlugin {
public:
    virtual std::string GetCodecName() const = 0;
    virtual TDecompressedData Decompress(const TCompressedData& data) = 0;
    virtual bool CanHandle(const TChunkMetadata& metadata) const = 0;
};
```

## 版本兼容性

- **格式兼容性**: 支持多版本日志格式
- **API 兼容性**: 保持向后兼容的接口
- **配置兼容性**: 新配置项有默认值

## 相关模块

- **Table Client**: 表数据读取
- **Chunk Client**: 分片数据操作
- **Object Client**: 对象存储接口

## 参考文档

- [YTsaurus 日志系统设计](../../../docs/journal-system.md)
- [性能优化指南](../../../docs/journal-performance.md)
- [复制延迟控制](../../../docs/replication-lag.md)
- [压缩算法比较](../../../docs/comparison-compression.md)

## 贡献指南

在修改此模块时：
1. 确保读取性能不降低
2. 添加充分的性能测试
3. 考虑内存使用效率
4. 保持压缩兼容性
5. 更新相关文档