# Unicode - Unicode 字符处理库

Unicode 处理库提供了完整的 Unicode 字符集支持，包括标准化、字符集操作、国际化域名处理等功能，是 YTsaurus 系统中处理多语言文本的核心组件。

## 🎯 核心功能

### Unicode 标准化 (Normalization)

Unicode 标准化是将 Unicode 文本转换为标准形式的过程，确保不同编码方式的相同字符具有相同的字节表示。

#### 四种标准化形式

```cpp
#include <library/cpp/unicode/normalization/normalization.h>

using namespace NUnicode;

// 规范化形式
enum ENormalization {
    NFD,  // 规范分解 (Canonical Decomposition)
    NFC,  // 规范分解 + 规范组合
    NFKD, // 兼容性分解 (Compatibility Decomposition)
    NFKC  // 兼容性分解 + 规范组合
};

// 使用标准化器
TNormalizer<NFC> normalizer;
TUtf32String normalized = normalizer.Normalize(inputString);

// 或者使用便利函数
TString result = Normalize<NFC>(utf8String);

// 批量标准化
Normalize<NFD>(input.begin(), input.size(), output);
```

#### 标准化形式详解

| 形式 | 中文名称 | 特点 | 适用场景 |
|------|----------|------|----------|
| **NFD** | 规范分解 | 将复合字符分解为基础字符+组合字符 | 文本比较、搜索 |
| **NFC** | 规范组合 | 分解后尽可能重新组合 | **推荐默认**、存储、网络传输 |
| **NFKD** | 兼容性分解 | 包含兼容性分解（如上标变普通字符） | 文本搜索、索引 |
| **NFKC** | 兼容性组合 | 兼容性分解 + 规范组合 | 数据清洗、规范化 |

#### 实际应用示例

```cpp
// 示例：处理不同的 "é" 表示方式
TString input1 = "é";           // U+00E9 (组合形式)
TString input2 = "e\u0301";     // e + ́ (分解形式)

TString normalized1 = Normalize<NFC>(input1);
TString normalized2 = Normalize<NFC>(input2);

// 现在两个字符串完全相同
assert(normalized1 == normalized2);

// 兼容性示例：处理上标数字
TString superscript = "H₂O";    // 使用上标 2
TString regular = Normalize<NFKC>(superscript);
// 结果: "H2O"
```

### Unicode 字符集 (UnicodeSet)

高效的 Unicode 字符集表示和操作，支持复杂的字符集查询和操作。

#### 基本字符集操作

```cpp
#include <library/cpp/unicode/set/unicode_set.h>

using namespace NUnicode;

// 创建字符集
TUnicodeSet asciiChars(0x00, 0x7F);              // ASCII 字符范围
TUnicodeSet digits = TUnicodeSet(WC_DIGIT);      // 数字字符类别
TUnicodeSet customSet("abc123");                 // 从字符串创建

// 字符集操作
TUnicodeSet combined = asciiChars + digits;      // 并集
TUnicodeSet complement = ~combined;              // 补集

// 字符查询
bool hasDigit = combined.Has('5');               // 检查是否包含字符
bool isEmpty = combined.Empty();                 // 检查是否为空
```

#### Unicode 类别支持

```cpp
// 支持所有 Unicode 类别
TUnicodeSet letters(WC_LETTER);                  // 所有字母
TUnicodeSet lowercase(WC_LOWER);                 // 小写字母
TUnicodeSet uppercase(WC_UPPER);                 // 大写字母
TUnicodeSet punctuation(WC_PUNCT);               // 标点符号
TUnicodeSet whitespace(WC_SPACE);                // 空白字符

// 按类别名称添加
TUnicodeSet hanChars;
hanChars.AddCategory("Han");                     // 汉字
hanChars.AddCategory("Hiragana");                // 平假名

// 混合字符集
TUnicodeSet mixed = letters + digits + punctuation;
mixed.MakeCaseInsensitive();                     // 转换为大小写不敏感
```

#### 高级字符集操作

```cpp
// 范围操作
TUnicodeSet wideChars;
wideChars.Add(0x4E00, 0x9FFF);                   // CJK 统一汉字
wideChars.Add(0x3040, 0x309F);                   // 平假名

// 字符集解析
TUnicodeSet parsedSet;
parsedSet.Parse("[a-zA-Z0-9]");                  // 正则表达式风格
parsedSet.Parse("[:Letter:]");                   // POSIX 类别风格

// 序列化
TString representation = parsedSet.ToString();   // 字符集表示
parsedSet.Save(&outputStream);                   // 保存到流
parsedSet.Load(&inputStream);                    // 从流加载
```

#### 内存优化特性

```cpp
// 高效的内存使用
TUnicodeSet smallSet('a', 'z');                  // 使用短缓冲区优化
TUnicodeSet staticSet(WC_DIGIT);                 // 引用静态数据

// 写时复制 (Copy-on-Write)
TUnicodeSet copy = smallSet;                     // 共享数据
copy.Add('0');                                   // 独立修改，不影响原集合
```

### Punycode 编码

支持国际化域名 (IDN) 的 Punycode 编码解码，符合 RFC 3492 标准。

#### 基础 Punycode 操作

```cpp
#include <library/cpp/unicode/punycode/punycode.h>

// Unicode 到 Punycode 转换
TUtf16String unicodeText = L"测试";
TString punycode = WideToPunycode(unicodeText);
// 结果: "xn--0zwm56d"

// Punycode 到 Unicode 转换
TUtf16String decoded = PunycodeToWide(punycode);
assert(decoded == unicodeText);
```

#### 域名处理

```cpp
// 完整域名处理 (自动添加 ACE 前缀)
TUtf16String unicodeDomain = L"测试.中国";
TString punycodeDomain = HostNameToPunycode(unicodeDomain);
// 结果: "xn--0zwm56d.xn--fiqs8s"

// 反向转换
TUtf16String original = PunycodeToHostName(punycodeDomain);

// 容错版本 (失败时返回原始字符串)
TString safePunycode = ForceHostNameToPunycode(unicodeDomain);
TUtf16String safeUnicode = ForcePunycodeToHostName(punycodeDomain);

// 检测是否为 Punycode
bool isPunycode = CanBePunycodeHostName("xn--example.com");
```

#### 错误处理

```cpp
try {
    TString result = WideToPunycode(unicodeText);
} catch (const TPunycodeError& e) {
    // 处理 Punycode 编码错误
    Cerr << "Punycode 编码失败: " << e.what() << Endl;
}
```

## 🚀 高级特性

### 性能优化

#### 内存管理
- **零拷贝操作**: 大量操作使用字符串视图避免内存分配
- **共享缓冲区**: UnicodeSet 支持数据共享，减少内存占用
- **分层存储**: 小集合使用栈缓冲区，大集合使用堆分配

#### 算法优化
- **范围查询优化**: UnicodeSet 使用二分查找加速字符查询
- **增量更新**: 支持字符集的增量修改
- **缓存友好**: 数据结构设计考虑 CPU 缓存局部性

### 扩展功能

#### 自定义字符集
```cpp
// 创建自定义字符集
TUnicodeSet customChars;

// 添加特定范围
customChars.Add(0x1F600, 0x1F64F);  // Emoji 表情

// 添加 Unicode 块
customChars.AddCategory("Emoticons");

// 混合操作
TUnicodeSet allowedChars = customChars + TUnicodeSet(WC_BASIC_LATIN);
allowedChars.Invert();  // 转换为禁用字符集
```

#### 字符集分析
```cpp
// 字符集统计
size_t count = 0;
for (wchar32 c = 0; c < TUnicodeSet::CODEPOINT_HIGH; ++c) {
    if (mySet.Has(c)) {
        ++count;
    }
}

// 字符集描述
TString description = mySet.ToString(true);  // 转义所有字符
```

## 📊 实际应用场景

### 1. 文本搜索和索引
```cpp
// 忽略大小写和重音符号的搜索
TUnicodeSet searchChars;
searchChars.AddCategory("Letter");
searchChars.MakeCaseInsensitive();

TNormalizer<NFKD> normalizer;
TUtf32String normalizedQuery = normalizer.Normalize(query);
TUtf32String normalizedText = normalizer.Normalize(text);

// 执行匹配...
```

### 2. 输入验证
```cpp
// 用户名验证：只允许字母、数字、下划线
TUnicodeSet allowedChars(WC_LETTER);
allowedChars.Add(WC_DIGIT);
allowedChars.Add('_');

bool isValid = true;
for (wchar32 c : username) {
    if (!allowedChars.Has(c)) {
        isValid = false;
        break;
    }
}
```

### 3. 国际化处理
```cpp
// 处理国际化域名
TString ProcessDomain(const TString& domain) {
    if (CanBePunycodeHostName(domain)) {
        return PunycodeToHostName(domain).to_utf8();
    } else {
        // 检查是否包含非 ASCII 字符
        TUtf16String unicode = UTF8ToUTF16(domain);
        return HostNameToPunycode(unicode);
    }
}
```

### 4. 文本规范化
```cpp
// 文本去重和标准化
TString NormalizeText(const TString& input) {
    // 1. Unicode 规范化
    TString normalized = Normalize<NFKC>(input);

    // 2. 大小写统一
    normalized.to_lower();

    // 3. 移除控制字符
    TUnicodeSet allowedChars(WC_PRINTABLE);
    TString result;
    for (char c : normalized) {
        if (allowedChars.Has(static_cast<wchar32>(c))) {
            result += c;
        }
    }

    return result;
}
```

## ⚡ 最佳实践

### 1. 选择合适的标准化形式
```cpp
// 数据存储和比较：使用 NFC
TString stored = Normalize<NFC>(userInput);

// 文本搜索：使用 NFKD 以获得更好的匹配
TString searchKey = Normalize<NFKD>(searchQuery);

// 数据清洗：使用 NFKC 处理兼容性字符
TString cleaned = Normalize<NFKC>(rawData);
```

### 2. 性能优化
```cpp
// 重用标准化器对象
TNormalizer<NFC> normalizer;  // 避免重复初始化

// 预检查是否需要标准化
if (!IsAlreadyNormalized<NFC>(text)) {
    return normalizer.Normalize(text);
}
```

### 3. 内存管理
```cpp
// 大量字符集操作时考虑内存使用
{
    TUnicodeSet tempSet;  // 自动析构，及时释放内存
    tempSet.Parse(complexPattern);
    // 使用 tempSet...
}  // 自动清理
```

### 4. 错误处理
```cpp
// 处理无效的 Unicode 数据
try {
    TUnicodeSet parsed;
    parsed.Parse(userInput);
} catch (const std::exception& e) {
    // 使用默认字符集或报错
    parsed = TUnicodeSet(WC_BASIC_LATIN);
}
```

## 🔗 相关模块

- **string_utils**: 字符串处理工具
- **regex**: 正则表达式支持
- **charset**: 字符集转换
- **json**: JSON 序列化中的 Unicode 处理
- **yson**: YSON 格式中的 Unicode 支持

## 📈 标准兼容性

### Unicode 标准
- **Unicode Version**: 支持最新 Unicode 标准
- **Normalization UAX #15**: 完全符合 Unicode 标准化附录
- **IDNA Standards**: 符合 RFC 3490、RFC 3492、RFC 5890

### 性能指标
- **字符集查询**: O(log n) 复杂度的范围查询
- **内存效率**: 智能缓冲区管理，平均内存节省 30-50%
- **处理速度**: 支持百万级字符的快速处理

Unicode 处理库为 YTsaurus 提供了完整的多语言文本支持，从基础的字符编码转换到复杂的国际化域名处理，覆盖了现代分布式系统中处理各种语言文本的需求。