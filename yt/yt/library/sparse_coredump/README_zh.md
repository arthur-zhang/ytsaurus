# Sparse Core Dump Library (稀疏核心转储库)

## 项目概述 (Overview)

Sparse Core Dump Library 是 YTsaurus 中用于处理大型应用程序核心转储文件的高效工具。该库实现了稀疏核心转储技术，通过识别和压缩核心转储中的零页（未使用的内存页面），大幅减少核心转储文件的大小，从而节省存储空间并提高转储和传输效率。

该库特别适用于内存密集型的大规模分布式系统，能够处理多 GB 甚至 TB 级别的核心转储文件，同时保持完整的问题诊断能力。

## 核心功能 (Core Features)

### 稀疏化处理
- **零页检测**: 自动识别核心转储中的零填充页面
- **块压缩**: 将连续的零页压缩为简单的元数据描述
- **页面级处理**: 以页面为单位（64KB）进行稀疏化处理
- **完整性保持**: 保持原始核心转储的诊断信息完整性

### 异步流式处理
- **异步 I/O**: 基于协程的异步读写操作
- **流式处理**: 支持大文件的流式处理，避免内存溢出
- **超时控制**: 可配置的读写超时机制
- **背压处理**: 自适应的流控制和背压管理

### 多种输出格式
- **文件输出**: 直接写入到文件的稀疏转储
- **流输出**: 输出到异步输出流
- **内存输出**: 内存中的稀疏转储表示
- **网络传输**: 支持网络流式传输

### 高效存储格式
- **压缩头部**: 使用特殊头部标记零页和常规页
- **元数据优化**: 最小化元数据存储开销
- **快速索引**: 支持快速定位特定页面

## 主要接口 (Main Interfaces)

### 基础稀疏化接口

```cpp
#include <yt/yt/library/sparse_coredump/sparse_coredump.h>

// 使用文件接口进行稀疏化
void SparseCoreDumpFile()
{
    // 打开输入核心转储文件
    TFile inputFile("core.dump", OpenExisting | RdOnly);

    // 创建输出文件
    TFile outputFile("core.sparse.dump", CreateAlways | WrOnly);

    // 执行稀疏化
    i64 originalSize = WriteSparseCoreDump(&inputFile, &outputFile);

    std::cout << "原始大小: " << originalSize << " 字节" << std::endl;
    std::cout << "稀疏大小: " << outputFile.GetLength() << " 字节" << std::endl;
    std::cout << "压缩比: " << (double)outputFile.GetLength() / originalSize << std::endl;
}
```

### 异步流式处理

```cpp
#include <yt/yt/core/concurrency/async_stream.h>

class TMySparseConsumer
    : public ISparseCoreDumpConsumer
{
public:
    explicit TMySparseConsumer(const TString& outputPath)
        : OutputFile_(outputPath, CreateAlways | WrOnly)
    { }

    void OnRegularBlock(TSharedRef block) override
    {
        // 处理常规数据块
        OutputFile_.Write(block.Begin(), block.Size());
        RegularBytesProcessed_ += block.Size();
    }

    void OnZeroBlock(i64 length) override
    {
        // 处理零块 - 可以记录或跳过
        ZeroBytesProcessed_ += length;

        // 写入零块头部
        OutputFile_.Write(ZeroBlockHeader.Begin(), ZeroBlockHeader.Size());

        // 写入长度信息
        i64 lengthValue = length;
        OutputFile_.Write(&lengthValue, sizeof(lengthValue));
    }

    void PrintStatistics()
    {
        std::cout << "处理完成:" << std::endl;
        std::cout << "  常规字节: " << RegularBytesProcessed_ << std::endl;
        std::cout << "  零字节: " << ZeroBytesProcessed_ << std::endl;
        std::cout << "  压缩率: " <<
            (double)RegularBytesProcessed_ / (RegularBytesProcessed_ + ZeroBytesProcessed_)
            << std::endl;
    }

private:
    TFile OutputFile_;
    i64 RegularBytesProcessed_ = 0;
    i64 ZeroBytesProcessed_ = 0;
};

void AsyncSparseCoreDump()
{
    // 创建消费者
    auto consumer = NYT::New<TMySparseConsumer>("async_core.sparse.dump");

    // 创建异步输入流
    auto inputStream = CreateAsyncInputStream("core.dump");

    // 执行异步稀疏化
    auto future = SparsifyCoreDump(
        inputStream,
        consumer,
        TDuration::Seconds(30)  // 读取超时
    );

    // 等待完成
    auto processedSize = future.Get();
    std::cout << "处理了 " << processedSize << " 字节" << std::endl;

    consumer->PrintStatistics();
}
```

### 流式写入器

```cpp
// 使用文件稀疏转储写入器
void UseFileWriter()
{
    TFile outputFile("core.sparse.dump", CreateAlways | WrOnly);
    TFileSparseCoreDumpWriter writer(&outputFile);

    // 模拟处理核心转储数据
    ProcessCoreDump([&writer](const TSharedRef& block, bool isZero) {
        if (isZero) {
            writer.OnZeroBlock(block.Size());
        } else {
            writer.OnRegularBlock(block);
        }
    });
}

// 使用异步流写入器
void UseStreamWriter()
{
    auto outputStream = CreateAsyncOutputStream("core.sparse.dump");
    TStreamSparseCoreDumpWriter writer(outputStream, TDuration::Minutes(5));

    ProcessCoreDumpAsync([&writer](const TSharedRef& block, bool isZero) {
        if (isZero) {
            writer.OnZeroBlock(block.Size());
        } else {
            writer.OnRegularBlock(block);
        }
    });
}
```

### 自定义消费者实现

```cpp
class TAnalysisConsumer
    : public ISparseCoreDumpConsumer
{
private:
    struct MemoryRegionStats {
        i64 TotalPages = 0;
        i64 ZeroPages = 0;
        i64 DataPages = 0;
    };

    std::unordered_map<TString, MemoryRegionStats> RegionStats_;
    i64 CurrentOffset_ = 0;

public:
    void OnRegularBlock(TSharedRef block) override
    {
        // 分析常规块内容
        AnalyzeMemoryBlock(block);
        CurrentOffset_ += block.Size();
    }

    void OnZeroBlock(i64 length) override
    {
        // 记录零块统计
        auto regionName = GetMemoryRegionName(CurrentOffset_);
        RegionStats_[regionName].ZeroPages += length / PageSize;
        RegionStats_[regionName].TotalPages += length / PageSize;
        CurrentOffset_ += length;
    }

    void PrintAnalysis()
    {
        std::cout << "内存区域分析:" << std::endl;
        for (const auto& [region, stats] : RegionStats_) {
            double zeroRatio = (double)stats.ZeroPages / stats.TotalPages;
            std::cout << region << ": "
                      << stats.TotalPages << " 页, "
                      << zeroRatio * 100 << "% 零页" << std::endl;
        }
    }

private:
    void AnalyzeMemoryBlock(const TSharedRef& block)
    {
        // 实现内存块分析逻辑
        // 可以检测模式、统计熵等
    }

    TString GetMemoryRegionName(i64 offset)
    {
        // 根据偏移量确定内存区域
        if (offset < HeapStart) return "Stack";
        if (offset < MappedStart) return "Heap";
        return "Mapped";
    }

    static constexpr i64 PageSize = 64 * 1024; // 64KB
    static constexpr i64 HeapStart = 0x100000000;
    static constexpr i64 MappedStart = 0x200000000;
};
```

## 使用方法 (Usage)

### 基本使用步骤

1. **选择输出方式**
```cpp
// 文件输出 - 适合小到中型转储
TFile file("output.sparse", CreateAlways | WrOnly);
TFileSparseCoreDumpWriter writer(&file);

// 异步流输出 - 适合大型转储
auto stream = CreateAsyncOutputStream("output.sparse");
TStreamSparseCoreDumpWriter writer(stream);
```

2. **实现消费者接口**
```cpp
class TMyConsumer : public ISparseCoreDumpConsumer
{
public:
    void OnRegularBlock(TSharedRef block) override;
    void OnZeroBlock(i64 length) override;
};
```

3. **执行稀疏化处理**
```cpp
// 同步处理
i64 processedSize = WriteSparseCoreDump(&inputFile, &outputFile);

// 异步处理
auto future = SparsifyCoreDump(inputStream, consumer, timeout);
auto processedSize = future.Get();
```

### 高级功能使用

#### 批量处理多个核心转储
```cpp
void ProcessMultipleCoreDumps(const std::vector<TString>& coreFiles)
{
    for (const auto& coreFile : coreFiles) {
        try {
            auto consumer = NYT::New<TBatchConsumer>(coreFile + ".sparse");
            auto inputStream = CreateAsyncInputStream(coreFile);

            auto future = SparsifyCoreDump(inputStream, consumer);
            auto size = future.Get();

            std::cout << "处理 " << coreFile << ": " << size << " 字节" << std::endl;
        } catch (const std::exception& ex) {
            std::cerr << "处理 " << coreFile << " 失败: " << ex.what() << std::endl;
        }
    }
}
```

#### 网络传输优化
```cpp
void TransferSparseCoreDump(const TString& remoteHost)
{
    auto networkStream = CreateNetworkStream(remoteHost, 8080);
    TStreamSparseCoreDumpWriter writer(networkStream, TDuration::Minutes(10));

    auto consumer = NYT::New<TNetworkConsumer>(writer);
    auto inputStream = CreateAsyncInputStream("core.dump");

    auto future = SparsifyCoreDump(inputStream, consumer);
    future.Get(); // 等待传输完成
}
```

## 性能考虑 (Performance Considerations)

### 内存优化
- **页面大小优化**: 使用 64KB 页面大小平衡压缩率和处理效率
- **内存映射**: 对大文件使用内存映射减少内存拷贝
- **缓冲管理**: 合理配置读写缓冲区大小

### I/O 性能
- **异步操作**: 所有 I/O 操作异步化避免阻塞
- **批量处理**: 批量处理数据块减少系统调用
- **预读取**: 智能预读取提高顺序访问性能

### 压缩效率
- **零页检测**: 高效的零页检测算法
- **模式识别**: 识别重复模式进一步压缩
- **增量处理**: 支持增量更新和差异处理

## 最佳实践 (Best Practices)

### 文件处理
1. **大小限制**: 对超大文件使用流式处理
2. **存储优化**: 选择合适的存储介质和路径
3. **并发控制**: 控制并发处理数量避免资源竞争
4. **清理机制**: 实现临时文件自动清理

### 错误处理
1. **超时管理**: 设置合理的读写超时时间
2. **重试机制**: 实现网络传输的重试逻辑
3. **部分恢复**: 支持从中断点继续处理
4. **日志记录**: 详细记录处理过程和错误信息

### 监控和调优
1. **性能指标**: 监控压缩率、处理速度等指标
2. **资源使用**: 跟踪 CPU、内存、I/O 使用情况
3. **阈值告警**: 设置性能和资源使用阈值
4. **自动调优**: 根据负载自动调整参数

### 安全考虑
1. **权限控制**: 确保核心转储文件的访问权限
2. **数据完整性**: 验证稀疏化后的数据完整性
3. **敏感信息**: 避免在转储中包含敏感信息
4. **传输安全**: 网络传输时使用加密保护

## 依赖项 (Dependencies)

### 核心依赖
- **yt/yt/core/concurrency**: 并发和协程支持
- **yt/yt/core/yson**: Yson 序列化支持
- **library/cpp/yt/memory**: 内存管理工具

### 系统依赖
- **Linux 系统**: 支持 Linux 特有的核心转储机制
- **文件系统**: 支持大文件和高性能 I/O
- **网络库**: 网络传输支持

### 可选依赖
- **压缩库**: 额外的压缩算法支持
- **加密库**: 数据传输加密支持
- **监控库**: 性能监控和指标收集

## 注意事项 (Important Notes)

### 内存管理
- **缓冲区大小**: 注意设置合适的缓冲区大小
- **内存泄漏**: 防止异步操作中的内存泄漏
- **大文件处理**: 避免将大文件完全加载到内存

### 文件系统限制
- **文件大小**: 注意文件系统的文件大小限制
- **磁盘空间**: 确保有足够的磁盘空间存储结果
- **权限问题**: 确保对文件和目录有适当的访问权限

### 网络传输
- **网络稳定性**: 网络不稳定可能导致传输中断
- **带宽限制**: 注意网络带宽限制
- **防火墙配置**: 确保网络端口开放

### 调试支持
- **调试符号**: 保留必要的调试符号
- **日志级别**: 适当调整日志级别
- **错误诊断**: 保留足够的错误诊断信息

### 兼容性注意
- **架构差异**: 不同 CPU 架构的核心转储格式可能不同
- **版本兼容**: 注意操作系统版本兼容性
- **工具链**: 使用匹配的工具链版本

该库为 YTsaurus 提供了高效的核心转储稀疏化能力，能够显著减少存储和传输开销，同时保持完整的诊断价值。