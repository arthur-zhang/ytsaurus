# CompProto 压缩协议库

## 项目描述

CompProto 是 YTsaurus 中的高性能数据压缩协议库，专门用于结构化数据的压缩存储和传输。该库实现了基于霍夫曼编码的压缩算法，结合了元数据管理和位级操作优化，为 YTsaurus 系统提供高效的数据压缩能力。

该库特别适用于具有重复模式的结构化数据压缩，能够显著减少存储空间占用和网络传输开销。

## 核心特性

### 🚀 高性能压缩
- 基于优化的霍夫曼编码算法
- 位级精确的压缩操作
- 内存友好的实现设计

### 📊 元数据管理
- 支持复杂的数据结构描述
- 灵活的字段类型定义
- 自动优化压缩策略

### 🔧 位级操作
- 高效的位缓冲区管理
- 支持变长编码
- 优化的内存访问模式

### 💾 缓存优化
- 内置智能缓存机制
- 减少重复计算开销
- 提高解压缩性能

## 主要组件

### 1. 压缩器核心 (TTable)
```cpp
struct TTable {
    ui32 CodeBase[64];      // 编码基址
    ui32 CodeMask[64];      // 编码掩码
    ui8 Length[64];         // 编码长度
    ui8 PrefLength[64];     // 前缀长度
    ui8 Id[64];             // 标识符

    // 高性能解压缩函数
    ui32 Decompress(const ui8* codes, ui64& offset) const;
};
```

#### 功能特点
- 支持 64 个编码表项
- 优化的内存布局
- 边界安全检查（支持 Valgrind 和 AddressSanitizer）
- 快速位级解压缩

### 2. 元数据管理 (TMetaInfo)
```cpp
template <class X>
struct TMetaInfo {
    X Index;                           // 索引信息
    X Count;                           // 计数信息
    X Mask;                            // 掩码信息
    X Scalar[MAX_ELEMENTS];            // 标量字段
    TAtomicSharedPtr<TMetaInfo> Repeated[MAX_ELEMENTS]; // 重复字段
    TScalarDefaultValue Default[MAX_ELEMENTS];          // 默认值

    ui32 ScalarMask;                   // 标量掩码
    ui32 RepeatedMask;                 // 重复字段掩码
    size_t Size;                       // 结构大小
    TString Name;                      // 名称
    TString ChildName[MAX_ELEMENTS];   // 子字段名称
    size_t Id;                         // ID
    TMetaInfo* Parent;                 // 父节点指针
};
```

#### 支持的元素类型
- **标量字段**: 固定大小的基本类型
- **重复字段**: 数组或列表类型
- **默认值**: 自动处理的缺失数据
- **层次结构**: 支持嵌套数据结构

### 3. 霍夫曼编码 (THuff)
```cpp
template <size_t CacheSize, typename TEntry>
struct TCache {
    ui32 CacheKey[CacheSize];
    TEntry CacheVal[CacheSize];
    size_t Hits;
    size_t Misses;

    ui32 Hash(ui32 key);
    void Clear();
};

struct TCode {
    i64 Probability;      // 概率权重
    ui32 Start;          // 起始位置
    ui32 Bits;           // 位数
    ui32 Prefix;         // 前缀
    ui32 PrefLength;     // 前缀长度
};
```

#### 编码特性
- 基于概率的自适应编码
- 智能缓存机制
- 优化的码表生成

### 4. 位缓冲区 (TBitBuffer)
```cpp
struct TBitBuffer {
    TVector<ui8> Out;     // 输出缓冲区
    ui64 Position;        // 当前位置
    ui64 Size;            // 缓冲区大小
    ui8 Counter;          // 计数器

    // 位级操作函数
    static ui64 Read(const ui8* out, ui64 position, size_t size);
    ui64 Read(ui64 position, size_t size);
    void Code(ui64 value, size_t size);
    ui64 Code(ui64 value, size_t size, ui64 position);
    void Junk(size_t junk = 1024);
};
```

#### 缓冲区特点
- 动态大小调整
- 位级精确操作
- 内存使用优化

## 算法原理

### 霍夫曼编码优化
库使用改进的霍夫曼编码算法：

#### 1. 概率统计
```cpp
// 统计数据出现概率
void BuildFrequencyTable(const TDataVector& data);
```

#### 2. 码表生成
```cpp
// 生成最优编码表
void GenerateCodeTable(TVector<TCode>& codes);
```

#### 3. 压缩优化
```cpp
// 使用优化的编码表进行压缩
ui32 CompressData(const ui8* input, ui8* output, size_t size);
```

### 位级压缩策略
- **前缀编码**: 使用变长前缀减少冗余
- **块对齐**: 优化内存访问模式
- **缓存友好**: 减少缓存未命中

## 使用示例

### 基本压缩操作
```cpp
#include <library/cpp/compproto/compressor.h>
#include <library/cpp/compproto/metainfo.h>
#include <library/cpp/compproto/huff.h>

using namespace NCompProto;

// 创建压缩表
TTable table;

// 准备压缩数据
TVector<ui8> inputData = {/* ... */};
TBitBuffer outputBuffer;

// 压缩数据
for (size_t i = 0; i < inputData.size(); ++i) {
    ui32 code = table.Encode(inputData[i]);
    outputBuffer.Code(code, table.Length[inputData[i]]);
}
```

### 元数据配置
```cpp
// 定义数据结构元信息
TMetaInfo<ui32> metaInfo;

// 配置标量字段
metaInfo.Scalar[0] = 42;        // 字段值
metaInfo.Default[0].Type = TScalarDefaultValue::Fixed;
metaInfo.Default[0].Value = 0;   // 默认值

// 配置重复字段
metaInfo.Repeated[0] = MakeAtomicShared<TMetaInfo<ui32>>();
metaInfo.Repeated[0]->Count = 10;

// 设置掩码
metaInfo.ScalarMask = 0x1;
metaInfo.RepeatedMask = 0x1;
```

### 缓存使用
```cpp
// 创建缓存
TCache<256, ui32> cache;

// 使用缓存查找
ui32 key = someKey;
ui32 value;
if (cache.Lookup(key, value)) {
    // 缓存命中
    return value;
} else {
    // 缓存未命中，计算并缓存
    value = ComputeValue(key);
    cache.Store(key, value);
    return value;
}
```

### 解压缩操作
```cpp
// 解压缩数据
ui64 offset = 0;
TVector<ui32> decompressedData;

while (offset < outputBuffer.Size) {
    ui32 value = table.Decompress(&outputBuffer.Out[0], offset);
    decompressedData.push_back(value);
}
```

## 性能特性

### 压缩效率
- **高压缩比**: 对于重复模式数据可达 10:1 以上
- **快速压缩**: 优化的位操作算法
- **内存效率**: 最小化内存分配

### 解压缩性能
- **O(1) 解码**: 常数时间解压缩
- **缓存优化**: 减少内存访问延迟
- **向量化**: 支持 SIMD 优化

### 内存使用
- **紧凑存储**: 位级精确的数据表示
- **智能预分配**: 动态缓冲区管理
- **内存池**: 减少分配开销

## 应用场景

### 1. 数据存储优化
- 减少磁盘存储空间
- 提高缓存命中率
- 优化数据传输

### 2. 网络传输
- 减少网络带宽占用
- 提高传输速度
- 降低延迟

### 3. 内存数据库
- 减少内存使用
- 提高查询性能
- 优化缓存效率

### 4. 日志压缩
- 压缩历史日志数据
- 提高存储效率
- 加速日志分析

## 最佳实践

### 1. 数据预处理
```cpp
// 确保数据适合压缩
void PrepareData(TVector<ui8>& data) {
    // 排序以提高压缩效率
    Sort(data.begin(), data.end());

    // 去重以减少冗余
    data.erase(Unique(data.begin(), data.end()), data.end());
}
```

### 2. 缓存配置
```cpp
// 根据使用模式调整缓存大小
const size_t CACHE_SIZE = 1024;  // 对于频繁访问的数据
const size_t SMALL_CACHE = 64;   // 对于偶发访问的数据
```

### 3. 错误处理
```cpp
try {
    // 压缩操作
    ui32 result = table.Decompress(data, offset);
} catch (const yexception& e) {
    // 处理解压缩错误
    Cerr << "Decompression failed: " << e.what() << Endl;
    throw;
}
```

### 4. 性能调优
```cpp
// 批量处理以提高效率
void BatchCompress(const TVector<TVector<ui8>>& batches) {
    for (const auto& batch : batches) {
        // 预分配内存
        outputBuffer.Reserve(batch.size() * 2);

        // 批量压缩
        for (ui8 value : batch) {
            CompressValue(value);
        }
    }
}
```

## 实现细节

### 内存对齐优化
```cpp
// 确保内存访问对齐
struct alignas(64) TAlignedTable : public TTable {
    // 确保缓存行对齐
};
```

### 编译时优化
```cpp
// 使用模板特化优化特定类型
template <>
inline ui32 TTable::DecodeSpecialized<ui8>(const ui8* data) {
    // 针对特定类型的优化实现
}
```

### 调试支持
```cpp
#ifdef DEBUG
    // 添加调试信息
    void DebugPrintState() const;
#endif
```

## 版本兼容性

### 向后兼容
- 保持接口稳定性
- 支持旧格式数据读取
- 渐进式功能升级

### 性能演进
- 持续优化算法效率
- 利用新硬件特性
- 改进内存管理

## 测试覆盖

### 单元测试
- 压缩/解压缩正确性
- 边界条件处理
- 错误情况验证

### 性能测试
- 不同数据类型的压缩比
- 解压缩速度基准测试
- 内存使用效率分析

### 压力测试
- 大数据量处理
- 长时间运行稳定性
- 并发安全性验证

## 限制与注意事项

### 使用限制
- 适合具有重复模式的数据
- 需要预先构建压缩表
- 对随机数据效果有限

### 注意事项
- 确保数据对齐要求
- 监控内存使用情况
- 处理压缩失败的情况

## 总结

CompProto 压缩协议库为 YTsaurus 系统提供了高效的数据压缩能力，通过精心的算法设计和性能优化，实现了出色的压缩比和解压缩速度。该库特别适合处理具有统计特征的结构化数据，是系统性能优化的重要组件。

通过合理使用该库提供的功能，开发者可以显著改善数据存储和传输效率，为构建高性能的大数据处理系统提供强有力的支撑。