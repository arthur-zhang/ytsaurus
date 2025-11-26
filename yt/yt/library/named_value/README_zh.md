# Named Value (命名值)

## 项目概述

Named Value 模块提供了一种便捷的方式来创建和管理命名的表格行数据。该模块通过 `TNamedValue` 类简化了测试代码中的行构建过程，支持多种数据类型的自动转换和类型安全的值管理。

## 核心功能

### 命名值管理
- **类型安全**: 支持强类型的命名值定义
- **自动转换**: 自动处理不同数据类型之间的转换
- **便利接口**: 提供简洁的 API 来创建表格行数据
- **测试友好**: 专门为测试场景优化的接口设计

### 数据类型支持
- **基本类型**: 支持 i64, ui64, double, bool, TString 等基本类型
- **特殊类型**: 支持 null, Any, Composite 等特殊数据类型
- **类型推导**: 自动推导和验证数据类型
- **统一接口**: 为所有数据类型提供统一的创建接口

## 主要接口

### 核心类：TNamedValue

```cpp
class TNamedValue
{
public:
    using TValue = std::variant<std::nullptr_t, i64, ui64, double, bool, TString, TAny, TComposite>;

    // 构造函数模板
    template <typename T>
    TNamedValue(TString name, T value);

    // 转换为 UnversionedValue
    NTableClient::TUnversionedValue ToUnversionedValue(const NTableClient::TNameTablePtr& nameTable) const;

    // 提取值
    static TValue ExtractValue(const NTableClient::TUnversionedValue& value);
};
```

### 便利函数

```cpp
// 创建命名行
NTableClient::TUnversionedOwningRow MakeRow(
    const NTableClient::TNameTablePtr& nameTable,
    const std::initializer_list<TNamedValue>& values);

NTableClient::TUnversionedOwningRow MakeRow(
    const NTableClient::TNameTablePtr& nameTable,
    const std::vector<TNamedValue>& values);

// 创建命名值列表
std::vector<TNamedValue> MakeNamedValueList(
    const NTableClient::TNameTablePtr& nameTable,
    NTableClient::TUnversionedRow row);
```

## 使用方法

### 基本使用示例

```cpp
#include <yt/yt/library/named_value/named_value.h>

using namespace NYT::NNamedValue;
using namespace NYT::NTableClient;

// 创建名称表
auto nameTable = New<TNameTable>();
auto idId = nameTable->RegisterName("id");
auto nameId = nameTable->RegisterName("name");
auto ageId = nameTable->RegisterName("age");
auto activeId = nameTable->RegisterName("active");

// 创建命名行
auto row = MakeRow(nameTable, {
    {"id", 42},
    {"name", "John Doe"},
    {"age", 30},
    {"active", true}
});

// 使用行数据
for (const auto& value : row) {
    Cout << "Column: " << nameTable->GetName(value.Id)
         << ", Value: " << value << Endl;
}
```

### 复杂数据类型示例

```cpp
// 处理复杂类型
auto complexRow = MakeRow(nameTable, {
    {"id", 123},
    {"json_data", EValueType::Any, "{\"key\": \"value\"}"},
    {"array_data", EValueType::Composite, "[1, 2, 3]"},
    {"description", nullptr},  // null 值
    {"score", 95.5}
});
```

### 测试代码集成示例

```cpp
class TableRowTest : public ::testing::Test {
protected:
    void SetUp() override {
        nameTable_ = CreateTestNameTable();
    }

    TNameTablePtr CreateTestNameTable() {
        auto table = New<TNameTable>();
        table->RegisterName("user_id");
        table->RegisterName("username");
        table->RegisterName("email");
        table->RegisterName("created_at");
        table->RegisterName("is_active");
        return table;
    }

    TUnversionedOwningRow CreateTestUser() {
        return MakeRow(nameTable_, {
            {"user_id", 1001},
            {"username", "testuser"},
            {"email", "test@example.com"},
            {"created_at", 1640995200000000ull},  // timestamp
            {"is_active", true}
        });
    }

    void VerifyUserRow(const TUnversionedOwningRow& row) {
        ASSERT_EQ(row.GetCount(), 5);
        EXPECT_EQ(row[0].Data.Int64, 1001);      // user_id
        EXPECT_EQ(row[1].Data.String, "testuser"); // username
        EXPECT_EQ(row[2].Data.String, "test@example.com"); // email
        EXPECT_TRUE(row[4].Data.Boolean);       // is_active
    }

private:
    TNameTablePtr nameTable_;
};
```

### 动态数据构建示例

```cpp
class DynamicRowBuilder {
public:
    DynamicRowBuilder(const TNameTablePtr& nameTable) : nameTable_(nameTable) {}

    void AddField(const TString& name, auto value) {
        namedValues_.emplace_back(name, value);
    }

    void AddNullField(const TString& name) {
        namedValues_.emplace_back(name, nullptr);
    }

    void AddJsonField(const TString& name, const TString& jsonValue) {
        namedValues_.emplace_back(name, EValueType::Any, jsonValue);
    }

    TUnversionedOwningRow Build() {
        return MakeRow(nameTable_, namedValues_);
    }

    void Clear() {
        namedValues_.clear();
    }

private:
    TNameTablePtr nameTable_;
    std::vector<TNamedValue> namedValues_;
};
```

## 配置说明

### 支持的数据类型

| 类型 | C++ 类型 | Yson 表示 | 说明 |
|------|----------|-----------|------|
| Null | std::nullptr_t | null | 空值 |
| Int64 | i64 | 42 | 64位有符号整数 |
| Uint64 | ui64 | 42u | 64位无符号整数 |
| Double | double | 3.14 | 双精度浮点数 |
| Boolean | bool | true | 布尔值 |
| String | TString | "hello" | 字符串 |
| Any | TAny | EValueType::Any, "json" | 任意类型数据 |
| Composite | TComposite | EValueType::Composite, "array" | 复合类型数据 |

### 类型转换规则

- **数值类型**: 自动在适当时候进行类型提升
- **字符串**: 支持 TString, TStringBuf, const char* 等字符串类型
- **指针处理**: 空指针自动转换为 null 值
- **枚举类型**: 枚举值自动转换为底层数值类型

## 性能考虑

### 内存使用
- **零拷贝**: 尽可能避免不必要的数据复制
- **延迟转换**: 在需要时才进行类型转换
- **批量操作**: 支持批量创建命名值提高效率

### 编译时优化
- **模板特化**: 为常用类型提供模板特化
- **内联函数**: 关键路径使用内联函数优化
- **常量折叠**: 编译时常量折叠和优化

## 最佳实践

### 1. 测试数据管理
```cpp
class TestDataFactory {
public:
    static TUnversionedOwningRow CreateUserRow(
        const TNameTablePtr& nameTable,
        i64 userId,
        const TString& username,
        const TString& email) {
        return MakeRow(nameTable, {
            {"user_id", userId},
            {"username", username},
            {"email", email},
            {"created_at", TInstant::Now().MicroSeconds()},
            {"is_active", true}
        });
    }

    static std::vector<TUnversionedOwningRow> CreateUserRows(
        const TNameTablePtr& nameTable,
        int count) {
        std::vector<TUnversionedOwningRow> rows;
        rows.reserve(count);

        for (int i = 0; i < count; ++i) {
            rows.push_back(CreateUserRow(
                nameTable,
                i + 1,
                "user_" + ToString(i),
                "user" + ToString(i) + "@example.com"
            ));
        }

        return rows;
    }
};
```

### 2. 类型安全的值提取
```cpp
class SafeValueExtractor {
public:
    template<typename T>
    static std::optional<T> ExtractValue(
        const TUnversionedOwningRow& row,
        const TNameTablePtr& nameTable,
        const TString& columnName) {
        auto columnId = nameTable->GetIdOrThrow(columnName);

        for (const auto& value : row) {
            if (value.Id == columnId) {
                return ExtractTypedValue<T>(value);
            }
        }

        return std::nullopt;
    }

private:
    template<typename T>
    static T ExtractTypedValue(const TUnversionedValue& value) {
        auto namedValue = TNamedValue::ExtractValue(value);
        if (std::holds_alternative<T>(namedValue)) {
            return std::get<T>(namedValue);
        }
        throw std::runtime_error("Type mismatch");
    }
};
```

## 依赖项

- **YT Table Client**: 表格客户端和行数据结构
- **Standard Library**: STL 容器和变体类型

## 注意事项

### 1. 性能影响
- 命名值主要设计用于测试，生产代码可能需要更高效的实现
- 类型转换可能带来一定的性能开销
- 频繁创建命名值对象可能导致内存压力

### 2. 类型安全
- 类型转换失败时会抛出异常
- 建议在类型不确定时进行适当的类型检查
- 注意数值类型的精度和范围限制

### 3. 内存管理
- OwningRow 会自动管理内存生命周期
- 避免长期持有大型行数据的引用
- 合理使用 RAII 模式管理资源