# Formats (数据格式)

Formats 是 YTsaurus 中处理各种数据格式的核心库，提供了全面的解析器、写入器和格式转换功能。

## 概述

Formats 库支持多种数据格式，包括：
- 结构化格式（YSON、JSON、YAML、Protobuf）
- 分隔符格式（DSV、YAMR）
- 二进制格式（Skiff、Arrow）
- 特殊格式（Web JSON、Schemaful/Schemaless）

## 核心组件

### 1. 格式解析器 (Parsers)
- **YSON Parser**: 解析 YSON 格式数据
- **DSV Parser**: 解析分隔符格式
- **YAML Parser**: 解析 YAML 格式
- **JSON Parser**: 解析 JSON 格式
- **Protobuf Parser**: 解析 Protobuf 格式
- **Skiff Parser**: 解析 Skiff 二进制格式
- **Arrow Parser**: 解析 Apache Arrow 格式

### 2. 格式写入器 (Writers)
- **YSON Writer**: 写入 YSON 格式
- **DSV Writer**: 写入分隔符格式
- **YAML Writer**: 写入 YAML 格式
- **Web JSON Writer**: 写入 Web 优化的 JSON
- **Protobuf Writer**: 写入 Protobuf 格式
- **Skiff Writer**: 写入 Skiff 二进制格式
- **Arrow Writer**: 写入 Apache Arrow 格式

### 3. 格式转换器 (Converters)
- **Skiff-YSON Converter**: Skiff 与 YSON 之间的转换
- **YQL-YSON Converter**: YQL 与 YSON 之间的转换
- **YSON Map to Unversioned Value**: YSON 到无版本值的转换

## 主要接口

### 解析器接口
```cpp
// 创建 DSV 解析器
std::unique_ptr<IParser> CreateParserForDsv(
    NYson::IYsonConsumer* consumer,
    TDsvFormatConfigPtr config,
    bool wrapWithMap = true);

// 创建 YSON 解析器
std::unique_ptr<IParser> CreateParserForYson(
    NYson::IYsonConsumer* consumer,
    NYson::EYsonType type,
    bool enableLinePositionInfo = false);
```

### 写入器接口
```cpp
// 无模式格式写入器
struct ISchemalessFormatWriter : public IUnversionedRowsetWriter {
    virtual TBlob GetContext() const = 0;
    virtual i64 GetWrittenSize() const = 0;
    [[nodiscard]] virtual TFuture<void> Flush() = 0;
    virtual bool WriteBatch(IUnversionedRowBatchPtr rowBatch) = 0;
};
```

### 创建函数
```cpp
// 为格式创建模式化写入器
IUnversionedRowsetWriterPtr CreateSchemafulWriterForFormat(
    const TFormat& format,
    TTableSchemaPtr schema,
    IAsyncOutputStreamPtr output);

// 为格式创建版本化写入器
IVersionedWriterPtr CreateVersionedWriterForFormat(
    const TFormat& format,
    TTableSchemaPtr schema,
    IAsyncOutputStreamPtr output);

// 创建静态表写入器
ISchemalessFormatWriterPtr CreateStaticTableWriterForFormat(
    const TFormat& format,
    TNameTablePtr nameTable,
    const std::vector<TTableSchemaPtr>& tableSchemas,
    const std::vector<std::optional<std::vector<std::string>>>& columns,
    IAsyncOutputStreamPtr output,
    bool enableContextSaving,
    TControlAttributesConfigPtr controlAttributesConfig,
    int keyColumnCount);
```

## 格式说明

### 1. DSV (Delimiter-Separated Values)
支持自定义分隔符的格式：
```cpp
TDsvFormatConfigPtr config = New<TDsvFormatConfig>();
config->FieldSeparator = "\t";  // 使用制表符
config->RecordSeparator = "\n"; // 使用换行符
config->EnableEscaping = true;  // 启用转义
```

### 2. YAMR (Yet Another MapReduce)
类似 Hadoop 的输出格式：
```cpp
TFormat yamrFormat = TFormat(
    "yamred_dsv",
    NYTree::CreateNodeFromYsonString(TStringBuf(
        "{key_column_names=[key]; "
        "has_subkey=true; "
        "value_column_names=[value]}")));
```

### 3. Skiff
高效的二进制格式：
- 类型安全
- 零拷贝序列化
- 高性能读写
- 支持复杂嵌套结构

### 4. Arrow
列式存储格式：
- 高效的列式操作
- 与 Spark 等系统集成
- 支持向量化处理

## 使用示例

### 解析 DSV 数据
```cpp
// 创建配置
TDsvFormatConfigPtr config = New<TDsvFormatConfig>();
config->FieldSeparator = ",";
config->HasHeader = true;

// 创建解析器
auto consumer = CreateYsonConsumer(...);
auto parser = CreateParserForDsv(consumer, config);

// 解析数据
parser->Read(inputStream);
```

### 写入 YSON 格式
```cpp
// 创建格式
TFormat ysonFormat = TFormat("yson");

// 创建写入器
auto output = CreateAsyncOutputStream(...);
auto writer = CreateSchemafulWriterForFormat(
    ysonFormat,
    schema,
    output);

// 写入数据
writer->Write(rows);
```

### 格式转换
```cpp
// 创建转换器
auto converter = CreateSkiffToYsonConverter(
    skiffSchema,
    ysonConsumer);

// 转换数据
converter->Convert(skiffData);
```

## 性能优化

### 1. 批量处理
- 使用批量写入接口
- 批量处理减少函数调用开销

### 2. 内存管理
- 使用对象池减少分配
- 零拷贝操作避免数据复制
- 及时释放大对象

### 3. 并行处理
- 支持异步写入
- 并行解析独立块

## 配置选项

### DSV 配置
- `FieldSeparator`: 字段分隔符
- `RecordSeparator`: 记录分隔符
- `EnableEscaping`: 是否启用转义
- `EscapingSymbol`: 转义符号
- `HasHeader`: 是否包含头部

### Protobuf 配置
- `MessageDescriptor`: Protobuf 消息描述
- `UseProtoExtensions`: 是否使用扩展
- `PrintAnnotations`: 是否打印注解

### Arrow 配置
- `BatchSize`: 批处理大小
- `Compression`: 压缩选项
- `Schema`: Arrow 模式定义

## 特殊功能

### 1. 转义处理
支持多种转义策略：
- C 风格转义
- CSV 风格转义
- 自定义转义规则

### 2. 类型推断
自动推断数据类型：
- 整数、浮点数检测
- 日期时间识别
- 布尔值解析

### 3. 错误处理
- 详细的错误位置信息
- 可配置的严格性级别
- 部分解析支持

## 最佳实践

### 1. 选择合适的格式
- **JSON**: 可读性好，适合调试
- **YSON**: YT 原生格式，功能最全
- **Skiff**: 高性能，内部存储
- **DSV**: 简单，兼容性好

### 2. 性能优化
```cpp
// 使用批量操作
writer->Prepare();
for (auto& batch : rowBatches) {
    writer->WriteBatch(batch);
}
writer->Finish();

// 启用压缩
config->EnableCompression = true;
```

### 3. 错误处理
```cpp
try {
    parser->Read(input);
} catch (const TParseError& e) {
    YT_LOG_ERROR("Parse error at line %v, column %v: %v",
        e.GetLine(),
        e.GetColumn(),
        e.GetMessage());
}
```

## 依赖项

- YTsaurus 核心库 (`yt/yt/core/`)
- 表客户端库 (`yt/yt/client/`)
- 格式库 (`yt/yt/client/formats/`)
- Apache Arrow 库（可选）
- Protobuf 库

## 注意事项

1. **编码**: 确保 UTF-8 编码一致性
2. **内存使用**: 大文件处理时注意内存限制
3. **性能**: 选择适合场景的格式
4. **兼容性**: 注意版本兼容性
5. **错误恢复**: 实现适当的错误恢复机制