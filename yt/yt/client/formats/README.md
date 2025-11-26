# YTsaurus Formats 模块

## 概述

Formats 模块是 YTsaurus 数据格式系统的核心实现，提供了多种数据格式的解析、生成和转换功能。该模块支持从简单的文本格式到复杂的二进制格式，为数据的读写、转换和互操作性提供了统一的接口。

## 核心功能

### 1. 多格式支持
- **YSON**: YTsaurus 原生序列化格式
- **JSON**: JavaScript Object Notation
- **DSV**: Delimiter-Separated Values
- **YAMR**: Yet Another MapReduce 格式
- **Protobuf**: Protocol Buffers 二进制格式
- **Arrow**: Apache Arrow 列式存储格式
- **Skiff**: YTsaurus 高效二进制格式
- **YAML**: YAML Ain't Markup Language
- **BLOB**: 二进制大对象格式

### 2. 复杂类型处理
- **位置模式 vs 命名模式**: 复杂类型的两种表示方式
- **字典模式**: 字符串键字典的处理方式
- **数值类型**: 小数、时间、UUID 的多种表示方法
- **嵌套结构**: 支持任意深度的嵌套数据结构

### 3. 数据转换
- **类型转换**: 自动和强制的类型转换
- **编码处理**: 字符编码和转义处理
- **模式匹配**: 结构化数据的模式验证
- **流式处理**: 大数据的流式读写

## 主要组件详解

### 1. 格式类型枚举 (EFormatType)

```cpp
DEFINE_ENUM(EFormatType,
    (Null)           // 空格式
    (Yson)           // YSON 格式
    (Json)           // JSON 格式
    (Dsv)            // 分隔符分隔值格式
    (Yamr)           // MapReduce 格式
    (YamredDsv)      // YAMR 风格的 DSV
    (SchemafulDsv)   // 带模式的 DSV
    (Protobuf)       // Protocol Buffers
    (WebJson)        // Web JSON 格式
    (Skiff)          // Skiff 二进制格式
    (Arrow)          // Apache Arrow 格式
    (Yaml)           // YAML 格式
    (Blob)           // 二进制大对象
);
```

### 2. 复杂类型模式 (EComplexTypeMode)

```cpp
DEFINE_ENUM(EComplexTypeMode,
    (Positional),  // 位置模式: [value1, value2, value3]
    (Named)        // 命名模式: {field1=value1, field2=value2}
);
```

#### 模式对比

| 模式 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| 位置模式 | 紧凑，高效 | 可读性差，顺序敏感 | 内部数据传输，性能优先 |
| 命名模式 | 可读性强，容错性好 | 体积较大 | 配置文件，调试输出 |

### 3. 数据类型枚举 (EDataType)

```cpp
DEFINE_ENUM(EDataType,
    (Null)        // 空数据
    (Binary)      // 二进制数据
    (Structured)  // 结构化数据
    (Tabular)     // 表格数据
);
```

### 4. 格式配置体系

#### YSON 格式配置 (TYsonFormatConfig)

```cpp
struct TYsonFormatConfig : public NTableClient::TTypeConversionConfig {
    NYson::EYsonFormat Format;          // YSON 子格式 (Binary, Text, Pretty)
    EComplexTypeMode ComplexTypeMode;   // 复杂类型模式
    EDictMode StringKeyedDictMode;      // 字典模式
    EDecimalMode DecimalMode;           // 小数模式 (Text, Binary)
    ETimeMode TimeMode;                 // 时间模式 (Text, Binary)
    EUuidMode UuidMode;                 // UUID 模式 (TextYql, TextYt, Binary)
    bool SkipNullValues;                // 跳过空值
};
```

#### 表格格式基类 (TTableFormatConfigBase)

```cpp
struct TTableFormatConfigBase : public NTableClient::TTypeConversionConfig {
    char RecordSeparator;     // 记录分隔符
    char FieldSeparator;      // 字段分隔符
    bool EnableEscaping;      // 启用转义
    char EscapingSymbol;      // 转义符号
    bool EnableTableIndex;    // 启用表索引
};
```

### 5. 格式类 (TFormat)

```cpp
class TFormat {
public:
    TFormat(EFormatType type, const NYTree::IAttributeDictionary* attributes = nullptr);

    EFormatType GetType() const;
    const NYTree::IAttributeDictionary& GetAttributes() const;

    bool operator==(const TFormat& other) const;

private:
    EFormatType Type_;
    NYTree::IAttributeDictionaryPtr Attributes_;
};
```

## 格式详解

### 1. YSON 格式

YSON (YTsaurus Serialized Object Notation) 是 YTsaurus 的原生序列化格式：

#### 特性
- **高效性**: 紧凑的二进制表示
- **完整性**: 保留所有类型信息
- **嵌套支持**: 支持任意深度的嵌套结构
- **版本兼容**: 向后和向前兼容

#### 使用示例

```cpp
// 创建 YSON 格式配置
auto ysonConfig = New<TYsonFormatConfig>();
ysonConfig->Format = NYson::EYsonFormat::Binary;
ysonConfig->ComplexTypeMode = EComplexTypeMode::Named;
ysonConfig->DecimalMode = EDecimalMode::Binary;
ysonConfig->TimeMode = ETimeMode::Binary;
ysonConfig->UuidMode = EUuidMode::Binary;

// 创建格式对象
TFormat format(EFormatType::Yson, NYTree::CreateEphemeralAttributes());
format.Attributes().Set("config", ysonConfig);
```

### 2. JSON 格式

JSON 格式的特殊配置和优化：

#### WebJson 格式配置 (TWebJsonFormatConfig)

```cpp
struct TWebJsonFormatConfig : public TTableFormatConfigBase {
    bool SupportUnsignedIntegers;  // 支持无符号整数
    bool StringifyNull;           // null 值字符串化
    bool AllowNaN;                // 允许 NaN 值
    bool AllowInfinity;           // 允许无穷大值
    bool SkipNullValues;          // 跳过空值
    bool ForcePortableRepresentation; // 强制可移植表示
};
```

#### 使用场景

```cpp
// API 响应格式
auto webJsonConfig = New<TWebJsonFormatConfig>();
webJsonConfig->StringifyNull = false;
webJsonConfig->AllowNaN = true;
webJsonConfig->SkipNullValues = true;

TFormat apiFormat(EFormatType::WebJson);
apiFormat.Attributes().Set("config", webJsonConfig);
```

### 3. DSV 格式

DSV (Delimiter-Separated Values) 格式的灵活配置：

#### DSV 格式配置 (TDsvFormatConfig)

```cpp
struct TDsvFormatConfig : public TDsvFormatConfigBase {
    bool EnableKeySwitch;  // 启用键切换
};
```

#### 使用示例

```cpp
// CSV 格式配置
auto csvConfig = New<TDsvFormatConfig>();
csvConfig->RecordSeparator = '\n';
csvConfig->FieldSeparator = ',';
csvConfig->EnableEscaping = true;
csvConfig->EscapingSymbol = '\\';
csvConfig->EnableKeySwitch = true;

TFormat csvFormat(EFormatType::Dsv);
csvFormat.Attributes().Set("config", csvConfig);
```

### 4. Protobuf 格式

Protocol Buffers 格式的类型系统支持：

#### Protobuf 配置结构

```cpp
// 表级配置
struct TProtobufTableConfig {
    std::vector<TProtobufColumnConfigPtr> Columns;  // 列配置
    std::vector<TString> RequiredWireFormat;        // 必需的线格式
    bool Strict;                                    // 严格模式
};

// 列级配置
struct TProtobufColumnConfig {
    TString Name;                    // 列名
    TString ProtoTypeName;           // Protobuf 类型名
    std::optional<int> FieldNumber;  // 字段编号
};

// 格式配置
struct TProtobufFormatConfig : public TTableFormatConfigBase {
    std::vector<TProtobufTableConfigPtr> Tables;  // 表配置
    bool SkipUnknownFields;                        // 跳过未知字段
};
```

#### 使用示例

```cpp
auto protoConfig = New<TProtobufFormatConfig>();
protoConfig->SkipUnknownFields = true;

auto tableConfig = New<TProtobufTableConfig>();
tableConfig->Strict = true;

auto columnConfig = New<TProtobufColumnConfig>();
columnConfig->Name = "user_id";
columnConfig->ProtoTypeName = "int64";
columnConfig->FieldNumber = 1;

tableConfig->Columns.push_back(columnConfig);
protoConfig->Tables.push_back(tableConfig);

TFormat protoFormat(EFormatType::Protobuf);
protoFormat.Attributes().Set("config", protoConfig);
```

### 5. Arrow 格式

Apache Arrow 列式存储格式支持：

```cpp
struct TArrowFormatConfig {
    std::optional<std::vector<std::string>> ColumnNames;  // 列名
    bool EnableColumnNames;                               // 启用列名
    bool EnableTimestamps;                                // 启用时间戳
    std::optional<std::string> Compression;              // 压缩算法
    bool DisableSchemaInference;                         // 禁用模式推断
};
```

### 6. Skiff 格式

YTsaurus 高效二进制格式：

```cpp
struct TSkiffFormatConfig {
    bool Strict;                    // 严格模式
    std::optional<int> Version;     // Skiff 版本
    bool EnableTypeValidation;      // 启用类型验证
};
```

## 高级功能

### 1. 数据类型转换

#### 复杂类型处理

```cpp
// 复杂类型的两种表示方式

// 位置模式示例
auto positionalData = "[\"value1\", \"value2\", \"value3\"]";

// 命名模式示例
auto namedData = "{field1=\"value1\", field2=\"value2\", field3=\"value3\"}";

// 配置转换
ysonConfig->ComplexTypeMode = EComplexTypeMode::Named; // 或 EComplexTypeMode::Positional
```

#### 数值类型模式

```cpp
// 小数表示模式
ysonConfig->DecimalMode = EDecimalMode::Text;   // 文本表示: "123.45"
ysonConfig->DecimalMode = EDecimalMode::Binary; // 二进制表示

// 时间表示模式
ysonConfig->TimeMode = ETimeMode::Text;        // ISO 8601 文本: "2023-01-01T00:00:00Z"
ysonConfig->TimeMode = ETimeMode::Binary;      // Unix 时间戳

// UUID 表示模式
ysonConfig->UuidMode = EUuidMode::TextYql;     // YQL 文本格式
ysonConfig->UuidMode = EUuidMode::TextYt;      // YTsaurus 文本格式
ysonConfig->UuidMode = EUuidMode::Binary;      // 二进制格式
```

### 2. 字典模式

```cpp
// 字符串键字典的处理方式
ysonConfig->StringKeyedDictMode = EDictMode::Positional; // 位置模式: ["key1", "value1", "key2", "value2"]
ysonConfig->StringKeyedDictMode = EDictMode::Named;      // 命名模式: {key1="value1", key2="value2"}
```

### 3. 转义处理

```cpp
// 转义规则 (转义符号为 '\\')
// '\0' -> "\0"
// '\n' -> "\n"
// '\t' -> "\t"
// 'X'  -> "\X" (如果 X 不在 ['\0', '\n', '\t'] 中)

tableConfig->EnableEscaping = true;
tableConfig->EscapingSymbol = '\\';
```

### 4. 控制属性

```cpp
struct TControlAttributesConfig : public NTableClient::TChunkReaderOptions {
    bool EnableKeySwitch;    // 启用键切换控制属性
    bool EnableEndOfStream;  // 启用流结束控制属性
};
```

## 使用方法

### 1. 基本格式创建

```cpp
#include <yt/yt/client/formats/public.h>
#include <yt/yt/client/formats/format.h>

using namespace NYT::NFormats;

// 创建简单格式
TFormat ysonFormat(EFormatType::Yson);
TFormat jsonFormat(EFormatType::Json);

// 创建带属性的格式
auto attributes = NYTree::CreateEphemeralAttributes();
attributes->Set("pretty", true);
TFormat prettyJsonFormat(EFormatType::Json, attributes.Get());
```

### 2. 配置化格式

```cpp
// 创建 YSON 配置
auto ysonConfig = New<TYsonFormatConfig>();
ysonConfig->Format = NYson::EYsonFormat::Pretty;
ysonConfig->ComplexTypeMode = EComplexTypeMode::Named;

// 创建格式对象
TFormat format(EFormatType::Yson);
format.Attributes().Set("config", ysonConfig);

// 序列化格式配置
NYson::TYsonString configYson = NYson::ConvertToYsonString(format);
```

### 3. 格式解析和转换

```cpp
// 从字符串解析格式
TFormat parsedFormat = NYson::ConvertTo<TFormat>(formatYson);

// 格式比较
if (format == parsedFormat) {
    // 格式相同
}

// 格式验证
if (format.GetType() == EFormatType::Yson) {
    auto config = format.Attributes().Find<TYsonFormatConfigPtr>("config");
    if (config) {
        // 使用 YSON 特定配置
    }
}
```

### 4. 数据解析器

```cpp
// 创建解析器
auto parser = CreateParser(format, schema);

// 解析数据
std::string inputData = /* ... 数据来源 ... */;
parser->Read(inputData.data(), inputData.size());
parser->Finish();  // 完成解析
```

### 5. 格式写入器

```cpp
// 创建写入器
auto writer = CreateFormatWriter(format, output);

// 写入数据
for (const auto& row : data) {
    writer->Write(row);
}
writer->Close();
```

## 性能优化

### 1. 二进制格式优化

```cpp
// 使用二进制格式提高性能
auto binaryConfig = New<TYsonFormatConfig>();
binaryConfig->Format = NYson::EYsonFormat::Binary;
binaryConfig->DecimalMode = EDecimalMode::Binary;
binaryConfig->TimeMode = ETimeMode::Binary;
binaryConfig->UuidMode = EUuidMode::Binary;
```

### 2. 流式处理

```cpp
// 大数据的流式处理
class StreamingFormatProcessor {
private:
    ISchemalessFormatWriterPtr writer_;
    std::unique_ptr<char[]> buffer_;
    size_t bufferSize_;

public:
    void ProcessStream(IInputStream* input) {
        while (true) {
            size_t bytesRead = input->Read(buffer_.get(), bufferSize_);
            if (bytesRead == 0) break;

            ProcessChunk(buffer_.get(), bytesRead);
        }
    }
};
```

### 3. 内存优化

```cpp
// 内存池管理
class FormatMemoryPool {
private:
    std::vector<std::unique_ptr<char[]>> buffers_;
    std::queue<char*> available_;

public:
    char* AcquireBuffer(size_t size) {
        if (!available_.empty()) {
            auto* buffer = available_.front();
            available_.pop();
            return buffer;
        }
        return new char[size];
    }

    void ReleaseBuffer(char* buffer) {
        available_.push(buffer);
    }
};
```

## 错误处理

### 1. 错误类型

```cpp
YT_DEFINE_ERROR_ENUM(
    ((InvalidFormat) (2800))  // 无效格式
);
```

### 2. 错误处理策略

```cpp
try {
    auto parser = CreateParser(format, schema);
    parser->Read(data, size);
} catch (const TErrorException& e) {
    if (e.GetErrorCode() == NYT::TErrorCode(2800)) { // InvalidFormat
        // 处理格式错误
        HandleFormatError(e);
    } else {
        // 处理其他错误
        HandleGenericError(e);
    }
}
```

### 3. 格式验证

```cpp
// 格式验证工具
class FormatValidator {
public:
    TError ValidateFormat(const TFormat& format) {
        switch (format.GetType()) {
            case EFormatType::Yson:
                return ValidateYsonFormat(format);
            case EFormatType::Json:
                return ValidateJsonFormat(format);
            case EFormatType::Dsv:
                return ValidateDsvFormat(format);
            default:
                return TError("Unsupported format type: %v", format.GetType());
        }
    }

private:
    TError ValidateYsonFormat(const TFormat& format) {
        auto config = format.Attributes().Find<TYsonFormatConfigPtr>("config");
        if (!config) {
            return TError("YSON format requires configuration");
        }
        return TError();
    }
};
```

## 扩展性

### 1. 自定义格式

```cpp
// 添加新格式类型
enum class EExtendedFormatType {
    ExistingFormats = EFormatType::Blob,
    CustomFormat = 100,
};

// 自定义格式配置
struct TCustomFormatConfig : public TTableFormatConfigBase {
    std::string CustomProperty;
    bool EnableCustomFeature;

    REGISTER_YSON_STRUCT(TCustomFormatConfig);
};
```

### 2. 格式转换器

```cpp
// 格式转换接口
class IFormatConverter {
public:
    virtual TFuture<TConvertedData> ConvertAsync(
        const TFormat& sourceFormat,
        const TFormat& targetFormat,
        const TDataFragment& data) = 0;
};
```

## 监控和诊断

### 1. 性能指标

```cpp
struct FormatMetrics {
    i64 TotalBytesProcessed;
    i64 RecordsProcessed;
    TDuration TotalProcessingTime;
    double ThroughputMBps;
    std::unordered_map<EFormatType, i64> FormatUsageCounts;
    std::unordered_map<EFormatType, TDuration> FormatProcessingTimes;
};
```

### 2. 诊断工具

```cpp
// 格式诊断
class FormatDiagnostics {
public:
    void LogFormatInfo(const TFormat& format) {
        YT_LOG_INFO("Format details (Type: %v, Attributes: %v)",
            format.GetType(), format.Attributes());
    }

    void LogProcessingStats(
        EFormatType formatType,
        i64 bytesProcessed,
        TDuration processingTime) {

        double throughput = static_cast<double>(bytesProcessed) /
                           processingTime.MilliSeconds() * 1000.0 / 1024.0 / 1024.0;

        YT_LOG_INFO("Format processing stats (Type: %v, Bytes: %v, Time: %v, Throughput: %.2f MB/s)",
            formatType, bytesProcessed, processingTime, throughput);
    }
};
```

## 最佳实践

### 1. 格式选择指南

| 使用场景 | 推荐格式 | 理由 |
|---------|---------|------|
| 内部数据传输 | YSON Binary | 最高效，完整类型信息 |
| API 接口 | JSON | 标准化，易于解析 |
| 配置文件 | YAML | 可读性强，支持注释 |
| 大数据分析 | Arrow | 列式存储，高效查询 |
| 日志处理 | DSV | 简单，易于分割 |
| 跨语言通信 | Protobuf | 强类型，版本兼容 |

### 2. 配置优化

```cpp
// 针对不同场景的优化配置

// 高性能内部传输
auto highPerfConfig = New<TYsonFormatConfig>();
highPerfConfig->Format = NYson::EYsonFormat::Binary;
highPerfConfig->ComplexTypeMode = EComplexTypeMode::Positional;
highPerfConfig->DecimalMode = EDecimalMode::Binary;
highPerfConfig->TimeMode = ETimeMode::Binary;
highPerfConfig->UuidMode = EUuidMode::Binary;

// 调试和开发
auto debugConfig = New<TYsonFormatConfig>();
debugConfig->Format = NYson::EYsonFormat::Pretty;
debugConfig->ComplexTypeMode = EComplexTypeMode::Named;
debugConfig->DecimalMode = EDecimalMode::Text;
debugConfig->TimeMode = ETimeMode::Text;
debugConfig->UuidMode = EUuidMode::TextYql;
```

### 3. 错误处理策略

```cpp
// 分层错误处理
class FormatErrorHandler {
public:
    TErrorOr<TProcessedData> HandleError(
        const TError& error,
        const TFormat& format,
        const TDataFragment& data) {

        if (error.GetErrorCode() == NYT::TErrorCode(2800)) { // InvalidFormat
            // 尝试格式检测和自动修复
            return TryAutoFixFormat(data);
        }

        if (IsRecoverableError(error)) {
            // 尝试重试
            return RetryProcessing(format, data);
        }

        return error;
    }
};
```

## 依赖项

### 内部依赖
- `yt/yt/client/table_client/config.h` - 表客户端配置
- `yt/yt/client/table_client/schema.h` - 表模式定义
- `yt/yt/core/ytree/yson_struct.h` - YSON 结构支持
- `yt/yt/core/logging/log.h` - 日志系统

### 外部依赖
- RapidJSON - JSON 解析库
- Protobuf - Protocol Buffers 库
- Apache Arrow - 列式存储库
- YAML-cpp - YAML 解析库

## 版本兼容性

- **格式版本**: 支持多版本格式解析
- **向后兼容**: 新版本支持旧格式
- **向前兼容**: 旧版本可处理新格式的子集

## 相关文档

- [YTsaurus 数据格式规范](../../../docs/data-formats.md)
- [YSON 格式详细说明](../../../docs/yson-format.md)
- [格式转换最佳实践](../../../docs/format-conversion.md)
- [性能优化指南](../../../docs/performance-optimization.md)

## 贡献指南

在添加新格式或修改现有格式时：
1. 设计清晰的配置结构
2. 实现完整的解析和生成功能
3. 添加充分的测试用例
4. 更新文档和示例
5. 考虑性能影响和内存使用
6. 确保向后兼容性