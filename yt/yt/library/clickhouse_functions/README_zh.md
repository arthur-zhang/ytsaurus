# ClickHouse 函数库

## 概述

这个库为 ClickHouse 与 YTsaurus 集成（CHYT）提供了各种 YSON 相关的函数和工具。它实现了 YSON 数据格式的解析、转换和显示功能，使 ClickHouse 能够高效地处理 YTsaurus 的数据。

## 功能特性

### YSON 格式支持

- **标准 YSON 格式**：Binary、Text、Pretty
- **扩展 YSON 格式**：UnescapedText、UnescapedPretty（用于更好的 Unicode 显示）
- **格式转换**：在不同 YSON 格式间转换
- **JSON 转换**：YSON 到 JSON 的转换

### YPath 功能

- **YPath 解析**：解析和执行 YPath 表达式
- **节点提取**：从 YSON 中提取指定路径的数据
- **嵌套访问**：支持复杂的嵌套结构访问

### 解析器适配器

- **JSON 兼容接口**：使用 ClickHouse JSON 解析器接口解析 YSON
- **类型映射**：YSON 类型到 ClickHouse 类型的映射
- **高效解析**：优化的解析性能

## 文件说明

### 核心文件

- `public.h` - 公共接口定义，包含扩展的 YSON 格式枚举
- `unescaped_yson.h/cpp` - 非转义 YSON 格式支持
- `unescaped_yson-inl.h` - 内联实现

### 转换功能

- `convert_yson.cpp` - YSON 格式转换实现
- `yson_to_json.cpp` - YSON 到 JSON 转换
- `yson_extract.cpp` - YSON 数据提取

### YPath 支持

- `ypath.cpp` - YPath 表达式处理

### 解析器适配

- `yson_parser_adapter.h/cpp` - YSON 解析器适配器

## 核心接口

### EExtendedYsonFormat 枚举

扩展的 YSON 格式定义：

```cpp
DEFINE_ENUM(EExtendedYsonFormat,
    (Binary)         // 二进制格式
    (Text)           // 文本格式
    (Pretty)         // 美化格式
    (UnescapedText)  // 非转义文本格式
    (UnescapedPretty) // 非转义美化格式
);
```

### TExtendedYsonWriter

扩展的 YSON 写入器：

```cpp
class TExtendedYsonWriter : public NYson::TYsonWriter {
public:
    TExtendedYsonWriter(
        IOutputStream* stream,
        EExtendedYsonFormat format = EExtendedYsonFormat::Binary,
        NYson::EYsonType type = NYson::EYsonType::Node,
        bool enableRaw = false,
        int indent = DefaultIndent);

    void OnStringScalar(TStringBuf value) override;
};
```

### TYsonParserAdapter

YSON 解析器适配器，提供与 ClickHouse JSON 解析器兼容的接口：

```cpp
struct TYsonParserAdapter {
    class Element;      // YSON 元素
    class Array;        // 数组操作
    class Object;       // 对象操作
};
```

## 使用示例

### YSON 格式转换

```cpp
#include <yt/yt/library/clickhouse_functions/unescaped_yson.h>

using namespace NYT::NClickHouseServer;

// 创建扩展 YSON 写入器
TStringStream stream;
TExtendedYsonWriter writer(&stream, EExtendedYsonFormat::UnescapedPretty);

// 写入数据
writer.OnStringScalar("你好世界");  // Unicode 字符不会被转义

// 转换格式
auto ysonStr = NYson::TYsonString("test");
auto converted = ConvertToYsonStringExtendedFormat(
    ysonStr, EExtendedYsonFormat::UnescapedText);
```

### YPath 表达式使用

```cpp
// 解析 YSON 并提取数据
auto ysonData = "{key={subkey=42}}";
auto extracted = ExtractYsonValue(ysonData, "/key/subkey");
// 结果：42
```

### 解析器适配器使用

```cpp
// 使用 JSON 接口解析 YSON
auto node = NYTree::ConvertToNode(NYson::TYsonString(ysonData));
TYsonParserAdapter::Element element(node);

// 类型检查
if (element.type() == DB::ElementType::STRING) {
    auto str = element.getString();
}
```

## 格式特性

### Unescaped 格式特点

- **Unicode 支持**：正确显示 Unicode 字符
- **控制字符转义**：只转义必要的控制字符
- **可读性**：提高日志和输出的可读性
- **兼容性**：保持与标准 YSON 的兼容性

### 格式对比

| 格式 | 特点 | 适用场景 |
|------|------|----------|
| Binary | 紧凑，高效 | 内部传输，存储 |
| Text | 简单文本 | 调试，日志 |
| Pretty | 格式化输出 | 显示给用户 |
| UnescapedText | Unicode 友好 | 国际化内容 |
| UnescapedPretty | 美化+Unicode | 国际化显示 |

## 实现原理

### 编码处理

- UTF-8 编码支持
- Unicode 字符检测
- 转义字符处理
- 字符串缓冲管理

### 类型映射

YSON 类型到 ClickHouse 类型的映射：

- String → STRING
- Int64 → INT64
- Uint64 → UINT64
- Double → DOUBLE
- Boolean → BOOL
- Map → OBJECT
- List → ARRAY
- Entity → NULL_VALUE

### 性能优化

- 零拷贝解析
- 缓冲区复用
- 延迟计算
- 内存池使用

## 依赖项

- ClickHouse 核心库
- YTsaurus YSON 库
- YTsaurus YTree 库
- 标准库组件

## 集成说明

### 在 ClickHouse 中使用

1. 注册自定义函数
2. 配置 YSON 格式支持
3. 设置字符编码

### 查询示例

```sql
-- 使用 YSON 格式化函数
SELECT formatYson(column, 'unescaped_pretty') FROM table;

-- 使用 YPath 提取
SELECT extractYson(yson_column, '/path/to/value') FROM table;
```

## 最佳实践

1. **选择合适的格式**：
   - 内部处理使用 Binary
   - 调试使用 Text 或 Pretty
   - 国际化内容使用 Unescaped 格式

2. **性能考虑**：
   - 避免频繁的格式转换
   - 复用解析器实例
   - 使用批量操作

3. **错误处理**：
   - 验证 YSON 格式
   - 处理编码错误
   - 提供错误恢复

## 测试

库包含全面的单元测试：

```bash
# 运行测试
ninja test_clickhouse_functions
```

测试覆盖：
- 格式转换
- Unicode 处理
- YPath 解析
- 错误情况
- 性能基准

## 故障排除

### 常见问题

1. **编码问题**
   - 确保使用 UTF-8 编码
   - 检查 BOM 标记
   - 验证字符有效性

2. **解析错误**
   - 验证 YSON 语法
   - 检查特殊字符
   - 确认格式匹配

3. **性能问题**
   - 减少格式转换
   - 使用缓冲区
   - 避免重复解析

## 未来扩展

计划中的功能：
- 更多 YSON 格式支持
- 性能优化
- 更丰富的 YPath 功能
- 自定义序列化器