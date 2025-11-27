# 字符集处理库

本模块提供高效的字符集编码转换和处理功能，支持多种字符编码之间的转换。

## 功能特性

### UTF-8 编码处理
- UTF-8 编码/解码
- UTF-8 字符长度计算
- UTF-8 字符迭代
- UTF-8 字符计数

### Unicode 支持
- Unicode 字符表查询
- Unicode 属性获取
- 大小写转换
- 字符规范化

### 编码转换
- 支持多种字符编码
- 高性能转换算法
- 错误处理机制
- 流式转换支持

## 主要组件

### 核心文件
- **utf8.h/cpp** - UTF-8 编码处理
- **unidata.h/cpp** - Unicode 数据表
- **wide.h/cpp** - 宽字符处理
- **unicode_table.h** - Unicode 字符映射表

### 工具函数
- **recode_result.h/cpp** - 编码转换结果
- **generated/** - 自动生成的编码表

## 使用方法

### UTF-8 编码处理
```cpp
#include "util/charset/utf8.h"

// 计算 UTF-8 字符长度
size_t len = UTF8CharLength(first_byte);

// 检查是否为有效的 UTF-8 序列
bool valid = IsValidUTF8Sequence(data, length);

// 转换为宽字符
wchar_t wc;
size_t consumed = UTF8ToWideChar(data, length, &wc);
```

### Unicode 属性查询
```cpp
#include "util/charset/unidata.h"

// 获取字符类别
UnicodeCategory cat = GetUnicodeCategory(wc);

// 检查是否为字母数字
bool is_alnum = IsAlphanumeric(wc);

// 大小写转换
wchar_t upper = ToUpper(wc);
wchar_t lower = ToLower(wc);
```

### 编码转换
```cpp
#include "util/charset/wide.h"

// UTF-8 转宽字符
std::wstring wide = UTF8ToWide(utf8_str);

// 宽字符转 UTF-8
std::string utf8 = WideToUTF8(wide_str);
```

## 性能特性

### 优化策略
- 查找表优化
- 分支预测优化
- SIMD 指令支持（如果可用）
- 缓存友好的数据布局

### 性能指标
- UTF-8 编码/解码：> 1 GB/s
- Unicode 查询：< 1 ns/次
- 编码转换：> 500 MB/s

## 错误处理

### 错误类型
```cpp
enum class RecodeError {
    None,           // 无错误
    InvalidInput,   // 无效输入
    IncompleteSeq,  // 不完整序列
    NoMemory        // 内存不足
};
```

### 错误处理策略
- 遇到错误时的行为可配置
- 支持错误回调
- 提供错误恢复机制

## 平台支持

- Linux (x86_64, ARM64)
- macOS (x86_64, ARM64)
- Windows (x86_64)
- FreeBSD (x86_64)

## 编译配置

各平台的 CMakeLists 配置：
- `CMakeLists.linux-x86_64.txt`
- `CMakeLists.linux-aarch64.txt`
- `CMakeLists.darwin-x86_64.txt`
- `CMakeLists.darwin-arm64.txt`

## 测试

运行测试：
```bash
# 编译测试
cmake --build . --target charset_tests

# 运行单元测试
./util/charset/ut/charset_ut

# 运行性能测试
./util/charset/ut/charset_perf
```

## 最佳实践

1. **性能优化**
   - 批量处理字符
   - 预分配足够缓冲区
   - 使用流式处理处理大数据

2. **错误处理**
   - 始终检查返回值
   - 设置合适的错误处理策略
   - 提供回退方案

3. **内存管理**
   - 使用 RAII 管理资源
   - 避免频繁的小内存分配
   - 重用缓冲区

## 依赖项

- 标准 C++ 库
- C++11 或更高版本
- 无外部依赖

## 版本历史

- v2.0: 添加 SIMD 优化
- v1.5: 支持更多 Unicode 版本
- v1.0: 初始版本

## 贡献指南

1. 遵循现有代码风格
2. 添加单元测试
3. 更新文档
4. 性能回归测试