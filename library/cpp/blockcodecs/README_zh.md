# Block Codecs - 块数据压缩库

## 项目概述

Block Codecs 是一个简单但功能强大的块数据压缩库，专为在内存中对整个数据块进行压缩/解压缩操作而设计。它是 `library/cpp/codecs` 的轻量级版本，专注于提供知名的标准压缩算法，不包含自适应学习功能。

该库支持多种主流压缩算法，包括：
- **LZ4/LZ4-HC**: 极速压缩算法，适合实时场景
- **Zstd/ZSTD 系列**: Facebook 开发的高效压缩算法
- **LZMA**: 7-Zip 压缩算法，提供高压缩比
- **Brotli**: Google 开发的压缩算法，适合 Web 场景
- **Bzip2**: 经典压缩算法，平衡压缩比和速度
- **Snappy**: Google 开发的快速压缩算法
- **Zlib**: 经典的 DEFLATE 压缩算法
- **Null**: 无压缩，用于测试和调试

## 文件说明

### 核心头文件
- **`codecs.h`**: 主要的编解码器接口头文件，导入了核心实现
- **`stream.h`**: 流式处理接口，提供基于块的压缩流功能

### 实现文件
- **`codecs.cpp`**: 编解码器的实现包装器
- **`stream.cpp`**: 流式压缩的实现

### 测试文件
- **`codecs_ut.cpp`**: 完整的单元测试套件，包含：
  - 所有编解码器的压缩/解压缩一致性测试
  - 流式处理的端到端测试
  - 最大解压缩长度限制测试
  - 编解码器列表验证测试

### 构建配置
- **`CMakeLists.txt`**: CMake 构建配置
- **`ya.make`**: YaTool 构建系统配置

## 使用示例

### 基本编解码使用
```cpp
#include <library/cpp/blockcodecs/codecs.h>

using namespace NBlockCodecs;

// 获取编解码器
const ICodec* codec = Codec("zstd_5");  // 使用 ZSTD 压缩级别 5

// 压缩数据
TString data = "这是需要压缩的数据";
TString compressed = codec->Encode(data);

// 解压缩数据
TString decompressed = codec->Decode(compressed);
```

### 流式压缩使用
```cpp
#include <library/cpp/blockcodecs/stream.h>

using namespace NBlockCodecs;

const ICodec* codec = Codec("lz4-fast");

// 创建压缩输出流
TStringStream output;
TCodedOutput codedOutput(&output, codec, 4096);  // 块大小 4KB

// 写入数据到压缩流
codedOutput << "第一段数据";
codedOutput << "第二段数据";
codedOutput << "第三段数据";

// 完成压缩
codedOutput.Finish();

// 创建解压缩输入流
TDecodedInput decodedInput(&output);
TString decompressedData = decodedInput.ReadAll();
```

### 枚举所有可用编解码器
```cpp
#include <library/cpp/blockcodecs/codecs.h>

using namespace NBlockCodecs;

// 获取所有可用编解码器列表
TCodecList codecs = ListAllCodecs();

for (const TString& codecName : codecs) {
    const ICodec* codec = Codec(codecName);
    Cerr << "编解码器: " << codecName << Endl;
}
```

## 实现原理

### 1. 块压缩架构
- **整块处理**: 数据按完整块进行压缩/解压缩，避免流式处理的复杂性
- **内存优化**: 所有操作在内存中完成，减少 I/O 开销
- **压缩比控制**: 支持多种压缩级别，在速度和压缩比之间取得平衡

### 2. 编解码器注册机制
- **插件化设计**: 通过 `PEERDIR()` 机制支持按需加载特定编解码器
- **运行时发现**: 使用 `ListAllCodecs()` 动态发现所有可用编解码器
- **统一接口**: 所有编解码器实现统一的 `ICodec` 接口

### 3. 流式处理
- **缓冲管理**: 智能缓冲区管理，自动处理数据块边界
- **透明编解码**: 通过流接口透明处理压缩/解压缩过程
- **错误处理**: 完善的错误检测和异常处理机制

### 4. 性能优化
- **零拷贝**: 尽可能避免数据拷贝操作
- **内存池**: 重用缓冲区减少内存分配开销
- **压缩参数调优**: 针对不同场景优化的默认参数

## 应用场景

### 1. 实时数据处理
- **日志压缩**: 实时压缩日志流，减少存储开销
- **网络传输**: 压缩网络数据包，减少带宽占用
- **缓存存储**: 压缩缓存数据，提高内存利用率

### 2. 批量数据处理
- **数据仓库**: 压缩存储历史数据
- **备份系统**: 高效压缩备份数据
- **数据归档**: 长期存储的数据压缩

### 3. 性能敏感场景
- **高频交易**: 使用 LZ4/FastLZ 等极速算法
- **实时通信**: 快速压缩网络消息
- **内存受限环境**: 选择合适的压缩算法平衡内存和性能

### 4. 存储优化
- **文件系统**: 压缩文件内容减少磁盘占用
- **数据库**: 压缩存储大文本或二进制数据
- **对象存储**: 压缩存储对象内容

### 5. 开发和测试
- **单元测试**: 使用 Null 编解码器进行性能基准测试
- **调试**: 通过不同压缩算法验证系统正确性
- **兼容性测试**: 测试不同压缩格式的兼容性

## 高级功能

### 1. 安全性配置
```cpp
// 设置最大解压缩长度，防止解压缩炸弹攻击
SetMaxPossibleDecompressedLength(100 * 1024 * 1024);  // 100MB

// 检查当前限制
size_t maxLen = GetMaxPossibleDecompressedLength();
```

### 2. 压缩级别选择
不同的编解码器支持不同的压缩级别：
- **速度优先**: `lz4-fast`, `fastlz`, `snappy`
- **平衡型**: `zstd_5`, `lz4-hc`, `brotli_6`
- **压缩比优先**: `zstd_22`, `lzma-9`, `bzip2-9`

### 3. 内存使用控制
- 可以通过调整块大小控制内存使用
- 支持流式处理，避免一次性加载大文件到内存

这个库为 YTsaurus 分布式存储系统提供了高效的数据压缩能力，在大数据存储和处理场景中发挥了关键作用。