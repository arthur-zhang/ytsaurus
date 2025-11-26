# Skiff 库

YTsaurus 高性能二进制序列化格式，为大规模数据处理提供高效的结构化数据存储和传输。

## 📋 项目概述

Skiff 是 YTsaurus 的二进制数据序列化格式，专为高性能数据处理而设计。它提供了紧凑的二进制编码、零拷贝解析和强类型 schema 支持，特别适合大规模数据管道、表格存储和网络传输场景。

### 🎯 核心特性

- **高效编码**: 紧凑的二进制格式，减少存储空间
- **零拷贝解析**: 避免数据拷贝，提高解析性能
- **强类型 Schema**: 编译时类型检查和运行时验证
- **向前兼容**: 支持 schema 演进和向后兼容
- **大整数支持**: 支持 128 位和 256 位整数
- **变体类型**: 支持 Union 和 Variant 数据类型
- **流式处理**: 支持流式读写，处理大文件

## 🏗️ 架构设计

### 组件结构

```
Skiff Library
├── Schema             # Schema 系统
│   ├── TSkiffSchema    # Schema 基类
│   ├── TSimpleTypeSchema # 简单类型 Schema
│   ├── TComplexSchema   # 复杂类型 Schema
│   └── TTupleSchema     # 元组 Schema
├── Parser            # 解析器
│   ├── TUncheckedSkiffParser # 快速解析器
│   ├── TSkiffParser    # 标准解析器
│   └── TSkiffValidator # Schema 验证器
├── Writer            # 编写器
│   ├── TSkiffWriter    # 标准写入器
│   └── TZeroCopyOutputWriter # 零拷贝写入器
├── Types             # 数据类型
│   ├── TInt128/256     # 大整数类型
│   ├── EWireType       # 线格式枚举
│   └── 序列化类型       # 各种基本类型
└── Utilities         # 工具类
    ├── Endian          # 字节序处理
    └── Validation      # 验证工具
```

### 数据类型系统

```
Skiff Type System
├── Simple Types      # 简单类型
│   ├── Int8/16/32/64 # 有符号整数
│   ├── Uint8/16/32/64 # 无符号整数
│   ├── Int128/256     # 大整数
│   ├── Float32/64     # 浮点数
│   ├── Boolean        # 布尔值
│   ├── String8/16/32  # 变长字符串
│   └── Yson32         # Yson 嵌入
├── Complex Types     # 复杂类型
│   ├── Tuple          # 结构体/元组
│   ├── Variant8/16   # 变体类型
│   └── RepeatedVariant # 重复变体
└── Special Types     # 特殊类型
    ├── Nothing        # 空值
    └── EndOfSequence  # 序列结束标记
```

## 💻 使用方法

### 基础序列化操作

```cpp
#include <library/cpp/skiff/skiff.h>
#include <library/cpp/skiff/skiff_schema.h>
#include <util/stream/file.h>

// 基础数据类型序列化
void BasicSerializationExample() {
    std::cout << "=== Basic Skiff Serialization ===" << std::endl;

    // 1. 简单数值类型
    {
        // 创建 Schema
        auto intSchema = NSkiff::CreateSimpleTypeSchema(NSkiff::EWireType::Int64);
        auto doubleSchema = NSkiff::CreateSimpleTypeSchema(NSkiff::EWireType::Double);
        auto boolSchema = NSkiff::CreateSimpleTypeSchema(NSkiff::EWireType::Boolean);

        // 序列化到内存
        TString output;

        {
            NSkiff::TSkiffWriter writer(&output);

            // 写入不同类型的数据
            writer.WriteInt64(42);
            writer.WriteDouble(3.14159);
            writer.WriteBoolean(true);
            writer.WriteInt8(-128);
            writer.WriteUint64(18446744073709551615ULL);
        }

        std::cout << "Serialized basic types to " << output.size() << " bytes" << std::endl;

        // 反序列化
        {
            NSkiff::TUncheckedSkiffParser parser(&output);

            i64 intValue = parser.ParseInt64();
            double doubleValue = parser.ParseDouble();
            bool boolValue = parser.ParseBoolean();
            i8 int8Value = parser.ParseInt8();
            ui64 uint64Value = parser.ParseUint64();

            std::cout << "Parsed values:" << std::endl;
            std::cout << "  Int64: " << intValue << std::endl;
            std::cout << "  Double: " << doubleValue << std::endl;
            std::cout << "  Boolean: " << (boolValue ? "true" : "false") << std::endl;
            std::cout << "  Int8: " << static_cast<int>(int8Value) << std::endl;
            std::cout << "  Uint64: " << uint64Value << std::endl;
        }
    }

    // 2. 字符串类型
    {
        std::vector<TString> strings = {
            "Hello, World!",
            "Skiff serialization",
            "YTsaurus data format",
            "高性能数据处理"
        };

        // 序列化字符串数组
        TString output;
        {
            NSkiff::TSkiffWriter writer(&output);
            for (const auto& str : strings) {
                writer.WriteString32(str);
            }
        }

        std::cout << "Serialized " << strings.size() << " strings to "
                  << output.size() << " bytes" << std::endl;

        // 反序列化
        {
            NSkiff::TUncheckedSkiffParser parser(&output);
            std::vector<TString> parsedStrings;

            for (size_t i = 0; i < strings.size(); ++i) {
                TStringBuf strBuf = parser.ParseString32();
                parsedStrings.push_back(TString(strBuf));
            }

            // 验证结果
            for (size_t i = 0; i < strings.size(); ++i) {
                assert(strings[i] == parsedStrings[i]);
            }

            std::cout << "Successfully parsed " << parsedStrings.size() << " strings" << std::endl;
        }
    }
}
```

### 结构化数据处理

```cpp
// 复杂数据结构序列化
void StructuredDataExample() {
    // 定义用户数据结构
    struct TUser {
        ui64 Id;
        TString Name;
        TString Email;
        i32 Age;
        bool IsActive;
        std::vector<TString> Tags;
        double Score;
    };

    // 创建 Schema
    auto userSchema = NSkiff::CreateTupleSchema({
        NSkiff::CreateSimpleTypeSchema(NSkiff::EWireType::Uint64)->SetName("id"),
        NSkiff::CreateSimpleTypeSchema(NSkiff::EWireType::String32)->SetName("name"),
        NSkiff::CreateSimpleTypeSchema(NSkiff::EWireType::String32)->SetName("email"),
        NSkiff::CreateSimpleTypeSchema(NSkiff::EWireType::Int32)->SetName("age"),
        NSkiff::CreateSimpleTypeSchema(NSkiff::EWireType::Boolean)->SetName("is_active"),
        NSkiff::CreateSimpleTypeSchema(NSkiff::EWireType::String32)->SetName("tags"),
        NSkiff::CreateSimpleTypeSchema(NSkiff::EWireType::Double)->SetName("score")
    });

    std::cout << "=== Structured Data Serialization ===" << std::endl;

    // 创建测试数据
    std::vector<TUser> users = {
        {1, "Alice Johnson", "alice@example.com", 28, true, {"developer", "python", "ai"}, 95.5},
        {2, "Bob Smith", "bob@example.com", 35, true, {"manager", "leadership"}, 87.2},
        {3, "Charlie Davis", "charlie@example.com", 42, false, {"architect", "design"}, 91.8},
        {4, "Diana Wilson", "diana@example.com", 31, true, {"data_science", "analytics"}, 89.3}
    };

    // 序列化用户数据
    TString output;
    {
        NSkiff::TSkiffWriter writer(&output);

        for (const auto& user : users) {
            writer.WriteUint64(user.Id);
            writer.WriteString32(user.Name);
            writer.WriteString32(user.Email);
            writer.WriteInt32(user.Age);
            writer.WriteBoolean(user.IsActive);
            writer.WriteString32(JoinStrings(user.Tags, ","));
            writer.WriteDouble(user.Score);
        }
    }

    std::cout << "Serialized " << users.size() << " users to "
              << output.size() << " bytes" << std::endl;
    std::cout << "Average size per user: " << static_cast<double>(output.size()) / users.size() << " bytes" << std::endl;

    // 反序列化
    {
        NSkiff::TUncheckedSkiffParser parser(&output);
        std::vector<TUser> parsedUsers;

        while (parser.HasData()) {
            TUser user;
            user.Id = parser.ParseUint64();
            user.Name = TString(parser.ParseString32());
            user.Email = TString(parser.ParseString32());
            user.Age = parser.ParseInt32();
            user.IsActive = parser.ParseBoolean();
            user.Tags = SplitString(TString(parser.ParseString32()), ",");
            user.Score = parser.ParseDouble();

            parsedUsers.push_back(user);
        }

        std::cout << "Successfully parsed " << parsedUsers.size() << " users" << std::endl;

        // 显示解析结果
        for (const auto& user : parsedUsers) {
            std::cout << "  User " << user.Id << ": " << user.Name
                      << " (" << user.Email << "), Age: " << user.Age
                      << ", Active: " << (user.IsActive ? "Yes" : "No")
                      << ", Score: " << user.Score << std::endl;
        }
    }
}
```

### Variant 类型处理

```cpp
void VariantTypeExample() {
    std::cout << "=== Variant Type Handling ===" << std::endl;

    // 定义变体类型 Schema
    auto valueSchema = NSkiff::CreateVariant8Schema({
        NSkiff::CreateSimpleTypeSchema(NSkiff::EWireType::Int64),      // 0: 整数
        NSkiff::CreateSimpleTypeSchema(NSkiff::EWireType::Double),     // 1: 浮点数
        NSkiff::CreateSimpleTypeSchema(NSkiff::EWireType::String32),   // 2: 字符串
        NSkiff::CreateSimpleTypeSchema(NSkiff::EWireType::Boolean)     // 3: 布尔值
    });

    // 定义数据点
    struct TDataPoint {
        TString Name;
        ui8 Type;  // 0=int64, 1=double, 2=string, 3=bool
        TString StringValue;
        i64 IntValue;
        double DoubleValue;
        bool BoolValue;
    };

    std::vector<TDataPoint> dataPoints = {
        {"counter", 0, "", 42, 0.0, false},
        {"pi_value", 1, "", 0, 3.14159, false},
        {"message", 2, "Hello, Skiff!", 0, 0.0, false},
        {"is_ready", 3, "", 0, 0.0, true},
        {"large_number", 0, "", 9223372036854775807LL, 0.0, false}
    };

    // 序列化变体数据
    TString output;
    {
        NSkiff::TSkiffWriter writer(&output);

        for (const auto& point : dataPoints) {
            writer.WriteString32(point.Name);
            writer.WriteUint8(point.Type);

            switch (point.Type) {
                case 0: // Int64
                    writer.WriteInt64(point.IntValue);
                    break;
                case 1: // Double
                    writer.WriteDouble(point.DoubleValue);
                    break;
                case 2: // String
                    writer.WriteString32(point.StringValue);
                    break;
                case 3: // Boolean
                    writer.WriteBoolean(point.BoolValue);
                    break;
                default:
                    throw std::runtime_error("Unknown variant type");
            }
        }
    }

    std::cout << "Serialized " << dataPoints.size() << " variant data points to "
              << output.size() << " bytes" << std::endl;

    // 反序列化
    {
        NSkiff::TUncheckedSkiffParser parser(&output);
        std::vector<TDataPoint> parsedPoints;

        while (parser.HasData()) {
            TDataPoint point;
            point.Name = TString(parser.ParseString32());
            point.Type = parser.ParseUint8();

            switch (point.Type) {
                case 0: // Int64
                    point.IntValue = parser.ParseInt64();
                    break;
                case 1: // Double
                    point.DoubleValue = parser.ParseDouble();
                    break;
                case 2: // String
                    point.StringValue = TString(parser.ParseString32());
                    break;
                case 3: // Boolean
                    point.BoolValue = parser.ParseBoolean();
                    break;
                default:
                    throw std::runtime_error("Unknown variant type");
            }

            parsedPoints.push_back(point);
        }

        std::cout << "Successfully parsed " << parsedPoints.size() << " variant data points" << std::endl;

        // 显示解析结果
        for (const auto& point : parsedPoints) {
            std::cout << "  " << point.Name << ": ";
            switch (point.Type) {
                case 0:
                    std::cout << point.IntValue << " (int64)";
                    break;
                case 1:
                    std::cout << point.DoubleValue << " (double)";
                    break;
                case 2:
                    std::cout << "\"" << point.StringValue << "\" (string)";
                    break;
                case 3:
                    std::cout << (point.BoolValue ? "true" : "false") << " (boolean)";
                    break;
            }
            std::cout << std::endl;
        }
    }
}
```

### 大整数类型处理

```cpp
void LargeIntegerExample() {
    std::cout << "=== Large Integer Types ===" << std::endl;

    // 创建测试数据
    NSkiff::TInt128 int128Value = {0x1234567890abcdefULL, 0xabcdef1234567890LL};
    NSkiff::TUint128 uint128Value = {0xfedcba0987654321ULL, 0x0fedcba987654321ULL};
    NSkiff::TInt256 int256Value = {{
        0x1111111111111111ULL,
        0x2222222222222222ULL,
        0x3333333333333333ULL,
        0x4444444444444444ULL
    }};
    NSkiff::TUint256 uint256Value = {{
        0xaaaaaaaaaaaaaaaaULL,
        0xbbbbbbbbbbbbbbbbULL,
        0xccccccccccccccccULL,
        0xddddddddddddddddULL
    }};

    // 序列化大整数
    TString output;
    {
        NSkiff::TSkiffWriter writer(&output);

        writer.WriteInt128(int128Value);
        writer.WriteUint128(uint128Value);
        writer.WriteInt256(int256Value);
        writer.WriteUint256(uint256Value);
    }

    std::cout << "Serialized large integers to " << output.size() << " bytes" << std::endl;

    // 反序列化
    {
        NSkiff::TUncheckedSkiffParser parser(&output);

        auto parsedInt128 = parser.ParseInt128();
        auto parsedUint128 = parser.ParseUint128();
        auto parsedInt256 = parser.ParseInt256();
        auto parsedUint256 = parser.ParseUint256();

        // 验证结果
        assert(parsedInt128.Low == int128Value.Low && parsedInt128.High == int128Value.High);
        assert(parsedUint128.Low == uint128Value.Low && parsedUint128.High == uint128Value.High);

        std::cout << "Successfully parsed large integers:" << std::endl;
        std::cout << "  Int128: 0x" << std::hex << parsedInt128.High << std::setfill('0')
                  << std::setw(16) << parsedInt128.Low << std::dec << std::endl;
        std::cout << "  Uint128: 0x" << std::hex << parsedUint128.High << std::setfill('0')
                  << std::setw(16) << parsedUint128.Low << std::dec << std::endl;
        std::cout << "  Int256: [" << std::hex;
        for (size_t i = 0; i < parsedInt256.Parts.size(); ++i) {
            std::cout << "0x" << std::setfill('0') << std::setw(16) << parsedInt256.Parts[i];
            if (i + 1 < parsedInt256.Parts.size()) std::cout << ", ";
        }
        std::cout << "]" << std::dec << std::endl;
    }
}
```

### 零拷贝优化处理

```cpp
#include <library/cpp/skiff/zerocopy_output_writer.h>
#include <util/stream/zerocopy.h>

void ZeroCopyExample() {
    std::cout << "=== Zero-Copy Optimization ===" << std::endl;

    // 创建大量测试数据
    const size_t recordCount = 100000;
    std::vector<std::vector<TString>> testRecords;

    for (size_t i = 0; i < recordCount; ++i) {
        std::vector<TString> record = {
            "record_" + std::to_string(i),
            "field_2_" + std::to_string(i),
            "field_3_" + std::to_string(i),
            "field_4_" + std::to_string(i),
            "field_5_" + std::to_string(i)
        };
        testRecords.push_back(record);
    }

    // 常规序列化
    TString regularOutput;
    auto regularStart = std::chrono::high_resolution_clock::now();

    {
        NSkiff::TSkiffWriter writer(&regularOutput);
        for (const auto& record : testRecords) {
            for (const auto& field : record) {
                writer.WriteString32(field);
            }
        }
    }

    auto regularEnd = std::chrono::high_resolution_clock::now();
    auto regularDuration = std::chrono::duration_cast<std::chrono::milliseconds>(regularEnd - regularStart);

    // 零拷贝序列化
    TString zeroCopyOutput;
    auto zeroCopyStart = std::chrono::high_resolution_clock::now();

    {
        TBufferOutput bufferOutput(zeroCopyOutput);
        NSkiff::TZeroCopyOutputWriter writer(&bufferOutput);

        for (const auto& record : testRecords) {
            for (const auto& field : record) {
                writer.WriteString32(field);
            }
        }

        writer.Finish();
    }

    auto zeroCopyEnd = std::chrono::high_resolution_clock::now();
    auto zeroCopyDuration = std::chrono::duration_cast<std::chrono::milliseconds>(zeroCopyEnd - zeroCopyStart);

    std::cout << "Performance comparison:" << std::endl;
    std::cout << "  Regular serialization: " << regularDuration.count() << " ms" << std::endl;
    std::cout << "  Zero-copy serialization: " << zeroCopyDuration.count() << " ms" << std::endl;
    std::cout << "  Speedup: " << static_cast<double>(regularDuration.count()) / zeroCopyDuration.count() << "x" << std::endl;

    // 验证结果一致性
    assert(regularOutput.size() == zeroCopyOutput.size());
    std::cout << "  Output sizes match: " << regularOutput.size() << " bytes" << std::endl;
}
```

### 流式处理

```cpp
void StreamProcessingExample() {
    std::cout << "=== Stream Processing ===" << std::endl;

    // 创建大型测试文件
    const size_t recordCount = 1000000;
    {
        TUnbufferedFileOutput fileOutput("large_skiff_data.skiff");
        NSkiff::TSkiffWriter writer(&fileOutput);

        for (size_t i = 0; i < recordCount; ++i) {
            writer.WriteUint64(i);  // ID
            writer.WriteString32("record_" + std::to_string(i));  // Name
            writer.WriteDouble(i * 1.5);  // Value
            writer.WriteBoolean(i % 2 == 0);  // IsEven
            writer.WriteInt64(static_cast<i64>(i - recordCount/2));  // Balance
        }

        writer.Finish();
    }

    std::cout << "Created test file with " << recordCount << " records" << std::endl;

    // 流式处理文件
    {
        TUnbufferedFileInput fileInput("large_skiff_data.skiff");
        NSkiff::TUncheckedSkiffParser parser(&fileInput);

        std::atomic<size_t> processedCount{0};
        std::atomic<i64> totalBalance{0};
        std::atomic<size_t> evenCount{0};
        std::atomic<double> totalValue{0.0};

        // 创建多个处理线程
        const size_t threadCount = 4;
        std::vector<std::thread> threads;

        std::mutex parseMutex;
        bool processingComplete = false;

        for (size_t t = 0; t < threadCount; ++t) {
            threads.emplace_back([&parser, &processedCount, &totalBalance, &evenCount, &totalValue,
                                 &parseMutex, &processingComplete, recordCount]() {
                size_t localCount = 0;
                i64 localBalance = 0;
                size_t localEvenCount = 0;
                double localValue = 0.0;

                while (!processingComplete) {
                    std::unique_lock<std::mutex> lock(parseMutex);

                    // 检查是否还有数据
                    if (!parser.HasData()) {
                        break;
                    }

                    // 批量处理记录
                    const size_t batchSize = 1000;
                    size_t processedInBatch = 0;

                    while (parser.HasData() && processedInBatch < batchSize) {
                        ui64 id = parser.ParseUint64();
                        auto name = parser.ParseString32();
                        double value = parser.ParseDouble();
                        bool isEven = parser.ParseBoolean();
                        i64 balance = parser.ParseInt64();

                        localBalance += balance;
                        if (isEven) localEvenCount++;
                        localValue += value;
                        processedInBatch++;
                        localCount++;
                    }

                    lock.unlock();

                    // 处理一批数据后定期报告
                    if (localCount % 10000 == 0) {
                        std::cout << "Thread processed " << localCount << " records" << std::endl;
                    }
                }

                // 更新全局计数器
                processedCount += localCount;
                totalBalance += localBalance;
                evenCount += localEvenCount;
                totalValue += localValue;
            });
        }

        // 等待所有线程完成
        for (auto& thread : threads) {
            thread.join();
        }

        std::cout << "\nStream processing results:" << std::endl;
        std::cout << "  Total records processed: " << processedCount.load() << std::endl;
        std::cout << "  Total balance: " << totalBalance.load() << std::endl;
        std::cout << "  Even records: " << evenCount.load() << std::endl;
        std::cout << "  Average value: " << totalValue.load() / processedCount.load() << std::endl;
    }
}
```

## 🔧 高级特性

### Schema 验证

```cpp
void SchemaValidationExample() {
    std::cout << "=== Schema Validation ===" << std::endl;

    // 创建严格的 Schema
    auto strictSchema = NSkiff::CreateTupleSchema({
        NSkiff::CreateSimpleTypeSchema(NSkiff::EWireType::Uint64)->SetName("id"),
        NSkiff::CreateSimpleTypeSchema(NSkiff::EWireType::String32)->SetName("name"),
        NSkiff::CreateSimpleTypeSchema(NSkiff::EWireType::Int32)->SetName("age"),
        NSkiff::CreateSimpleTypeSchema(NSkiff::EWireType::Double)->SetName("score")
    });

    // 创建验证器
    NSkiff::TSkiffValidator validator(strictSchema);

    // 有效的数据
    TString validData;
    {
        NSkiff::TSkiffWriter writer(&validData);
        writer.WriteUint64(123);
        writer.WriteString32("John Doe");
        writer.WriteInt32(30);
        writer.WriteDouble(95.5);
    }

    // 无效的数据（缺少字段）
    TString invalidData;
    {
        NSkiff::TSkiffWriter writer(&invalidData);
        writer.WriteUint64(456);
        writer.WriteString32("Jane Smith");
        // 缺少 age 和 score 字段
    }

    // 验证有效数据
    {
        NSkiff::TUncheckedSkiffParser parser(&validData);
        auto validationResult = validator.Validate(parser);
        if (validationResult.IsValid()) {
            std::cout << "✓ Valid data passed validation" << std::endl;
        } else {
            std::cout << "✗ Valid data failed validation" << std::endl;
            for (const auto& error : validationResult.GetErrors()) {
                std::cout << "  Error: " << error << std::endl;
            }
        }
    }

    // 验证无效数据
    {
        NSkiff::TUncheckedSkiffParser parser(&invalidData);
        auto validationResult = validator.Validate(parser);
        if (validationResult.IsValid()) {
            std::cout << "✓ Invalid data unexpectedly passed validation" << std::endl;
        } else {
            std::cout << "✓ Invalid data correctly failed validation:" << std::endl;
            for (const auto& error : validationResult.GetErrors()) {
                std::cout << "  Error: " << error << std::endl;
            }
        }
    }
}
```

## 🧪 测试和性能基准

### 性能测试

```cpp
#include <library/cpp/testing/gtest/gtest.h>
#include <chrono>
#include <random>

class SkiffPerformanceTest : public ::testing::Test {
protected:
    void SetUp() override {
        GenerateTestData();
    }

    void GenerateTestData() {
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_int_distribution<ui64> idDist(1, 1000000);
        std::uniform_int_distribution<i32> ageDist(18, 80);
        std::uniform_real_distribution<double> scoreDist(0.0, 100.0);
        std::uniform_int_distribution<int> nameLenDist(5, 20);

        TestData_.reserve(100000);
        for (int i = 0; i < 100000; ++i) {
            std::string name;
            int nameLen = nameLenDist(gen);
            for (int j = 0; j < nameLen; ++j) {
                name += 'a' + (gen() % 26);
            }

            TestData_.push_back({
                idDist(gen),
                TString(name),
                ageDist(gen),
                scoreDist(gen)
            });
        }
    }

    struct TTestRecord {
        ui64 Id;
        TString Name;
        i32 Age;
        double Score;
    };

    std::vector<TTestRecord> TestData_;
};

TEST_F(SkiffPerformanceTest, SerializationBenchmark) {
    std::cout << "=== Skiff Serialization Performance ===" << std::endl;

    // Skiff 序列化
    auto skiffStart = std::chrono::high_resolution_clock::now();
    TString skiffData;
    {
        NSkiff::TSkiffWriter writer(&skiffData);
        for (const auto& record : TestData_) {
            writer.WriteUint64(record.Id);
            writer.WriteString32(record.Name);
            writer.WriteInt32(record.Age);
            writer.WriteDouble(record.Score);
        }
    }
    auto skiffEnd = std::chrono::high_resolution_clock::now();
    auto skiffDuration = std::chrono::duration_cast<std::chrono::microseconds>(skiffEnd - skiffStart);

    std::cout << "Skiff serialization:" << std::endl;
    std::cout << "  Time: " << skiffDuration.count() << " μs" << std::endl;
    std::cout << "  Throughput: " << (TestData_.size() * 1000000.0) / skiffDuration.count() << " records/sec" << std::endl;
    std::cout << "  Data size: " << skiffData.size() << " bytes" << std::endl;
    std::cout << "  Bytes per record: " << static_cast<double>(skiffData.size()) / TestData_.size() << std::endl;
}

TEST_F(SkiffPerformanceTest, DeserializationBenchmark) {
    // 先序列化数据
    TString skiffData;
    {
        NSkiff::TSkiffWriter writer(&skiffData);
        for (const auto& record : TestData_) {
            writer.WriteUint64(record.Id);
            writer.WriteString32(record.Name);
            writer.WriteInt32(record.Age);
            writer.WriteDouble(record.Score);
        }
    }

    // Skiff 反序列化
    auto skiffStart = std::chrono::high_resolution_clock::now();
    std::vector<TTestRecord> parsedData;
    {
        NSkiff::TUncheckedSkiffParser parser(&skiffData);
        while (parser.HasData()) {
            TTestRecord record;
            record.Id = parser.ParseUint64();
            record.Name = TString(parser.ParseString32());
            record.Age = parser.ParseInt32();
            record.Score = parser.ParseDouble();
            parsedData.push_back(record);
        }
    }
    auto skiffEnd = std::chrono::high_resolution_clock::now();
    auto skiffDuration = std::chrono::duration_cast<std::chrono::microseconds>(skiffEnd - skiffStart);

    std::cout << "Skiff deserialization:" << std::endl;
    std::cout << "  Time: " << skiffDuration.count() << " μs" << std::endl;
    std::cout << "  Throughput: " << (parsedData.size() * 1000000.0) / skiffDuration.count() << " records/sec" << std::endl;

    // 验证数据正确性
    ASSERT_EQ(TestData_.size(), parsedData.size());
    for (size_t i = 0; i < TestData_.size(); ++i) {
        ASSERT_EQ(TestData_[i].Id, parsedData[i].Id);
        ASSERT_EQ(TestData_[i].Name, parsedData[i].Name);
        ASSERT_EQ(TestData_[i].Age, parsedData[i].Age);
        ASSERT_DOUBLE_EQ(TestData_[i].Score, parsedData[i].Score);
    }
}
```

## 📈 最佳实践

### 性能优化建议

1. **使用零拷贝**: 对性能关键路径使用零拷贝写入器
2. **批量处理**: 批量序列化/反序列化以提高效率
3. **预分配缓冲区**: 为已知大小的数据预分配缓冲区
4. **流式处理**: 对大文件使用流式处理避免内存溢出
5. **Schema 优化**: 设计高效的 Schema 结构

### 内存管理

```cpp
void MemoryOptimizedProcessing() {
    // 使用 RAII 管理资源
    class TSkiffProcessor {
    public:
        TSkiffProcessor(size_t bufferSize = 64 * 1024)
            : BufferSize_(bufferSize)
        {
            Buffer_.Reserve(BufferSize_);
        }

        void ProcessRecord(const TMyRecord& record) {
            // 使用预留的缓冲区
            Buffer_.clear();

            {
                NSkiff::TSkiffWriter writer(&Buffer_);
                // 序列化记录
                SerializeRecord(writer, record);
            }

            // 处理序列化后的数据
            ProcessSerializedData(Buffer_);
        }

    private:
        size_t BufferSize_;
        TString Buffer_;
    };
}
```

### 错误处理

```cpp
void RobustSkiffProcessing() {
    try {
        NSkiff::TUncheckedSkiffParser parser(&inputData);

        while (parser.HasData()) {
            try {
                // 解析单个记录
                auto record = ParseRecord(parser);
                ProcessRecord(record);

            } catch (const NSkiff::TSkiffException& e) {
                std::cerr << "Skiff parsing error: " << e.what() << std::endl;
                // 跳过损坏的记录，继续处理
                continue;
            }
        }

    } catch (const std::exception& e) {
        std::cerr << "Fatal error in Skiff processing: " << e.what() << std::endl;
        throw;
    }
}
```

## 🔗 相关模块

- **YSON**: YTsaurus 原生序列化格式
- **JSON**: JSON 数据处理
- **Streams**: 流处理和文件操作
- **Memory**: 内存管理优化
- **Threading**: 并发处理支持

Skiff 库为 YTsaurus 提供了高性能的二进制序列化能力，支持复杂的数据结构和零拷贝优化，是大规模数据处理场景中的重要工具。通过强类型 Schema 和高效的编码算法，Skiff 在保持数据完整性的同时，提供了出色的性能表现。