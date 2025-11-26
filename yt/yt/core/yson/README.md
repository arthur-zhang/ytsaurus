# YSON 模块

## 模块概述

`yt/yt/core/yson` 模块是 YTsaurus 分布式系统的原生数据序列化格式 YSON (YTsaurus Serialized Object Notation) 的实现库。YSON 是一种高性能的二进制序列化格式，类似于 JSON 但具有更好的性能和更丰富的类型支持。该模块提供 YSON 的解析、生成、序列化和反序列化功能，为 YTsaurus 系统的数据存储、网络传输和配置管理提供高效的数据格式支持。

## 主要功能

### 1. YSON 解析
- **二进制解析**: 高效的二进制 YSON 解析
- **文本解析**: 可读的文本 YSON 格式解析
- **流式解析**: 支持大文件的流式解析
- **类型推断**: 自动类型推断和转换

### 2. YSON 生成
- **二进制生成**: 高效的二进制 YSON 生成
- **文本生成**: 可读的文本 YSON 格式生成
- **格式化输出**: 美化的 YSON 格式化
- **类型标记**: 完整的类型信息标记

### 3. 类型系统
- **基础类型**: 支持整数、浮点、字符串、布尔等
- **集合类型**: 支持列表、映射等集合类型
- **特殊类型**: 支持 null、yson64 等特殊类型
- **类型转换**: 类型间的安全转换

### 4. 性能优化
- **零拷贝**: 尽可能避免数据拷贝
- **内存池**: 优化内存分配和释放
- **批量操作**: 批量序列化和反序列化
- **缓存优化**: 解析结果的缓存机制

## YSON 格式特性

### 二进制 YSON
- **紧凑高效**: 比文本格式更紧凑
- **类型信息**: 包含完整的类型信息
- **快速解析**: 二进制格式快速解析
- **向后兼容**: 格式版本兼容性

### 文本 YSON
- **可读性**: 人类可读的文本格式
- **调试友好**: 便于调试和测试
- **向后兼容**: 与二进制格式兼容
- **简洁语法**: 类似 JSON 的简洁语法

## 使用示例

### YSON 解析
```cpp
#include <yt/yt/core/yson/parser.h>

using namespace NYT::NYson;

// 解析文本 YSON
TYsonString ysonText = TYsonString(TStringBuf("{key=value; items=[1,2,3]}"));
TYsonStringBuf parsed = ParseYsonStringBuffer(ysonText);

// 解析二进制 YSON
TString binaryData = GetBinaryYsonData();
auto node = ConvertToNode(TYsonString(binaryData));
```

### YSON 生成
```cpp
#include <yt/yt/core/yson/writer.h>

// 创建 YSON 构建器
TStringBuilderOutput output;
TYsonWriter writer(&output, EYsonFormat::Text);

// 写入 YSON 数据
writer.OnBeginMap();
writer.OnKeyedItem("key");
writer.OnStringScalar("value");
writer.OnKeyedItem("items");
writer.OnBeginList();
writer.OnInt64Scalar(1);
writer.OnInt64Scalar(2);
writer.OnInt64Scalar(3);
writer.OnEndList();
writer.OnEndMap();

TString ysonResult = output.Str();
```

### 类型转换
```cpp
#include <yt/yt/core/yson/consumer.h>

// 从 YSON 转换到 C++ 类型
auto mapNode = ConvertToNode(ysonString)->AsMap();
auto key = mapNode->GetChildValueOrThrow<TString>("key");

// 从 C++ 类型转换到 YSON
std::vector<int> items = {1, 2, 3};
auto ysonNode = ConvertToNode(items);
auto ysonString = ConvertToYsonString(items);
```

### 流式处理
```cpp
// 使用 SAX 风格的 YSON 解析器
class MyYsonConsumer : public IYsonConsumer {
public:
    void OnStringScalar(TStringBuf value) override {
        std::cout << "String: " << value << std::endl;
    }

    void OnInt64Scalar(i64 value) override {
        std::cout << "Int: " << value << std::endl;
    }

    void OnBeginMap() override { /* 处理映射开始 */ }
    void OnEndMap() override { /* 处理映射结束 */ }
    // ... 其他回调方法
};

MyYsonConsumer consumer;
ParseYsonStringBuffer(ysonData, &consumer);
```

## 配置选项

### 解析选项
- **格式类型**: 文本格式或二进制格式
- **类型推断**: 是否启用类型自动推断
- **严格模式**: 严格的语法验证
- **错误恢复**: 解析错误时的恢复策略

### 生成选项
- **格式类型**: 输出的 YSON 格式
- **缩进**: 格式化时的缩进
- **类型标记**: 是否输出类型标记
- **编码**: 字符编码选择

## 性能对比

### vs JSON
- **解析速度**: YSON 比 JSON 快 2-3 倍
- **存储空间**: 二进制 YSON 比 JSON 紧凑 30-50%
- **类型安全**: 内置类型系统，无需额外 Schema
- **功能丰富**: 支持更丰富的数据类型

### vs Protocol Buffers
- **灵活性**: 无需预定义 Schema
- **调试性**: 文本格式便于调试
- **动态性**: 支持动态类型和结构
- **易用性**: 更简单易用的 API

## 依赖关系

- **yt/yt/core/misc**: 基础工具和错误处理
- **yt/yt/core/actions**: 异步操作支持
- **标准库**: C++ 标准库

## 最佳实践

1. **格式选择**: 根据场景选择文本或二进制格式
2. **错误处理**: 正确处理 YSON 解析错误
3. **性能优化**: 对于大数据使用流式处理
4. **内存管理**: 注意 YSON 对象的生命周期管理
5. **类型安全**: 使用强类型接口避免类型错误