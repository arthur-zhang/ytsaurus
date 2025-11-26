# Erasure Coding (纠删码)

纠删码是 YTsaurus 中实现数据冗余和容错的核心技术，通过编码算法将数据分割成多个块，并生成校验块以支持数据恢复。

## 概述

纠删码系统提供以下核心功能：
- 数据编码和分割
- 校验块生成
- 数据块恢复（修复）
- 多种编码算法支持
- 高效的编解码性能

## 支持的编码器

### 1. Reed-Solomon 编码
- **ReedSolomon_6_3**: 6个数据块 + 3个校验块
  - 容忍最多3个块丢失
  - 存储开销: 50%
  - 适用于读多写少场景

- **ReedSolomon_3_3**: 3个数据块 + 3个校验块
  - 容忍最多3个块丢失
  - 存储开销: 100%
  - 高冗余度，适用于关键数据

### 2. LRC (Locally Repairable Code) 编码
- **Lrc_12_2_2**: 12个数据块 + 2个全局校验块 + 2个局部校验块
  - 容忍最多4个块丢失
  - 支持局部修复，降低修复带宽
  - 适用于大规模分布式存储

### 3. 实现变体
每种编码都有多种实现变体：
- **Jerasure**: 基于 Jerasure 库的实现
- **ISA**: 基于 Intel ISA-L 库的优化实现
- **自定义实现**: YTsaurus 自研的高性能实现

## 核心接口

### ICodec 接口
```cpp
struct ICodec {
    // 获取编码器ID
    virtual ECodec GetId() const = 0;

    // 编码数据块，生成校验块
    virtual std::vector<TSharedRef> Encode(const std::vector<TSharedRef>& blocks) const = 0;

    // 解码/修复缺失的块
    virtual std::vector<TSharedRef> Decode(
        const std::vector<TSharedRef>& blocks,
        const TPartIndexList& erasedIndices) const = 0;

    // 检查是否可以修复
    virtual bool CanRepair(const TPartIndexList& erasedIndices) const = 0;
    virtual bool CanRepair(const TPartIndexSet& erasedIndices) const = 0;

    // 获取修复所需的块索引
    virtual std::optional<TPartIndexList> GetRepairIndices(
        const TPartIndexList& erasedIndices) const = 0;

    // 获取数据块数量
    virtual int GetDataPartCount() const = 0;

    // 获取校验块数量
    virtual int GetParityPartCount() const = 0;

    // 获取保证可修复的最大块数
    virtual int GetGuaranteedRepairablePartCount() const = 0;

    // 获取字大小（块大小的对齐要求）
    virtual int GetWordSize() const = 0;

    // 检查是否为按字节编码
    virtual bool IsBytewise() const = 0;
};
```

## 编码器工厂函数
```cpp
// 根据ID查找编码器（返回nullptr如果不支持）
ICodec* FindCodec(ECodec id);

// 根据ID获取编码器（抛出异常如果不支持）
ICodec* GetCodec(ECodec id);

// 获取最有效的等效编码器ID
ECodec GetEffectiveCodecId(ECodec id);

// 获取所有支持的编码器列表
const std::vector<ECodec>& GetSupportedCodecIds();
```

## 使用方法

### 基本编码示例
```cpp
// 获取编码器
auto codec = GetCodec(ECodec::IsaReedSolomon_6_3);

// 准备数据块（6个块）
std::vector<TSharedRef> dataBlocks;
for (int i = 0; i < 6; ++i) {
    dataBlocks.push_back(MakeSharedRef(data[i], size[i]));
}

// 编码生成校验块
auto parityBlocks = codec->Encode(dataBlocks);
// 现在有 6个数据块 + 3个校验块
```

### 数据修复示例
```cpp
// 假设丢失了索引为 1, 4, 8 的块
TPartIndexList erasedIndices = {1, 4, 8};

// 检查是否可以修复
if (codec->CanRepair(erasedIndices)) {
    // 获取修复所需的块
    auto repairIndices = codec->GetRepairIndices(erasedIndices);

    // 收集可用块
    std::vector<TSharedRef> availableBlocks;
    for (int idx : *repairIndices) {
        if (std::find(erasedIndices.begin(), erasedIndices.end(), idx) == erasedIndices.end()) {
            availableBlocks.push_back(blocks[idx]);
        }
    }

    // 执行修复
    auto repairedBlocks = codec->Decode(availableBlocks, erasedIndices);
}
```

## 性能优化

### 1. 实现选择
- **ISA-L**: Intel平台上的最优选择，利用SIMD指令加速
- **Jerasure**: 通用性好，跨平台兼容
- **自定义实现**: 针对YTsaurus场景优化

### 2. 内存优化
- 使用零拷贝技术
- 内存对齐优化
- 批量处理减少开销

### 3. 并行处理
- 编码可并行化
- 修复可利用多线程
- 异步I/O支持

## 应用场景

### 1. 分布式文件系统
- 数据块冗余存储
- 故障节点自动恢复
- 降低存储成本

### 2. 对象存储
- 多副本替代方案
- 耐久性保证
- 降低网络带宽

### 3. 备份系统
- 高效的增量备份
- 快速数据恢复
- 存储空间优化

## 配置建议

### 编码器选择
- **高可靠性需求**: ReedSolomon_3_3
- **平衡性能与可靠性**: ReedSolomon_6_3
- **大规模存储**: Lrc_12_2_2

### 参数调优
- 块大小：建议64KB-1MB
- 并发度：根据CPU核心数调整
- 内存使用：合理配置缓冲区大小

## 依赖项

- YTsaurus 核心库
- Intel ISA-L (可选，用于优化实现)
- Jerasure 库 (可选，用于通用实现)

## 注意事项

1. **块对齐**: 所有块大小必须是字大小的倍数
2. **索引管理**: 正确处理数据块和校验块的索引
3. **错误处理**: 检查修复可行性再执行操作
4. **性能考虑**: 编解码是CPU密集型操作
5. **内存管理**: 注意大块的内存分配和释放