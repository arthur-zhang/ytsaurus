# Scheme - 数据结构描述和操作库

## 项目概述

Scheme 库为 YTsaurus 提供了强大的动态数据结构描述和操作能力。该库实现了类似 JSON 的数据模型，支持多种数据类型（空值、布尔、数值、字符串、数组、字典等），并提供了高效的序列化/反序列化、数据访问和操作接口。

## 核心功能

### 数据类型支持

- **Null**: 空值类型
- **Bool**: 布尔类型 (true/false)
- **IntNumber**: 整数类型
- **FloatNumber**: 浮点数类型
- **String**: 字符串类型
- **Array**: 数组类型，支持元素序列
- **Dict**: 字典类型，支持键值对映射

### 操作特性

- **写时复制 (COW)**: 高效的内存管理，支持共享和独立修改
- **类型安全**: 强类型检查和转换
- **序列化支持**: JSON 和 Protobuf 格式的互转换
- **合并操作**: 支持复杂的数据合并策略
- **路径访问**: 支持点号路径访问嵌套数据

## 重要文件说明

### 核心头文件

- **`scheme.h/cpp`**: 主要的 Scheme 库接口，定义了 `TValue` 核心类和相关操作
- **`scimpl.h/cpp`**: Scheme 内部实现细节，包含核心数据结构和方法
- **`scimpl_private.h/cpp`**: 私有实现细节，内部使用的工具函数
- **`scheme_cast.h`**: 类型转换和强制转换接口
- **`fwd.h`**: 前向声明和基础类型定义

### 格式支持

- **`scimpl_protobuf.cpp`**: Protobuf 格式的序列化/反序列化实现
- **`scimpl_json_read.cpp`**: JSON 格式读取和解析实现
- **`scimpl_json_write.cpp`**: JSON 格式写入和序列化实现
- **`scimpl_select.rl6`**: Ragel 状态机定义，用于高效的文本解析

### 定义和工具

- **`scimpl_defs.h`**: 核心定义和常量

## 使用示例

### 基础数据操作

```cpp
#include <library/cpp/scheme/scheme.h>

using namespace NSc;

// 创建不同类型的值
TValue nullValue = TValue::Null();
TValue boolValue = TValue::Bool(true);
TValue intValue = TValue::IntNumber(42);
TValue floatValue = TValue::FloatNumber(3.14);
TValue stringValue = TValue::String("Hello, World!");

// 创建数组
TValue array = TValue::Array();
array.PushBack(TValue::IntNumber(1));
array.PushBack(TValue::String("test"));
array.PushBack(TValue::Bool(true));

// 创建字典
TValue dict = TValue::Dict();
dict.Set("name", TValue::String("YTsaurus"));
dict.Set("version", TValue::String("1.0"));
dict.Set("port", TValue::IntNumber(8080));
```

### 复杂嵌套结构

```cpp
// 创建复杂的嵌套数据结构
TValue config = TValue::Dict();

// 数据库配置
TValue database = TValue::Dict();
database.Set("host", TValue::String("localhost"));
database.Set("port", TValue::IntNumber(5432));
database.Set("name", TValue::String("ytsaurus"));

// 连接池配置
TValue connectionPool = TValue::Dict();
connectionPool.Set("max_connections", TValue::IntNumber(100));
connectionPool.Set("min_connections", TValue::IntNumber(10));
connectionPool.Set("timeout", TValue::FloatNumber(30.0));

database.Set("connection_pool", connectionPool);
config.Set("database", database);

// 服务配置数组
TValue services = TValue::Array();
TValue webService = TValue::Dict();
webService.Set("name", TValue::String("web"));
webService.Set("port", TValue::IntNumber(80));
services.PushBack(webService);

TValue apiService = TValue::Dict();
apiService.Set("name", TValue::String("api"));
apiService.Set("port", TValue::IntNumber(8080));
services.PushBack(apiService);

config.Set("services", services);
```

### 数据访问和查询

```cpp
// 使用点号路径访问嵌套数据
TValue dbPort = config.Select("database.port");  // 获取数据库端口
TValue serviceName = config.Select("services.0.name");  // 获取第一个服务名称

// 安全访问，返回默认值
TValue maxConn = config.Select("database.connection_pool.max_connections", TValue::IntNumber(50));

// 检查路径是否存在
bool hasDatabase = config.Has("database");
bool hasTimeout = config.Has("database.connection_pool.timeout");

// 遍历数组
if (services.IsArray()) {
    for (size_t i = 0; i < services.GetSize(); ++i) {
        TValue service = services[i];
        if (service.Has("name") && service.Has("port")) {
            TString name = service["name"].GetString();
            int port = service["port"].GetInt();
            // 处理服务配置...
        }
    }
}

// 遍历字典
if (database.IsDict()) {
    for (auto it = database.Begin(); it != database.End(); ++it) {
        TString key = it.GetKey();
        TValue value = it.GetValue();
        // 处理配置项...
    }
}
```

### JSON 序列化/反序列化

```cpp
#include <library/cpp/scheme/scimpl_json_read.h>
#include <library/cpp/scheme/scimpl_json_write.h>

// JSON 序列化
TString jsonString = JsonWrite(config, true);  // true 表示美化输出

// JSON 反序列化
TValue parsedConfig;
if (JsonRead(jsonString, parsedConfig)) {
    // 成功解析 JSON
    TString version = parsedConfig.Select("version", "unknown").GetString();
} else {
    // 解析失败处理
}
```

### Protobuf 支持

```cpp
#include <library/cpp/scheme/scimpl_protobuf.h>

// 转换为 Protobuf 格式
TString protobufData = ProtobufWrite(config);

// 从 Protobuf 格式读取
TValue configFromProto;
if (ProtobufRead(protobufData, configFromProto)) {
    // 成功解析 Protobuf 数据
}
```

### 数据合并

```cpp
// 定义合并选项
TMergeOptions options;
options.ArrayMergeMode = TMergeOptions::EArrayMergeMode::Merge;

// 基础配置
TValue baseConfig = TValue::Dict();
baseConfig.Set("server", TValue::Dict());
baseConfig["server"].Set("host", TValue::String("localhost"));
baseConfig["server"].Set("port", TValue::IntNumber(8080));
baseConfig.Set("features", TValue::Array());
baseConfig["features"].PushBack(TValue::String("basic_auth"));

// 覆盖配置
TValue overrideConfig = TValue::Dict();
overrideConfig.Set("server", TValue::Dict());
overrideConfig["server"].Set("port", TValue::IntNumber(9090));  // 覆盖端口
overrideConfig.Set("debug", TValue::Bool(true));               // 新增调试模式

// 合并配置
TValue mergedConfig = baseConfig.Merge(overrideConfig, options);
```

### 写时复制 (COW) 语义

```cpp
// 原始数据
TValue original = TValue::Dict();
original.Set("value", TValue::IntNumber(42));

// 浅拷贝（共享数据）
TValue shallowCopy = original;  // 默认浅拷贝
shallowCopy.Set("shared", TValue::Bool(true));

// 此时 original 和 shallowCopy 都包含 "shared" 字段

// 深拷贝（独立数据）
TValue deepCopy = original.Clone();
deepCopy.Set("independent", TValue::String("test"));

// 只有 deepCopy 包含 "independent" 字段，original 不受影响

// 修改触发 COW
shallowCopy = shallowCopy.Clone();  // 强制分离
shallowCopy.Set("separated", TValue::Bool(true));
```

## 实现原理

### 核心数据结构

```cpp
class TValue {
private:
    mutable TCorePtr TheCore;     // 引用计数的核心数据结构
    bool CopyOnWrite = false;     // 写时复制标志

public:
    enum class EType {
        Null, Bool, IntNumber, FloatNumber,
        String, Array, Dict
    };
};
```

### 内存管理

- **引用计数**: 使用智能指针管理数据生命周期
- **写时复制**: 修改时自动进行深度复制
- **内存池**: 高效的内存分配和回收

### 性能优化

- **零拷贝访问**: 直接访问内部数据结构
- **延迟序列化**: 按需进行序列化操作
- **缓存友好**: 数据结构设计考虑 CPU 缓存效率

## 应用场景

### 1. 配置管理

```cpp
class ConfigurationManager {
private:
    TValue config;

public:
    bool LoadFromFile(const TString& filePath) {
        // 读取配置文件
        TFileInput file(filePath);
        TString jsonContent = file.ReadAll();

        return JsonRead(jsonContent, config);
    }

    template<typename T>
    T GetConfigValue(const TString& path, const T& defaultValue = T{}) {
        TValue value = config.Select(path);
        if (value.IsNull()) {
            return defaultValue;
        }

        if constexpr (std::is_same_v<T, TString>) {
            return value.GetString();
        } else if constexpr (std::is_integral_v<T>) {
            return static_cast<T>(value.GetInt());
        } else if constexpr (std::is_floating_point_v<T>) {
            return static_cast<T>(value.GetFloat());
        }

        return defaultValue;
    }

    void UpdateConfig(const TString& path, const TValue& newValue) {
        // 支持点号路径更新
        auto parts = StringSplitter(path).Split('.');
        TValue* current = &config;

        for (auto it = parts.begin(); std::next(it) != parts.end(); ++it) {
            TString part = *it;
            if (!current->Has(part)) {
                current->Set(part, TValue::Dict());
            }
            *current = (*current)[part];
        }

        current->Set(*std::prev(parts.end()), newValue);
    }
};
```

### 2. API 响应处理

```cpp
class ApiResponseHandler {
public:
    struct UserInfo {
        TString id;
        TString name;
        TString email;
        TVector<TString> roles;
    };

    TMaybe<UserInfo> ParseUserInfo(const TString& jsonResponse) {
        TValue response;
        if (!JsonRead(jsonResponse, response)) {
            return Nothing();
        }

        if (!response.Has("data") || response["data"].IsNull()) {
            return Nothing();
        }

        TValue userData = response["data"];
        UserInfo info;

        info.id = userData.Select("id", "").GetString();
        info.name = userData.Select("name", "").GetString();
        info.email = userData.Select("email", "").GetString();

        // 解析角色数组
        if (userData.Has("roles") && userData["roles"].IsArray()) {
            TValue rolesArray = userData["roles"];
            for (size_t i = 0; i < rolesArray.GetSize(); ++i) {
                info.roles.push_back(rolesArray[i].GetString());
            }
        }

        return info;
    }
};
```

### 3. 数据验证和转换

```cpp
class DataValidator {
public:
    bool ValidateSchema(const TValue& data, const TValue& schema) {
        // 简化的 JSON Schema 验证实现
        if (!schema.IsDict()) {
            return false;
        }

        TString type = schema.Select("type", "").GetString();

        if (type == "object") {
            if (!data.IsDict()) {
                return false;
            }

            if (schema.Has("required") && schema["required"].IsArray()) {
                TValue required = schema["required"];
                for (size_t i = 0; i < required.GetSize(); ++i) {
                    TString field = required[i].GetString();
                    if (!data.Has(field)) {
                        return false;  // 缺少必需字段
                    }
                }
            }

            return true;
        } else if (type == "array") {
            return data.IsArray();
        } else if (type == "string") {
            return data.IsString();
        } else if (type == "number") {
            return data.IsIntNumber() || data.IsFloatNumber();
        } else if (type == "boolean") {
            return data.IsBool();
        }

        return false;
    }

    TValue ConvertToFormat(const TValue& data, const TString& format) {
        if (format == "json") {
            return JsonWrite(data);
        } else if (format == "protobuf") {
            return ProtobufWrite(data);
        } else if (format == "yaml") {
            // YAML 格式转换实现
            return ConvertToYaml(data);
        }

        return TValue::Null();
    }
};
```

### 4. 动态配置更新

```cpp
class DynamicConfig {
private:
    TValue currentConfig;
    THashMap<TString, std::function<void(const TValue&)>> watchers;

public:
    void RegisterWatcher(const TString& path, std::function<void(const TValue&)> callback) {
        watchers[path] = callback;
    }

    void UpdateConfig(const TString& jsonConfig) {
        TValue newConfig;
        if (!JsonRead(jsonConfig, newConfig)) {
            return;
        }

        // 检测变化并通知观察者
        for (const auto& [path, callback] : watchers) {
            TValue oldValue = currentConfig.Select(path);
            TValue newValue = newConfig.Select(path);

            if (!IsEqual(oldValue, newValue)) {
                callback(newValue);
            }
        }

        currentConfig = newConfig;
    }

private:
    bool IsEqual(const TValue& a, const TValue& b) {
        // 简化的值比较实现
        if (a.GetType() != b.GetType()) {
            return false;
        }

        switch (a.GetType()) {
            case TValue::EType::Null:
                return b.IsNull();
            case TValue::EType::Bool:
                return a.GetBool() == b.GetBool();
            case TValue::EType::IntNumber:
                return a.GetInt() == b.GetInt();
            case TValue::EType::FloatNumber:
                return a.GetFloat() == b.GetFloat();
            case TValue::EType::String:
                return a.GetString() == b.GetString();
            default:
                return false;  // 复杂类型需要更深入的比较
        }
    }
};
```

## 最佳实践

### 1. 性能优化

```cpp
// 重用 TValue 对象
class OptimizedParser {
private:
    static thread_local TValue parseBuffer;  // 线程本地缓冲区

public:
    TMaybe<TValue> ParseJson(const TString& json) {
        if (JsonRead(json, parseBuffer)) {
            return parseBuffer.Clone();  // 返回副本以避免外部修改
        }
        return Nothing();
    }
};
```

### 2. 错误处理

```cpp
template<typename T>
T SafeGet(const TValue& value, const TString& path, const T& defaultValue = T{}) {
    try {
        TValue result = value.Select(path);
        if (result.IsNull()) {
            return defaultValue;
        }

        if constexpr (std::is_same_v<T, TString>) {
            return result.GetString();
        } else if constexpr (std::is_integral_v<T>) {
            return static_cast<T>(result.GetInt());
        } else if constexpr (std::is_floating_point_v<T>) {
            return static_cast<T>(result.GetFloat());
        } else if constexpr (std::is_same_v<T, bool>) {
            return result.GetBool();
        }

        return defaultValue;
    } catch (const std::exception& e) {
        // 记录错误并返回默认值
        Cerr << "获取配置值失败 " << path << ": " << e.what() << Endl;
        return defaultValue;
    }
}
```

### 3. 类型安全的访问器

```cpp
class TypedAccessor {
public:
    template<typename T>
    static T Get(const TValue& value, const TString& path, const T& defaultValue = T{}) {
        static_assert(
            std::is_arithmetic_v<T> || std::is_same_v<T, TString> || std::is_same_v<T, bool>,
            "支持的类型: 数值类型, TString, bool"
        );

        return SafeGet(value, path, defaultValue);
    }

    static TVector<TString> GetStringArray(const TValue& value, const TString& path) {
        TVector<TString> result;
        TValue arrayValue = value.Select(path);

        if (arrayValue.IsArray()) {
            result.reserve(arrayValue.GetSize());
            for (size_t i = 0; i < arrayValue.GetSize(); ++i) {
                if (arrayValue[i].IsString()) {
                    result.push_back(arrayValue[i].GetString());
                }
            }
        }

        return result;
    }
};
```

## 相关模块

- **json**: JSON 处理库
- **protobuf**: Protocol Buffers 支持
- **config**: 配置管理系统
- **yaml**: YAML 格式支持
- **serialization**: 序列化框架

Scheme 库为 YTsaurus 提供了强大的动态数据处理能力，特别适用于配置管理、API 数据交换、动态配置等场景，是系统中数据处理的核心组件。