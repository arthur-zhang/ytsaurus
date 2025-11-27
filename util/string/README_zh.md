# 字符串处理库

本模块提供高效的字符串处理功能，包括字符编码、字符串转换、转义处理、十六进制编码等工具。

## 功能特性

### 字符编码
- ASCII 字符处理
- 编码检测和转换
- 字符集支持
- Unicode 处理

### 字符串操作
- 高效的字符串转换
- 数值转换函数
- 字符串构建器
- 迭代器支持

### 转义和编码
- 各种转义格式
- 十六进制编码/解码
- Base64 编码
- URL 编码

## 主要组件

### 核心功能
- **ascii.h/cpp** - ASCII 字符处理
- **cast.h/cpp** - 字符串类型转换
- **cstriter.h/cpp** - C 字符串迭代器
- **builder.h/cpp** - 字符串构建器

### 编码转换
- **escape.h/cpp** - 字符串转义
- **hex.h/cpp** - 十六进制编码
- **base64.h** - Base64 编码（如果存在）

## 使用方法

### ASCII 字符处理
```cpp
#include "util/string/ascii.h"

// 字符类型检查
bool isAlpha = IsAlpha(ch);      // 是否为字母
bool isDigit = IsDigit(ch);      // 是否为数字
bool isSpace = IsSpace(ch);      // 是否为空格
bool isLower = IsLower(ch);      // 是否为小写
bool isUpper = IsUpper(ch);      // 是否为大写

// 字符转换
char lower = ToLower(ch);
char upper = ToUpper(ch);

// 字符串转换
TString lowerStr = to_lower("HELLO");
TString upperStr = to_upper("hello");
```

### 字符串转换
```cpp
#include "util/string/cast.h"

// 字符串到数值
int i = FromString<int>("123");
double d = FromString<double>("3.14");
bool b = FromString<bool>("true");

// 数值到字符串
TString str1 = ToString(123);
TString str2 = ToString(3.14);

// 错误处理
try {
    int value = FromString<int>("invalid");
} catch (const TBadCastException& e) {
    // 处理转换错误
}
```

### 字符串构建器
```cpp
#include "util/string/builder.h"

// 创建构建器
TStringBuilder builder(1024);  // 预分配 1KB

// 追加各种类型
builder << "Hello, " << 42 << " worlds!";

// 格式化追加
builder << Sprintf("Value: %.2f", 3.14159);

// 获取结果
TString result = builder;
```

### 转义处理
```cpp
#include "util/string/escape.h"

// C 风格转义
TString escaped = CEscape("Hello\nWorld");  // "Hello\\nWorld"
TString unescaped = CUnescape("Hello\\nWorld");  // "Hello\nWorld"

// JSON 转义
TString jsonEscaped = JsonEscape("\"quote\"");  // "\\\"quote\\\""

// HTML 转义
TString htmlEscaped = HtmlEscape("<tag>");  // "&lt;tag&gt;"
```

### 十六进制编码
```cpp
#include "util/string/hex.h"

// 十六进制编码
TString hexStr = HexEncode(data, size);  // "48656c6c6f"

// 十六进制解码
TString decoded = HexDecode("48656c6c6f");  // "Hello"

// 大小写格式
TString upperHex = HexEncodeUpper(data, size);  // "48656C6C6F"

// 带分隔符
TString formatted = HexEncode(data, size, ":");  // "48:65:6c:6c:6f"
```

### 字符串迭代
```cpp
#include "util/string/cstriter.h"

// 字符串迭代器
TCStringIterator iter("Hello, World!");
while (iter) {
    char ch = *iter;
    ProcessChar(ch);
    ++iter;
}

// 反向迭代
TCStringReverseIterator riter(str);
while (riter) {
    char ch = *riter;
    ProcessChar(ch);
    ++riter;
}
```

## 字符类型检查

### ASCII 字符分类
```cpp
// 字母数字
bool isAlnum = IsAlnum(ch);  // A-Z, a-z, 0-9

// 空白字符
bool isSpace = IsSpace(ch);  // 空格、制表、换行等

// 控制字符
bool isCntrl = IsCntrl(ch);  // ASCII 0-31, 127

// 可打印字符
bool isPrint = IsPrint(ch);  // ASCII 32-126

// 图形字符
bool isGraph = IsGraph(ch);  // 可打印字符，不包括空格
```

## 高级功能

### 分词处理
```cpp
#include "util/string/split.h"  // 如果存在

// 字符串分割
TVector<TString> parts;
Split("a,b,c", ",", parts);

// 带限制的分割
SplitLimit("a,b,c,d", ",", parts, 2);  // 最多分成 2 部分
```

### 模式匹配
```cpp
// 通配符匹配
bool matches = WildcardMatch("hello*.txt", "hello_world.txt");

// 正则表达式支持（如果可用）
bool matches2 = RegExMatch(R"(\d{4}-\d{2}-\d{2})", "2023-01-01");
```

### 字符串模板
```cpp
#include "util/string/template.h"  // 如果存在

// 简单模板
TTemplate tmpl("Hello, ${name}!");
TString result = tmpl.Substitute("name", "World");
```

## 性能优化

### 避免拷贝
```cpp
// 使用 TStringBuf 避免拷贝
void ProcessString(const TStringBuf& str);

// 移动语义
TString str = BuildString();  // 返回值优化
```

### 内存预分配
```cpp
// 预分配足够空间
TStringBuilder builder;
builder.Reserve(1024);

// 使用 reserve 避免重新分配
TString str;
str.reserve(1000);
str = data;
```

### 字符串池
```cpp
#include "util/string/pool.h"  // 如果存在

// 使用字符串池
TStringPool pool;
TString interned = pool.Intern("frequently_used_string");
```

## 测试

### 单元测试
```bash
# 运行所有测试
./ut/string_ut

# 运行特定测试
./ut/string_ut --gtest_filter="CastTest.*"
```

### 性能测试
```bash
# 字符串转换性能
./ut/string_perf --test=cast

# 编码解码性能
./ut/string_perf --test=encoding
```

## 最佳实践

1. **字符串构建**
   - 使用 TStringBuilder 拼接
   - 预分配足够空间
   - 避免频繁的 + 操作

2. **类型转换**
   - 使用 FromString/ToString
   - 处理转换异常
   - 验证输入范围

3. **编码处理**
   - 明确编码格式
   - 处理非法字符
   - 选择合适的转义方式

## 安全考虑

1. **缓冲区溢出**
   - 使用安全的字符串函数
   - 检查长度限制
   - 避免固定大小缓冲区

2. **注入攻击**
   - 正确转义特殊字符
   - 验证输入内容
   - 使用参数化查询

## 平台支持

- Linux (x86_64, ARM64)
- macOS (x86_64, ARM64)
- Windows (x86_64)

## 依赖项

- 标准 C++ 库
- C++11 或更高版本
- 无外部依赖

## 版本历史

- v3.0: 添加更多编码支持
- v2.5: 性能优化
- v2.0: 重构 API
- v1.0: 初始版本