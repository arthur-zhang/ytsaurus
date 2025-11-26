# String Utils - 字符串工具库

字符串工具库提供了一系列功能强大的字符串处理、编码解码、格式转换等功能，是 YTsaurus 系统中处理文本数据的核心组件。

## 🎯 核心功能

### 编码解码模块

#### Base64 编解码
- **标准 Base64**: 符合 RFC 4648 标准的 Base64 编解码
- **URL 安全 Base64**: 适用于 URL 和文件名的 Base64 变体
- **无填充 Base64**: 移除填充字符的紧凑格式

#### Base32 编解码
- **标准 Base32**: RFC 4648 Base32 编码支持
- **安全变体**: 适用于敏感场景的 Base32 实现

### URL 和 CGI 处理

#### 引号转义 (Quote)
```cpp
#include <library/cpp/string_utils/quote/quote.h>

// CGI 转义 - 将空格转换为 +，特殊字符转换为 %xx
TString escaped = CGIEscapeRet("hello world!");

// URL 转义 - 保留更多字符，适用于 URL 路径
TString urlEscaped = UrlEscapeRet("path/to/file");

// 带安全字符的引用
TString quoted = Quote("/path/to/resource", "/");
```

#### 转义函数对比
| 函数 | 空格处理 | 适用场景 | 特殊字符 |
|------|----------|----------|----------|
| `CGIEscape` | 转为 `+` | CGI 参数 | 全部转义 |
| `UrlEscape` | 保留空格 | URL 路径 | 选择性转义 |
| `Quote` | 保留空格 | 用户定义 | 可配置安全字符 |

### 文本格式处理

#### CSV 解析
符合 RFC 4180 标准的 CSV 解析器，支持：
- 自定义分隔符和引号字符
- 复杂字段值处理
- 流式行处理

```cpp
#include <library/cpp/string_utils/csv/csv.h>

using namespace NCsvFormat;

// 解析 CSV 字符串
TString csvData = "name,age,city\n\"John Doe\",30,\"New York\"";
CsvSplitter splitter(csvData, ',', '"');

while (splitter.Step()) {
    TStringBuf field = splitter.Consume();
    // 处理字段...
}

// 直接转换为向量
TVector<TString> fields = static_cast<TVector<TString>>(splitter);
```

#### 大小写解析
支持人类可读的大小格式字符串解析：

```cpp
#include <library/cpp/string_utils/parse_size/parse_size.h>

using namespace NSize;

// 解析各种大小格式
ui64 size1 = ParseSize("10KB");     // 10240
ui64 size2 = ParseSize("1.5GB");    // 1610612736
ui64 size3 = ParseSize("100MB");    // 104857600

// 便利的构造函数
TSize size = FromGigaBytes(2);      // 2GB
ui64 bytes = size.GetValue();       // 2147483648
```

### 安全字符串处理

#### 密钥字符串 (SecretString)
专为存储敏感数据设计的安全字符串类：

```cpp
#include <library/cpp/string_utils/secret_string/secret_string.h>

using namespace NSecretString;

// 创建安全字符串
TSecretString secret("my_secret_password");

// 获取值（自动零终止）
TZtStringBuf value = secret.Value();

// 特性：
// 1. 从核心转储中排除 (MADV_DONTDUMP)
// 2. 释放时自动清零内存
// 3. 防止意外的内存泄露
```

#### 安全特性
- **内存保护**: 使用 `madvise(MADV_DONTDUMP)` 防止核心转储
- **自动清零**: 析构时自动将内存清零
- **调试器防护**: 在调试器中难以直接访问内容

### 字符串转换

#### 字符串扫描
提供高效的字符串扫描和分析功能：

```cpp
#include <library/cpp/string_utils/scan/scan.h>

// 快速数字解析
TStringBuf str = "12345";
int value;
bool success = ScanInt(str, &value);  // value = 12345, success = true
```

#### 宽松转义器
处理包含转义字符的字符串：

```cpp
#include <library/cpp/string_utils/relaxed_escaper/relaxed_escaper.h>

// 处理转义序列
TString input = "hello\\nworld\\t!";
TString unescaped = RelaxedUnescape(input);
// 结果: "hello\nworld\t!"
```

### 编辑距离算法

#### Levenshtein 距离
计算字符串之间的编辑距离：

```cpp
#include <library/cpp/string_utils/levenshtein_diff/levenshtein_diff.h>

// 计算编辑距离
size_t distance = LevenshteinDistance("kitten", "sitting");
// 结果: 3 (k→s, e→i, 添加 g)
```

### 字符串缓冲区

#### 零终止字符串缓冲区 (ZtStrBuf)
提供零终止的字符串视图：

```cpp
#include <library/cpp/string_utils/ztstrbuf/ztstrbuf.h>

// 创建零终止字符串缓冲区
TZtStringBuf buf("hello");

// 自动保证零终止
const char* cstr = buf.c_str();  // "hello"
size_t len = buf.size();          // 5
```

## 📊 性能特性

### 内存效率
- **零拷贝设计**: 大量操作使用字符串视图避免内存拷贝
- **预计算缓冲区**: 编解码操作提供精确的缓冲区大小计算
- **内存池优化**: 频繁分配的字符串使用内存池

### 处理速度
- **SIMD 优化**: 关键路径使用 SIMD 指令加速
- **无分支算法**: 编解码算法采用无分支实现
- **缓存友好**: 数据结构设计考虑 CPU 缓存局部性

### 安全性
- **边界检查**: 所有操作都有严格的边界检查
- **内存安全**: 防止缓冲区溢出和越界访问
- **异常安全**: 提供强异常安全保证

## 🛠️ 使用场景

### Web 应用开发
```cpp
// URL 参数处理
TString param = CGIEscapeRet(userInput);

// CSV 数据导出
TString csvData = GenerateCSV();
CsvSplitter parser(csvData);
```

### 数据处理管道
```cpp
// 大小格式解析
ui64 fileSize = ParseSize(configValue["max_file_size"]);

// 安全密码存储
TSecretString dbPassword(passwordFromEnv);
```

### 网络协议实现
```cpp
// Base64 编码
TString encoded = Base64EncodeUrlNoPadding(binaryData);

// URL 路径处理
TString safePath = Quote(userPath, "/\\");
```

## ⚡ 最佳实践

### 1. 选择合适的编码
- **Web URL**: 使用 `Base64EncodeUrlNoPadding`
- **标准传输**: 使用 `Base64Encode`
- **文件名**: 使用 `Base32` 编码

### 2. 安全字符串使用
```cpp
// 好的做法：及时销毁敏感数据
{
    TSecretString apiKey(secretValue);
    // 使用 API 密钥...
    // 析构时自动清零内存
}
```

### 3. 性能优化
```cpp
// 避免不必要的拷贝
TStringBuf input = largeString;
auto result = Base64Encode(input, buffer);  // 直接写入缓冲区

// 预计算缓冲区大小
constexpr size_t bufSize = Base64EncodeBufSize(inputSize);
char buffer[bufSize];
```

### 4. 错误处理
```cpp
try {
    TString decoded = Base64StrictDecode(encoded);
} catch (const yexception& e) {
    // 处理解码错误
    Cerr << "Base64 解码失败: " << e.what() << Endl;
}
```

## 🔗 相关模块

- **unicode**: Unicode 字符串处理
- **regex**: 正则表达式支持
- **json**: JSON 序列化/反序列化
- **yson**: YSON 格式处理
- **protobuf**: Protocol Buffers 支持

## 📈 扩展性

### 添加新的编码格式
1. 继承现有接口模式
2. 提供缓冲区大小计算函数
3. 实现编码/解码函数
4. 添加相应的单元测试

### 自定义字符串处理器
```cpp
// 示例：自定义 CSV 处理器
class CustomCsvProcessor {
public:
    void ProcessField(const TStringBuf field) {
        // 自定义字段处理逻辑
    }
};
```

字符串工具库为 YTsaurus 提供了全面的文本处理能力，从基本的编码转换到安全的密钥管理，覆盖了现代分布式系统中的各种字符串处理需求。