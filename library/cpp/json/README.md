# JSON 库

高性能的 JSON 解析、生成和处理库。

## 概述

该库提供了完整的 JSON 数据格式支持，包括高效的解析器、生成器、查询语言等功能。设计用于处理大规模的 JSON 数据，在性能和内存使用方面都进行了优化。

## 核心特性

### 高性能解析
- **流式解析**: 支持大规模 JSON 文件的流式处理
- **内存高效**: 最小化内存分配和拷贝
- **错误恢复**: 智能的错误检测和恢复机制
- **编码支持**: 支持 UTF-8 等多种编码

### 数据操作
- **DOM 操作**: 完整的文档对象模型
- **查询语言**: 类似 XPath 的 JSON 查询
- **路径操作**: JSONPath 路径表达式
- **数据验证**: JSON Schema 验证支持

### 序列化支持
- **快速序列化**: 高效的 JSON 生成
- **格式化输出**: 美化的 JSON 格式化
- **压缩输出**: 紧凑的 JSON 格式
- **自定义序列化**: 支持自定义类型序列化

## 主要组件

### 核心解析器
```cpp
#include <json/json.h>

// 解析 JSON 字符串
TJsonValue ParseJson(const TString& jsonStr) {
    TJsonParser parser;
    return parser.Parse(jsonStr);
}

// 从文件解析
TJsonValue LoadJsonFromFile(const TString& filePath) {
    TFile file(filePath, OpenExisting | RdOnly);
    TString content = file.ReadAll();
    return ParseJson(content);
}
```

### JSON 值类型
```cpp
TJsonValue value;

// 不同类型的值
value = true;                           // 布尔值
value = 123;                            // 整数
value = 3.14;                           // 浮点数
value = "hello world";                  // 字符串
value = TJsonValue::CreateArray();      // 数组
value = TJsonValue::CreateMap();        // 对象

// 类型检查
if (value.IsBoolean()) { /* ... */ }
if (value.IsInteger()) { /* ... */ }
if (value.IsString()) { /* ... */ }
if (value.IsArray()) { /* ... */ }
if (value.IsMap()) { /* ... */ }
```

### 数组和对象操作
```cpp
// 数组操作
TJsonArray array = TJsonValue::CreateArray();
array.PushBack(1);
array.PushBack("hello");
array.PushBack(true);

for (const auto& item : array) {
    std::cout << item.ToString() << std::endl;
}

// 对象操作
TJsonObject object = TJsonValue::CreateMap();
object["name"] = "John";
object["age"] = 30;
object["active"] = true;

for (const auto& [key, value] : object) {
    std::cout << key << ": " << value.ToString() << std::endl;
}
```

## 使用示例

### 基本解析和生成
```cpp
#include <json/json.h>

void BasicExample() {
    // 解析 JSON 字符串
    TString jsonStr = R"({
        "name": "Alice",
        "age": 25,
        "skills": ["C++", "Python", "JavaScript"],
        "active": true,
        "score": 95.5
    })";

    TJsonValue value = ParseJson(jsonStr);

    // 访问数据
    TString name = value["name"].GetString();
    int age = value["age"].GetInteger();
    bool active = value["active"].GetBoolean();

    // 访问数组
    TJsonArray skills = value["skills"].GetArray();
    for (const auto& skill : skills) {
        std::cout << skill.GetString() << std::endl;
    }

    // 生成 JSON
    TJsonObject result = TJsonValue::CreateMap();
    result["status"] = "success";
    result["data"] = value;

    std::cout << result.ToString() << std::endl;
}
```

### JSON 查询
```cpp
#include <json/query.h>

void JsonQueryExample() {
    TJsonValue data = LoadJsonFromFile("large_data.json");

    // 使用 JSONPath 查询
    TJsonQuery query("$.users[?(@.age > 30)].name");
    auto names = query.Evaluate(data);

    // 复杂查询
    TJsonQuery complexQuery("$.store.book[*].author");
    auto authors = complexQuery.Evaluate(data);

    for (const auto& author : authors) {
        std::cout << author.GetString() << std::endl;
    }
}
```

### 流式处理
```cpp
#include <json/stream.h>

void StreamingExample() {
    // 流式解析大文件
    TJsonStreamReader reader("large_file.json");

    TJsonValue item;
    while (reader.Read(item)) {
        ProcessJsonItem(item);
    }

    // 流式生成
    TJsonStreamWriter writer("output.json");
    writer.StartArray();

    for (const auto& data : GenerateData()) {
        writer.Write(ToJsonValue(data));
    }

    writer.EndArray();
}
```

### 自定义序列化
```cpp
// 自定义类型序列化
struct TPerson {
    TString Name;
    int Age;
    TVector<TString> Hobbies;
};

void SerializePerson(const TPerson& person, TJsonValue& json) {
    TJsonObject obj = TJsonValue::CreateMap();
    obj["name"] = person.Name;
    obj["age"] = person.Age;

    TJsonArray hobbies = TJsonValue::CreateArray();
    for (const auto& hobby : person.Hobbies) {
        hobbies.PushBack(hobby);
    }
    obj["hobbies"] = hobbies;

    json = obj;
}

TPerson DeserializePerson(const TJsonValue& json) {
    TPerson person;
    person.Name = json["name"].GetString();
    person.Age = json["age"].GetInteger();

    const TJsonArray& hobbies = json["hobbies"].GetArray();
    for (const auto& hobby : hobbies) {
        person.Hobbies.push_back(hobby.GetString());
    }

    return person;
}
```

## 性能优化

### 内存优化
```cpp
// 使用字符串视图减少拷贝
void ProcessJson(const TStringView& jsonStr) {
    TJsonParser parser;
    parser.SetCopyStrings(false);  // 避免字符串拷贝
    auto value = parser.Parse(jsonStr);
}

// 预分配内存
TJsonArray array;
array.Reserve(10000);  // 预分配容量
```

### 解析优化
```cpp
// 批量解析
TVector<TJsonValue> ParseBatch(const TVector<TString>& jsonStrings) {
    TJsonParser parser;
    TVector<TJsonValue> results;
    results.reserve(jsonStrings.size());

    for (const auto& jsonStr : jsonStrings) {
        results.push_back(parser.Parse(jsonStr));
    }

    return results;
}

// 异步解析
TFuture<TJsonValue> AsyncParseJson(const TString& jsonStr) {
    return Async([jsonStr]() {
        TJsonParser parser;
        return parser.Parse(jsonStr);
    });
}
```

### 生成优化
```cpp
// 紧凑格式生成
TJsonWriter writer;
writer.SetCompact(true);  // 生成紧凑的 JSON
TString result = writer.Write(value);

// 自定义格式化
TJsonFormatter formatter;
formatter.SetIndent(2);
formatter.SetNewLine("\n");
TString formatted = formatter.Format(value);
```

## 错误处理

### 解析错误
```cpp
try {
    TJsonValue value = ParseJson(invalidJson);
} catch (const TJsonParseException& e) {
    std::cerr << "Parse error at line " << e.GetLine()
              << ", column " << e.GetColumn() << ": "
              << e.what() << std::endl;
} catch (const TJsonException& e) {
    std::cerr << "JSON error: " << e.what() << std::endl;
}
```

### 类型安全访问
```cpp
// 安全的类型访问
TString GetStringValue(const TJsonValue& value, const TString& key) {
    if (value.IsMap() && value.HasKey(key)) {
        const auto& item = value[key];
        if (item.IsString()) {
            return item.GetString();
        }
    }
    return TString();  // 默认值
}

// 带默认值的访问
int GetIntValue(const TJsonValue& value, const TString& key, int defaultValue) {
    if (value.IsMap() && value.HasKey(key)) {
        const auto& item = value[key];
        if (item.IsInteger()) {
            return item.GetInteger();
        }
    }
    return defaultValue;
}
```

## JSON Schema 验证

```cpp
#include <json/schema.h>

void SchemaValidationExample() {
    // 定义 Schema
    TString schemaStr = R"({
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer", "minimum": 0},
            "email": {"type": "string", "format": "email"}
        },
        "required": ["name", "age"]
    })";

    TJsonSchema schema = ParseJsonSchema(schemaStr);
    TJsonValidator validator(schema);

    // 验证数据
    TJsonValue data = ParseJson(jsonData);
    TValidationResult result = validator.Validate(data);

    if (!result.IsValid()) {
        for (const auto& error : result.GetErrors()) {
            std::cout << "Validation error: " << error.GetMessage()
                      << " at path: " << error.GetPath() << std::endl;
        }
    }
}
```

## 高级功能

### JSON Patch 操作
```cpp
#include <json/patch.h>

void JsonPatchExample() {
    TJsonValue original = ParseJson(R"({"name": "John", "age": 30})");
    TJsonArray patch = ParseJson(R"([
        {"op": "replace", "path": "/age", "value": 31},
        {"op": "add", "path": "/email", "value": "john@example.com"}
    ])");

    TJsonValue result = ApplyJsonPatch(original, patch);
}
```

### JSON Merge
```cpp
void JsonMergeExample() {
    TJsonValue base = ParseJson(R"({"a": 1, "b": 2})");
    TJsonValue update = ParseJson(R"({"b": 3, "c": 4})");

    TJsonValue merged = MergeJson(base, update);
    // 结果: {"a": 1, "b": 3, "c": 4}
}
```

### JSON Pointer
```cpp
void JsonPointerExample() {
    TJsonValue data = ParseJson(R"({
        "users": [
            {"name": "Alice", "age": 25},
            {"name": "Bob", "age": 30}
        ]
    })");

    // 使用 JSON Pointer 路径
    TJsonValue name = GetJsonPointer(data, "/users/1/name");
    // 结果: "Bob"

    SetJsonPointer(data, "/users/1/age", 31);
    // 更新第二个用户的年龄
}
```

## 应用场景

### 配置管理
```cpp
class TConfigManager {
private:
    TJsonValue config_;

public:
    void LoadConfig(const TString& configFile) {
        config_ = LoadJsonFromFile(configFile);
    }

    template<typename T>
    T GetConfig(const TString& path, const T& defaultValue = T{}) const {
        TJsonValue value = GetJsonPointer(config_, path);
        if (value.IsUndefined()) {
            return defaultValue;
        }
        return FromJson<T>(value);
    }
};
```

### API 响应处理
```cpp
class TApiClient {
public:
    TJsonArray GetUsers() {
        THttpResponse response = HttpGet("/api/users");
        TJsonValue data = ParseJson(response.GetBody());
        return data.GetArray();
    }

    TJsonValue GetUser(const TString& userId) {
        THttpResponse response = HttpGet("/api/users/" + userId);
        return ParseJson(response.GetBody());
    }
};
```

### 数据转换
```cpp
class TDataTransformer {
public:
    TJsonValue TransformToApi(const TDataRecord& record) {
        TJsonObject result = TJsonValue::CreateMap();
        result["id"] = record.Id;
        result["name"] = record.Name;
        result["timestamp"] = record.Timestamp;

        // 转换状态枚举
        TString status = RecordStatusToString(record.Status);
        result["status"] = status;

        return result;
    }
};
```

## 最佳实践

### 错误处理
- 始终检查 JSON 值的类型
- 提供合理的默认值
- 捕获和处理解析异常

### 性能优化
- 避免不必要的字符串拷贝
- 预分配容器容量
- 使用流式处理处理大文件

### 内存管理
- 及时释放大型 JSON 对象
- 使用智能指针管理生命周期
- 避免循环引用

这个 JSON 库为 YTsaurus 项目提供了强大的数据序列化和交换能力，支持从简单的配置文件到复杂的数据传输协议等各种应用场景。