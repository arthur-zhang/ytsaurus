# YTsaurus Complex Types 模块

## 概述

Complex Types 模块是 YTsaurus 客户端库中专门用于处理复杂数据类型的核心组件。该模块提供了对 YTsaurus 复杂类型系统的完整支持，包括类型检查、格式转换、扫描器生成等功能。

## 主要功能

### 1. 类型兼容性检查
- **文件**: `check_type_compatibility.h/cpp`
- **功能**: 检查两种复杂类型之间的兼容性
- **用途**: 模式演进、数据迁移、类型验证

### 2. YSON 格式转换
- **文件**: `yson_format_conversion.h/cpp`
- **功能**: 提供命名模式和位置模式之间的转换
- **支持类型**:
  - Struct (结构体)
  - VariantStruct (变体结构)
  - Dict (字典)
  - Decimal (小数)
  - Time (时间)
  - UUID (通用唯一标识符)

### 3. 扫描器工厂
- **文件**: `scanner_factory.h`
- **功能**: 生成高效的复杂数据类型扫描器
- **支持**: 可选类型、列表、元组、结构体等
- **特性**: 模板化设计，类型安全

### 4. 类型合并
- **文件**: `merge_complex_types.h/cpp`
- **功能**: 合并两个复杂类型
- **用途**: 模式合并、类型推断

### 5. 特殊工具类
- **文件**: `infinite_entity.h/cpp`
- **功能**: 提供无限实体解析器
- **用途**: 处理循环引用或无限数据流

## 核心组件详解

### TScannerFactory 类
```cpp
template <typename... TArgs>
class TScannerFactory
```
用于生成高效的数据扫描器，支持：
- Optional 扫描器：处理可选字段
- List 扫描器：处理列表数据
- Tuple 扫描器：处理元组数据
- Struct 扫描器：处理结构体数据

### 转换器配置
```cpp
struct TYsonConverterConfig {
    EComplexTypeMode ComplexTypeMode = EComplexTypeMode::Named;
    EDictMode StringKeyedDictMode = EDictMode::Positional;
    EDecimalMode DecimalMode = EDecimalMode::Binary;
    ETimeMode TimeMode = ETimeMode::Binary;
    EUuidMode UuidMode = EUuidMode::Binary;
    bool SkipNullValues = false;
};
```

## 使用方法

### 1. 类型兼容性检查
```cpp
#include <yt/yt/client/complex_types/check_type_compatibility.h>

auto [compatibility, error] = CheckTypeCompatibility(oldType, newType);
if (compatibility != ESchemaCompatibility::FullyCompatible) {
    // 处理不兼容的情况
}
```

### 2. 创建 YSON 转换器
```cpp
#include <yt/yt/client/complex_types/yson_format_conversion.h>

TYsonConverterConfig config;
config.ComplexTypeMode = NFormats::EComplexTypeMode::Named;

auto converter = CreateYsonServerToClientConverter(descriptor, config);
converter(value, consumer);
```

### 3. 使用扫描器工厂
```cpp
#include <yt/yt/client/complex_types/scanner_factory.h>

auto scanner = TScannerFactory<>::CreateOptionalScanner(
    descriptor, applier, element);
scanner(&cursor, args...);
```

## 性能优化

### 1. 零拷贝设计
- 使用 `IZeroCopyInput` 接口减少内存拷贝
- 支持流式数据处理

### 2. 模板化实现
- 编译时类型检查
- 内联优化
- 避免运行时类型信息开销

### 3. 缓存机制
- 转换器缓存减少重复创建开销
- 扫描器复用提高解析效率

## 依赖项

### 内部依赖
- `yt/yt/client/table_client/public.h` - 表客户端接口
- `yt/yt/core/yson/pull_parser.h` - YSON 解析器
- `yt/yt/core/yson/public.h` - YSON 公共接口

### 外部依赖
- 标准库 C++ 运行时
- 系统级 I/O 接口

## 实现原理

### 1. 类型系统设计
- 使用递归类型定义
- 支持嵌套复杂类型
- 类型擦除和恢复机制

### 2. 解析器架构
- 基于 Pull Parser 的流式解析
- 事件驱动的处理模式
- 异常安全保证

### 3. 内存管理
- RAII 资源管理
- 智能指针使用
- 移动语义优化

## 错误处理

### 1. 类型检查错误
```cpp
void ThrowUnexpectedYsonTokenException(
    const TComplexTypeFieldDescriptor& descriptor,
    const TYsonPullParserCursor& cursor,
    const std::vector<EYsonItemType>& expected);
```

### 2. 异常安全
- 强异常安全保证
- 资源自动清理
- 上下文信息保留

## 扩展性

### 1. 自定义类型支持
- 插件式类型注册
- 自定义转换器实现
- 类型策略配置

### 2. 性能调优
- 编译时配置选项
- 运行时参数调优
- 性能监控接口

## 测试和验证

该模块包含完整的单元测试覆盖：
- 类型兼容性测试
- 转换器功能测试
- 扫描器性能测试
- 错误处理验证

## 版本兼容性

- 向后兼容：支持旧版本 API
- 模式演进：支持结构化数据模式变更
- 数据迁移：提供平滑的数据迁移路径

## 相关文档

- [YTsaurus 复杂类型系统文档](../../../docs/complex-types.md)
- [YSON 格式规范](../../../docs/yson-format.md)
- [表客户端 API 参考](../table_client/README.md)

## 贡献指南

在贡献代码时，请确保：
1. 添加适当的单元测试
2. 更新相关文档
3. 遵循代码风格规范
4. 性能测试通过基准要求