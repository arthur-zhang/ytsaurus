# Misc 模块

## 模块概述

`yt/yt/core/misc` 模块是 YTsaurus 分布式系统的工具库集合，提供了大量的基础工具函数、数据结构、算法和实用工具。该模块包含字符串处理、时间处理、错误处理、数学计算、序列化等基础功能，为整个 YTsaurus 系统提供通用的工具支持。

## 主要功能

### 1. 字符串处理
- **字符串操作**: 字符串分割、连接、替换等操作
- **编码转换**: Base64、Hex 等编码转换
- **格式化**: 字符串格式化和模板
- **路径处理**: 文件路径操作和处理

### 2. 错误处理
- **TError**: 统一的错误类型和传播机制
- **异常处理**: C++ 异常和错误码转换
- **错误链**: 错误原因的链式追踪
- **错误格式**: 错误信息的格式化

### 3. 时间处理
- **时间戳**: 高精度时间戳获取
- **时间间隔**: TDuration 时间间隔类型
- **时间格式**: 多种时间格式支持
- **时间计算**: 时间相关的计算操作

### 4. 数学工具
- **随机数**: 高质量随机数生成器
- **哈希函数**: 多种哈希算法实现
- **数学运算**: 常用数学函数和常量
- **统计工具**: 基础统计计算工具

### 5. 序列化
- **二进制序列化**: 高效的二进制序列化
- **文本序列化**: 可读的文本序列化
- **版本兼容**: 序列化版本兼容性
- **压缩序列化**: 压缩序列化支持

## 核心组件

### TError 系统
YTsaurus 的统一错误处理系统，支持：
- 错误码和消息
- 错误原因链
- 错误属性和上下文
- 错误的序列化和传输

### TDuration 和 TInstant
时间处理的核心类型：
- 高精度时间戳
- 时间间隔计算
- 时间格式化
- 时间比较操作

### 字符串工具
- TStringBuf: 零拷贝字符串视图
- Format: 类型安全的字符串格式化
- Split/Join: 字符串分割和连接

## 使用示例

### 错误处理
```cpp
#include <yt/yt/core/misc/error.h>

using namespace NYT;

// 创建错误
TError error("Operation failed")
    << TErrorAttribute("operation", "read")
    << TErrorAttribute("path", "/data/file.txt");

// 包装错误
TError wrappedError = TError("Failed to process data")
    << error;

// 检查错误
if (error.IsOK()) {
    // 成功
} else {
    std::cout << "Error: " << error.GetMessage() << std::endl;
}
```

### 时间处理
```cpp
#include <yt/yt/core/misc/timestamp.h>

using namespace NYT;

// 获取当前时间
TInstant now = TInstant::Now();

// 创建时间间隔
TDuration timeout = TDuration::Seconds(30);

// 时间计算
TInstant deadline = now + timeout;

// 格式化时间
TString timeStr = ToString(now);
```

### 字符串处理
```cpp
#include <yt/yt/core/misc/string_builder.h>

using namespace NYT;

// 字符串构建
TStringBuilder builder;
builder.AppendFormat("Processing %d items", count);
builder.AppendString(" completed");

TString result = builder.Flush();

// 字符串分割
std::vector<TString> parts = SplitString("a,b,c", ",");

// 字符串连接
TString joined = JoinStrings(parts, ";");
```

### 随机数生成
```cpp
#include <yt/yt/core/misc/random.h>

// 生成随机数
TRandomGenerator rng;
ui32 randomValue = rng.Generate<ui32>();
double randomDouble = rng.Generate<double>();
```

## 性能特性

- **零拷贝**: 尽可能避免不必要的数据拷贝
- **内存高效**: 优化内存分配和使用
- **类型安全**: 强类型接口减少运行时错误
- **内联优化**: 关键函数内联提高性能

## 依赖关系

- **标准库**: C++ 标准库
- **系统库**: 操作系统相关函数
- **第三方库**: 如加密库、压缩库等

## 设计原则

1. **性能优先**: 优化高频使用的工具函数
2. **类型安全**: 使用强类型和模板保证类型安全
3. **易用性**: 提供简洁直观的接口
4. **可扩展**: 支持自定义类型和操作
5. **兼容性**: 保持 API 的向后兼容性