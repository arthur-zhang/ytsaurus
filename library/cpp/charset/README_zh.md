# Charset 字符编码库

## 项目描述

Charset 库是 YTsaurus 中专门用于处理各种字符编码转换和操作的综合性工具库。它提供了丰富的字符集检测、编码转换、大小写不敏感字符串处理等功能，支持超过100种不同的字符编码格式。

该库在原有的俄文 README 基础上，为中文用户提供了更完整的文档说明和使用指南。

## 核心特性

### 🌍 多编码支持
- 支持超过100种字符编码格式
- 覆盖主流的单字节和多字节编码
- 包含各种国际标准编码和平台特定编码

### 🔄 编码转换
- 高效的编码间转换功能
- 基于系统 libiconv 库实现
- 支持兼容性回退机制

### 🔍 编码检测
- 智能字符集自动检测
- 支持常见的西里尔字母编码识别
- 可靠的编码验证机制

### 📝 大小写不敏感处理
- 专用的 TCiString 类
- 支持多种编码的大小写不敏感比较
- 提供相应的哈希算法支持

## 主要组件

### 1. 字符编码枚举 (ECharset)
```cpp
enum ECharset {
    CODES_UNSUPPORTED = -2,
    CODES_UNKNOWN = -1,
    CODES_WIN,              // WINDOWS_1251
    CODES_KOI8,             // KOI8_U
    CODES_UTF8,             // UTF8
    CODES_UTF_16LE,         // UTF_16LE
    CODES_UTF_16BE,         // UTF_16BE
    // ... 更多编码格式
};
```

### 2. 编码转换函数 (Recoding)
```cpp
// 主要转换函数
TString Recode(ECharset from, ECharset to, const TString& input);

// UTF-8 到宽字符串转换
TUtf16String UTF8ToWide(const char* text, size_t len, const CodePage& cp);
```

### 3. 大小写不敏感字符串 (TCiString)
```cpp
class TCiString: public TString {
    // 使用大小写不敏感的比较器和哈希
    // 支持多种编码格式
};
```

### 4. 字符编码检测 (Codepage Detection)
```cpp
// 编码自动检测功能
ECharset DetectCharset(const TString& text);
```

## 支持的编码格式

### 单字节编码
- **西里尔字母编码**: Windows-1251, KOI8-U, IBM-866, ISO-8859-5
- **欧洲语言编码**: ISO-8859 系列 (1-16), Windows-1250-1258
- **平台特定编码**: MAC 系列编码, IBM CP 系列

### 多字节编码
- **Unicode**: UTF-8, UTF-16LE, UTF-16BE
- **东亚编码**: GBK, Big5, EUC-JP, EUC-KR, Shift_JIS
- **其他国际编码**: ISO-2022 系列, 各种国家标准编码

### 特殊编码
- **Yandex 内部编码**: YANDEX (Windows-1251 的超集)
- **地区变体**: 哈萨克语、鞑靼语等语言变体

## 使用示例

### 基本编码转换
```cpp
#include <library/cpp/charset/doccodes.h>
#include <library/cpp/charset/recyr.hh>

// UTF-8 转换为 Windows-1251
TString utf8Text = "你好世界";
TString win1251Text = Recode(CODES_UTF8, CODES_WIN, utf8Text);

// Windows-1251 转换为 UTF-8
TString utf8Text = Recode(CODES_WIN, CODES_UTF8, win1251Text);
```

### 大小写不敏感字符串比较
```cpp
#include <library/cpp/charset/ci_string.h>

TCiString str1("Hello World");
TCiString str2("HELLO WORLD");

// 大小写不敏感比较
bool equal = (str1 == str2);  // 返回 true

// 可用于容器
THashMap<TCiString, int> ciMap;
ciMap["Key"] = 42;
int value = ciMap["key"];  // 可以正常获取到值
```

### 宽字符串处理
```cpp
#include <library/cpp/charset/wide.h>

// UTF-8 转宽字符串，支持编码回退
CodePage cp(CODES_WIN);
TUtf16String wideText = UTF8ToWide(utf8Text, strlen(utf8Text), cp);
```

### 编码检测
```cpp
#include <library/cpp/charset/codepage.h>

// 自动检测文本编码
TString unknownText = "一些文本...";
ECharset detectedCharset = DetectCharset(unknownText);
```

## 应用场景

### 1. 数据处理与转换
- 文件编码格式转换
- 数据库字符集处理
- 网络数据编码转换

### 2. 文本处理
- 跨编码文本搜索
- 大小写不敏感字符串操作
- 多语言文本处理

### 3. 兼容性处理
- 遗留系统编码支持
- 平台间数据交换
- 国际化应用支持

### 4. 数据导入导出
- 各种编码格式的文件处理
- 字符编码标准化
- 数据清洗与转换

## 架构设计

### 核心模块
- **doccodes.h**: 编码格式定义和枚举
- **codepage.h/cpp**: 基础编码页面操作
- **recyr.hh/cpp**: 编码转换实现
- **wide.h/cpp**: 宽字符串处理
- **ci_string.h/cpp**: 大小写不敏感字符串

### Lite 版本
`library/cpp/charset/lite` 子库提供了不依赖 libiconv 的精简功能：
- 基本编码转换
- UTF-8 处理功能
- 核心字符串操作

### 依赖关系
- **libiconv**: 编码转换核心库
- **util 基础库**: 字符串和容器支持
- **测试框架**: 单元测试和集成测试

## 性能特点

### 高效转换
- 基于系统优化的 libiconv 库
- 支持大块数据的流式处理
- 内存使用优化

### 低开销检测
- 快速编码识别算法
- 最小化内存分配
- 支持增量检测

## 最佳实践

### 1. 编码选择建议
```cpp
// 推荐使用 UTF-8 作为内部编码格式
const ECharset DEFAULT_CHARSET = CODES_UTF8;

// 遗留数据兼容性处理
if (IsLegacyData(data)) {
    data = Recode(detect, CODES_UTF8, data);
}
```

### 2. 错误处理
```cpp
try {
    TString result = Recode(from, to, input);
} catch (const std::exception& e) {
    // 处理编码转换错误
    // 可以尝试其他编码或使用兼容性转换
}
```

### 3. 性能优化
```cpp
// 对于大量转换操作，考虑复用 CodePage 对象
CodePage converter(CODES_WIN);
for (const auto& item : items) {
    TString converted = converter.Recode(item);
}
```

### 4. 内存管理
```cpp
// 使用 TUninitialized 避免不必要的初始化
TCiString str(TUninitialized());
str.resize(expectedSize);
// 直接填充数据...
```

## 版本兼容性

### 向后兼容
- 保持与现有代码的兼容性
- 支持遗留的 Yandex 内部编码
- 渐进式迁移路径

### 新增编码
- 通过枚举扩展支持新编码
- 保持编码检测的准确性
- 更新转换映射表

## 测试覆盖

### 单元测试
- 编码转换正确性测试
- 边界条件测试
- 错误处理测试

### 性能测试
- 大数据量转换性能
- 内存使用效率
- 并发安全性测试

### 兼容性测试
- 跨平台编码一致性
- 不同 libiconv 版本兼容性
- 历史数据兼容性验证

## 限制与注意事项

### 使用限制
- 某些冷门编码可能支持有限
- 编码检测不是 100% 准确
- 大文件处理需要内存考虑

### 最佳实践
- 优先使用 UTF-8 编码
- 提供编码验证机制
- 处理转换失败的情况

## 总结

Charset 库为 YTsaurus 系统提供了完整的字符编码处理能力，是处理多语言数据和编码转换的核心组件。通过合理使用其提供的功能，可以有效解决各种字符编码相关的问题，确保数据的正确性和系统的兼容性。