# YSON 库

YTsaurus 原生序列化格式，提供高性能的数据序列化和反序列化功能，专为分布式系统设计。

## 📋 项目概述

YSON 是 YTsaurus 的原生数据序列化格式，类似于 JSON 但提供了更好的性能和类型支持。它支持丰富的数据类型、二进制编码、流式处理和高效的内存使用，是 YTsaurus 生态系统的核心数据格式。

### 🎯 核心特性

- **高性能**: 优化的序列化和反序列化性能
- **丰富类型**: 支持字符串、整数、浮点数、布尔值、列表、映射等
- **二进制格式**: 紧凑的二进制编码，减少存储空间
- **流式处理**: 支持流式读写，处理大规模数据
- **类型安全**: 强类型系统支持
- **向后兼容**: 支持格式版本演进
- **跨语言**: 多语言支持

## 🏗️ 架构设计

### 组件结构

```
YSON Library
├── Core              # 核心组件
│   ├── TNode          # 节点类
│   ├── TTokenizer    # 词法分析器
│   ├── TLexer        # 语法分析器
│   └── TParser       # 解析器
├── Writer            # 写入器
│   ├── TYsonWriter   # YSON 写入器
│   └── TConsumer     # 消费者接口
├── Node              # 节点操作
│   ├── TNodeVisitor  # 节点访问者
│   ├── TSerialize    # 序列化工具
│   └── TNodeUtil     # 节点工具
├── Pull              # 拉式解析器
│   ├── TYsonPullParser # 拉式解析器
│   └── TEvent         # 解析事件
└── Utilities         # 工具类
    ├── TDetail        # 内部实现
    └── TToken         # 令牌类型
```

### 数据类型系统

```
YSON Type System
├── Primitive Types   # 原始类型
│   ├── String        # 字符串
│   ├── Int64         # 64位有符号整数
│   ├── Uint64        # 64位无符号整数
│   ├── Double        # 双精度浮点数
│   ├── Boolean       # 布尔值
│   └── Null          # 空值
├── Collection Types  # 集合类型
│   ├── List          # 列表/数组
│   └── Map           # 映射/字典
└── Special Types     # 特殊类型
    └── Undefined     # 未定义值
```

## 💻 使用方法

### 基础 YSON 操作

```cpp
#include <library/cpp/yson/node/node.h>
#include <library/cpp/yson/writer.h>
#include <library/cpp/yson/consumer.h>
#include <util/stream/file.h>

void BasicYSONExample() {
    std::cout << "=== Basic YSON Operations ===" << std::endl;

    // 1. 创建基本节点
    NYT::TNode stringValue = "Hello, YSON!";
    NYT::TNode intValue = 42;
    NYT::TNode doubleValue = 3.14159;
    NYT::TNode boolValue = true;
    NYT::TNode nullValue = NYT::TNode::CreateNull();

    // 2. 创建列表
    NYT::TNode listValue = NYT::TNode::CreateList();
    listValue.Add("first item");
    listValue.Add(2);
    listValue.Add(3.14);
    listValue.Add(false);

    // 3. 创建映射
    NYT::TNode mapValue = NYT::TNode::CreateMap();
    mapValue["name"] = "Alice";
    mapValue["age"] = 30;
    mapValue["scores"] = NYT::TNode::CreateList();
    mapValue["scores"].Add(95);
    mapValue["scores"].Add(87);
    mapValue["scores"].Add(92);
    mapValue["active"] = true;

    std::cout << "Created YSON nodes:" << std::endl;
    std::cout << "String: " << stringValue.AsString() << std::endl;
    std::cout << "Int: " << intValue.AsInt64() << std::endl;
    std::cout << "Double: " << doubleValue.AsDouble() << std::endl;
    std::cout << "Bool: " << (boolValue.AsBool() ? "true" : "false") << std::endl;
    std::cout << "List size: " << listValue.AsList().Size() << std::endl;
    std::cout << "Map keys: ";
    for (const auto& [key, value] : mapValue.AsMap()) {
        std::cout << key << " ";
    }
    std::cout << std::endl;

    // 4. 节点类型检查
    std::cout << "\nNode types:" << std::endl;
    std::cout << "stringValue type: " << stringValue.GetType() << std::endl;
    std::cout << "intValue type: " << intValue.GetType() << std::endl;
    std::cout << "listValue type: " << listValue.GetType() << std::endl;
    std::cout << "mapValue type: " << mapValue.GetType() << std::endl;
}
```

### YSON 序列化和反序列化

```cpp
void YSONSerializationExample() {
    std::cout << "=== YSON Serialization ===" << std::endl;

    // 创建复杂的数据结构
    NYT::TNode config = NYT::TNode::CreateMap();
    config["application"] = "YTsaurus Worker";
    config["version"] = "1.0.0";
    config["debug"] = false;

    // 服务器配置
    config["server"] = NYT::TNode::CreateMap();
    config["server"]["host"] = "0.0.0.0";
    config["server"]["port"] = 9000;
    config["server"]["workers"] = 4;

    // 数据库配置
    config["database"] = NYT::TNode::CreateMap();
    config["database"]["driver"] = "postgres";
    config["database"]["host"] = "localhost";
    config["database"]["port"] = 5432;
    config["database"]["name"] = "ytsaurus";

    // 连接池配置
    config["database"]["pool"] = NYT::TNode::CreateMap();
    config["database"]["pool"]["min_connections"] = 2;
    config["database"]["pool"]["max_connections"] = 20;
    config["database"]["pool"]["timeout"] = 30;

    // 功能开关
    config["features"] = NYT::TNode::CreateList();
    config["features"].Add("metrics");
    config["features"].Add("profiling");
    config["features"].Add("debug_mode");

    // 序列化为字符串
    TString ysonText = NYT::NodeToYsonString(config);
    std::cout << "Serialized to YSON text:" << std::endl;
    std::cout << ysonText << std::endl;

    // 序列化为二进制
    TString ysonBinary = NYT::NodeToYsonString(config, NYson::EYsonFormat::Binary);
    std::cout << "\nBinary YSON size: " << ysonBinary.size() << " bytes" << std::endl;
    std::cout << "Text YSON size: " << ysonText.size() << " bytes" << std::endl;

    // 反序列化
    NYT::TNode parsedConfig = NYT::NodeFromYsonString(ysonText);
    std::cout << "\nDeserialized configuration:" << std::endl;
    std::cout << "Application: " << parsedConfig["application"].AsString() << std::endl;
    std::cout << "Server port: " << parsedConfig["server"]["port"].AsInt64() << std::endl;
    std::cout << "Database host: " << parsedConfig["database"]["host"].AsString() << std::endl;
    std::cout << "Pool max connections: " << parsedConfig["database"]["pool"]["max_connections"].AsInt64() << std::endl;

    // 保存到文件
    {
        TUnbufferedFileOutput output("config.yson");
        output << ysonText;
        std::cout << "Configuration saved to config.yson" << std::endl;
    }
}
```

### 流式 YSON 处理

```cpp
#include <library/cpp/yson/pull/parser.h>
#include <library/cpp/yson/detail.h>

void StreamYSONExample() {
    std::cout << "=== Stream YSON Processing ===" << std::endl;

    // 创建大型 YSON 数据
    TString largeYsonData;
    {
        TStringOutput output(largeYsonData);
        NYson::TYsonWriter writer(&output, NYson::EYsonFormat::Text);

        writer.OnBeginMap();
        writer.OnKeyedItem("users");
        writer.OnBeginList();

        // 生成大量用户数据
        for (int i = 0; i < 100000; ++i) {
            writer.OnBeginMap();
            writer.OnKeyedItem("id");
            writer.OnInt64Scalar(i);
            writer.OnKeyedItem("name");
            writer.OnStringScalar("User_" + std::to_string(i));
            writer.OnKeyedItem("age");
            writer.OnInt64Scalar(20 + (i % 50));
            writer.OnKeyedItem("active");
            writer.OnBooleanScalar(i % 3 != 0);
            writer.OnKeyedItem("score");
            writer.OnDoubleScalar(50.0 + (i % 50));
            writer.OnEndMap();
        }

        writer.OnEndList();
        writer.OnEndMap();
        writer.Finish();
    }

    std::cout << "Generated YSON data size: " << largeYsonData.size() << " bytes" << std::endl;

    // 流式处理
    {
        TMemoryInput input(largeYsonData);
        NYson::TYsonPullParser parser(&input, NYson::EYsonType::Node);

        std::atomic<int> userCount{0};
        std::atomic<int> activeCount{0};
        std::atomic<double> totalScore{0.0};
        std::atomic<int> totalAge{0};

        while (!parser.IsFinished()) {
            auto event = parser.Parse();

            if (event.GetType() == NYson::TYsonPullParser::TEvent::EType::BeginMap) {
                // 开始用户记录
                std::string name;
                int age = 0;
                bool active = false;
                double score = 0.0;
                bool hasName = false, hasAge = false, hasActive = false, hasScore = false;

                // 读取用户记录
                while (true) {
                    auto mapEvent = parser.Parse();

                    if (mapEvent.GetType() == NYson::TYsonPullParser::TEvent::EType::EndMap) {
                        break;
                    }

                    if (mapEvent.GetType() == NYson::TYsonPullParser::TEvent::EType::KeyedItem) {
                        std::string key = mapEvent.GetString();

                        auto valueEvent = parser.Parse();
                        switch (valueEvent.GetType()) {
                            case NYson::TYsonPullParser::TEvent::EType::StringScalar:
                                if (key == "name") {
                                    name = valueEvent.GetString();
                                    hasName = true;
                                }
                                break;
                            case NYson::TYsonPullParser::TEvent::EType::Int64Scalar:
                                if (key == "age") {
                                    age = valueEvent.GetInt64();
                                    hasAge = true;
                                }
                                break;
                            case NYson::TYsonPullParser::TEvent::EType::BooleanScalar:
                                if (key == "active") {
                                    active = valueEvent.GetBoolean();
                                    hasActive = true;
                                }
                                break;
                            case NYson::TYsonPullParser::TEvent::EType::DoubleScalar:
                                if (key == "score") {
                                    score = valueEvent.GetDouble();
                                    hasScore = true;
                                }
                                break;
                            default:
                                break;
                        }
                    }
                }

                // 更新统计信息
                if (hasName && hasAge && hasActive && hasScore) {
                    userCount++;
                    if (active) activeCount++;
                    totalScore += score;
                    totalAge += age;

                    // 定期报告进度
                    if (userCount % 10000 == 0) {
                        std::cout << "Processed " << userCount.load() << " users..." << std::endl;
                    }
                }
            }
        }

        std::cout << "\nProcessing completed:" << std::endl;
        std::cout << "Total users: " << userCount.load() << std::endl;
        std::cout << "Active users: " << activeCount.load() << std::endl;
        std::cout << "Average age: " << static_cast<double>(totalAge.load()) / userCount.load() << std::endl;
        std::cout << "Average score: " << totalScore.load() / userCount.load() << std::endl;
    }
}
```

### YSON 转换和操作

```cpp
void YSONTransformationExample() {
    std::cout << "=== YSON Transformation ===" << std::endl;

    // 原始数据
    TString rawData = R"({
    "employees": [
        {"name": "Alice", "department": "Engineering", "salary": 120000},
        {"name": "Bob", "department": "Sales", "salary": 80000},
        {"name": "Charlie", "department": "Engineering", "salary": 130000},
        {"name": "Diana", "department": "Marketing", "salary": 90000},
        {"name": "Eve", "department": "Engineering", "salary": 110000}
    ]
})";

    // 解析原始数据
    NYT::TNode data = NYT::NodeFromYsonString(rawData);

    // 1. 计算部门统计
    NYT::TNode departmentStats = NYT::TNode::CreateMap();
    std::map<TString, std::vector<int>> deptEmployees;
    std::map<TString, double> deptSalaries;

    const auto& employees = data["employees"].AsList();
    for (int i = 0; i < employees.Size(); ++i) {
        const auto& employee = employees[i];
        TString name = employee["name"].AsString();
        TString dept = employee["department"].AsString();
        double salary = employee["salary"].AsDouble();

        deptEmployees[dept].push_back(i);
        deptSalaries[dept] += salary;
    }

    // 构建部门统计
    for (const auto& [dept, employeeIndices] : deptEmployees) {
        NYT::TNode deptInfo = NYT::TNode::CreateMap();
        deptInfo["employee_count"] = static_cast<i64>(employeeIndices.size());
        deptInfo["total_salary"] = deptSalaries[dept];
        deptInfo["average_salary"] = deptSalaries[dept] / employeeIndices.size();

        // 添加员工列表
        NYT::TNode employeeList = NYT::TNode::CreateList();
        for (int idx : employeeIndices) {
            employeeList.Add(employees[idx]["name"]);
        }
        deptInfo["employees"] = employeeList;

        departmentStats[dept] = deptInfo;
    }

    std::cout << "Department statistics:" << std::endl;
    for (const auto& [dept, info] : departmentStats.AsMap()) {
        std::cout << dept << ": "
                  << info["employee_count"].AsInt64() << " employees, "
                  << "avg salary: $" << info["average_salary"].AsDouble()
                  << std::endl;
    }

    // 2. 数据过滤和转换
    NYT::TNode highEarners = NYT::TNode::CreateList();
    NYT::TNode engineeringEmployees = NYT::TNode::CreateList();

    for (int i = 0; i < employees.Size(); ++i) {
        const auto& employee = employees[i];
        double salary = employee["salary"].AsDouble();
        TString dept = employee["department"].AsString();

        // 高薪员工（> 100k）
        if (salary > 100000) {
            NYT::TNode highEarner = NYT::TNode::CreateMap();
            highEarner["name"] = employee["name"];
            highEarner["department"] = employee["department"];
            highEarner["salary"] = employee["salary"];
            highEarner["salary_grade"] = salary > 120000 ? "A" : "B";
            highEarners.Add(highEarner);
        }

        // 工程部员工
        if (dept == "Engineering") {
            NYT::TNode engEmployee = NYT::TNode::CreateMap();
            engEmployee["name"] = employee["name"];
            engEmployee["salary"] = employee["salary"];
            engEmployee["salary_category"] = salary > 125000 ? "Senior" :
                                           salary > 110000 ? "Middle" : "Junior";
            engineeringEmployees.Add(engEmployee);
        }
    }

    // 3. 创建汇总报告
    NYT::TNode report = NYT::TNode::CreateMap();
    report["total_employees"] = static_cast<i64>(employees.Size());
    report["high_earners_count"] = static_cast<i64>(highEarners.AsList().Size());
    report["engineering_team_size"] = static_cast<i64>(engineeringEmployees.AsList().Size());
    report["department_breakdown"] = departmentStats;
    report["high_earners"] = highEarners;
    report["engineering_employees"] = engineeringEmployees;

    // 输出报告
    TString reportYson = NYT::NodeToYsonString(report);
    std::cout << "\nGenerated report:" << std::endl;
    std::cout << reportYson << std::endl;

    // 保存报告
    TUnbufferedFileOutput output("employee_report.yson");
    output << reportYson;
    std::cout << "Report saved to employee_report.yson" << std::endl;
}
```

### YSON 验证和错误处理

```cpp
#include <library/cpp/yson/node/serialize.h>

void YSONValidationExample() {
    std::cout << "=== YSON Validation ===" << std::endl;

    // 定义验证规则
    class TUserValidator {
    public:
        struct TValidationResult {
            bool IsValid = true;
            std::vector<TString> Errors;
            std::vector<TString> Warnings;

            void AddError(const TString& error) {
                IsValid = false;
                Errors.push_back(error);
            }

            void AddWarning(const TString& warning) {
                Warnings.push_back(warning);
            }
        };

        static TValidationResult ValidateUser(const NYT::TNode& userNode) {
            TValidationResult result;

            // 检查必需字段
            if (!userNode.HasKey("name")) {
                result.AddError("Missing required field: name");
            } else if (!userNode["name"].IsString()) {
                result.AddError("Field 'name' must be a string");
            }

            if (!userNode.HasKey("email")) {
                result.AddError("Missing required field: email");
            } else if (!userNode["email"].IsString()) {
                result.AddError("Field 'email' must be a string");
            }

            if (!userNode.HasKey("age")) {
                result.AddError("Missing required field: age");
            } else if (!userNode["age"].IsInt64()) {
                result.AddError("Field 'age' must be an integer");
            } else {
                i64 age = userNode["age"].AsInt64();
                if (age < 0 || age > 150) {
                    result.AddError("Age must be between 0 and 150");
                }
                if (age < 18) {
                    result.AddWarning("User is under 18 years old");
                }
            }

            if (!userNode.HasKey("active")) {
                result.AddWarning("Missing optional field: active");
            } else if (!userNode["active"].IsBool()) {
                result.AddError("Field 'active' must be a boolean");
            }

            return result;
        }
    };

    // 测试数据
    std::vector<std::pair<TString, NYT::TNode>> testUsers = {
        // 有效用户
        {"Valid User", NYT::TNode::CreateMap()
            .Set("name", "John Doe")
            .Set("email", "john@example.com")
            .Set("age", 30)
            .Set("active", true)
        },
        // 缺少必需字段
        {"Incomplete User", NYT::TNode::CreateMap()
            .Set("name", "Jane Smith")
            .Set("age", 25)
        },
        // 类型错误
        {"Type Error User", NYT::TNode::CreateMap()
            .Set("name", "Bob Johnson")
            .Set("email", "bob@example.com")
            .Set("age", "not_a_number")
            .Set("active", "yes")
        },
        // 数值范围错误
        {"Invalid Age User", NYT::TNode::CreateMap()
            .Set("name", "Alice Brown")
            .Set("email", "alice@example.com")
            .Set("age", 200)
            .Set("active", false)
        }
    };

    std::cout << "Validating test users:" << std::endl;

    for (const auto& [description, userNode] : testUsers) {
        std::cout << "\n" << description << ":" << std::endl;

        auto validationResult = TUserValidator::ValidateUser(userNode);

        if (validationResult.IsValid) {
            std::cout << "  ✓ User validation passed" << std::endl;
        } else {
            std::cout << "  ✗ User validation failed" << std::endl;
        }

        if (!validationResult.Errors.empty()) {
            std::cout << "  Errors:" << std::endl;
            for (const auto& error : validationResult.Errors) {
                std::cout << "    - " << error << std::endl;
            }
        }

        if (!validationResult.Warnings.empty()) {
            std::cout << "  Warnings:" << std::endl;
            for (const auto& warning : validationResult.Warnings) {
                std::cout << "    - " << warning << std::endl;
            }
        }
    }
}
```

### YSON 性能优化

```cpp
#include <chrono>
#include <vector>

void YSONPerformanceExample() {
    std::cout << "=== YSON Performance Optimization ===" << std::endl;

    // 生成大量测试数据
    const size_t recordCount = 100000;
    std::vector<NYT::TNode> records;

    std::cout << "Generating " << recordCount << " test records..." << std::endl;

    auto generateStart = std::chrono::high_resolution_clock::now();

    for (size_t i = 0; i < recordCount; ++i) {
        NYT::TNode record = NYT::TNode::CreateMap();
        record["id"] = static_cast<i64>(i);
        record["name"] = "Record_" + std::to_string(i);
        record["value"] = static_cast<double>(i * 1.5);
        record["active"] = (i % 3) == 0;
        record["category"] = "Category_" + std::to_string(i % 10);

        // 添加子列表
        NYT::TNode tags = NYT::TNode::CreateList();
        tags.Add("tag1_" + std::to_string(i));
        tags.Add("tag2_" + std::to_string(i));
        record["tags"] = tags;

        records.push_back(record);
    }

    auto generateEnd = std::chrono::high_resolution_clock::now();
    auto generateDuration = std::chrono::duration_cast<std::chrono::milliseconds>(generateEnd - generateStart);

    std::cout << "Generated in " << generateDuration.count() << " ms" << std::endl;

    // 1. 单个记录序列化
    TString singleSerialized;
    auto singleStart = std::chrono::high_resolution_clock::now();

    for (const auto& record : records) {
        singleSerialized += NYT::NodeToYsonString(record) + "\n";
    }

    auto singleEnd = std::chrono::high_resolution_clock::now();
    auto singleDuration = std::chrono::duration_cast<std::chrono::milliseconds>(singleEnd - singleStart);

    std::cout << "\nSingle serialization:" << std::endl;
    std::cout << "  Time: " << singleDuration.count() << " ms" << std::endl;
    std::cout << "  Size: " << singleSerialized.size() << " bytes" << std::endl;
    std::cout << "  Throughput: " << (recordCount * 1000.0) / singleDuration.count() << " records/sec" << std::endl;

    // 2. 批量序列化
    NYT::TNode batchData = NYT::TNode::CreateList();
    for (const auto& record : records) {
        batchData.Add(record);
    }

    TString batchSerialized;
    auto batchStart = std::chrono::high_resolution_clock::now();
    batchSerialized = NYT::NodeToYsonString(batchData);
    auto batchEnd = std::chrono::high_resolution_clock::now();
    auto batchDuration = std::chrono::duration_cast<std::chrono::milliseconds>(batchEnd - batchStart);

    std::cout << "\nBatch serialization:" << std::endl;
    std::cout << "  Time: " << batchDuration.count() << " ms" << std::endl;
    std::cout << "  Size: " << batchSerialized.size() << " bytes" << std::endl;
    std::cout << "  Throughput: " << (recordCount * 1000.0) / batchDuration.count() << " records/sec" << std::endl;
    std::cout << "  Compression ratio: " << static_cast<double>(batchSerialized.size()) / singleSerialized.size() << std::endl;

    // 3. 内存优化的流式处理
    TString streamSerialized;
    auto streamStart = std::chrono::high_resolution_clock::now();

    {
        TStringOutput output(streamSerialized);
        NYson::TYsonWriter writer(&output, NYson::EYsonFormat::Text);

        writer.OnBeginList();
        for (const auto& record : records) {
            NYT::NodeToYson(record, &writer);
        }
        writer.OnEndList();
        writer.Finish();
    }

    auto streamEnd = std::chrono::high_resolution_clock::now();
    auto streamDuration = std::chrono::duration_cast<std::chrono::milliseconds>(streamEnd - streamStart);

    std::cout << "\nStream serialization:" << std::endl;
    std::cout << "  Time: " << streamDuration.count() << " ms" << std::endl;
    std::cout << "  Size: " << streamSerialized.size() << " bytes" << std::endl;
    std::cout << "  Throughput: " << (recordCount * 1000.0) / streamDuration.count() << " records/sec" << std::endl;

    // 性能对比
    std::cout << "\nPerformance comparison:" << std::endl;
    std::cout << "  Batch vs Single: " << static_cast<double>(singleDuration.count()) / batchDuration.count() << "x faster" << std::endl;
    std::cout << "  Stream vs Single: " << static_cast<double>(singleDuration.count()) / streamDuration.count() << "x faster" << std::endl;
    std::cout << "  Stream vs Batch: " << static_cast<double>(batchDuration.count()) / streamDuration.count() << "x faster" << std::endl;
}
```

## 🔧 高级特性

### 自定义 YSON 消费者

```cpp
// 自定义 YSON 消费者，用于特定数据处理
class TStatisticsConsumer : public NYson::TYsonConsumerBase {
public:
    struct TStatistics {
        size_t MapCount = 0;
        size_t ListCount = 0;
        size_t StringCount = 0;
        size_t Int64Count = 0;
        size_t DoubleCount = 0;
        size_t BoolCount = 0;
        size_t NullCount = 0;
        size_t TotalBytes = 0;
    };

    explicit TStatisticsConsumer(TStatistics& stats)
        : Stats_(stats)
    {}

    void OnStringScalar(TStringBuf value) override {
        Stats_.StringCount++;
        Stats_.TotalBytes += value.size();
    }

    void OnInt64Scalar(i64 value) override {
        Stats_.Int64Count++;
        Stats_.TotalBytes += sizeof(i64);
    }

    void OnUint64Scalar(ui64 value) override {
        Stats_.Int64Count++;  // Count as int64 for simplicity
        Stats_.TotalBytes += sizeof(ui64);
    }

    void OnDoubleScalar(double value) override {
        Stats_.DoubleCount++;
        Stats_.TotalBytes += sizeof(double);
    }

    void OnBooleanScalar(bool value) override {
        Stats_.BoolCount++;
        Stats_.TotalBytes += sizeof(bool);
    }

    void OnEntity() override {
        Stats_.NullCount++;
    }

    void OnBeginList() override {
        Stats_.ListCount++;
    }

    void OnEndList() override {}

    void OnBeginMap() override {
        Stats_.MapCount++;
    }

    void OnEndMap() override {}

    void OnKeyedItem(TStringBuf key) override {
        Stats_.TotalBytes += key.size();
    }

    void OnAttributes() override {}

    void OnBeginAttributes() override {}

    void OnEndAttributes() override {}

private:
    TStatistics& Stats_;
};

void CustomConsumerExample() {
    std::cout << "=== Custom YSON Consumer ===" << std::endl;

    // 创建复杂的 YSON 数据
    TString complexData = NYT::NodeToYsonString(NYT::TNode::CreateMap()
        .Set("users", NYT::TNode::CreateList()
            .Add(NYT::TNode::CreateMap()
                .Set("id", 1)
                .Set("name", "Alice")
                .Set("active", true)
                .Set("score", 95.5))
            .Add(NYT::TNode::CreateMap()
                .Set("id", 2)
                .Set("name", "Bob")
                .Set("active", false)
                .Set("score", 87.2)))
        .Set("metadata", NYT::TNode::CreateMap()
            .Set("version", "1.0")
            .Set("created_at", 1640995200)
            .Set("tags", NYT::TNode::CreateList()
                .Add("production")
                .Add("v1"))));

    std::cout << "Analyzing YSON data structure..." << std::endl;

    TStatisticsConsumer::TStatistics stats;
    TStatisticsConsumer consumer(stats);

    // 解析并分析数据
    TMemoryInput input(complexData);
    NYson::Parse(&consumer, &input, NYson::EYsonType::Node);

    std::cout << "YSON Analysis Results:" << std::endl;
    std::cout << "  Maps: " << stats.MapCount << std::endl;
    std::cout << "  Lists: " << stats.ListCount << std::endl;
    std::cout << "  Strings: " << stats.StringCount << std::endl;
    std::cout << "  Integers: " << stats.Int64Count << std::endl;
    std::cout << "  Doubles: " << stats.DoubleCount << std::endl;
    std::cout << "  Booleans: " << stats.BoolCount << std::endl;
    std::cout << "  Nulls: " << stats.NullCount << std::endl;
    std::cout << "  Estimated total bytes: " << stats.TotalBytes << std::endl;
}
```

## 🧪 测试和验证

### 单元测试示例

```cpp
#include <library/cpp/testing/gtest/gtest.h>

class YSONTest : public ::testing::Test {
protected:
    void SetUp() override {
        // 创建测试数据
        TestNode_ = NYT::TNode::CreateMap();
        TestNode_["string_value"] = "test_string";
        TestNode_["int_value"] = 42;
        TestNode_["double_value"] = 3.14159;
        TestNode_["bool_value"] = true;
        TestNode_["null_value"] = NYT::TNode::CreateNull();
        TestNode_["list_value"] = NYT::TNode::CreateList();
        TestNode_["list_value"].Add("item1");
        TestNode_["list_value"].Add(2);
        TestNode_["list_value"].Add(false);
    }

    NYT::TNode TestNode_;
};

TEST_F(YSONTest, BasicSerialization) {
    TString ysonText = NYT::NodeToYsonString(TestNode_);
    NYT::TNode parsedNode = NYT::NodeFromYsonString(ysonText);

    EXPECT_EQ(parsedNode["string_value"].AsString(), TestNode_["string_value"].AsString());
    EXPECT_EQ(parsedNode["int_value"].AsInt64(), TestNode_["int_value"].AsInt64());
    EXPECT_DOUBLE_EQ(parsedNode["double_value"].AsDouble(), TestNode_["double_value"].AsDouble());
    EXPECT_EQ(parsedNode["bool_value"].AsBool(), TestNode_["bool_value"].AsBool());
    EXPECT_TRUE(parsedNode["null_value"].IsNull());
    EXPECT_EQ(parsedNode["list_value"].AsList().Size(), TestNode_["list_value"].AsList().Size());
}

TEST_F(YSONTest, TypeChecking) {
    EXPECT_TRUE(TestNode_["string_value"].IsString());
    EXPECT_TRUE(TestNode_["int_value"].IsInt64());
    EXPECT_TRUE(TestNode_["double_value"].IsDouble());
    EXPECT_TRUE(TestNode_["bool_value"].IsBool());
    EXPECT_TRUE(TestNode_["null_value"].IsNull());
    EXPECT_TRUE(TestNode_["list_value"].IsList());

    EXPECT_FALSE(TestNode_["string_value"].IsInt64());
    EXPECT_FALSE(TestNode_["int_value"].IsString());
}

TEST_F(YSONTest, NodeOperations) {
    // 测试复制
    NYT::TNode copy = TestNode_;
    EXPECT_EQ(copy["int_value"].AsInt64(), 42);

    // 测试修改
    copy["int_value"] = 100;
    EXPECT_EQ(copy["int_value"].AsInt64(), 100);
    EXPECT_EQ(TestNode_["int_value"].AsInt64(), 42);  // 原节点不变

    // 测试移动
    NYT::TNode moved = std::move(copy);
    EXPECT_EQ(moved["int_value"].AsInt64(), 100);
}
```

## 📈 最佳实践

### 性能优化建议

1. **批量操作**: 对大量数据使用批量序列化
2. **流式处理**: 对大文件使用流式处理减少内存使用
3. **预分配**: 为已知大小的数据预分配内存
4. **二进制格式**: 在性能关键场景使用二进制格式
5. **避免频繁复制**: 使用引用和移动语义

### 内存管理

```cpp
void EfficientYSONProcessing() {
    // 使用 RAII 管理资源
    class TYSONProcessor {
    public:
        TYSONProcessor(size_t bufferSize = 64 * 1024)
            : BufferSize_(bufferSize)
        {
            Buffer_.Reserve(BufferSize_);
        }

        template <typename T>
        TString SerializeBatch(const std::vector<T>& items) {
            Buffer_.clear();

            NYT::TNode list = NYT::TNode::CreateList();
            for (const auto& item : items) {
                list.Add(ConvertToNode(item));
            }

            return NYT::NodeToYsonString(list);
        }

    private:
        template <typename T>
        NYT::TNode ConvertToNode(const T& item) {
            // 类型特定的转换逻辑
            return NYT::TNode();  // 实现
        }

        size_t BufferSize_;
        TString Buffer_;
    };
}
```

### 错误处理

```cpp
void RobustYSONProcessing() {
    try {
        NYT::TNode node = NYT::NodeFromYsonString(inputData);

        // 安全的类型访问
        if (node.IsString()) {
            std::string value = node.AsString();
            ProcessStringValue(value);
        } else if (node.IsInt64()) {
            i64 value = node.AsInt64();
            ProcessIntValue(value);
        } else {
            std::cerr << "Unsupported node type" << std::endl;
        }

    } catch (const NYT::TNode::TTypeError& e) {
        std::cerr << "Type error: " << e.what() << std::endl;
    } catch (const NYT::TNode::TLookupError& e) {
        std::cerr << "Lookup error: " << e.what() << std::endl;
    } catch (const std::exception& e) {
        std::cerr << "General error: " << e.what() << std::endl;
    }
}
```

## 🔗 相关模块

- **JSON**: JSON 数据格式支持
- **Skiff**: 二进制序列化格式
- **Streams**: 流处理和文件操作
- **String**: 字符串处理工具
- **Memory**: 内存管理优化

YSON 库为 YTsaurus 提供了原生的序列化格式支持，结合了 JSON 的可读性和二进制格式的高效性。通过丰富的数据类型支持、流式处理能力和高性能的序列化/反序列化，YSON 成为 YTsaurus 生态系统中数据交换和存储的核心格式。