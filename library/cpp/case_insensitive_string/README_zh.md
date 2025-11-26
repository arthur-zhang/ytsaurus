# Case Insensitive String - 大小写不敏感字符串库

## 项目概述

Case Insensitive String 是一个专业的大小写不敏感字符串处理库，提供了基于 C++ traits 机制的大小写不敏感字符串类型。该库通过自定义字符特征（char traits）实现了大小写不敏感的比较操作，同时保持了与标准字符串库的兼容性。

该库提供了两种主要实现：
- **TCaseInsensitiveString**: 基于 locale 的全 Unicode 大小写不敏感字符串
- **TCaseInsensitiveAsciiString**: 仅针对 ASCII 字符的高性能大小写不敏感字符串

## 核心功能

### 字符串类型
- **TCaseInsensitiveString**: 支持完整 Unicode 的大小写不敏感字符串
- **TCaseInsensitiveStringBuf**: 大小写不敏感字符串缓冲区视图
- **TCaseInsensitiveAsciiString**: 仅 ASCII 字符的高性能实现
- **TCaseInsensitiveAsciiStringBuf**: ASCII 字符串缓冲区视图

### 操作支持
- **大小写不敏感比较**: 支持相等性比较和排序
- **高效哈希计算**: 专门的哈希函数支持容器操作
- **标准库兼容**: 与 std::string 接口保持一致
- **流式输出**: 支持输出流操作
- **转义处理**: 提供 C 风格字符串转义功能

## 文件说明

### 核心头文件
- **`case_insensitive_string.h`**: 主要的字符串类型定义和哈希特化
- **`case_insensitive_char_traits.h`**: 字符特征类定义，实现大小写不敏感行为

### 实现文件
- **`case_insensitive_string.cpp`**: 字符串操作的实现，包含哈希计算
- **`case_insensitive_char_traits.cpp`**: 字符特征的具体实现

### 测试文件
- **`case_insensitive_string_ut.cpp`**: 完整的单元测试套件

### 构建配置
- **`CMakeLists.txt`**: CMake 构建配置
- **`ya.make`**: YaTool 构建系统配置

## 实现原理

### 1. 字符特征（Char Traits）机制
```cpp
// 基础模板，定义通用的大小写不敏感操作
template <typename TImpl>
struct TCommonCaseInsensitiveCharTraits : private std::char_traits<char> {
    static bool eq(char c1, char c2) {
        return TImpl::ToCommonCase(c1) == TImpl::ToCommonCase(c2);
    }

    static bool lt(char c1, char c2) {
        return TImpl::ToCommonCase(c1) < TImpl::ToCommonCase(c2);
    }
};
```

### 2. 两种实现策略

#### Locale 感知实现
```cpp
struct TCaseInsensitiveCharTraits {
    static char ToCommonCase(char ch) {
        return std::toupper((unsigned char)ch);  // 使用标准库的 toupper
    }
};
```

#### ASCII 优化实现
```cpp
struct TCaseInsensitiveAsciiCharTraits {
    static unsigned char ToCommonCase(char ch) {
        return AsciiToLower(ch);  // 使用快速的 ASCII 转换
    }
};
```

### 3. 高效哈希算法
```cpp
// 使用 MurmurHash2A 算法，支持批处理优化
template <auto ToLower>
struct TCaseInsensitiveHash {
    static size_t ComputeHash(const char* s, size_t n) {
        TMurmurHash2A<size_t> hash;
        std::array<char, sizeof(size_t)> buf;

        // 批处理优化：一次处理 size_t 大小的数据块
        size_t headSize = n - n % buf.size();
        for (size_t i = 0; i < headSize; i += buf.size()) {
            for (size_t j = 0; j < buf.size(); ++j) {
                buf[j] = ToLower(s[i + j]);
            }
            hash.Update(buf.data(), buf.size());
        }

        // 处理剩余字节
        return HashTail(hash, s + headSize, n - headSize);
    }
};
```

## 使用示例

### 基本使用
```cpp
#include <library/cpp/case_insensitive_string/case_insensitive_string.h>

void BasicUsage() {
    // 创建大小写不敏感字符串
    TCaseInsensitiveString str1 = "Hello World";
    TCaseInsensitiveString str2 = "HELLO WORLD";

    // 比较操作
    if (str1 == str2) {
        std::cout << "字符串相等（大小写不敏感）" << std::endl;
    }

    // 容器使用
    std::unordered_set<TCaseInsensitiveString> stringSet;
    stringSet.insert("First");
    stringSet.insert("FIRST");  // 不会重复插入

    std::cout << "集合大小: " << stringSet.size() << std::endl;  // 输出: 1
}
```

### ASCII 优化版本
```cpp
void AsciiOptimizedUsage() {
    // 使用 ASCII 优化版本，性能更好但仅支持 ASCII 字符
    TCaseInsensitiveAsciiString key1 = "user123";
    TCaseInsensitiveAsciiString key2 = "USER123";

    // 作为 Map 键值
    std::unordered_map<TCaseInsensitiveAsciiString, int> userScores;
    userScores[key1] = 100;

    // 大小写不敏感访问
    int score = userScores["user123"];     // 100
    int score2 = userScores["USER123"];    // 100
}
```

### 容器操作
```cpp
#include <unordered_map>
#include <unordered_set>

void ContainerOperations() {
    // 使用作为哈希表的键
    std::unordered_map<TCaseInsensitiveString, std::string> headers;
    headers["Content-Type"] = "application/json";
    headers["content-type"] = "text/html";  // 会覆盖之前的值

    // 检查存在性
    if (headers.contains("CONTENT-TYPE")) {
        std::cout << "找到 Content-Type 头" << std::endl;
    }

    // 集合操作
    std::unordered_set<TCaseInsensitiveString> tags;
    tags.insert("JavaScript");
    tags.insert("javascript");  // 重复项，不会插入

    std::cout << "标签数量: " << tags.size() << std::endl;  // 输出: 1
}
```

### HTTP 头处理示例
```cpp
class HttpHeaders {
private:
    std::unordered_map<TCaseInsensitiveString, TCaseInsensitiveString> headers_;

public:
    void SetHeader(const std::string& name, const std::string& value) {
        headers_[TCaseInsensitiveString(name)] = TCaseInsensitiveString(value);
    }

    std::string GetHeader(const std::string& name) const {
        auto it = headers_.find(TCaseInsensitiveString(name));
        return it != headers_.end() ? std::string(it->second) : std::string();
    }

    bool HasHeader(const std::string& name) const {
        return headers_.contains(TCaseInsensitiveString(name));
    }
};

// 使用示例
HttpHeaders headers;
headers.SetHeader("Content-Type", "application/json");
headers.SetHeader("content-length", "1024");

// 大小写不敏感访问
std::string contentType = headers.GetHeader("CONTENT-TYPE");  // "application/json"
std::string contentLength = headers.GetHeader("Content-Length");  // "1024"
```

### 配置管理示例
```cpp
class CaseInsensitiveConfig {
private:
    std::unordered_map<TCaseInsensitiveAsciiString, std::string> config_;

public:
    void Set(const std::string& key, const std::string& value) {
        config_[TCaseInsensitiveAsciiString(key)] = value;
    }

    std::optional<std::string> Get(const std::string& key) const {
        auto it = config_.find(TCaseInsensitiveAsciiString(key));
        return it != config_.end() ? std::optional<std::string>(it->second) : std::nullopt;
    }

    template<typename T>
    T GetOrDefault(const std::string& key, const T& defaultValue) const {
        auto value = Get(key);
        if (!value) return defaultValue;

        // 简单的类型转换（实际使用中可能需要更复杂的转换）
        if constexpr (std::is_same_v<T, int>) {
            return std::stoi(*value);
        } else if constexpr (std::is_same_v<T, bool>) {
            return *value == "true" || *value == "1";
        } else {
            return T(*value);
        }
    }
};

// 使用示例
CaseInsensitiveConfig config;
config.Set("database_url", "postgresql://localhost:5432/mydb");
config.Set("DATABASE_URL", "mysql://localhost:3306/mydb");  // 会覆盖之前的值

std::string dbUrl = config.GetOrDefault<std::string>("database_url", "default://");
bool debugMode = config.GetOrDefault<bool>("DEBUG_MODE", false);
```

## 性能特性

### 时间复杂度
- **字符串比较**: O(n)，其中 n 是字符串长度
- **哈希计算**: O(n)，使用 MurmurHash 算法
- **容器查找**: 平均 O(1)，基于哈希表

### 内存使用
- **字符串存储**: 与 std::string 相同
- **哈希计算**: 无额外内存开销（栈上缓冲区）
- **特化模板**: 编译时优化，零运行时开销

### 优化策略
- **批处理哈希**: 一次处理多个字符，减少函数调用开销
- **栈缓冲区**: 避免动态内存分配
- **特化模板**: 编译时类型推导，避免虚函数调用

## 与标准库的集成

### 流式输出支持
```cpp
#include <iostream>

TCaseInsensitiveString str = "Hello";
std::cout << str << std::endl;  // 输出: Hello
```

### 字符串转义
```cpp
TCaseInsensitiveString str = "Hello\nWorld";
auto escaped = EscapeC(str);  // "Hello\\nWorld"
```

### 容器特化
```cpp
// 完全支持标准容器
std::vector<TCaseInsensitiveString> vec;
std::set<TCaseInsensitiveString> set;
std::unordered_map<TCaseInsensitiveString, int> map;
```

## 应用场景

### 1. HTTP 头处理
- **请求头解析**: 大小写不敏感的 HTTP 头字段处理
- **配置文件**: 配置项名称大小写不敏感
- **API 参数**: REST API 参数名称标准化

### 2. 数据库操作
- **列名处理**: 数据库列名大小写不敏感匹配
- **表名映射**: 表名大小写统一处理
- **SQL 关键字**: SQL 关键字大小写处理

### 3. 文件系统
- **文件扩展名**: 文件扩展名大小写不敏感比较
- **路径处理**: 文件路径大小写处理（在某些文件系统上）
- **配置文件**: INI、JSON 等配置文件键名处理

### 4. 用户界面
- **搜索功能**: 大小写不敏感的用户搜索
- **标签系统**: 标签名称大小写标准化
- **用户输入**: 用户输入的大小写容错处理

## 注意事项

### 1. Null 字节处理
```cpp
// 警告：包含 null 字节的字符串比较可能不正确
TCaseInsensitiveAsciiString str1("ab\0c", 4);
TCaseInsensitiveAsciiString str2("ab\0d", 4);
// str1 == str2 可能为 true（取决于实现）
```

### 2. Locale 依赖
- **TCaseInsensitiveString**: 结果受当前 locale 影响
- **TCaseInsensitiveAsciiString**: 不受 locale 影响，结果稳定

### 3. 性能考虑
- **ASCII 版本**: 对于纯 ASCII 数据，使用 TCaseInsensitiveAsciiString
- **Unicode 支持**: 需要 Unicode 支持时使用 TCaseInsensitiveString
- **哈希缓存**: 对于频繁比较的字符串，考虑缓存哈希值

### 4. 线程安全
- **不可变性**: 字符串对象本身是线程安全的
- **容器操作**: 标准容器的线程安全规则适用

## 最佳实践

### 1. 选择合适的类型
```cpp
// 纯 ASCII 数据，高性能要求
TCaseInsensitiveAsciiString asciiKey = "user_id";

// 需要 Unicode 支持
TCaseInsensitiveString unicodeKey = "café_name";
```

### 2. 容器使用
```cpp
// 使用 reserve 减少重新哈希
std::unordered_set<TCaseInsensitiveString> tags;
tags.reserve(expectedSize);
```

### 3. 性能优化
```cpp
// 对于大量比较操作，考虑预计算哈希
auto hash = CaseInsensitiveStringHash(str.data(), str.size());
```

### 4. 错误处理
```cpp
// 检查字符串有效性后再转换
if (IsValidAscii(input)) {
    TCaseInsensitiveAsciiString str(input);
}
```

这个库为 YTsaurus 系统中需要大小写不敏感字符串处理的场景提供了高效、可靠的解决方案，特别适用于网络协议解析、配置管理和用户界面等领域。