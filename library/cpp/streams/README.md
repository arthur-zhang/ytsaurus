# Streams 流处理库

YTsaurus 高性能流处理库，提供统一的流式数据处理接口和多种压缩算法支持。

## 📋 项目概述

Streams 库为 YTsaurus 提供了完整的流式数据处理基础设施，包括数据压缩、解压缩、流转换等功能。库采用了统一的流接口设计，支持链式操作，特别适合处理大规模数据流的场景。

### 🎯 核心特性

- **统一接口**: 基于 `IInputStream` 和 `IOutputStream` 的统一流接口
- **多种压缩算法**: 支持 LZMA、XZ、Brotli、Zstd、Snappy、LZ4、Bzip2 等
- **零拷贝优化**: 支持零拷贝流操作，减少内存开销
- **链式处理**: 支持流式操作的链式组合
- **内存效率**: 优化的内存使用，支持大文件处理
- **异步支持**: 与异步框架集成，支持非阻塞操作

## 🏗️ 架构设计

### 核心组件结构

```
Streams Library
├── Base Streams        # 基础流接口
│   ├── IInputStream     # 输入流接口
│   ├── IOutputStream    # 输出流接口
│   └── IZeroCopyInput   # 零拷贝输入流
├── Compression         # 压缩算法
│   ├── LZMA           # LZMA 压缩
│   ├── XZ             # XZ 压缩
│   ├── Zstd           # Zstandard 压缩
│   ├── Brotli         # Brotli 压缩
│   ├── Snappy         # Snappy 压缩
│   ├── LZ4            # LZ4 压缩
│   └── Bzip2          # Bzip2 压缩
├── Utilities          # 工具类
│   ├── ZC Memory Input # 零拷贝内存输入
│   └── Stream Helpers  # 流辅助工具
└── Tests             # 测试用例
    ├── Unit Tests      # 单元测试
    └── Integration     # 集成测试
```

### 流处理架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Source   │───▶│   Compression   │───▶│   Data Sink     │
│                 │    │   Stream        │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   File Input    │───▶│  Decompression  │───▶│  Memory Buffer  │
│                 │    │   Stream        │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Network Stream │───▶│  Transform      │───▶│  File Output    │
│                 │    │   Stream        │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 💻 使用方法

### 基础流操作

```cpp
#include <library/cpp/streams/lzma/lzma.h>
#include <library/cpp/streams/zstd/zstd.h>
#include <library/cpp/streams/brotli/const.h>
#include <util/stream/file.h>
#include <util/stream/buffer.h>

// 基础文件流操作
void BasicStreamExample() {
    // 文件输出流
    TUnbufferedFileOutput fileOutput("output.txt");
    fileOutput << "Hello, World!" << Endl;

    // 文件输入流
    TUnbufferedFileInput fileInput("output.txt");
    TString content;
    fileInput >> content;

    std::cout << "Content: " << content << std::endl;

    // 缓冲流
    TBufferedOutput bufferedOutput(fileOutput);
    bufferedOutput << "Buffered output" << Endl;
    bufferedOutput.Finish();
}

// 流式数据处理
void StreamProcessingExample() {
    // 创建输入文件
    {
        TUnbufferedFileOutput output("data.txt");
        for (int i = 0; i < 1000; ++i) {
            output << "Line " << i << ": Some data content" << Endl;
        }
    }

    // 读取和处理
    TUnbufferedFileInput input("data.txt");
    TString line;
    int lineCount = 0;

    while (input.ReadLine(line)) {
        lineCount++;
        // 处理每一行
        if (lineCount % 100 == 0) {
            std::cout << "Processed " << lineCount << " lines" << std::endl;
        }
    }

    std::cout << "Total lines: " << lineCount << std::endl;
}
```

### LZMA/XZ 压缩

```cpp
#include <library/cpp/streams/lzma/lzma.h>
#include <library/cpp/streams/xz/decompress.h>

// LZMA 压缩示例
void LZMACompressionExample() {
    // 准备原始数据
    std::vector<TString> originalData = {
        "This is line 1 of the original data.",
        "LZMA compression provides excellent compression ratios.",
        "It is particularly good for text data.",
        "Multiple lines of test data for compression.",
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    };

    // 压缩数据
    {
        TUnbufferedFileOutput fileOutput("compressed.lzma");
        TLzmaCompress compressor(&fileOutput, 9);  // 最高压缩级别

        for (const auto& line : originalData) {
            compressor << line << Endl;
        }

        compressor.Finish();  // 确保所有数据都被压缩
    }

    // 解压缩数据
    {
        TUnbufferedFileInput fileInput("compressed.lzma");
        TLzmaDecompress decompressor(&fileInput);

        TString line;
        std::vector<TString> decompressedData;

        while (decompressor.ReadLine(line)) {
            decompressedData.push_back(line);
        }

        // 验证解压缩结果
        ASSERT(originalData.size() == decompressedData.size());
        for (size_t i = 0; i < originalData.size(); ++i) {
            ASSERT(originalData[i] == decompressedData[i]);
        }

        std::cout << "LZMA compression/decompression successful!" << std::endl;
        std::cout << "Original lines: " << originalData.size() << std::endl;
    }
}

// 内存中 LZMA 压缩
void InMemoryLZMAExample() {
    TString originalText = "This is a sample text for LZMA compression testing. "
                          "LZMA is known for its excellent compression ratios "
                          "and is used in many compression tools like 7-Zip.";

    // 压缩到内存缓冲区
    TString compressedData;
    {
        TStringOutput stringOutput(compressedData);
        TLzmaCompress compressor(&stringOutput, 7);
        compressor << originalText;
        compressor.Finish();
    }

    // 从内存缓冲区解压缩
    TString decompressedText;
    {
        TStringInput stringInput(compressedData);
        TLzmaDecompress decompressor(&stringInput);

        char buffer[1024];
        size_t bytesRead;
        while ((bytesRead = decompressor.Read(buffer, sizeof(buffer))) > 0) {
            decompressedText.append(buffer, bytesRead);
        }
    }

    std::cout << "Original size: " << originalText.size() << std::endl;
    std::cout << "Compressed size: " << compressedData.size() << std::endl;
    std::cout << "Compression ratio: " << (double)compressedData.size() / originalText.size() << std::endl;
    std::cout << "Decompression successful: " << (originalText == decompressedText) << std::endl;
}
```

### Zstd 压缩

```cpp
#include <library/cpp/streams/zstd/zstd.h>

void ZstdCompressionExample() {
    // 准备大量测试数据
    std::vector<TString> testData;
    for (int i = 0; i < 10000; ++i) {
        testData.push_back("Test data entry " + std::to_string(i) + " with some additional content");
    }

    // Zstd 压缩（支持流式处理）
    {
        TUnbufferedFileOutput fileOutput("data.zst");
        TZstdCompress compressor(&fileOutput, 6);  // 压缩级别 1-22

        for (const auto& data : testData) {
            compressor << data << '\n';
        }

        compressor.Finish();
    }

    // Zstd 解压缩
    {
        TUnbufferedFileInput fileInput("data.zst");
        TZstdDecompress decompressor(&fileInput);

        TString line;
        std::vector<TString> decompressedData;
        int lineCount = 0;

        while (decompressor.ReadLine(line)) {
            decompressedData.push_back(line);
            lineCount++;

            if (lineCount % 1000 == 0) {
                std::cout << "Decompressed " << lineCount << " lines" << std::endl;
            }
        }

        std::cout << "Zstd decompression completed. Total lines: " << lineCount << std::endl;
    }

    // 比较压缩性能
    CompareCompressionPerformance();
}

void CompareCompressionPerformance() {
    TString data;
    for (int i = 0; i < 100000; ++i) {
        data += "Sample data line " + std::to_string(i) + " with repetitive content for better compression\n";
    }

    std::cout << "Original size: " << data.size() << " bytes" << std::endl;

    // 测试不同压缩级别
    for (int level : {1, 3, 6, 9, 12, 15, 18, 22}) {
        TString compressed;
        {
            TStringOutput output(compressed);
            TZstdCompress compressor(&output, level);
            compressor.Write(data.data(), data.size());
            compressor.Finish();
        }

        double ratio = (double)compressed.size() / data.size();
        std::cout << "Zstd level " << level << ": " << compressed.size()
                  << " bytes (ratio: " << ratio << ")" << std::endl;
    }
}
```

### Brotli 压缩

```cpp
#include <library/cpp/streams/brotli/const.h>

// Brotli 压缩示例
void BrotliCompressionExample() {
    // 准备 HTML/JSON 等文本数据（Brotli 对文本压缩效果好）
    TString jsonData = R"({
    "users": [
        {"id": 1, "name": "Alice", "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "email": "bob@example.com"},
        {"id": 3, "name": "Charlie", "email": "charlie@example.com"}
    ],
    "products": [
        {"id": 101, "name": "Laptop", "price": 999.99},
        {"id": 102, "name": "Mouse", "price": 29.99},
        {"id": 103, "name": "Keyboard", "price": 79.99}
    ]
})";

    // Brotli 压缩
    TString compressedJson;
    {
        TStringOutput output(compressedJson);
        TBrotliCompress compressor(&output, 5);  // 压缩级别 1-11
        compressor << jsonData;
        compressor.Finish();
    }

    // Brotli 解压缩
    TString decompressedJson;
    {
        TStringInput input(compressedJson);
        TBrotliDecompress decompressor(&input);

        char buffer[2048];
        size_t bytesRead;
        while ((bytesRead = decompressor.Read(buffer, sizeof(buffer))) > 0) {
            decompressedJson.append(buffer, bytesRead);
        }
    }

    std::cout << "JSON original size: " << jsonData.size() << std::endl;
    std::cout << "JSON compressed size: " << compressedJson.size() << std::endl;
    std::cout << "Compression ratio: " << (double)compressedJson.size() / jsonData.size() << std::endl;
    std::cout << "Decompression successful: " << (jsonData == decompressedJson) << std::endl;
}
```

### Snappy/LZ4 快速压缩

```cpp
// Snappy 快速压缩示例
void SnappyCompressionExample() {
    // Snappy 适合需要高速的场景
    std::vector<TString> logData;
    for (int i = 0; i < 1000; ++i) {
        logData.push_back("[2023-01-01 12:34:56] INFO: Log message " +
                         std::to_string(i) + " with some additional context");
    }

    // 压缩日志数据
    {
        TUnbufferedFileOutput output("logs.snappy");
        TSnappyCompress compressor(&output);

        for (const auto& log : logData) {
            compressor << log << '\n';
        }

        compressor.Finish();
    }

    // 解压缩日志数据
    {
        TUnbufferedFileInput input("logs.snappy");
        TSnappyDecompress decompressor(&input);

        TString line;
        std::vector<TString> decompressedLogs;
        while (decompressor.ReadLine(line)) {
            decompressedLogs.push_back(line);
        }

        std::cout << "Snappy compression completed" << std::endl;
        std::cout << "Original logs: " << logData.size() << std::endl;
        std::cout << "Decompressed logs: " << decompressedLogs.size() << std::endl;
    }
}

// LZ4 超快压缩示例
void LZ4CompressionExample() {
    // LZ4 提供极快的压缩和解压缩速度
    TString largeData;
    for (int i = 0; i < 100000; ++i) {
        largeData += "LZ4 fast compression test data entry number " + std::to_string(i) + "\n";
    }

    // 测量压缩时间
    auto start = std::chrono::high_resolution_clock::now();

    TString compressed;
    {
        TStringOutput output(compressed);
        TLZ4Compress compressor(&output);
        compressor.Write(largeData.data(), largeData.size());
        compressor.Finish();
    }

    auto compressionTime = std::chrono::high_resolution_clock::now() - start;
    auto compressionMs = std::chrono::duration_cast<std::chrono::milliseconds>(compressionTime);

    // 测量解压缩时间
    start = std::chrono::high_resolution_clock::now();

    TString decompressed;
    {
        TStringInput input(compressed);
        TLZ4Decompress decompressor(&input);

        char buffer[4096];
        size_t bytesRead;
        while ((bytesRead = decompressor.Read(buffer, sizeof(buffer))) > 0) {
            decompressed.append(buffer, bytesRead);
        }
    }

    auto decompressionTime = std::chrono::high_resolution_clock::now() - start;
    auto decompressionMs = std::chrono::duration_cast<std::chrono::milliseconds>(decompressionTime);

    std::cout << "LZ4 Performance Results:" << std::endl;
    std::cout << "Original size: " << largeData.size() << " bytes" << std::endl;
    std::cout << "Compressed size: " << compressed.size() << " bytes" << std::endl;
    std::cout << "Compression ratio: " << (double)compressed.size() / largeData.size() << std::endl;
    std::cout << "Compression time: " << compressionMs.count() << " ms" << std::endl;
    std::cout << "Decompression time: " << decompressionMs.count() << " ms" << std::endl;
    std::cout << "Data integrity: " << (largeData == decompressed ? "OK" : "FAILED") << std::endl;
}
```

### 链式流处理

```cpp
// 链式压缩和转换
void ChainStreamExample() {
    // 创建复杂的流处理链：压缩 -> 加密 -> 写入文件
    std::vector<TString> sensitiveData = {
        "Confidential document 1",
        "Secret message 2",
        "Private information 3"
    };

    {
        TUnbufferedFileOutput fileOutput("encrypted_data.zst");

        // 流处理链：Zstd压缩 -> （可在此处添加加密流）
        TZstdCompress compressor(&fileOutput, 6);

        for (const auto& data : sensitiveData) {
            compressor << data << '\n';
        }

        compressor.Finish();
    }

    // 读取和处理链：解密 -> 解压缩 -> 读取
    {
        TUnbufferedFileInput fileInput("encrypted_data.zst");

        // 流处理链：（解密流）-> Zstd解压缩
        TZstdDecompress decompressor(&fileInput);

        TString line;
        while (decompressor.ReadLine(line)) {
            std::cout << "Recovered: " << line << std::endl;
        }
    }
}

// 多重压缩（演示性的，实际中很少使用）
void MultipleCompressionExample() {
    TString originalData = "This data will be compressed multiple times for demonstration";

    // 第一层：LZ4 快速压缩
    TString firstCompressed;
    {
        TStringOutput output(firstCompressed);
        TLZ4Compress compressor1(&output);
        compressor1 << originalData;
        compressor1.Finish();
    }

    // 第二层：Zstd 压缩
    TString secondCompressed;
    {
        TStringOutput output(secondCompressed);
        TZstdCompress compressor2(&output, 6);
        compressor2.Write(firstCompressed.data(), firstCompressed.size());
        compressor2.Finish();
    }

    std::cout << "Original size: " << originalData.size() << std::endl;
    std::cout << "After 1st compression: " << firstCompressed.size() << std::endl;
    std::cout << "After 2nd compression: " << secondCompressed.size() << std::endl;

    // 反向解压缩
    TString firstDecompressed;
    {
        TStringInput input(secondCompressed);
        TZstdDecompress decompressor2(&input);

        char buffer[4096];
        size_t bytesRead;
        while ((bytesRead = decompressor2.Read(buffer, sizeof(buffer))) > 0) {
            firstDecompressed.append(buffer, bytesRead);
        }
    }

    TString finalDecompressed;
    {
        TStringInput input(firstDecompressed);
        TLZ4Decompress decompressor1(&input);

        char buffer[4096];
        size_t bytesRead;
        while ((bytesRead = decompressor1.Read(buffer, sizeof(buffer))) > 0) {
            finalDecompressed.append(buffer, bytesRead);
        }
    }

    std::cout << "Decompression successful: " << (originalData == finalDecompressed) << std::endl;
}
```

### 零拷贝流操作

```cpp
#include <util/stream/zerocopy.h>
#include <library/cpp/streams/zc_memory_input/zc_memory_input.h>

void ZeroCopyStreamExample() {
    // 准备数据
    TString data = "Large chunk of data for zero-copy demonstration. "
                  "Zero-copy operations reduce memory copies and improve performance.";

    // 创建零拷贝输入流
    TMemoryInput memoryInput(data.data(), data.size());
    TZCMemoryInput zcInput(&memoryInput);

    // 零拷贝读取
    const void* ptr;
    size_t size;

    while (zcInput.Next(&ptr, &size)) {
        std::cout << "Read " << size << " bytes at address " << ptr << std::endl;

        // 直接使用数据，无需拷贝
        TString chunk(static_cast<const char*>(ptr), size);
        // 处理 chunk...
    }

    // 零拷贝与压缩结合
    TString compressed;
    {
        TStringOutput output(compressed);
        TMemoryInput memoryInput(data.data(), data.size());
        TZCMemoryInput zcInput(&memoryInput);
        TZstdCompress compressor(&output, 6);

        // 零拷贝读取，直接压缩
        const void* ptr;
        size_t size;
        while (zcInput.Next(&ptr, &size)) {
            compressor.Write(ptr, size);
        }

        compressor.Finish();
    }

    std::cout << "Zero-copy compression completed" << std::endl;
    std::cout << "Original: " << data.size() << " bytes" << std::endl;
    std::cout << "Compressed: " << compressed.size() << " bytes" << std::endl;
}
```

## 🔧 高级特性

### 异步流处理

```cpp
#include <library/cpp/threading/future/future.h>

// 异步压缩大文件
TFuture<void> AsyncCompressFile(const TString& inputFile, const TString& outputFile, int compressionLevel) {
    return NThreading::Async([inputFile, outputFile, compressionLevel]() -> void {
        TUnbufferedFileInput input(inputFile);
        TUnbufferedFileOutput output(outputFile);
        TZstdCompress compressor(&output, compressionLevel);

        // 缓冲区大小优化
        constexpr size_t BUFFER_SIZE = 64 * 1024; // 64KB
        std::vector<char> buffer(BUFFER_SIZE);

        size_t totalRead = 0;
        size_t bytesRead;

        while ((bytesRead = input.Read(buffer.data(), BUFFER_SIZE)) > 0) {
            compressor.Write(buffer.data(), bytesRead);
            totalRead += bytesRead;

            // 进度报告
            if (totalRead % (1024 * 1024) == 0) { // 每MB报告一次
                std::cout << "Compressed " << totalRead / (1024 * 1024) << " MB" << std::endl;
            }
        }

        compressor.Finish();
        std::cout << "Compression completed. Total: " << totalRead << " bytes" << std::endl;
    });
}

void AsyncCompressionExample() {
    // 创建大测试文件
    {
        TUnbufferedFileOutput output("large_file.txt");
        for (int i = 0; i < 100000; ++i) {
            output << "Line " << i << ": This is test data for large file compression\n";
        }
    }

    // 异步压缩文件
    auto compressionFuture = AsyncCompressFile("large_file.txt", "large_file.zst", 6);

    // 可以在压缩过程中做其他工作
    std::cout << "Compression started in background..." << std::endl;
    std::cout << "Doing other work while compression runs..." << std::endl;

    // 等待压缩完成
    compressionFuture.WaitSync();
    std::cout << "Background compression completed!" << std::endl;
}
```

### 流式数据分析

```cpp
// 流式数据分析工具
class TStreamAnalyzer {
public:
    struct TStats {
        size_t TotalBytes = 0;
        size_t TotalLines = 0;
        size_t TotalWords = 0;
        std::unordered_map<char, size_t> CharFrequency;
    };

    template <typename TInputStream>
    TStats AnalyzeStream(TInputStream& stream) {
        TStats stats;
        TString line;
        std::vector<char> buffer(8192);

        while (stream.ReadLine(line)) {
            stats.TotalLines++;
            stats.TotalBytes += line.size() + 1; // +1 for newline

            // 字符频率统计
            for (char c : line) {
                stats.CharFrequency[c]++;
            }

            // 单词计数（简单实现）
            std::istringstream iss(line);
            std::string word;
            while (iss >> word) {
                stats.TotalWords++;
            }

            // 处理大文件时定期报告进度
            if (stats.TotalLines % 1000 == 0) {
                std::cout << "Analyzed " << stats.TotalLines << " lines" << std::endl;
            }
        }

        return stats;
    }

    void PrintStats(const TStats& stats) const {
        std::cout << "\n=== Stream Analysis Results ===" << std::endl;
        std::cout << "Total bytes: " << stats.TotalBytes << std::endl;
        std::cout << "Total lines: " << stats.TotalLines << std::endl;
        std::cout << "Total words: " << stats.TotalWords << std::endl;

        std::cout << "\nTop 10 characters:" << std::endl;
        std::vector<std::pair<char, size_t>> sortedChars(
            stats.CharFrequency.begin(), stats.CharFrequency.end());
        std::sort(sortedChars.begin(), sortedChars.end(),
                 [](const auto& a, const auto& b) { return a.second > b.second; });

        for (int i = 0; i < std::min(10, (int)sortedChars.size()); ++i) {
            char c = sortedChars[i].first;
            size_t count = sortedChars[i].second;
            if (std::isprint(c)) {
                std::cout << "'" << c << "': " << count << std::endl;
            } else {
                std::cout << "'\\x" << std::hex << (int)c << "': " << count << std::endl;
            }
        }
    }
};

void StreamAnalysisExample() {
    // 创建测试数据
    {
        TUnbufferedFileOutput output("test_data.txt");
        for (int i = 0; i < 10000; ++i) {
            output << "Test line " << i << " with various characters: ";
            output << "ABCDEFGHIJKLMNOPQRSTUVWXYZ ";
            output << "abcdefghijklmnopqrstuvwxyz ";
            output << "0123456789 ";
            output << "!@#$%^&*()_+-=[]{}|;':\",./<>?" << std::endl;
        }
    }

    // 分析原始文件
    TStreamAnalyzer analyzer;
    {
        TUnbufferedFileInput input("test_data.txt");
        auto stats = analyzer.AnalyzeStream(input);
        std::cout << "Original file analysis:" << std::endl;
        analyzer.PrintStats(stats);
    }

    // 分析压缩后的文件（先解压缩再分析）
    {
        TUnbufferedFileInput fileInput("test_data.txt");
        TUnbufferedFileOutput fileOutput("test_data.zst");
        TZstdCompress compressor(&fileOutput, 6);

        char buffer[8192];
        size_t bytesRead;
        while ((bytesRead = fileInput.Read(buffer, sizeof(buffer))) > 0) {
            compressor.Write(buffer, bytesRead);
        }
        compressor.Finish();

        // 分析压缩文件
        TUnbufferedFileInput zstdInput("test_data.zst");
        TZstdDecompress decompressor(&zstdInput);
        auto compressedStats = analyzer.AnalyzeStream(decompressor);

        std::cout << "\nCompressed file analysis:" << std::endl;
        analyzer.PrintStats(compressedStats);
    }
}
```

## 🧪 测试和验证

### 压缩算法比较测试

```cpp
#include <library/cpp/testing/gtest/gtest.h>

class CompressionTest : public ::testing::Test {
protected:
    void SetUp() override {
        // 生成测试数据
        for (int i = 0; i < 10000; ++i) {
            TestData_.append("Sample data line " + std::to_string(i) +
                           " with some repeated content for compression testing\n");
        }
    }

    std::string TestData_;
};

TEST_F(CompressionTest, CompareCompressionRatios) {
    struct TCompressionResult {
        std::string Algorithm;
        size_t OriginalSize;
        size_t CompressedSize;
        double Ratio;
        std::chrono::milliseconds CompressionTime;
        std::chrono::milliseconds DecompressionTime;
    };

    std::vector<TCompressionResult> results;

    // 测试 Zstd
    {
        auto start = std::chrono::high_resolution_clock::now();
        std::string compressed;
        {
            std::stringoutput output(compressed);
            TZstdCompress compressor(&output, 6);
            compressor.Write(TestData_.data(), TestData_.size());
            compressor.Finish();
        }
        auto compressionTime = std::chrono::high_resolution_clock::now() - start;

        start = std::chrono::high_resolution_clock::now();
        std::string decompressed;
        {
            std::stringinput input(compressed);
            TZstdDecompress decompressor(&input);
            char buffer[4096];
            size_t bytesRead;
            while ((bytesRead = decompressor.Read(buffer, sizeof(buffer))) > 0) {
                decompressed.append(buffer, bytesRead);
            }
        }
        auto decompressionTime = std::chrono::high_resolution_clock::now() - start;

        results.push_back({"Zstd", TestData_.size(), compressed.size(),
                         (double)compressed.size() / TestData_.size(),
                         std::chrono::duration_cast<std::chrono::milliseconds>(compressionTime),
                         std::chrono::duration_cast<std::chrono::milliseconds>(decompressionTime)});
    }

    // 测试 LZ4
    {
        auto start = std::chrono::high_resolution_clock::now();
        std::string compressed;
        {
            std::stringoutput output(compressed);
            TLZ4Compress compressor(&output);
            compressor.Write(TestData_.data(), TestData_.size());
            compressor.Finish();
        }
        auto compressionTime = std::chrono::high_resolution_clock::now() - start;

        start = std::chrono::high_resolution_clock::now();
        std::string decompressed;
        {
            std::stringinput input(compressed);
            TLZ4Decompress decompressor(&input);
            char buffer[4096];
            size_t bytesRead;
            while ((bytesRead = decompressor.Read(buffer, sizeof(buffer))) > 0) {
                decompressed.append(buffer, bytesRead);
            }
        }
        auto decompressionTime = std::chrono::high_resolution_clock::now() - start;

        results.push_back({"LZ4", TestData_.size(), compressed.size(),
                         (double)compressed.size() / TestData_.size(),
                         std::chrono::duration_cast<std::chrono::milliseconds>(compressionTime),
                         std::chrono::duration_cast<std::chrono::milliseconds>(decompressionTime)});
    }

    // 输出比较结果
    std::cout << "\n=== Compression Algorithm Comparison ===" << std::endl;
    std::cout << std::setw(10) << "Algorithm"
              << std::setw(15) << "Original Size"
              << std::setw(15) << "Compressed Size"
              << std::setw(10) << "Ratio"
              << std::setw(15) << "Comp Time (ms)"
              << std::setw(18) << "Decomp Time (ms)" << std::endl;
    std::cout << std::string(90, '-') << std::endl;

    for (const auto& result : results) {
        std::cout << std::setw(10) << result.Algorithm
                  << std::setw(15) << result.OriginalSize
                  << std::setw(15) << result.CompressedSize
                  << std::setw(10) << std::fixed << std::setprecision(3) << result.Ratio
                  << std::setw(15) << result.CompressionTime.count()
                  << std::setw(18) << result.DecompressionTime.count()
                  << std::endl;
    }
}

TEST_F(CompressionTest, DataIntegrityTest) {
    // 测试所有压缩算法的数据完整性
    std::vector<std::function<std::string()>> compressors = {
        [this]() -> std::string {
            std::string compressed;
            std::stringoutput output(compressed);
            TZstdCompress compressor(&output, 6);
            compressor.Write(TestData_.data(), TestData_.size());
            compressor.Finish();
            return compressed;
        },
        [this]() -> std::string {
            std::string compressed;
            std::stringoutput output(compressed);
            TLZ4Compress compressor(&output);
            compressor.Write(TestData_.data(), TestData_.size());
            compressor.Finish();
            return compressed;
        }
    };

    std::vector<std::function<std::string(const std::string&)>> decompressors = {
        [](const std::string& compressed) -> std::string {
            std::string decompressed;
            std::stringinput input(compressed);
            TZstdDecompress decompressor(&input);
            char buffer[4096];
            size_t bytesRead;
            while ((bytesRead = decompressor.Read(buffer, sizeof(buffer))) > 0) {
                decompressed.append(buffer, bytesRead);
            }
            return decompressed;
        },
        [](const std::string& compressed) -> std::string {
            std::string decompressed;
            std::stringinput input(compressed);
            TLZ4Decompress decompressor(&input);
            char buffer[4096];
            size_t bytesRead;
            while ((bytesRead = decompressor.Read(buffer, sizeof(buffer))) > 0) {
                decompressed.append(buffer, bytesRead);
            }
            return decompressed;
        }
    };

    // 测试每种压缩/解压缩组合
    for (size_t i = 0; i < compressors.size(); ++i) {
        auto compressed = compressors[i]();
        auto decompressed = decompressors[i](compressed);

        EXPECT_EQ(TestData_, decompressed)
            << "Data integrity check failed for algorithm " << i;
    }
}
```

## 📈 最佳实践

### 压缩算法选择指南

1. **Zstd**: 通用压缩，平衡速度和压缩率
2. **LZ4**: 速度优先，适合实时数据处理
3. **Snappy**: Google开发的快速压缩，适合日志数据
4. **Brotli**: 文本数据压缩，适合Web内容
5. **LZMA**: 最高压缩率，适合归档存储

### 性能优化建议

1. **缓冲区大小**: 使用64KB-1MB缓冲区获得最佳性能
2. **压缩级别**: 根据需求选择合适的压缩级别
3. **流式处理**: 对大文件使用流式处理避免内存溢出
4. **零拷贝**: 在性能关键路径使用零拷贝操作

### 错误处理

```cpp
void RobustStreamProcessing() {
    try {
        TUnbufferedFileInput input("data.txt");
        TUnbufferedFileOutput output("compressed.zst");
        TZstdCompress compressor(&output, 6);

        char buffer[64 * 1024];
        size_t totalRead = 0;

        while (true) {
            size_t bytesRead = input.Read(buffer, sizeof(buffer));
            if (bytesRead == 0) break;

            compressor.Write(buffer, bytesRead);
            totalRead += bytesRead;
        }

        compressor.Finish();

        std::cout << "Successfully compressed " << totalRead << " bytes" << std::endl;

    } catch (const std::exception& e) {
        std::cerr << "Stream processing error: " << e.what() << std::endl;
        // 错误处理逻辑
    }
}
```

## 🔗 相关模块

- **FileSystem**: 文件系统操作
- **Memory**: 内存管理
- **Threading**: 异步处理支持
- **Containers**: 数据结构支持
- **JSON/YAML/XML**: 数据格式支持

Streams 库为 YTsaurus 提供了强大的流处理能力，支持多种压缩算法和优化技术，是处理大规模数据流的核心组件。通过统一的接口设计，开发者可以轻松地在不同压缩算法间切换，实现最佳的性能和存储效率平衡。