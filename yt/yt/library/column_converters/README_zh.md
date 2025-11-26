# 列转换器库

## 概述

这个库提供了将行数据转换为列式存储格式的功能。它支持将 YTsaurus 的行格式数据高效地转换为列式表示，适用于数据分析、OLAP 查询和列式存储系统。

## 功能特性

### 数据类型支持

- **整数类型**：int8, int16, int32, int64
- **浮点类型**：float, double
- **字符串类型**：可变长度字符串
- **布尔类型**：true/false 值
- **NULL 值**：支持空值处理

### 转换特性

- **批量转换**：高效处理大量行数据
- **内存优化**：使用位图和缓冲区优化内存使用
- **列式布局**：生成列式存储格式
- **类型安全**：编译时类型检查

## 文件说明

### 核心接口

- `column_converter.h/cpp` - 列转换器基础接口和实现
- `helpers.h/cpp` - 辅助函数和工具

### 类型特定转换器

- `integer_column_converter.h/cpp` - 整数列转换器
- `floating_point_column_converter.h/cpp` - 浮点数列转换器
- `string_column_converter.h/cpp` - 字符串列转换器
- `boolean_column_converter.h/cpp` - 布尔列转换器
- `null_column_converter.h/cpp` - 空值列转换器

### 构建文件

- `CMakeLists.txt` - CMake 构建配置
- `CMakeLists.*.txt` - 针对不同平台的特定构建配置
- `ya.make` - YaMake 构建系统配置

## 核心接口

### IColumnConverter

列转换器基础接口：

```cpp
struct IColumnConverter : private TNonCopyable {
    virtual ~IColumnConverter() = default;

    // 转换行值为列式格式
    virtual TConvertedColumn Convert(TRange<TUnversionedRowValues> rowsValues) = 0;
};
```

### TColumnConverters

主要的列转换管理器：

```cpp
class TColumnConverters {
public:
    // 转换多行数据为列式格式
    TConvertedColumnRange ConvertRowsToColumns(
        TRange<NTableClient::TUnversionedRow> rows,
        const THashMap<int, NTableClient::TColumnSchema>& columnSchemas);
};
```

### 数据结构

#### TConvertedColumn

转换后的列结构：

```cpp
struct TConvertedColumn {
    std::vector<TOwningColumn> Columns;  // 拥有的列数据
    TBatchColumn* RootColumn;            // 根列引用
};
```

#### TOwningColumn

拥有所有权的列数据：

```cpp
struct TOwningColumn {
    TBatchColumnPtr Column;      // 列数据
    TSharedRef NullBitmap;       // NULL 值位图
    TSharedRef ValueBuffer;      // 值缓冲区
    TSharedRef StringBuffer;     // 字符串缓冲区
};
```

## 使用示例

### 基本转换

```cpp
#include <yt/yt/library/column_converters/column_converter.h>

using namespace NYT::NColumnConverters;
using namespace NYT::NTableClient;

// 创建列转换器
TColumnConverters converter;

// 准备行数据
std::vector<TUnversionedRow> rows = /* 获取行数据 */;

// 定义列结构
THashMap<int, TColumnSchema> columnSchemas;
columnSchemas[0] = TColumnSchema("id", EValueType::Int64);
columnSchemas[1] = TColumnSchema("name", EValueType::String);

// 执行转换
auto columnRange = converter.ConvertRowsToColumns(rows, columnSchemas);

// 访问转换后的列
for (const auto& column : columnRange) {
    // 处理列数据
}
```

### 类型特定转换

```cpp
// 创建整数列转换器
auto intConverter = CreateIntegerColumnConverter(
    EValueType::Int64,
    /*allowNull*/ true);

// 创建字符串列转换器
auto stringConverter = CreateStringColumnConverter(
    EValueType::String,
    /*allowNull*/ false);

// 转换数据
std::vector<const TUnversionedValue*> values = /* 获取值 */;
auto intColumn = intConverter->Convert(values);
auto stringColumn = stringConverter->Convert(values);
```

## 实现原理

### 转换流程

1. **类型识别**：根据列模式确定转换器
2. **内存分配**：预分配列缓冲区
3. **数据转换**：将行数据转换为列格式
4. **NULL 处理**：更新 NULL 位图
5. **缓冲区管理**：管理多个缓冲区生命周期

### 内存布局

- **值缓冲区**：存储实际的数据值
- **NULL 位图**：标记 NULL 值位置
- **字符串缓冲区**：存储变长字符串数据
- **偏移量数组**：记录字符串偏移

### 优化策略

- **批量处理**：减少函数调用开销
- **内存预分配**：避免动态扩容
- **SIMD 优化**：使用向量指令加速
- **缓存友好**：优化内存访问模式

## 性能特性

### 转换效率

- **行到列转换**：O(n) 复杂度
- **内存访问**：顺序访问，缓存友好
- **并行化**：支持多线程转换

### 内存使用

- **紧凑存储**：列式存储减少内存占用
- **延迟分配**：按需分配缓冲区
- **共享缓冲区**：多个列共享字符串缓冲区

## 类型映射

### 整数类型

| YTsaurus 类型 | C++ 类型 | 存储大小 |
|--------------|----------|----------|
| Int8 | i8 | 1 byte |
| Int16 | i16 | 2 bytes |
| Int32 | i32 | 4 bytes |
| Int64 | i64 | 8 bytes |

### 浮点类型

| YTsaurus 类型 | C++ 类型 | 存储大小 |
|--------------|----------|----------|
| Double | double | 8 bytes |
| Float | float | 4 bytes |

### 其他类型

| YTsaurus 类型 | 处理方式 |
|--------------|----------|
| String | 变长字符串，带偏移量 |
| Boolean | 位打包存储 |
| Null | 位图标记 |

## NULL 值处理

### 位图表示

- 每个位对应一个值的 NULL 状态
- 1 表示 NULL，0 表示非 NULL
- 使用 TBitmap 进行高效管理

### 处理策略

- **显式 NULL**：在位图中标记
- **隐式 NULL**：默认值处理
- **混合模式**：部分列允许 NULL

## 错误处理

### 常见错误

1. **类型不匹配**
   - 验证值类型与列模式一致
   - 提供类型转换选项

2. **内存不足**
   - 分批处理大数据
   - 优化内存使用

3. **数据损坏**
   - 验证数据完整性
   - 提供恢复机制

## 依赖项

- YTsaurus 表客户端库
- YTsaurus 核心库
- 内存管理库
- 位图操作库

## 平台支持

- Linux x86_64
- Linux aarch64
- macOS x86_64
- macOS arm64

## 最佳实践

### 性能优化

1. **批量处理**：一次转换多行数据
2. **预分配**：预估数据大小
3. **类型匹配**：避免不必要的类型转换
4. **内存对齐**：确保数据对齐

### 内存管理

1. **及时释放**：转换完成后释放资源
2. **复用缓冲区**：多次转换复用内存
3. **监控使用**：跟踪内存消耗

### 错误处理

1. **输入验证**：检查输入数据有效性
2. **异常安全**：使用 RAII 管理资源
3. **日志记录**：记录转换错误

## 测试

库包含全面的测试：

```bash
# 运行测试
ninja test_column_converters
```

测试覆盖：
- 各类型转换正确性
- NULL 值处理
- 边界条件
- 性能基准
- 错误情况

## 未来扩展

计划中的功能：

- 更多数据类型支持
- SIMD 优化加速
- 压缩存储支持
- 并行转换优化
- 流式处理模式