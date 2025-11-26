# YTsaurus File Client 模块

## 概述

File Client 模块是 YTsaurus 分布式文件系统的客户端实现，提供了高效的文件读写操作支持。该模块专门针对大文件的分布式存储进行了优化，支持分块写入、签名验证和并发操作等高级功能。

## 核心功能

### 1. 分布式文件写入
- **分块写入**: 大文件自动分块存储
- **并发写入**: 多线程并行写入提高性能
- **断点续传**: 支持写入中断后的恢复
- **压缩存储**: 自动压缩减少存储空间

### 2. 签名验证
- **完整性保证**: 使用数字签名确保文件完整性
- **防篡改**: 检测文件在传输或存储过程中的篡改
- **安全认证**: 验证文件来源和真实性

### 3. 高性能配置
- **可调块大小**: 根据文件大小和网络条件优化
- **内存管理**: 高效的内存使用和缓冲策略
- **错误恢复**: 智能的错误处理和重试机制

## 主要组件

### 1. 文件分块写入配置 (TFileChunkWriterConfig)

```cpp
struct TFileChunkWriterConfig : public virtual NChunkClient::TEncodingWriterConfig {
    i64 BlockSize;  // 写入块大小

    REGISTER_YSON_STRUCT(TFileChunkWriterConfig);
};
```

#### 配置参数详解

**BlockSize (块大小)**
- **类型**: `i64`
- **默认值**: 16_MB (16,777,216 字节)
- **范围**: 必须大于 0
- **用途**: 控制文件写入时的块大小，影响性能和内存使用

#### 块大小选择策略

| 文件大小 | 推荐块大小 | 说明 |
|---------|-----------|------|
| < 10MB | 1MB - 4MB | 小文件使用较小块 |
| 10MB - 1GB | 16MB (默认) | 中等文件使用默认值 |
| > 1GB | 32MB - 64MB | 大文件使用较大块 |
| > 10GB | 64MB - 128MB | 超大文件最大化块大小 |

### 2. 签名类型定义

```cpp
// 分布式写入文件会话签名
YT_DEFINE_STRONG_TYPEDEF(TSignedDistributedWriteFileSessionPtr, NSignature::TSignaturePtr);

// 写入文件分片 Cookie 签名
YT_DEFINE_STRONG_TYPEDEF(TSignedWriteFileFragmentCookiePtr, NSignature::TSignaturePtr);

// 写入文件分片结果签名
YT_DEFINE_STRONG_TYPEDEF(TSignedWriteFileFragmentResultPtr, NSignature::TSignaturePtr);
```

#### 签名类型说明

1. **TSignedDistributedWriteFileSessionPtr**
   - **用途**: 标识分布式写入会话
   - **包含**: 会话ID、时间戳、用户信息
   - **安全性**: 防止会话劫持和伪造

2. **TSignedWriteFileFragmentCookiePtr**
   - **用途**: 验证文件分片写入权限
   - **包含**: 分片位置、大小、校验和
   - **作用**: 确保分片写入的合法性

3. **TSignedWriteFileFragmentResultPtr**
   - **用途**: 确认分片写入结果
   - **包含**: 写入状态、实际大小、存储位置
   - **重要性**: 提供写入结果的不可否认性

## 使用方法

### 1. 基本文件写入

```cpp
#include <yt/yt/client/file_client/public.h>
#include <yt/yt/client/file_client/config.h>

using namespace NYT::NFileClient;

// 创建写入配置
auto writerConfig = New<TFileChunkWriterConfig>();
writerConfig->BlockSize = 32_MB;  // 自定义块大小

// 创建文件写入器
auto writer = CreateFileWriter(filePath, writerConfig);

// 写入数据
std::vector<char> data = LoadFileData();
writer->Write(data.data(), data.size());

// 完成写入
writer->Finish();
```

### 2. 分布式写入

```cpp
// 创建分布式写入会话
auto sessionSignature = CreateDistributedWriteSession(
    "/path/to/large/file",
    fileSize,
    userIdentity);

// 获取分片写入 Cookie
std::vector<TSignedWriteFileFragmentCookiePtr> cookies;
for (size_t i = 0; i < fragmentCount; ++i) {
    auto cookie = GetWriteFragmentCookie(sessionSignature, i, fragmentSize);
    cookies.push_back(cookie);
}

// 并行写入分片
std::vector<TFuture<TSignedWriteFileFragmentResultPtr>> writeResults;
for (const auto& cookie : cookies) {
    auto result = WriteFragmentAsync(cookie, fragmentData);
    writeResults.push_back(result);
}

// 等待所有分片完成
auto allResults = WaitFor(AllSet(writeResults))
    .ValueOrThrow();

// 验证和合并结果
ValidateAndCombineResults(sessionSignature, allResults);
```

### 3. 配置优化

```cpp
// 根据文件大小优化配置
TFileChunkWriterConfigPtr CreateOptimizedConfig(i64 fileSize) {
    auto config = New<TFileChunkWriterConfig>();

    if (fileSize < 10_MB) {
        config->BlockSize = 1_MB;
    } else if (fileSize < 100_MB) {
        config->BlockSize = 4_MB;
    } else if (fileSize < 1_GB) {
        config->BlockSize = 16_MB;  // 默认值
    } else if (fileSize < 10_GB) {
        config->BlockSize = 32_MB;
    } else {
        config->BlockSize = 64_MB;
    }

    return config;
}
```

### 4. 错误处理和重试

```cpp
// 带重试的文件写入
template<typename TWriteFunc>
T WriteWithRetry(TWriteFunc writeFunc, int maxRetries = 3) {
    for (int attempt = 0; attempt <= maxRetries; ++attempt) {
        try {
            return writeFunc();
        } catch (const TFileChunkWriterException& e) {
            if (attempt == maxRetries) {
                throw;
            }

            // 检查是否可重试
            if (!e.IsRetriable()) {
                throw;
            }

            // 指数退避
            auto delay = TDuration::MilliSeconds(100 * (1 << attempt));
            TDelay::Wait(delay);

            YT_LOG_WARNING("File write retry (Attempt: %v, Error: %v)",
                attempt + 1, e);
        }
    }
}
```

## 性能优化

### 1. 内存管理

```cpp
// 内存池管理
class FileWriteMemoryPool {
private:
    std::vector<std::unique_ptr<char[]>> buffers_;
    std::queue<char*> availableBuffers_;
    size_t bufferSize_;

public:
    char* AcquireBuffer() {
        if (availableBuffers_.empty()) {
            buffers_.emplace_back(std::make_unique<char[]>(bufferSize_));
            return buffers_.back().get();
        }
        auto* buffer = availableBuffers_.front();
        availableBuffers_.pop();
        return buffer;
    }

    void ReleaseBuffer(char* buffer) {
        availableBuffers_.push(buffer);
    }
};
```

### 2. 并发写入

```cpp
// 并行分片写入
class ParallelFileWriter {
private:
    TFileChunkWriterConfigPtr config_;
    int concurrency_;

public:
    std::vector<TFuture<void>> WriteParallel(
        const std::vector<TDataFragment>& fragments) {

        std::vector<TFuture<void>> futures;

        // 使用线程池限制并发度
        for (const auto& fragment : fragments) {
            auto future = BIND([this, fragment] {
                WriteSingleFragment(fragment);
            }).AsyncVia(GetThreadPoolInvoker())->Run();

            futures.push_back(future);
        }

        return futures;
    }
};
```

### 3. 压缩优化

```cpp
// 自适应压缩策略
class AdaptiveCompression {
private:
    struct CompressionStats {
        double CompressionRatio;
        TDuration CompressionTime;
        TDuration WriteTime;
    };

public:
    bool ShouldCompress(i64 dataSize, const std::string& mimeType) {
        // 小文件不压缩
        if (dataSize < 1_MB) {
            return false;
        }

        // 已压缩格式不压缩
        if (IsAlreadyCompressed(mimeType)) {
            return false;
        }

        // 根据历史压缩率决定
        auto stats = GetCompressionStats(mimeType);
        return stats.CompressionRatio > 1.5;
    }
};
```

## 安全性考虑

### 1. 签名验证

```cpp
// 签名验证流程
class SignatureValidator {
public:
    bool ValidateWriteSession(
        const TSignedDistributedWriteFileSessionPtr& signature) {

        // 验证签名有效性
        if (!NSignature::VerifySignature(signature)) {
            return false;
        }

        // 验证会话未过期
        if (signature->GetExpirationTime() < TInstant::Now()) {
            return false;
        }

        // 验证用户权限
        return HasWritePermission(signature->GetUserId(), signature->GetPath());
    }

    bool ValidateFragmentCookie(
        const TSignedWriteFileFragmentCookiePtr& cookie,
        const TSignedDistributedWriteFileSessionPtr& session) {

        // 验证 Cookie 与 Session 的关联性
        if (cookie->GetSessionId() != session->GetSessionId()) {
            return false;
        }

        // 验证分片位置合法性
        if (cookie->GetOffset() + cookie->GetSize() > session->GetFileSize()) {
            return false;
        }

        return true;
    }
};
```

### 2. 数据完整性

```cpp
// 校验和计算和验证
class DataIntegrityChecker {
private:
    static constexpr size_t CHECKSUM_SIZE = 32;

public:
    std::array<char, CHECKSUM_SIZE> CalculateChecksum(
        const void* data, size_t size) {

        // 使用 SHA-256 计算校验和
        std::array<char, CHECKSUM_SIZE> checksum;
        SHA256(data, size, checksum.data());
        return checksum;
    }

    bool VerifyIntegrity(
        const void* data, size_t size,
        const std::array<char, CHECKSUM_SIZE>& expectedChecksum) {

        auto actualChecksum = CalculateChecksum(data, size);
        return actualChecksum == expectedChecksum;
    }
};
```

## 监控和诊断

### 1. 性能指标

```cpp
struct FileWriteMetrics {
    // 写入性能
    i64 TotalBytesWritten;
    TDuration TotalWriteTime;
    double ThroughputMBps;

    // 分片信息
    int TotalFragments;
    int SuccessfulFragments;
    int FailedFragments;

    // 错误统计
    std::unordered_map<TString, int> ErrorCounts;
    std::unordered_map<TString, TDuration> ErrorRecoveryTimes;

    // 资源使用
    i64 PeakMemoryUsage;
    i64 AverageMemoryUsage;
    int MaxConcurrentWrites;
};
```

### 2. 诊断工具

```cpp
// 文件写入状态监控
class FileWriteDiagnostics {
public:
    void LogWriteProgress(
        const TString& filePath,
        i64 bytesWritten,
        i64 totalBytes) {

        double progress = static_cast<double>(bytesWritten) / totalBytes;
        YT_LOG_INFO("File write progress (Path: %v, Progress: %.2f%%, Written: %v, Total: %v)",
            filePath, progress * 100, bytesWritten, totalBytes);
    }

    void LogFragmentStatus(
        const TSignedWriteFileFragmentCookiePtr& cookie,
        const TErrorOr<TSignedWriteFileFragmentResultPtr>& result) {

        if (result.IsOK()) {
            YT_LOG_DEBUG("Fragment write succeeded (Offset: %v, Size: %v)",
                cookie->GetOffset(), cookie->GetSize());
        } else {
            YT_LOG_ERROR("Fragment write failed (Offset: %v, Size: %v, Error: %v)",
                cookie->GetOffset(), cookie->GetSize(), result);
        }
    }
};
```

## 最佳实践

### 1. 配置优化

```cpp
// 文件类型特定配置
TFileChunkWriterConfigPtr GetOptimalConfig(const TString& filePath) {
    auto config = New<TFileChunkWriterConfig>();

    auto extension = GetFileExtension(filePath);

    if (extension == "log" || extension == "txt") {
        // 文本文件：较小块，便于随机访问
        config->BlockSize = 4_MB;
    } else if (extension == "mp4" || extension == "avi") {
        // 视频文件：中等块，平衡性能和内存
        config->BlockSize = 16_MB;
    } else if (extension == "zip" || extension == "gz") {
        // 压缩文件：较大块，避免额外压缩开销
        config->BlockSize = 64_MB;
    } else {
        // 默认配置
        config->BlockSize = 16_MB;
    }

    return config;
}
```

### 2. 错误处理策略

```cpp
// 分层错误处理
enum class EFileWriteError {
    TemporaryNetworkIssue,    // 临时网络问题
    StorageQuotaExceeded,    // 存储配额超限
    InsufficientPermissions, // 权限不足
    DataCorruption,         // 数据损坏
    SessionExpired,         // 会话过期
};

class FileWriteErrorHandler {
public:
    TError HandleError(EFileWriteError error, const TError& originalError) {
        switch (error) {
            case EFileWriteError::TemporaryNetworkIssue:
                return TError("Temporary network issue, will retry")
                    << originalError;

            case EFileWriteError::StorageQuotaExceeded:
                return TError("Storage quota exceeded, cleanup required")
                    << originalError;

            case EFileWriteError::InsufficientPermissions:
                return TError("Insufficient write permissions")
                    << originalError;

            case EFileWriteError::DataCorruption:
                return TError("Data corruption detected, restart write")
                    << originalError;

            case EFileWriteError::SessionExpired:
                return TError("Write session expired, create new session")
                    << originalError;
        }
    }
};
```

## 依赖项

### 内部依赖
- `yt/yt/client/signature/public.h` - 数字签名支持
- `yt/yt/client/chunk_client/config.h` - 分块客户端配置
- `yt/yt/core/misc/public.h` - 核心公共定义

### 外部依赖
- 加密库 (OpenSSL)
- 压缩库 (zlib, lz4)
- 哈希库 (SHA-256)
- 网络通信库

## 扩展性

### 1. 自定义编码器

```cpp
class ICustomFileEncoder {
public:
    virtual TEncodedData Encode(const TDataFragment& input) = 0;
    virtual TDataFragment Decode(const TEncodedData& input) = 0;
    virtual TString GetCodecName() const = 0;
};
```

### 2. 存储后端扩展

```cpp
class IFileStorageBackend {
public:
    virtual TFuture<void> WriteChunk(
        const TChunkId& chunkId,
        const TDataFragment& data) = 0;

    virtual TFuture<TDataFragment> ReadChunk(
        const TChunkId& chunkId) = 0;

    virtual TFuture<void> DeleteChunk(
        const TChunkId& chunkId) = 0;
};
```

## 版本兼容性

- **配置兼容性**: 新增配置项有合理默认值
- **签名兼容性**: 支持多版本签名算法
- **API 兼容性**: 保持向后兼容的接口

## 相关模块

- **Chunk Client**: 底层分块存储实现
- **Signature Client**: 数字签名和验证
- **Object Client**: 对象存储接口
- **Table Client**: 结构化数据存储

## 参考文档

- [YTsaurus 文件系统设计](../../../docs/file-system.md)
- [分布式文件存储架构](../../../docs/distributed-storage.md)
- [文件客户端配置参考](../../../docs/file-client-config.md)
- [安全性和签名验证](../../../docs/security.md)

## 贡献指南

在修改此模块时：
1. 保持配置参数的向后兼容性
2. 添加充分的性能测试
3. 考虑内存使用效率
4. 确保安全性不被破坏
5. 更新相关文档