# 纠删码（Erasure Code）编解码库

基于纠删码的数据保护和容错编解码库，支持 LRC 和 Reed-Solomon 编码。

## 概述

该库提供了基于纠删码的数据编解码功能，能够为数据块生成校验块，并在部分数据丢失时恢复原始数据。支持两种主要的编码算法：LRC（Locally Repairable Code）和 Reed-Solomon 编码。

## 核心特性

### 编码算法
- **LRC 编码**: 本地可修复编码，支持快速局部修复
- **Reed-Solomon 编码**: 经典的纠删码算法，提供强大的容错能力
- **多后端支持**: 支持 Jerasure 和 Intel ISA-L 优化实现

### 性能优化
- **ISA-L 加速**: Intel ISA-L 库的高性能 SIMD 优化
- **指令集适配**: 自动适配 SSE4.2、AVX2 等指令集
- **多线程安全**: 线程安全的编解码操作

### 灵活配置
- **可配置参数**: 支持自定义数据块和校验块数量
- **模板设计**: 支持不同的数据类型
- **流式处理**: 支持任意数据流处理

## 编码类型

### LRC 编码（Locally Repairable Code）
- **配置**: LRC 2k-2-2（2个全局校验块，2个本地校验块）
- **特点**: 快速局部修复，适合分布式存储
- **适用**: 大规模分布式文件系统

### Reed-Solomon 编码
- **配置**: Reed-Solomon n-k（n个总块，k个数据块）
- **特点**: 高可靠性，数学理论成熟
- **适用**: 关键数据保护

## 主要组件

### 核心接口
```cpp
template <class TBlobType>
struct ICodec {
    // 编码：从数据块生成校验块
    virtual std::vector<TBlobType> Encode(const std::vector<TBlobType>& blocks) const = 0;

    // 解码：恢复丢失的块
    virtual std::vector<TBlobType> Decode(
        const std::vector<TBlobType>& blocks,
        const TPartIndexList& erasedIndices) const = 0;

    // 检查是否可以修复
    virtual bool CanRepair(const TPartIndexList& erasedIndices) const = 0;

    // 获取修复所需的块索引
    virtual std::optional<TPartIndexList> GetRepairIndices(const TPartIndexList& erasedIndices) const = 0;
};
```

### 参数配置
```cpp
// 编码参数
virtual int GetDataPartCount() const = 0;              // 数据块数量
virtual int GetParityPartCount() const = 0;            // 校验块数量
virtual int GetGuaranteedRepairablePartCount() const = 0; // 可修复的最大块数
virtual int GetWordSize() const = 0;                  // 字大小
```

## 使用示例

### 基本 LRC 编解码
```cpp
#include <erasure/codec.h>
#include <erasure/lrc.h>

using namespace NErasure;

// 创建 LRC 编解码器（2k-2-2 配置）
TLrcCodec<TBlobType> codec(4, 2, 2); // 4个数据块，2个全局校验，2个本地校验

// 编码数据
std::vector<TBlobType> dataBlocks = {
    CreateBlob("data1"),
    CreateBlob("data2"),
    CreateBlob("data3"),
    CreateBlob("data4")
};

auto parityBlocks = codec.Encode(dataBlocks);
// 现在有 8 个块：4个数据块 + 4个校验块
```

### 数据恢复
```cpp
// 模拟数据丢失
TPartIndexList lostIndices = {0, 3}; // 丢失第1和第4个块
std::vector<TBlobType> remainingBlocks;

// 收集剩余的块
for (int i = 0; i < codec.GetTotalPartCount(); ++i) {
    if (std::find(lostIndices.begin(), lostIndices.end(), i) == lostIndices.end()) {
        remainingBlocks.push_back(GetBlock(i));
    }
}

// 检查是否可以修复
if (codec.CanRepair(lostIndices)) {
    // 获取修复所需的块索引
    auto repairIndices = codec.GetRepairIndices(lostIndices);

    // 提取所需的块
    std::vector<TBlobType> repairBlocks;
    for (int idx : *repairIndices) {
        repairBlocks.push_back(remainingBlocks[idx]);
    }

    // 执行修复
    auto recoveredBlocks = codec.Decode(repairBlocks, lostIndices);
}
```

### Reed-Solomon 编解码
```cpp
#include <erasure/reed_solomon.h>

// 创建 Reed-Solomon 编解码器（6+2 配置）
TReedSolomonCodec<TBlobType> codec(6, 2); // 6个数据块，2个校验块

// 编码和恢复过程与 LRC 类似
auto parity = codec.Encode(dataBlocks);
auto recovered = codec.Decode(availableBlocks, lostIndices);
```

## 实现后端

### Intel ISA-L 后端
- **高性能**: 使用 SIMD 指令优化
- **指令集支持**: SSE4.2、AVX2、AVX512
- **跨平台**: 支持 x86_64 和部分 ARM64
- **限制**: 仅支持 WordSize = 8

### Jerasure 后端
- **兼容性**: 广泛的平台支持
- **灵活性**: 支持不同的 WordSize
- **性能**: 相对较慢但稳定
- **线程安全**: 大 WordSize 时需要注意线程安全

## 性能优化

### CPU 指令集优化
```cpp
// ISA-L 会自动选择最优实现
if (HasSSE42()) {
    // 使用 SSE4.2 优化版本
} else if (HasAVX2()) {
    // 使用 AVX2 优化版本
} else {
    // 使用基础实现
}
```

### 内存优化
- **对齐访问**: 确保数据按字大小对齐
- **批量处理**: 批量处理多个数据块
- **缓存友好**: 优化内存访问模式

## 应用场景

### 分布式存储
- **文件系统**: 分布式文件系统的数据冗余
- **对象存储**: 云存储的数据保护
- **备份系统**: 高效的数据备份和恢复

### 数据库系统
- **数据冗余**: 数据库副本的容错保护
- **日志保护**: WAL 日志的可靠性保证
- **快照备份**: 高效的数据快照

### 网络传输
- **可靠传输**: 不可靠网络上的可靠数据传输
- **广播通信**: 一对多的可靠数据分发
- **卫星通信**: 高延迟网络的容错传输

## 最佳实践

### 编码选择
```cpp
// 根据应用场景选择合适的编码
if (needFastLocalRepair) {
    // 使用 LRC，适合快速局部修复
    TLrcCodec<TBlobType> codec(dataBlocks, globalParity, localParity);
} else if (needMaximumReliability) {
    // 使用 Reed-Solomon，提供最大可靠性
    TReedSolomonCodec<TBlobType> codec(dataBlocks, parityBlocks);
}
```

### 性能优化
```cpp
// 使用合适的 WordSize
constexpr int wordSize = 8; // ISA-L 的最优配置

// 确保数据块大小对齐
size_t blockSize = ((dataSize + wordSize - 1) / wordSize) * wordSize;

// 批量处理以提高缓存效率
for (size_t i = 0; i < dataBlocks.size(); i += batchSize) {
    ProcessBatch(dataBlocks, i, batchSize);
}
```

### 错误处理
```cpp
// 检查修复可能性
if (!codec.CanRepair(lostIndices)) {
    throw std::runtime_error("数据丢失过多，无法修复");
}

// 验证修复结果
auto recovered = codec.Decode(availableBlocks, lostIndices);
ValidateRecovery(recovered, originalData);
```

## 技术细节

### LRC 编码结构
- **全局校验**: 跨所有数据块的校验
- **本地校验**: 局部数据块的校验
- **修复策略**: 优先使用本地校验进行快速修复

### Reed-Solomon 编码原理
- **伽罗瓦域**: 基于有限域的数学运算
- **范德蒙德矩阵**: 编码矩阵的构建
- **系统编码**: 数据块在编码后保持不变

### 错误检测
- **校验和**: 块级别的完整性检查
- **边界检查**: 防止越界访问
- **数据验证**: 修复后的数据验证

## 平台支持

### x86_64 平台
- **完整支持**: 所有功能和优化
- **ISA-L**: 完整的 SIMD 优化
- **性能**: 最佳性能表现

### ARM64 平台
- **基础支持**: Jerasure 后端
- **ISA-L**: 部分支持（2.29+ 版本）
- **性能**: 基础性能表现

### 其他平台
- **兼容模式**: Jerasure 后端
- **功能完整**: 所有编码算法支持
- **性能**: 基础性能

## 依赖库

### Intel ISA-L
- **官网**: https://github.com/intel/isa-l
- **版本**: 2.29+ 推荐
- **功能**: SIMD 优化的纠删码实现

### Jerasure
- **官网**: http://jerasure.org
- **版本**: 稳定版本
- **功能**: 通用纠删码库

## 注意事项

1. **内存对齐**: 确保数据块按字大小对齐
2. **线程安全**: 注意大 WordSize 时的线程安全问题
3. **性能考虑**: ISA-L 在支持的平台上性能更优
4. **错误处理**: 始终检查编码和解码的返回结果
5. **数据一致性**: 修复后验证数据的完整性

## 相关文档

- [YTsaurus Erasure Code 文档](https://wiki.yandex-team.ru/yt/userdoc/erasure/)
- [编码算法设计](https://wiki.yandex-team.ru/ignatijjkolesnichenko/yt/erasure/)
- [Intel ISA-L 文档](https://github.com/intel/isa-l)
- [Jerasure 库文档](http://jerasure.org)