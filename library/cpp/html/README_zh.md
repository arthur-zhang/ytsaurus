# HTML 处理库

## 项目概述

HTML 处理库提供了一组用于处理 HTML 文本的 C++ 工具函数，主要包括 HTML 实体解码、文本转义和 PCDATA 编码/解码功能。该库严格遵循 HTML5 标准，为 Web 应用程序提供可靠的 HTML 文本处理能力。

## 主要功能

### HTML 实体处理
- 支持完整的 HTML5 命名实体和数字实体
- 提供单个字符和批量解码功能
- 支持多字符实体（双码点实体）
- 特殊的属性值解码规则

### 文本转义
- HTML 属性值转义
- HTML 文本内容转义
- 防止 XSS 攻击的安全编码

### PCDATA 处理
- HTML PCDATA 编码和解码
- 特殊字符的安全转换

## 文件说明

### `/escape/` - HTML 转义模块
- **`escape.h`** - 定义了 HTML 转义的主要接口
  - `EscapeAttributeValue()` - 转义 HTML 属性值
  - `EscapeText()` - 转义 HTML 文本内容
- **`escape.cpp`** - 转义函数的实现

### `/entity/` - HTML 实体处理模块
- **`htmlentity.h`** - HTML 实体解码的核心接口
  - `HtTryDecodeEntity()` - 尝试解码命名或数字实体
  - `HtEntDecodeStep()` - 逐步解码实体
  - `HtEntDecode()` - 完整字符串解码
  - `HtDecodeAttrToUtf8()` - 属性值特殊解码
  - `HtLinkDecode()` - 链接解码（包含 URL 编码）
- **`htmlentity.cpp`** - 实体解码实现
- **`decoder.h`** - 解码器内部接口
- **`decoder.rl6`** - Ragel 状态机定义文件

### `/pcdata/` - PCDATA 处理模块
- **`pcdata.h`** - PCDATA 编码/解码接口
  - `EncodeHtmlPcdata()` - 将文本编码为 HTML PCDATA
  - `DecodeHtmlPcdata()` - 解码 HTML PCDATA
  - `EncodeHtmlPcdataAppend()` - 追加式编码
- **`pcdata.cpp`** - PCDATA 处理实现
- **`pcdata_ut.cpp`** - 单元测试

## 使用示例

### HTML 文本转义
```cpp
#include <library/cpp/html/escape/escape.h>

// 转义 HTML 文本内容
TString userInput = "<script>alert('xss')</script>";
TString safeText = NHtml::EscapeText(userInput);
// 结果: &lt;script&gt;alert('xss')&lt;/script&gt;

// 转义 HTML 属性值
TString attrValue = "value with \"quotes\" & symbols";
TString safeAttr = NHtml::EscapeAttributeValue(attrValue);
// 结果: value with &quot;quotes&quot; &amp; symbols
```

### HTML 实体解码
```cpp
#include <library/cpp/html/entity/htmlentity.h>

// 解码命名实体
TString encoded = "Tom &amp; Jerry &lt;3";
wchar32 buffer[100];
size_t decoded = HtEntDecode(CODES_UTF8, encoded.c_str(), encoded.size(),
                           buffer, 100);

// 解码属性值中的实体
char output[256];
size_t written = HtDecodeAttrToUtf8(CODES_UTF8, "title=&quot;Test&quot;",
                                  19, output, 256);
```

### PCDATA 编码/解码
```cpp
#include <library/cpp/html/pcdata/pcdata.h>

// 编码为 PCDATA
TString text = "5 < 10 && 3 > 1";
TString encoded = EncodeHtmlPcdata(text);
// 结果: 5 &lt; 10 &amp;&amp; 3 &gt; 1

// 解码 PCDATA
TString decoded = DecodeHtmlPcdata(encoded);
// 结果: 5 < 10 && 3 > 1
```

## 实现原理

### HTML 实体解码
1. **状态机解析**：使用 Ragel 生成的状态机解析器，高效识别实体模式
2. **双重码点支持**：处理某些实体对应的多个 Unicode 字符
3. **编码兼容**：支持多种字符编码间的转换
4. **容错处理**：对格式不正确的实体提供合理的降级处理

### 文本转义算法
1. **字符映射**：根据 HTML 规范将特殊字符映射到对应实体
2. **性能优化**：避免不必要的字符串复制
3. **内存安全**：提供缓冲区长度检查和溢出保护

### PCDATA 处理
1. **双向转换**：提供编码和解码的对称操作
2. **状态保持**：可选的 `&` 符号处理控制

## 应用场景

### Web 安全
- **XSS 防护**：对用户输入进行 HTML 转义
- **内容安全策略**：确保动态生成的内容符合安全规范
- **输入验证**：处理来自不可信源的 HTML 内容

### 内容处理
- **HTML 清理**：清理和标准化 HTML 内容
- **文本提取**：从 HTML 中提取纯文本内容
- **格式转换**：在不同格式间转换文本内容

### 数据处理
- **爬虫开发**：处理网页抓取中的 HTML 实体
- **搜索引擎**：索引网页内容的预处理
- **数据迁移**：处理包含 HTML 标记的数据

## 性能特点

- **高效解析**：使用状态机实现 O(n) 时间复杂度
- **内存优化**：最小化内存分配和复制
- **批量处理**：支持批量解码以提高吞吐量
- **缓存友好**：优化的数据结构提高缓存命中率

## 标准兼容性

- **HTML5 标准**：完全符合 WHATWG HTML5 规范
- **实体集合**：支持 HTML5 定义的所有命名实体
- **数字实体**：支持十进制和十六进制数字实体
- **属性规则**：遵循属性值的特殊解析规则