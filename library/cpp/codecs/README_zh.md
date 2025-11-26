# Codecs - 高级压缩算法库

## 项目概述

Codecs 是一个功能强大的压缩算法库，提供统一接口的多种压缩算法实现和序列化支持。与 `library/cpp/blockcodecs` 不同，该库专注于提供自适应学习和高级压缩算法，支持静态字典编译，适用于需要优化压缩比的复杂场景。

该库支持多种高级压缩算法，包括：
- **Delta 编码**: 适用于序列数据的差分压缩
- **Huffman 编码**: 基于频率统计的熵编码
- **PFor 编码**: 分段优化整数压缩
- **ZSTD 字典编码**: 使用预训练字典的 ZSTD 压缩
- **Solar 编码**: 专门优化的数值压缩算法
- **组合编码**: 多种算法的管道组合

## 核心功能

### 统一编解码接口
- **ICodec 接口**: 所有编解码器的基础接口
- **编解码操作**: Encode/Decode 方法支持多种输入格式
- **序列化支持**: 编解码器配置的持久化和恢复
- **训练机制**: 支持基于数据分布的自适应优化

### 高级特性
- **自适应学习**: 根据数据特征优化压缩参数
- **管道组合**: 多种算法的链式组合
- **静态字典**: 支持预编译的高效字典
- **性能估算**: 编解码前后的大小预估
- **线程本地存储**: 优化的多线程性能

## 文件说明

### 核心头文件
- **`codecs.h`**: 主要的编解码器接口定义和基础实现
- **`codecs_registry.h`**: 编解码器注册和管理机制
- **`sample.h`**: 数据采样和序列读取接口

### 算法实现
- **`delta_codec.h/cpp`**: Delta 差分编码算法
- **`huffman_codec.h/cpp`**: Huffman 熵编码算法
- **`pfor_codec.h/cpp`**: PFor 分段优化编码
- **`zstd_dict_codec.h/cpp`**: ZSTD 字典压缩
- **`solar_codec.h/cpp`**: Solar 数值压缩算法
- **`comptable_codec.h/cpp`**: 压缩表编码
- **`float_huffman.h/cpp`**: 专门的浮点数 Huffman 编码

### 支持组件
- **`tls_cache.h/cpp`**: 线程本地存储缓存
- **`codecs_registry.cpp`**: 编解码器注册表实现
- **`codecs.cpp`**: 核心编解码操作实现

### 构建配置
- **`ya.make`**: YaTool 构建系统配置

## 核心接口

### ICodec 接口
```cpp
class ICodec {
public:
    // 编码操作
    virtual ui8 Encode(TStringBuf input, TBuffer& output) const = 0;
    virtual void Decode(TStringBuf input, TBuffer& output) const = 0;

    // 学习和训练
    virtual void Learn(ISequenceReader& reader);
    virtual bool NeedsTraining() const;
    virtual bool AlreadyTrained() const;

    // 性能估算
    virtual size_t ApproximateSizeOnEncode(size_t sz) const;
    virtual size_t ApproximateSizeOnDecode(size_t sz) const;

    // 序列化
    virtual void Save(IOutputStream* out) const;
    virtual void Load(IInputStream* in);

    // 元数据
    virtual TString GetName() const = 0;
    virtual TCodecTraits Traits() const;
};
```

### 编解码器特征
```cpp
struct TCodecTraits {
    ui32 RecommendedSampleSize = 0;      // 推荐的训练样本大小
    ui16 SizeOfInputElement = 1;         // 输入元素大小
    ui8 SizeOnEncodeMultiplier = 1;      // 编码大小倍数
    ui8 SizeOnEncodeAddition = 0;        // 编码大小增量
    ui8 SizeOnDecodeMultiplier = 1;      // 解码大小倍数

    bool NeedsTraining = false;          // 是否需要训练
    bool PreservesPrefixGrouping = false; // 是否保持前缀分组
    bool Irreversible = false;           // 是否不可逆
    bool PaddingBit = 0;                 // 填充位
    bool AssumesStructuredInput = false;  // 是否假设结构化输入
};
```

## 使用示例

### 基本编解码
```cpp
#include <library/cpp/codecs/codecs.h>

using namespace NCodecs;

void BasicUsage() {
    // 获取编解码器实例
    TCodecPtr codec = ICodec::GetInstance("delta");

    // 准备数据
    TVector<ui64> data = {100, 105, 110, 115, 120};
    TBuffer input;
    input.Append(data.data(), data.size() * sizeof(ui64));

    // 编码
    TBuffer encoded;
    ui8 paddingBits = codec->Encode(input, encoded);

    // 解码
    TBuffer decoded;
    codec->Decode(encoded, decoded);

    // 验证结果
    Y_ASSERT(decoded.Size() == input.Size());
    Y_ASSERT(memcmp(decoded.Data(), input.Data(), input.Size()) == 0);
}
```

### 自适应训练
```cpp
void TrainingExample() {
    TCodecPtr codec = ICodec::GetInstance("huffman");

    // 准备训练数据
    TVector<TString> trainingData = {
        "hello world",
        "hello there",
        "hello everyone",
        "goodbye world",
        "goodbye all"
    };

    // 训练编解码器
    codec->Learn(trainingData.begin(), trainingData.end());

    // 使用训练后的编解码器
    TString text = "hello universe";
    TBuffer input(text.data(), text.size());
    TBuffer encoded;
    codec->Encode(input, encoded);

    std::cout << "原始大小: " << input.Size() << std::endl;
    std::cout << "压缩后大小: " << encoded.Size() << std::endl;
}
```

### 管道组合
```cpp
void PipelineExample() {
    // 创建管道编解码器
    TCodecPtr delta = ICodec::GetInstance("delta");
    TCodecPtr huffman = ICodec::GetInstance("huffman");

    TPipelineCodec pipeline;
    pipeline.AddCodec(delta)     // 先进行 Delta 编码
               .AddCodec(huffman); // 再进行 Huffman 编码

    // 准备数据
    TVector<ui64> sequence = {100, 101, 102, 103, 104};
    TBuffer input;
    input.Append(sequence.data(), sequence.size() * sizeof(ui64));

    // 压缩
    TBuffer compressed;
    pipeline.Encode(input, compressed);

    // 解压缩
    TBuffer decompressed;
    pipeline.Decode(compressed, decompressed);
}
```

### 序列化编解码器
```cpp
void SerializationExample() {
    // 创建并训练编解码器
    TCodecPtr codec = ICodec::GetInstance("huffman");

    TVector<TString> data = {"apple", "banana", "cherry", "date"};
    codec->Learn(data.begin(), data.end());

    // 序列化编解码器配置
    TStringBuf serialized;
    TBuffer buffer;
    TMemoryOutput output(&buffer);
    ICodec::Store(&output, codec);
    serialized = TStringBuf(buffer.Data(), buffer.Size());

    // 恢复编解码器
    TMemoryInput input(serialized.data(), serialized.size());
    TCodecPtr restored = ICodec::Restore(&input);

    // 验证恢复的编解码器
    Y_ASSERT(restored->GetName() == codec->GetName());
    Y_ASSERT(restored->AlreadyTrained());
}
```

### Delta 编码专门用法
```cpp
void DeltaCodecExample() {
    using namespace NCodecs;

    // 针对 ui64 序列的 Delta 编码
    TDeltaCodec<ui64> deltaCodec;

    // 递增序列数据
    TVector<ui64> sequence;
    for (ui64 i = 1000; i < 2000; i += 10) {
        sequence.push_back(i);
    }

    TBuffer input;
    input.Append(sequence.data(), sequence.size() * sizeof(ui64));

    // 编码
    TBuffer encoded;
    deltaCodec.Encode(input, encoded);

    std::cout << "原始数据大小: " << input.Size() << " 字节" << std::endl;
    std::cout << "Delta 编码后: " << encoded.Size() << " 字节" << std::endl;
    std::cout << "压缩比: " << (double)encoded.Size() / input.Size() << std::endl;

    // 解码
    TBuffer decoded;
    deltaCodec.Decode(encoded, decoded);
}
```

### 性能优化使用
```cpp
void PerformanceOptimizedExample() {
    using namespace NCodecs;

    // 使用推荐样本大小进行训练
    TCodecPtr codec = ICodec::GetInstance("pfor");

    // 获取编解码器特征
    TCodecTraits traits = codec->Traits();
    std::cout << "推荐样本大小: " << traits.RecommendedSampleSize << std::endl;

    // 准备大样本进行训练
    TVector<TString> largeDataset;
    for (int i = 0; i < traits.RecommendedSampleSize; ++i) {
        largeDataset.push_back("sample_data_" + ToString(i));
    }

    // 训练编解码器
    codec->Learn(largeDataset.begin(), largeDataset.end());

    // 使用性能估算功能
    size_t originalSize = 1024 * 1024; // 1MB
    size_t estimatedSize = codec->ApproximateSizeOnEncode(originalSize);

    std::cout << "预估压缩后大小: " << estimatedSize << " 字节" << std::endl;

    // 预分配输出缓冲区
    TBuffer output;
    output.Reserve(estimatedSize);
}
```

## 算法详解

### 1. Delta 编码
适用于有序或递增序列数据的高效压缩：

```cpp
template <typename T = ui64, bool UnsignedDelta = true>
class TDeltaCodec {
    // 处理增量溢出的解码器
    struct TDecoder {
        T Last = 0;
        T Result = 0;
        bool First = true;
        bool Invalid = false;

        bool Decode(TDelta t);
    };
};
```

**适用场景**:
- 时间序列数据
- 递增 ID 序列
- 排序后的数值数据

### 2. Huffman 编码
基于符号频率的熵编码算法：

```cpp
class THuffmanCodec {
    // 频率统计和树构建
    void BuildFrequencyTable(ISequenceReader& reader);
    void BuildHuffmanTree();

    // 编码表生成
    void GenerateCodes();
};
```

**适用场景**:
- 文本数据压缩
- 具有明显偏态分布的数据
- 可重复性高的数据

### 3. PFor 编码
分段优化的整数压缩算法：

```cpp
template <typename T>
class TPForCodec {
    // 分段参数
    ui32 FrameSize = 128;
    ui32 ExceptionsThreshold = 10;

    // 编码优化
    void OptimizeFrame(const T* data, size_t size);
    void HandleExceptions(const T* data, size_t size);
};
```

**适用场景**:
- 大量整数数据
- 具有局部相似性的数据
- 数值范围相对集中的数据

### 4. 管道组合
多种算法的链式组合：

```cpp
class TPipelineCodec {
    TVector<TCodecPtr> Pipeline;

    // 管道处理
    ui8 Encode(TStringBuf in, TBuffer& out) const override;
    void Decode(TStringBuf in, TBuffer& out) const override;

    // 训练协调
    void DoLearnX(ISequenceReader& in, double sampleSizeMult) override;
};
```

**常用组合**:
- Delta + Huffman: 递增序列的高效压缩
- PFor + Huffman: 整数数据的优化压缩
- Custom + ZSTD: 自定义字典的高效压缩

## 注册机制

### 编解码器注册
```cpp
// 自动注册机制
template <typename TCodec>
void RegisterCodec() {
    RegisterCodecFactory(new NPrivate::TInstanceFactory<TCodec>());
}

// 注册所有内置编解码器
void RegisterBuiltinCodecs() {
    RegisterCodec<TDeltaCodec<ui32>>();
    RegisterCodec<TDeltaCodec<ui64>>();
    RegisterCodec<THuffmanCodec>();
    RegisterCodec<TPForCodec<ui32>>();
    RegisterCodec<TSolarCodec>();
    RegisterCodec<TZstdDictCodec>();
    // ... 其他编解码器
}
```

### 动态获取
```cpp
// 通过名称获取编解码器
TCodecPtr codec = ICodec::GetInstance("delta");

// 获取所有可用编解码器列表
TVector<TString> codecs = ICodec::GetCodecsList();
for (const TString& name : codecs) {
    std::cout << "可用编解码器: " << name << std::endl;
}
```

## 性能特性

### 时间复杂度
- **编码**: O(n) - 线性时间处理
- **解码**: O(n) - 线性时间还原
- **训练**: O(n log n) - 需要排序和统计

### 空间复杂度
- **内存使用**: 与数据大小成线性关系
- **编解码器状态**: 通常几 KB 到几 MB
- **训练数据**: 根据推荐样本大小

### 优化策略
- **线程本地存储**: 减少锁竞争
- **内存预分配**: 减少动态分配开销
- **批处理优化**: 提高缓存利用率

## 应用场景

### 1. 数据库系统
```cpp
// 列式存储的压缩
class ColumnCompressor {
public:
    TCodecPtr GetCompressorForColumn(const ColumnMeta& meta) {
        if (meta.IsSequence) {
            return ICodec::GetInstance("delta");
        } else if (meta.HasHighCardinality) {
            return ICodec::GetInstance("huffman");
        } else {
            return ICodec::GetInstance("pfor");
        }
    }
};
```

### 2. 时间序列存储
```cpp
// 时间序列数据压缩
class TimeSeriesCompressor {
    TCodecPtr deltaCodec;
    TCodecPtr huffmanCodec;
    TPipelineCodec pipeline;

public:
    TimeSeriesCompressor() {
        deltaCodec = ICodec::GetInstance("delta");
        huffmanCodec = ICodec::GetInstance("huffman");
        pipeline.AddCodec(deltaCodec).AddCodec(huffmanCodec);
    }

    size_t CompressSeries(const TVector<TimePoint>& series, TBuffer& output) {
        TBuffer input;
        input.Append(series.data(), series.size() * sizeof(TimePoint));
        return pipeline.Encode(input, output);
    }
};
```

### 3. 日志压缩
```cpp
// 日志数据的高效压缩
class LogCompressor {
    TCodecPtr codec;

public:
    LogCompressor() {
        codec = ICodec::GetInstance("huffman");

        // 使用历史日志数据进行训练
        TVector<TString> historicalLogs = LoadHistoricalLogs();
        codec->Learn(historicalLogs.begin(), historicalLogs.end());
    }

    void CompressLogEntry(const TString& entry, TBuffer& compressed) {
        TBuffer input(entry.data(), entry.size());
        codec->Encode(input, compressed);
    }
};
```

### 4. 网络传输优化
```cpp
// 网络数据包压缩
class NetworkCompressor {
    TMap<TString, TCodecPtr> codecRegistry;

public:
    NetworkCompressor() {
        // 为不同类型的数据注册专门的编解码器
        codecRegistry["json"] = CreateTrainedHuffman("data/json_samples.txt");
        codecRegistry["binary"] = ICodec::GetInstance("delta");
        codecRegistry["text"] = ICodec::GetInstance("huffman");
    }

    size_t CompressPacket(const Packet& packet, TBuffer& output) {
        auto it = codecRegistry.find(packet.ContentType);
        if (it != codecRegistry.end()) {
            TBuffer input(packet.Data, packet.Size);
            return it->second->Encode(input, output);
        }
        return packet.Size; // 不压缩
    }
};
```

## 最佳实践

### 1. 编解码器选择
```cpp
// 根据数据特征选择合适的编解码器
TCodecPtr SelectOptimalCodec(const DataCharacteristics& chars) {
    if (chars.IsSortedNumeric) {
        return ICodec::GetInstance("delta");
    } else if (chars.HasSkewedDistribution) {
        return ICodec::GetInstance("huffman");
    } else if (chars.IsIntegerArray) {
        return ICodec::GetInstance("pfor");
    } else {
        return ICodec::GetInstance("huffman"); // 默认选择
    }
}
```

### 2. 训练数据优化
```cpp
// 使用代表性训练数据
void TrainWithRepresentativeData(TCodecPtr codec, const DataStats& stats) {
    TVector<TString> samples;

    // 根据统计特征生成训练样本
    if (stats.HasPatterns) {
        samples = GeneratePatternBasedSamples(stats);
    } else {
        samples = LoadRandomSamples(stats.RecommendedSampleSize);
    }

    codec->Learn(samples.begin(), samples.end());
}
```

### 3. 性能监控
```cpp
// 编解码性能监控
class CodecPerformanceMonitor {
    struct Metrics {
        size_t OriginalSize = 0;
        size_t CompressedSize = 0;
        TDuration EncodeTime;
        TDuration DecodeTime;
    };

public:
    Metrics MeasureCodec(TCodecPtr codec, const TVector<TString>& data) {
        Metrics metrics;

        // 测量编码性能
        auto start = TInstant::Now();
        for (const auto& item : data) {
            TBuffer input(item.data(), item.size());
            TBuffer output;
            codec->Encode(input, output);
            metrics.OriginalSize += input.Size();
            metrics.CompressedSize += output.Size();
        }
        metrics.EncodeTime = TInstant::Now() - start;

        // 测量解码性能（类似实现）

        return metrics;
    }
};
```

### 4. 错误处理
```cpp
// 健壮的错误处理
class SafeCodecOperations {
public:
    static bool SafeEncode(TCodecPtr codec, TStringBuf input, TBuffer& output) {
        try {
            codec->Encode(input, output);
            return true;
        } catch (const TCodecException& e) {
            Cerr << "编码失败: " << e.what() << Endl;
            output.Assign(input.data(), input.size()); // 降级到不压缩
            return false;
        }
    }

    static bool SafeDecode(TCodecPtr codec, TStringBuf input, TBuffer& output) {
        try {
            codec->Decode(input, output);
            return true;
        } catch (const TCodecException& e) {
            Cerr << "解码失败: " << e.what() << Endl;
            return false;
        }
    }
};
```

## 注意事项

### 1. 内存管理
- 编解码器状态占用内存，需要适当释放
- 大数据集处理时注意内存峰值
- 使用线程本地存储避免竞争

### 2. 数据一致性
- 训练数据应与实际数据分布一致
- 定期重新训练以适应数据变化
- 保存编解码器状态用于一致性解码

### 3. 性能权衡
- 训练时间 vs 压缩效果的权衡
- 内存使用 vs 压缩比的权衡
- 编解码速度 vs 压缩比的权衡

### 4. 兼容性
- 注意不同版本间的编解码器兼容性
- 序列化的编解码器配置需要版本控制
- 测试边界条件和异常情况

这个库为 YTsaurus 系统提供了高效的自适应压缩能力，特别适用于需要优化存储和传输性能的大数据场景。通过统一的接口设计和丰富的算法选择，可以根据不同数据特征选择最优的压缩策略。