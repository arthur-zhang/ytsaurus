# RE2 正则表达式库

## 项目概述

`NRe2` 是 YTsaurus 中对 Google RE2 正则表达式库的封装，提供了引用计数版本的 RE2 类，使其能够在 YSON 序列化的配置中便捷使用。该库解决了原生 `re2::RE2` 不可默认构造的问题，同时提供了 YSON 序列化和反序列化支持。

## 核心功能

- **引用计数支持**：提供基于 `TRefCounted` 的 RE2 包装类
- **YSON 序列化**：支持正则表达式模式字符串的序列化和反序列化
- **向后兼容**：完全兼容 RE2 库的所有功能
- **错误处理**：提供详细的正则表达式解析错误信息

## 主要接口

### TRe2 类

```cpp
#include <yt/yt/library/re2/public.h>

using namespace NYT::NRe2;

// 创建正则表达式对象
TRe2Ptr regex = New<TRe2>("\\d+");  // 匹配数字

// 检查正则表达式是否有效
if (regex->ok()) {
    // 使用正则表达式
    bool matched = RE2::FullMatch("123", *regex);
} else {
    // 处理错误
    Cout << "Regex error: " << regex->error() << Endl;
}

// 完整匹配
bool isMatch = RE2::FullMatch("hello world", *regex);

// 部分匹配
bool found = RE2::PartialMatch("abc123def", *regex);

// 提取匹配组
std::string number;
RE2::FullMatch("value: 42", *regex, &number);
```

### YSON 序列化

```cpp
#include <yt/yt/library/re2/re2.h>

// 序列化到 YSON
TRe2Ptr pattern = New<TRe2>("[a-z]+");
NYson::IYsonConsumer* consumer = ...;
Serialize(pattern, consumer);

// 从 YSON 反序列化
NYTree::INodePtr node = ...;
TRe2Ptr deserializedPattern;
Deserialize(deserializedPattern, node);

// 使用流式解析器反序列化
NYson::TYsonPullParserCursor* cursor = ...;
Deserialize(deserializedPattern, cursor);
```

## 使用方法

### 基本用法

```cpp
#include <yt/yt/library/re2/re2.h>

using namespace NYT::NRe2;

// 创建正则表达式
auto emailRegex = New<TRe2>(R"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})");

if (!emailRegex->ok()) {
    THROW_ERROR_EXCEPTION("Invalid email regex: %v", emailRegex->error());
}

// 验证邮箱
std::string email = "user@example.com";
if (RE2::FullMatch(email, *emailRegex)) {
    Cout << "Valid email" << Endl;
}
```

### 在配置中使用

```cpp
struct TConfig {
    TRe2Ptr Pattern;

    void Register(NYTree::TVisitor* visitor) {
        visitor->Visit("pattern", Pattern)
            .Default(New<TRe2>("\\w+"));
    }
};

// 配置可以通过 YSON 加载
auto config = New<TConfig>();
NYTree::INodePtr configNode = ...;
config->Load(configNode);
```

### 高级匹配操作

```cpp
auto regex = New<TRe2>("(\\d{4})-(\\d{2})-(\\d{2})");

// 提取日期组件
std::string year, month, day;
if (RE2::FullMatch("2023-12-25", *regex, &year, &month, &day)) {
    Cout << "Year: " << year << ", Month: " << month << ", Day: " << day << Endl;
}

// 替换操作
std::string text = "Date: 2023-12-25";
std::string result = RE2::Replace(text, *regex, R"(\2/\3/\1)");  // "Date: 12/25/2023"
```

## 性能考虑

- **编译开销**：正则表达式在构造时编译，建议复用 TRe2 对象
- **内存管理**：引用计数避免不必要的拷贝，支持共享所有权
- **匹配效率**：继承 RE2 的高效匹配算法，时间复杂度通常为线性

```cpp
// 推荐：复用正则表达式对象
class TextProcessor {
public:
    TextProcessor()
        : wordRegex_(New<TRe2>("\\b\\w+\\b"))
    { }

    std::vector<std::string> extractWords(const std::string& text) {
        // 复用已编译的正则表达式
        // ...
    }

private:
    TRe2Ptr wordRegex_;
};
```

## 最佳实践

1. **错误检查**：始终检查正则表达式的有效性
2. **对象复用**：避免重复创建相同的正则表达式
3. **模式优化**：使用高效的正则表达式模式
4. **异常安全**：使用 RAII 管理资源

```cpp
// 最佳实践示例
class RegexValidator {
public:
    RegexValidator(const TString& pattern) {
        regex_ = New<TRe2>(pattern);
        if (!regex_->ok()) {
            THROW_ERROR_EXCEPTION("Invalid regex pattern %v: %v",
                pattern, regex_->error());
        }
    }

    bool validate(const TString& input) const {
        return RE2::FullMatch(input, *regex_);
    }

private:
    TRe2Ptr regex_;
};
```

## 依赖项

- **contrib/libs/re2**：Google RE2 正则表达式库
- **yt/yt/core/yson**：YSON 序列化支持
- **yt/yt/core/ytree**：YSON 树形结构支持

## 注意事项

- **线程安全**：TRe2 对象在读取时是线程安全的，写入时需要同步
- **模式限制**：RE2 不支持反向引用等复杂正则特性
- **编码处理**：确保输入字符串使用正确的编码
- **性能监控**：在性能敏感的场景中监控匹配性能

```cpp
// 线程安全使用示例
class ThreadSafeRegexMatcher {
public:
    bool match(const TString& input) const {
        // 读取操作是线程安全的
        return RE2::PartialMatch(input, *regex_);
    }

private:
    const TRe2Ptr regex_ = New<TRe2>("\\btest\\b");
};
```

该库为 YTsaurus 提供了高效、安全的正则表达式处理能力，特别适用于需要正则表达式配置管理和文本处理的场景。