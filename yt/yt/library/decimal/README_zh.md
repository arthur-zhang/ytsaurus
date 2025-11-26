# Decimal 库

## 概述

Decimal 库提供了高精度十进制数值的支持，专为 YTsaurus 系统设计。该库实现了最多 76 位精度的十进制数运算，支持二进制和文本格式之间的转换，适用于金融、计算和其他需要精确数值计算的场景。

## 功能特性

- **高精度支持**: 最多支持 76 位精度的十进制数
- **多种存储格式**: 支持 32 位、64 位、128 位和 256 位的二进制表示
- **格式转换**: 提供文本和二进制格式之间的高效转换
- **性能优化**: 针对频繁转换操作提供无内存分配的版本
- **数值验证**: 内置精度和小数位数的验证机制
- **统一接口**: 提供一致的 API 用于不同精度的数值处理

## 文件说明

- `decimal.h` - 核心头文件，定义 TDecimal 类和相关的数据结构
- `decimal.cpp` - 主要实现文件，包含所有转换和验证逻辑
- `unittests/` - 单元测试目录，包含全面的测试用例
  - `decimal_ut.cpp` - 单元测试实现文件

## 核心接口

### TDecimal 类

主要的静态方法包括：

- **验证方法**:
  - `ValidatePrecisionAndScale(int precision, int scale)` - 验证精度和小数位数
  - `ValidateBinaryValue(TStringBuf binaryValue, int precision, int scale)` - 验证二进制值

- **格式转换**:
  - `BinaryToText(TStringBuf binaryDecimal, int precision, int scale)` - 二进制转文本
  - `TextToBinary(TStringBuf textDecimal, int precision, int scale)` - 文本转二进制
  - 无分配版本：提供缓冲区版本以避免内存分配

- **数值写入**:
  - `WriteBinary32/64/128/256()` - 写入不同精度的二进制格式
  - `WriteBinary128Variadic()` - 根据精度自动选择 128 位格式
  - `WriteBinary256Variadic()` - 根据精度自动选择 256 位格式

- **数值解析**:
  - `ParseBinary32/64/128/256()` - 解析不同精度的二进制格式

### 数据结构

- **TValue128**: 128 位有符号整数值，使用低 64 位和高 64 位表示
- **TValue256**: 256 位有符号整数值，使用 8 个 32 位部分的数组表示

## 使用示例

```cpp
#include <yt/yt/library/decimal/decimal.h>

using namespace NYT::NDecimal;

// 验证精度和小数位数
TDecimal::ValidatePrecisionAndScale(10, 2);

// 文本转二进制
auto textValue = "123.45";
auto binaryValue = TDecimal::TextToBinary(textValue, 10, 2);

// 二进制转文本
char buffer[TDecimal::MaxTextSize];
auto convertedText = TDecimal::BinaryToText(
    binaryValue,
    10,  // precision
    2,   // scale
    buffer,
    sizeof(buffer)
);

// 获取二进制大小
int binarySize = TDecimal::GetValueBinarySize(10);

// 写入 32 位值
char writeBuffer[32];
auto written = TDecimal::WriteBinary32(5, 12345, writeBuffer, sizeof(writeBuffer));
```

## 实现原理

该库使用固定精度的十进制表示法，通过以下方式实现：

1. **内部表示**: 使用整数类型的二进制表示，避免浮点数精度损失
2. **精度管理**: 通过精度（precision）和小数位数（scale）参数管理数值范围
3. **格式转换**: 优化的算法实现文本和二进制之间的高效转换
4. **内存优化**: 提供缓冲区版本避免频繁的内存分配

## 常量定义

- `MaxPrecision = 76` - 支持的最大精度
- `MaxBinarySize = 32` - 最大二进制大小（256 位）
- `MaxTextSize = 79` - 最大文本大小（包括符号和小数点）

## 依赖项

- `library/cpp/int128/int128.h` - 128 位整数支持
- `util/system/defaults.h` - 系统默认定义
- `util/generic/string.h` - 字符串处理
- `<array>` - 标准库数组支持

## 平台支持

支持所有 YTsaurus 支持的平台：
- Linux (x86_64, aarch64)
- macOS (x86_64, arm64)

## 错误处理

库提供了完善的错误处理机制：
- 精度和小数位数验证
- 二进制值格式验证
- 异常抛出机制用于无效输入

## 性能考虑

- 使用静态方法避免对象创建开销
- 提供无分配版本用于高性能场景
- 针对不同精度优化的专用函数
- 内联关键路径代码以提高性能