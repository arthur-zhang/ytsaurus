# Skiff Extensions Library (Skiff 扩展库)

## 项目概述 (Overview)

Skiff Extensions Library 是 YTsaurus 中对 Skiff 二进制序列化格式的扩展实现。Skiff 是一种高效的二进制数据格式，专门为大规模数据处理和分布式计算场景设计。该扩展库提供了多表解析、序列化、模式匹配等高级功能，支持高性能的数据读写操作。

该库基于协程实现异步解析，支持多种 Skiff 模式的并发处理，是 YTsaurus 数据处理管道中的关键组件，为表格式数据的序列化和反序列化提供了高效解决方案。

## 核心功能 (Core Features)

### 多表解析器
- **TSkiffMultiTableParser**: 支持多个 Skiff 表的并发解析
- **协程异步处理**: 基于协程的异步数据流处理
- **模式列表支持**: 处理复杂的 Skiff 模式列表
- **列标识管理**: 支持表列标识符的自动管理

### 高性能序列化
- **零拷贝序列化**: 最小化内存拷贝开销
- **批量处理**: 支持批量数据读写操作
- **流式处理**: 流式数据处理，支持大数据量
- **内存优化**: 高效的内存使用和回收

### 模式匹配和验证
- **模式匹配**: 复杂 Skiff 模式的自动匹配
- **类型转换**: 自动类型转换和验证
- **字段描述**: 详细字段信息描述和映射

### 扩展功能
- **范围索引**: 支持数据范围索引列
- **行索引**: 内置行索引支持
- **错误处理**: 完善的错误检测和处理机制

## 主要接口 (Main Interfaces)

### 多表解析器使用

```cpp
#include <yt/yt/library/skiff_ext/parser.h>

class TMySkiffConsumer
{
public:
    void OnRowStart(int tableIndex)
    {
        std::cout << "开始处理表 " << tableIndex << " 的行" << std::endl;
    }

    void OnField(const TString& fieldName, const TSkiffValue& value)
    {
        std::cout << "字段 " << fieldName << ": " << value.ToString() << std::endl;
    }

    void OnRowEnd()
    {
        std::cout << "行处理完成" << std::endl;
    }
};

void ProcessSkiffData()
{
    TMySkiffConsumer consumer;

    // 定义 Skiff 模式
    NSkiff::TSkiffSchemaList schemaList = {
        NSkiff::CreateSimpleSchema({
            NSkiff::CreateTupleSchema({
                NSkiff::CreateInt64Schema(),
                NSkiff::CreateStringSchema(),
            })
        })
    };

    // 表列标识符
    std::vector<TSkiffTableColumnIds> tablesColumnIds = {
        {0, 1}  // 列索引映射
    };

    // 创建解析器
    TSkiffMultiTableParser<TMySkiffConsumer> parser(
        &consumer,
        schemaList,
        tablesColumnIds,
        "range_index",  // 范围索引列名
        "row_index"     // 行索引列名
    );

    // 处理数据
    TString data = ReadSkiffDataFromFile("data.skiff");
    parser.Read(data);
    parser.Finish();

    std::cout << "读取字节数: " << parser.GetReadBytesCount() << std::endl;
}
```

### 序列化接口

```cpp
#include <yt/yt/library/skiff_ext/serialize.h>

void SerializeSkiffValue()
{
    NSkiff::EWireType wireType = NSkiff::EWireType::Int64;

    // 序列化到 Yson
    NYT::NYson::TYsonWriter writer(&std::cout);
    NSkiff::Serialize(wireType, &writer);

    // 从 Yson 反序列化
    NYT::NYTree::INodePtr node = NYT::NYTree::ConvertToNode(42);
    NSkiff::EWireType deserializedType;
    NSkiff::Deserialize(deserializedType, node);
}

void SerializeFromPullParser()
{
    TString ysonData = "42";
    NYT::NYson::TYsonPullParser parser(ysonData);
    NYT::NYson::TYsonPullParserCursor cursor(&parser);

    NSkiff::EWireType wireType;
    NSkiff::Deserialize(wireType, &cursor);
}
```

### 模式匹配使用

```cpp
#include <yt/yt/library/skiff_ext/schema_match.h>

bool ValidateSkiffSchema(const NSkiff::TSkiffSchemaPtr& schema)
{
    try {
        // 验证模式兼容性
        ValidateSchemaCompatibility(schema, expectedSchema_);

        // 检查字段类型
        auto fieldInfo = GetFieldInfo(schema, "my_field");
        if (fieldInfo.Type != NSkiff::EWireType::String) {
            return false;
        }

        return true;
    } catch (const std::exception& ex) {
        std::cerr << "模式验证失败: " << ex.what() << std::endl;
        return false;
    }
}
```

## 使用方法 (Usage)

### 基本使用流程

1. **定义消费者接口**
```cpp
class TMyConsumer
{
public:
    void OnRowStart(int tableIndex);
    void OnField(int fieldIndex, const TSkiffValue& value);
    void OnRowEnd();
    void OnTableEnd(int tableIndex);
};
```

2. **创建解析器**
```cpp
TSkiffMultiTableParser<TMyConsumer> parser(
    &consumer,
    schemaList,
    tablesColumnIds,
    rangeIndexColumnName,
    rowIndexColumnName
);
```

3. **处理数据流**
```cpp
while (hasMoreData) {
    TString chunk = ReadNextChunk();
    parser.Read(chunk);
}
parser.Finish();
```

### 高级功能使用

#### 自定义字段处理
```cpp
class TCustomConsumer
{
private:
    std::unique_ptr<NSkiff::TSkiffDecoder> decoder_;

public:
    TCustomConsumer()
    {
        decoder_ = NSkiff::CreateDecoder(someSchema);
    }

    void OnField(int fieldIndex, const TSharedRef& data)
    {
        auto value = decoder_->Decode(fieldIndex, data);
        ProcessFieldValue(fieldIndex, value);
    }
};
```

#### 错误处理和恢复
```cpp
try {
    parser.Read(dataChunk);
} catch (const NSkiff::TSkiffException& ex) {
    std::cerr << "Skiff 解析错误: " << ex.what() << std::endl;

    // 尝试恢复
    if (CanRecoverFromError(ex)) {
        parser.SkipToNextRow();
    } else {
        throw;
    }
}
```

## 性能考虑 (Performance Considerations)

### 内存优化
- **协程管道**: 使用协程管道实现零拷贝数据传递
- **内存池**: 预分配内存池减少动态分配开销
- **批量处理**: 批量处理数据减少函数调用开销

### 并发处理
- **异步解析**: 协程实现异步解析，提高吞吐量
- **多表并发**: 支持多个表的并发解析处理
- **流水线处理**: 解析和消费可以并行进行

### I/O 优化
- **流式读取**: 支持流式读取，避免大内存占用
- **缓冲机制**: 内置缓冲机制减少系统调用
- **预读取**: 支持数据预读取提高缓存命中率

## 最佳实践 (Best Practices)

### 数据处理
1. **批量消费**: 实现批量消费接口减少回调开销
2. **内存复用**: 复用数据结构减少内存分配
3. **错误边界**: 实现适当的错误边界处理
4. **流控制**: 实现背压控制防止内存溢出

### 模式设计
1. **模式验证**: 在解析前验证模式兼容性
2. **类型映射**: 建立清晰的类型映射关系
3. **向后兼容**: 保持模式的向后兼容性
4. **版本控制**: 实现模式版本控制机制

### 性能优化
1. **预热阶段**: 预热解析器和消费者
2. **内存预分配**: 预分配数据结构减少运行时分配
3. **批处理大小**: 根据系统特点调整批处理大小
4. **监控指标**: 监控解析性能和资源使用

### 错误处理
1. **异常安全**: 确保异常安全的数据处理
2. **错误恢复**: 实现错误恢复机制
3. **日志记录**: 详细记录解析错误信息
4. **状态检查**: 定期检查解析器状态

## 依赖项 (Dependencies)

### 核心依赖
- **library/cpp/skiff**: Skiff 核心库
- **yt/yt/core/ytree**: Yson 结构处理
- **yt/yt/core/yson**: Yson 序列化支持
- **yt/yt/core/concurrency**: 并发和协程支持

### 系统依赖
- **Coroutine 支持**: C++20 协程支持
- **内存管理**: 高效内存分配器
- **原子操作**: 原子操作和锁机制

### 可选依赖
- **压缩库**: 支持数据压缩
- **校验库**: 数据完整性校验
- **性能分析**: 性能分析工具集成

## 注意事项 (Important Notes)

### 线程安全
- **解析器实例**: 每个 TSkiffMultiTableParser 实例不是线程安全的
- **消费者并发**: 消费者实现需要考虑并发访问
- **共享状态**: 避免在消费者间共享可变状态

### 内存管理
- **生命周期**: 确保数据在解析完成前保持有效
- **引用计数**: 正确管理 SharedRef 的引用计数
- **内存泄漏**: 注意协程中的内存泄漏风险

### 错误处理
- **异常传播**: Skiff 异常可能跨越协程边界传播
- **部分解析**: 错误可能导致部分数据解析
- **状态恢复**: 解析器错误后的状态恢复

### 性能警告
- **频繁回调**: 避免过于频繁的回调影响性能
- **内存拷贝**: 注意不必要的内存拷贝操作
- **锁竞争**: 避免解析路径上的锁竞争

### 兼容性注意
- **模式变更**: Skiff 模式变更需要考虑兼容性
- **版本升级**: 注意版本升级时的格式变化
- **平台差异**: 注意不同平台的字节序和对齐

该库为 YTsaurus 提供了高效的 Skiff 数据格式处理能力，正确使用可以显著提升数据序列化和反序列化的性能。