# CompTable 压缩表库

## 项目描述

CompTable 是 YTsaurus 中的高性能数据压缩表库，专门用于基于统计特征的通用数据压缩。该库通过分析数据的分布特征，构建最优的霍夫曼编码表，实现高效的数据压缩和解压缩。

CompTable 结合了统计分析、哈希优化和分层编码技术，特别适合处理具有重复模式和统计规律的数据集，能够达到很高的压缩比和快速的处理速度。

## 核心特性

### 📊 智能统计分析
- 自动分析数据分布特征
- 构建频率统计表
- 优化编码策略选择

### 🎯 分层霍夫曼编码
- 10层自适应编码表
- 前缀优化的变长编码
- 高效的码表构建算法

### ⚡ 高性能处理
- 快速哈希索引
- 批量数据处理
- 内存友好的实现

### 🔧 灵活配置
- 支持高质量和快速模式
- 可配置的压缩参数
- 自适应优化策略

## 主要组件

### 1. 压缩表核心 (TCompressorTable)
```cpp
struct TCompressorTable {
    ui32 Table[65536];                    // 主压缩表
    ui32 HashMul;                         // 哈希乘数
    NCompProto::TCoderEntry HuffCodes[10]; // 霍夫曼编码表
    ui8 HuffIndices[256];                 // 霍夫曼索引表

    // 核心操作函数
    void GetHuffCode(const NCompProto::TCoderEntry& entry,
                    ui32 value, ui64& bitCode, ui8& bitLength) const;
    void GetLastHuffCode(ui32 value, ui64& bitCode, ui8& bitLength) const;
    void GetHuffCode(ui32 value, ui64& bitCode, ui8& bitLength) const;

    // 构建和查询函数
    ui8 GetHuffIndex(ui8 prefix);
    void BuildHuffCodes(i64 totalFreq, i64 freqs[65536]);
    bool BuildHuffCodes(i64 totalFreq, i64 freqs[65536], i64 add);
};
```

#### 核心特点
- **64K 编码表**: 支持 65536 个不同的值编码
- **10层霍夫曼编码**: 分层处理不同频率的数据
- **哈希优化**: 快速的值到编码映射
- **前缀编码**: 高效的变长编码实现

### 2. 数据采样器 (TDataSampler)
```cpp
struct TDataSampler {
    enum { Size = 1 << 18 };             // 256K 采样槽
    ui32 EntryVal[Size];                  // 采样值
    i64 EntryHit[Size];                   // 命中计数
    i64 Counter;                          // 总计数

public:
    TDataSampler();
    void BuildTable(TCompressorTable& table) const;
    void AddStat(ui32 val);
    void AddStat(const TStringBuf& stringBuf);
};
```

#### 采样特性
- **大规模采样**: 256K 个采样槽
- **频率统计**: 准确的值出现频率
- **增量更新**: 支持动态数据统计
- **字符串支持**: 直接处理字符串数据

### 3. 块压缩器 (TChunkCompressor)
```cpp
class TChunkCompressor {
public:
    TChunkCompressor(bool highQuality, const TCompressorTable& table);
    void Compress(TStringBuf data, TVector<char>* result) const;
    ~TChunkCompressor();

private:
    bool HighQuality;                     // 质量模式标志
    THolder<TDataCompressor> Compressor; // 内部压缩器
};
```

#### 压缩模式
- **高质量模式**: 更好的压缩比，稍慢的速度
- **快速模式**: 更快的压缩速度，适中的压缩比
- **块处理**: 高效的批量数据压缩

### 4. 块解压缩器 (TChunkDecompressor)
```cpp
class TChunkDecompressor {
public:
    TChunkDecompressor(bool highQuality, const TCompressorTable& table);
    void Decompress(TStringBuf data, TVector<char>* result) const;
    ~TChunkDecompressor();

private:
    bool HighQuality;                      // 质量模式标志
    THolder<TDataDecompressor> Decompressor; // 内部解压缩器
};
```

## 算法原理

### 统计分析与码表构建

#### 1. 数据采样
```cpp
// 数据采样过程
void TDataSampler::AddStat(ui32 val) {
    size_t index = HashIndex(val, HashMul);
    if (EntryVal[index] == val || EntryHit[index] == 0) {
        EntryVal[index] = val;
        EntryHit[index]++;
    } else {
        // 处理哈希冲突
        HandleHashCollision(index, val);
    }
    Counter++;
}
```

#### 2. 频率统计
```cpp
// 构建频率表
void BuildFrequencyTable(i64 freqs[65536]) {
    for (size_t i = 0; i < Size; ++i) {
        if (EntryHit[i] > 0) {
            freqs[EntryVal[i]] = EntryHit[i];
        }
    }
}
```

#### 3. 霍夫曼编码生成
```cpp
// 分层霍夫曼编码构建
bool TCompressorTable::BuildHuffCodes(i64 totalFreq, i64 freqs[65536], i64 add) {
    TVector<NCompProto::TCode> codes;

    // 定义编码层: 0, 1, 2, 4, 8, 10, 12, 14, 16, 32 位
    size_t bits[] = {0, 1, 2, 4, 8, 10, 12, 14, 16, 32};

    for (size_t i = 0; i < 9; ++i) {
        size_t size = 1 << bits[i];
        ui32 weight = CalculateWeight(freqs, offset, size);
        codes.push_back(NCompProto::TCode(weight + add, offset, bits[i]));
    }

    // 构建霍夫曼树
    return NCompProto::BuildHuff(codes);
}
```

### 压缩编码过程

#### 1. 值到编码映射
```cpp
void TCompressorTable::GetHuffCode(ui32 value, ui64& bitCode, ui8& bitLength) const {
    // 查找对应的编码层
    for (auto huffCode : HuffCodes) {
        if (huffCode.MinValue <= value && value < huffCode.MaxValue()) {
            // 生成前缀编码
            ui64 code = value - huffCode.MinValue;
            bitCode = (code << huffCode.PrefixBits) | huffCode.Prefix;
            bitLength = huffCode.AllBits;
            return;
        }
    }
}
```

#### 2. 位级压缩
```cpp
// 位级数据压缩
void CompressValue(ui32 value, TBitBuffer& buffer) {
    ui64 bitCode;
    ui8 bitLength;

    table.GetHuffCode(value, bitCode, bitLength);
    buffer.WriteBits(bitCode, bitLength);
}
```

## 使用示例

### 基本压缩流程
```cpp
#include <library/cpp/comptable/comptable.h>
using namespace NCompTable;

// 1. 创建数据采样器
TDataSampler sampler;

// 2. 收集数据统计信息
TVector<TString> data = {/* 数据集 */};
for (const auto& item : data) {
    sampler.AddStat(item);
}

// 3. 构建压缩表
TCompressorTable table;
sampler.BuildTable(table);

// 4. 创建压缩器
TChunkCompressor compressor(true, table);  // 高质量模式

// 5. 压缩数据
TVector<char> compressed;
for (const auto& item : data) {
    compressor.Compress(item, &compressed);
}
```

### 解压缩操作
```cpp
// 创建解压缩器
TChunkDecompressor decompressor(true, table);

// 解压缩数据
TVector<char> decompressed;
TStringBuf compressedData(compressed.data(), compressed.size());
decompressor.Decompress(compressedData, &decompressed);

// 验证结果
assert(decompressed.size() == originalData.size());
assert(memcmp(decompressed.data(), originalData.data(), originalData.size()) == 0);
```

### 性能测试示例
```cpp
// 性能基准测试
template <bool HQ>
void PerformanceTest(const TCompressorTable& table,
                    const TVector<TString>& testData) {
    TChunkCompressor compressor(HQ, table);
    TChunkDecompressor decompressor(HQ, table);

    size_t originalSize = 0;
    size_t compressedSize = 0;
    TSimpleTimer timer;

    for (const auto& data : testData) {
        TVector<char> compressed;
        TVector<char> decompressed;

        // 压缩
        compressor.Compress(data, &compressed);
        originalSize += data.size();
        compressedSize += compressed.size();

        // 解压缩验证
        TStringBuf compressedBuf(compressed.data(), compressed.size());
        decompressor.Decompress(compressedBuf, &decompressed);

        assert(decompressed == TString(data));
    }

    double elapsed = timer.Get();
    double throughput = originalSize / (1024.0 * 1024.0) / elapsed;
    double ratio = double(originalSize) / double(compressedSize);

    Cout << "吞吐量: " << throughput << " MB/s" << Endl;
    Cout << "压缩比: " << ratio << ":1" << Endl;
}
```

### 自定义数据类型处理
```cpp
// 处理结构化数据
struct MyStruct {
    ui32 Id;
    ui32 Value;
    ui64 Timestamp;
};

// 提取特征用于压缩
void ExtractFeatures(const MyStruct& data, TDataSampler& sampler) {
    sampler.AddStat(data.Id);
    sampler.AddStat(data.Value);
    sampler.AddStat(ui32(data.Timestamp & 0xFFFFFFFF));
    sampler.AddStat(ui32(data.Timestamp >> 32));
}
```

## 性能特性

### 压缩效率
- **高压缩比**: 对于具有重复模式的数据可达 5:1 到 15:1
- **快速处理**: 支持每秒数百 MB 的处理速度
- **自适应优化**: 根据数据特征自动调整策略

### 内存使用
- **低内存占用**: 采样器使用约 2MB 内存
- **缓存友好**: 优化的内存访问模式
- **线性扩展**: 内存使用与数据量成线性关系

### 处理速度
- **快速模式**: 优化的速度，适中的压缩比
- **高质量模式**: 更好的压缩比，合理的速度
- **批量处理**: 高效的批量数据操作

## 应用场景

### 1. 日志压缩
- Web 服务器日志压缩
- 应用程序日志存储
- 系统监控数据压缩

### 2. 数据库存储
- 列式存储压缩
- 索引数据压缩
- 备份数据压缩

### 3. 网络传输
- 数据传输优化
- 缓存数据压缩
- 消息队列优化

### 4. 文件系统
- 文件内容压缩
- 元数据压缩
- 版本控制系统

## 最佳实践

### 1. 数据预处理
```cpp
// 优化数据以提高压缩效果
void OptimizeData(TVector<TString>& data) {
    // 排序以获得更好的局部性
    Sort(data.begin(), data.end());

    // 去重减少冗余
    data.erase(Unique(data.begin(), data.end()), data.end());

    // 标准化格式
    for (auto& item : data) {
        NormalizeString(item);
    }
}
```

### 2. 采样策略
```cpp
// 智能采样策略
void SmartSampling(TDataSampler& sampler, const TVector<TString>& data) {
    // 分层采样
    size_t step = Max<size_t>(1, data.size() / 100000);  // 最多采样 10 万条

    for (size_t i = 0; i < data.size(); i += step) {
        sampler.AddStat(data[i]);
    }

    // 添加边界情况
    if (!data.empty()) {
        sampler.AddStat(data.front());
        sampler.AddStat(data.back());
    }
}
```

### 3. 模式选择
```cpp
// 根据场景选择压缩模式
bool SelectCompressionMode(const TVector<TString>& data) {
    size_t totalSize = 0;
    for (const auto& item : data) {
        totalSize += item.size();
    }

    // 小数据或实时处理用快速模式
    if (totalSize < 1024 * 1024) {  // 1MB
        return false;  // 快速模式
    }

    // 存储优化用高质量模式
    return true;  // 高质量模式
}
```

### 4. 错误处理
```cpp
// 健壮的压缩处理
bool SafeCompress(const TCompressorTable& table,
                 const TString& data,
                 TVector<char>* result) {
    try {
        TChunkCompressor compressor(true, table);
        compressor.Compress(data, result);
        return true;
    } catch (const std::exception& e) {
        Cerr << "压缩失败: " << e.what() << Endl;
        // 回退到原始数据
        result->assign(data.begin(), data.end());
        return false;
    }
}
```

## 实现细节

### 哈希优化
```cpp
// 快速哈希函数
size_t HashIndex(ui32 value, ui32 hashMul) {
    return (value * hashMul) >> (32 - hashSizeLog);
}

// 哈希冲突处理
void HandleHashCollision(size_t index, ui32 value) {
    // 线性探测
    for (size_t i = 1; i < Size; ++i) {
        size_t newIndex = (index + i) & (Size - 1);
        if (EntryVal[newIndex] == value || EntryHit[newIndex] == 0) {
            EntryVal[newIndex] = value;
            EntryHit[newIndex]++;
            break;
        }
    }
}
```

### 编码优化
```cpp
// 位操作优化
inline void WriteOptimized(ui64 value, ui8 bits, TBitBuffer& buffer) {
    // 检查是否可以快速写入
    if (buffer.CanWriteFast(bits)) {
        buffer.WriteFast(value, bits);
    } else {
        buffer.WriteSlow(value, bits);
    }
}
```

### 内存对齐
```cpp
// 确保结构体对齐
struct alignas(64) TAlignedCompressorTable : public TCompressorTable {
    // 缓存行对齐，提高访问效率
};
```

## 版本兼容性

### 序列化支持
```cpp
// 支持表的序列化
template <>
class TSerializer<NCompTable::TCompressorTable> {
public:
    static void Save(IOutputStream* out, const TCompressorTable& table);
    static void Load(IInputStream* in, TCompressorTable& table);
};
```

### 向后兼容
- 保持压缩表格式稳定
- 支持旧版本数据读取
- 渐进式功能升级

## 测试覆盖

### 正确性测试
- 压缩/解压缩一致性验证
- 边界条件处理
- 错误输入处理

### 性能测试
- 不同数据类型的压缩比
- 处理速度基准测试
- 内存使用效率分析

### 压力测试
- 大数据量处理能力
- 长时间运行稳定性
- 并发安全性验证

## 限制与注意事项

### 使用限制
- 最小数据量要求（统计准确性）
- 内存使用与数据特征相关
- 某些随机数据压缩效果有限

### 性能考虑
- 表构建时间开销
- 内存访问模式优化
- 缓存未命中的影响

## 总结

CompTable 压缩表库为 YTsaurus 系统提供了强大而灵活的数据压缩能力。通过智能的统计分析、分层编码和性能优化，该库能够在保持高处理速度的同时实现优秀的压缩效果。

该库特别适合处理具有统计规律的大规模数据集，是数据存储和传输优化的重要工具。通过合理使用其提供的各种功能和配置选项，开发者可以根据具体应用场景获得最佳的压缩性能。