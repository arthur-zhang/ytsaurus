# Compression 模块

## 模块概述

`yt/yt/core/compression` 模块是 YTsaurus 分布式系统的压缩处理核心库，提供了统一的高性能数据压缩和解压缩接口。该模块集成了多种主流压缩算法，包括 LZ4、Zstd、Brotli、Zlib、LZMA、Bzip2 和 Snappy 等，为 YTsaurus 系统中的数据存储、网络传输和缓存优化提供灵活的压缩解决方案。

模块采用插件化架构设计，通过 `ICodec` 接口抽象不同压缩算法的实现细节，同时提供高级的字典压缩功能和流式处理能力，能够满足从实时数据处理到大规模数据归档等各种场景的压缩需求。

## 主要功能

### 1. 统一编解码器接口 (ICodec)
- **类型安全**: 强类型的编解码器接口，编译时保证类型正确性
- **批量处理**: 支持单个数据块和多个数据块的批量压缩
- **内存效率**: 基于共享引用的内存管理，最小化数据拷贝
- **算法抽象**: 统一的接口屏蔽不同压缩算法的实现差异

### 2. 多种压缩算法支持
- **Snappy**: 高速压缩，适合实时数据处理
- **LZ4/LZ4 High Compression**: 极速压缩，平衡速度和压缩率
- **Zstd**: 现代压缩算法，优秀的压缩率和速度平衡
- **Brotli**: Web 优化的压缩算法，高压缩率
- **Zlib/Gzip**: 经典压缩算法，广泛的兼容性
- **LZMA**: 高压缩率，适合归档场景
- **Bzip2**: 高压缩率，适合文本数据
- **ZstdFast**: Zstd 的快速模式，优化压缩速度

### 3. 字典压缩 (Dictionary Compression)
- **字典训练**: 从样本数据中自动训练压缩字典
- **上下文感知**: 基于字典的上下文相关压缩
- **内存优化**: 预处理的字典表示，优化运行时性能
- **并发支持**: 字典可被多个压缩/解压缩实例并发使用

### 4. 流式处理 (Stream Processing)
- **流式接口**: 支持大数据量的流式压缩和解压缩
- **内存高效**: 无需将全部数据加载到内存中
- **适配器模式**: 与标准输入输出流的适配
- **分段处理**: 支持数据的分块处理和重组

### 5. 压缩级别控制
- **精细级别**: 每种算法提供多个压缩级别
- **质量权衡**: 在压缩率和压缩速度间灵活选择
- **场景适配**: 针对不同使用场景优化参数

### 6. 性能优化
- **零拷贝**: 尽可能避免数据拷贝操作
- **SIMD 优化**: 利用 CPU 的 SIMD 指令集加速
- **内存池**: 预分配内存缓冲区减少动态分配
- **多线程**: 支持并行压缩和解压缩

## 文件说明

### 核心接口文件
- **public.h**: 模块的公共接口声明，定义 ECodec 枚举和类型前向声明
- **codec.h/c**: 核心的 ICodec 接口定义和编解码器管理
- **private.h**: 私有接口和内部实现细节
- **public.cpp**: 模块初始化和编解码器注册

### 字典压缩文件
- **dictionary_codec.h/c**: 字典压缩的核心接口和实现
- **IDictionaryCompressionCodec**: 字典压缩编解码器接口
- **IDigestedCompressionDictionary**: 预处理的压缩字典
- **IDigestedDecompressionDictionary**: 预处理的解压缩字典

### 流式处理文件
- **stream.h/c**: 流式压缩的源汇和适配器实现
- **TSource/TSink**: 数据源和数据汇的抽象
- **TRefSource**: 基于内存引用的数据源
- **TRefsVectorSource**: 基于引用向量的数据源
- **TBlobSink**: 基于内存块的数据汇

### 具体算法实现文件
- **snappy.h/c**: Snappy 算法实现
- **lz.h/c**: LZ4 算法实现
- **zstd.h/c**: Zstd 算法实现，包括同步标签和字典支持
- **zlib.h/c**: Zlib/Gzip 算法实现
- **brotli.h/c**: Brotli 算法实现
- **lzma.h/c**: LZMA 算法实现
- **bzip2.h/c**: Bzip2 算法实现

### 测试文件
- **unittests/codec_ut.cpp**: 编解码器基础功能测试
- **unittests/dictionary_compression_ut.cpp**: 字典压缩功能测试
- **unittests/stream_ut.cpp**: 流式处理功能测试

## 使用方法

### 基本压缩使用
```cpp
#include <yt/yt/core/compression/codec.h>

// 获取指定编解码器
auto* codec = NYT::NCompression::GetCodec(NYT::NCompression::ECodec::Zstd_6);

// 压缩单个数据块
auto input = NYT::TSharedRef::FromString("Hello, YTsaurus!");
auto compressed = codec->Compress(input);

// 解压缩
auto decompressed = codec->Decompress(compressed);

// 验证结果
assert(decompressed.Size() == input.Size());
assert(memcmp(decompressed.Begin(), input.Begin(), input.Size()) == 0);
```

### 批量数据处理
```cpp
#include <yt/yt/core/compression/codec.h>

// 准备多个数据块
std::vector<NYT::TSharedRef> blocks;
blocks.push_back(NYT::TSharedRef::FromString("First block"));
blocks.push_back(NYT::TSharedRef::FromString("Second block"));
blocks.push_back(NYT::TSharedRef::FromString("Third block"));

// 批量压缩
auto* codec = NYT::NCompression::GetCodec(NYT::NCompression::ECodec::Lz4);
auto compressed = codec->Compress(blocks);

// 批量解压缩
auto decompressed = codec->Decompress(compressed);
```

### 字典压缩使用
```cpp
#include <yt/yt/core/compression/dictionary_codec.h>

// 获取字典压缩编解码器
auto* dictCodec = NYT::NCompression::GetDictionaryCompressionCodec();

// 训练字典
std::vector<NYT::TSharedRef> samples;
samples.push_back(NYT::TSharedRef::FromString("Sample data 1"));
samples.push_back(NYT::TSharedRef::FromString("Sample data 2"));

auto dictResult = dictCodec->TrainCompressionDictionary(64 * 1024, samples);
if (dictResult.IsOK()) {
    auto dictionary = dictResult.Value();

    // 估算并创建消化字典
    auto compressedDictSize = dictCodec->EstimateDigestedCompressionDictionarySize(
        dictionary->Size(), 3);
    auto storage = NYT::TSharedMutableRef::Allocate(compressedDictSize);

    auto digestedDict = dictCodec->ConstructDigestedCompressionDictionary(
        dictionary, storage, 3);

    // 创建压缩器
    auto compressor = dictCodec->CreateDictionaryCompressor(digestedDict);

    // 使用压缩器压缩数据
    NYT::NCompression::TChunkedMemoryPool pool;
    auto input = NYT::TRef::FromString("Data to compress");
    auto compressed = compressor->Compress(&pool, input);
}
```

### 流式压缩使用
```cpp
#include <yt/yt/core/compression/stream.h>

// 使用 Snappy 流式压缩
NYT::TBlob output;
NYT::TSharedRef input = NYT::TSharedRef::FromString("Large data chunk");

NYT::NCompression::NDetail::TRefSource source(input);
NYT::NCompression::NDetail::TBlobSink sink(&output);

NYT::NCompression::NDetail::SnappyCompress(&source, &output);
```

### 不同压缩算法选择
```cpp
#include <yt/yt/core/compression/public.h>

// 根据使用场景选择合适的压缩算法
enum class CompressionScenario {
    RealTime,      // 实时处理，优先速度
    Balanced,      // 平衡速度和压缩率
    HighRatio,     // 高压缩率，优先空间
    Archive        // 归档，最高压缩率
};

NYT::NCompression::ECodec SelectCodec(CompressionScenario scenario) {
    switch (scenario) {
        case CompressionScenario::RealTime:
            return NYT::NCompression::ECodec::Snappy;
        case CompressionScenario::Balanced:
            return NYT::NCompression::ECodec::Lz4;
        case CompressionScenario::HighRatio:
            return NYT::NCompression::ECodec::Zstd_6;
        case CompressionScenario::Archive:
            return NYT::NCompression::ECodec::Lzma_9;
    }
}
```

### 检查支持的编解码器
```cpp
#include <yt/yt/core/compression/codec.h>

// 获取所有支持的编解码器
const auto& supportedCodecs = NYT::NCompression::GetSupportedCodecs();

// 获取被禁用的编解码器
const auto& forbiddenCodecs = NYT::NCompression::GetForbiddenCodecs();

// 检查特定编解码器是否可用
bool isSnappySupported = std::find(
    supportedCodecs.begin(),
    supportedCodecs.end(),
    NYT::NCompression::ECodec::Snappy) != supportedCodecs.end();
```

## 依赖关系

### 内部依赖
- **yt/yt/core/misc**: 基础工具、错误处理和内存管理
- **yt/yt/core/logging**: 日志记录功能
- **library/cpp/yt/memory**: YT 特定的内存管理工具

### 外部依赖
- **Snappy**: Google 开源的高速压缩库
- **LZ4**: 极速压缩算法库
- **Zstd**: Facebook 开发的现代压缩库
- **Brotli**: Google 开发的 Web 压缩库
- **Zlib**: 经典压缩库
- **LZMA SDK**: 7-Zip 的压缩算法
- **Bzip2**: Bzip2 压缩库
- **C++20**: 现代 C++ 特性支持

## 实现原理

### 编解码器注册机制
模块使用静态注册机制，每个压缩算法的实现都会在程序启动时注册到全局编解码器表中。`GetCodec()` 函数通过算法 ID 查找并返回相应的编解码器实例。

### 内存管理策略
- **共享引用**: 使用 `TSharedRef` 管理数据块生命周期
- **零拷贝**: 在可能的情况下避免数据拷贝
- **内存池**: 字典压缩使用内存池减少分配开销
- **RAII**: 自动资源管理，防止内存泄漏

### 字典压缩原理
字典压缩通过两阶段过程实现：
1. **训练阶段**: 分析样本数据，提取重复模式生成字典
2. **压缩阶段**: 使用字典对数据进行上下文相关压缩

### 流式处理架构
流式处理基于生产者-消费者模式：
- **Source**: 数据源抽象，支持多种输入类型
- **Sink**: 数据汇抽象，支持多种输出目标
- **适配器**: 与标准 I/O 流的适配实现

### 错误处理
- **类型化错误**: 使用 `TError` 类型传递详细错误信息
- **异常安全**: 保证异常情况下的资源清理
- **降级策略**: 压缩失败时可选择不压缩或使用备用算法

## 压缩算法对比

### Snappy
- **特点**: 高速度，中等压缩率
- **适用场景**: 实时数据处理，网络传输
- **压缩率**: 通常为原始数据的 40-60%
- **速度**: 压缩 > 200MB/s，解压缩 > 500MB/s

### LZ4/LZ4 High Compression
- **特点**: 极高速度，可配置压缩率
- **适用场景**: 高性能存储系统，缓存压缩
- **压缩率**: LZ4: 40-50%，LZ4HC: 35-45%
- **速度**: 压缩 > 400MB/s，解压缩 > 1GB/s

### Zstd
- **特点**: 现代算法，优秀的压缩率和速度平衡
- **适用场景**: 通用压缩，大数据处理
- **压缩率**: 级别 6: 30-40%，级别 20: 25-35%
- **速度**: 级别 6: 100-200MB/s，级别 20: 10-50MB/s

### Brotli
- **特点**: Web 优化，高压缩率
- **适用场景**: Web 内容压缩，静态资源
- **压缩率**: 通常优于 Zstd 10-20%
- **速度**: 压缩较慢，解压缩速度快

### LZMA
- **特点**: 最高压缩率，较慢速度
- **适用场景**: 数据归档，长期存储
- **压缩率**: 通常为原始数据的 20-30%
- **速度**: 压缩 < 50MB/s，解压缩 50-100MB/s

### Zlib/Gzip
- **特点**: 广泛兼容，平衡性能
- **适用场景**: 通用压缩，兼容性要求高的场景
- **压缩率**: 级别 6: 35-45%
- **速度**: 压缩 50-100MB/s，解压缩 200-400MB/s

## 性能优化建议

### 算法选择
- **实时场景**: 使用 Snappy 或 LZ4
- **存储优化**: 使用 Zstd 中等级别
- **网络传输**: 使用 LZ4 或 Zstd 快速模式
- **归档存储**: 使用 LZMA 或 Zstd 最高级别

### 缓冲区管理
- **块大小**: 通常 64KB-1MB 的块大小效果最好
- **内存预分配**: 预分配缓冲区避免运行时分配
- **批量处理**: 批量处理多个小块比单个处理更高效

### 并发处理
- **并行压缩**: 对独立的块使用多线程并行压缩
- **流水线**: 压缩和解压缩可以使用流水线处理
- **NUMA 优化**: 在 NUMA 系统上注意内存亲和性

## 最佳实践

### 数据预处理
- **对齐数据**: 确保数据按合适的边界对齐
- **去除噪音**: 在压缩前去除无关或冗余数据
- **数据分组**: 将相似的数据分组后一起压缩

### 字典使用
- **样本选择**: 选择代表性的数据样本训练字典
- **字典大小**: 根据数据特性选择合适的字典大小
- **字典更新**: 定期更新字典以适应数据变化

### 错误处理
- **降级机制**: 准备压缩失败时的降级策略
- **资源监控**: 监控内存和 CPU 使用情况
- **日志记录**: 记录压缩性能和错误信息

### 测试验证
- **完整性测试**: 确保压缩解压缩后的数据完整性
- **性能测试**: 在真实数据上测试压缩性能
- **兼容性测试**: 验证不同版本间的兼容性

## 监控和调试

### 性能指标
- **压缩率**: 压缩后大小与原始大小的比率
- **吞吐量**: 每秒处理的压缩/解压缩数据量
- **延迟**: 单次压缩/解压缩操作的时间
- **内存使用**: 压缩过程中的内存占用

### 调试工具
- **算法对比**: 在实际数据上对比不同算法的效果
- **性能分析**: 使用性能分析工具定位瓶颈
- **内存分析**: 检查内存分配和泄漏
- **错误日志**: 分析压缩失败的原因

## 扩展点

- **自定义编解码器**: 实现 ICodec 接口添加新的压缩算法
- **流式适配器**: 实现自定义的 Source 和 Sink
- **字典策略**: 实现自定义的字典训练和管理策略
- **性能优化**: 添加特定硬件的优化实现
- **监控集成**: 集成外部性能监控系统

## 未来发展

### 新算法支持
- 持续跟踪和集成新的压缩算法
- 支持硬件加速的压缩实现
- 适配特定数据类型的专用压缩算法

### 性能提升
- 利用新的 CPU 指令集优化
- 改进并行处理能力
- 优化内存使用模式

### 功能增强
- 增强的字典管理功能
- 自适应压缩算法选择
- 更丰富的监控和调试工具