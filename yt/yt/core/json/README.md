# JSON 模块

## 模块概述

`yt/yt/core/json` 模块是 YTsaurus 分布式系统的 JSON 处理库，提供了完整的 JSON 解析、生成、序列化和反序列化功能。该模块实现了高效的 JSON 流式解析器，支持大文件处理和内存优化的操作，为 YTsaurus 系统中的配置管理、数据交换和 API 通信提供 JSON 格式支持。

## 主要功能

### 1. JSON 解析
- **流式解析**: 支持大文件的流式 JSON 解析
- **SAX 解析**: 基于事件的 SAX 解析器
- **DOM 解析**: 内存中的 DOM 树解析
- **错误处理**: 详细的 JSON 解析错误信息

### 2. JSON 生成
- **格式化输出**: 美化的 JSON 格式化输出
- **紧凑输出**: 压缩的 JSON 紧凑输出
- **编码转换**: Unicode 字符编码处理
- **转义处理**: 特殊字符的正确转义

### 3. 类型转换
- **序列化**: C++ 对象到 JSON 的序列化
- **反序列化**: JSON 到 C++ 对象的反序列化
- **类型映射**: C++ 类型到 JSON 类型的映射
- **自定义转换**: 支持自定义类型转换器

### 4. 配置集成
- **JSON 配置**: 基于 JSON 的配置文件格式
- **动态配置**: JSON 格式的动态配置更新
- **验证规则**: JSON 配置的验证规则
- **默认值**: JSON 配置的默认值处理

## 文件说明

### 核心文件
- **json.h**: JSON 核心接口定义
- **json_callbacks.h/c**: JSON 回调解析器
- **json_parser.h**: JSON 解析器实现
- **json_writer.h**: JSON 写入器实现

### 辅助文件
- **config.h/c**: JSON 配置管理
- **helpers.h/c**: JSON 处理辅助函数
- **json_value.h**: JSON 值类型定义

## 使用示例

### 基本 JSON 解析
```cpp
#include <yt/yt/core/json/json.h>

using namespace NYT::NJson;

// 解析 JSON 字符串
auto jsonValue = ParseJson(R"({
    "name": "YTsaurus",
    "version": "1.0.0",
    "features": ["storage", "processing"]
})");

// 访问 JSON 值
auto name = jsonValue["name"].GetString();
auto version = jsonValue["version"].GetString();
auto features = jsonValue["features"].GetArray();
```

### JSON 生成
```cpp
#include <yt/yt/core/json/json_writer.h>

// 创建 JSON 对象
TJsonValue jsonObject;
jsonObject["name"] = TJsonValue("YTsaurus");
jsonObject["version"] = TJsonValue("1.0.0");

// 添加数组
TJsonValue features(TJsonValue::Type::Array);
features.PushBack(TJsonValue("storage"));
features.PushBack(TJsonValue("processing"));
jsonObject["features"] = features;

// 生成 JSON 字符串
TString jsonStr = WriteJson(jsonObject, EJsonFormat::Pretty);
```

### 流式解析
```cpp
#include <yt/yt/core/json/json_callbacks.h>

// 使用 SAX 解析器解析大 JSON 文件
class MyJsonHandler : public TJsonCallbacks {
public:
    bool OnString(const TStringBuf& key, const TStringBuf& value) override {
        std::cout << key << ": " << value << std::endl;
        return true;
    }
};

MyJsonHandler handler;
ParseJson(jsonData, &handler);
```

### 类型序列化
```cpp
struct MyStruct {
    std::string name;
    int version;
    std::vector<std::string> features;
};

// 序列化到 JSON
MyStruct obj{"YTsaurus", 1, {"storage", "processing"}};
auto json = ConvertToJson(obj);

// 反序列化
auto parsedObj = ConvertFromJson<MyStruct>(json);
```

## 配置选项

### 解析配置
- **严格模式**: 严格的 JSON 语法验证
- **注释支持**: 是否允许 JSON 注释
- **尾随逗号**: 是否允许尾随逗号
- **错误恢复**: 错误时的恢复策略

### 生成配置
- **缩进**: JSON 格式化的缩进空格数
- **排序**: 对象键的字母排序
- **转义**: Unicode 字符的转义策略
- **精度**: 浮点数的输出精度

## 性能特性

- **流式处理**: 支持超大 JSON 文件的流式处理
- **内存高效**: 最小化内存分配和拷贝
- **快速解析**: 高性能的 JSON 解析器
- **零拷贝**: 尽可能避免数据拷贝操作

## 依赖关系

- **yt/yt/core/misc**: 基础工具和字符串处理
- **yt/yt/core/ytree**: YTree 配置系统集成
- **标准库**: C++ 标准库的字符串和容器

## 扩展点

- **自定义解析器**: 实现自定义的 JSON 解析器
- **类型转换器**: 为自定义类型实现转换器
- **验证器**: 实现 JSON 数据验证逻辑
- **格式化器**: 自定义 JSON 输出格式

## 最佳实践

1. **错误处理**: 始终检查 JSON 解析的错误状态
2. **内存管理**: 对于大文件使用流式解析避免内存溢出
3. **类型安全**: 使用强类型的 JSON 访问方法
4. **配置验证**: 验证 JSON 配置的完整性和正确性
5. **性能优化**: 在性能关键路径使用预编译的 JSON 模式