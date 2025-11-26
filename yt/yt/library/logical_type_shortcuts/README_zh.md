# Logical Type Shortcuts (逻辑类型快捷函数)

## 项目概述

Logical Type Shortcuts 模块提供了一套便捷的函数来创建 YTsaurus 中的逻辑类型。这些快捷函数大大简化了复杂类型的创建过程，特别适用于需要大量创建逻辑类型的场景，如测试代码和动态模式构建。

## 核心功能

### 简单类型快捷函数
- **整数类型**: Int8, Int16, Int32, Int64, Uint8, Uint16, Uint32, Uint64
- **浮点类型**: Float, Double
- **字符串类型**: Utf8, String
- **日期时间类型**: Date, Datetime, Timestamp, Interval, Date32, Datetime64, Timestamp64, Interval64
- **时区日期时间类型**: TzDate, TzDatetime, TzTimestamp, TzDate32, TzDatetime64, TzTimestamp64
- **特殊类型**: Json, Null, Void, Uuid
- **复合类型**: Yson (Any), Bool

### 复合类型构建器
- **可选类型**: Optional(element)
- **小数类型**: Decimal(precision, scale)
- **列表类型**: List(element)
- **元组类型**: Tuple(types...)
- **结构类型**: Struct(name1, type1, name2, type2, ...)
- **变体类型**: VariantTuple(types...), VariantStruct(name1, type1, ...)
- **字典类型**: Dict(key, value)
- **标签类型**: Tagged(tag, element)

## 主要接口

### 简单类型快捷函数

```cpp
namespace NYT::NTableClient::NLogicalTypeShortcuts {

// 整数类型
TLogicalTypePtr Int8();
TLogicalTypePtr Int16();
TLogicalTypePtr Int32();
TLogicalTypePtr Int64();

// 无符号整数类型
TLogicalTypePtr Uint8();
TLogicalTypePtr Uint16();
TLogicalTypePtr Uint32();
TLogicalTypePtr Uint64();

// 浮点类型
TLogicalTypePtr Float();
TLogicalTypePtr Double();

// 字符串类型
TLogicalTypePtr Utf8();
TLogicalTypePtr String();

// 日期时间类型
TLogicalTypePtr Date();
TLogicalTypePtr Datetime();
TLogicalTypePtr Timestamp();
TLogicalTypePtr Interval();
TLogicalTypePtr Date32();
TLogicalTypePtr Datetime64();
TLogicalTypePtr Timestamp64();
TLogicalTypePtr Interval64();

// 时区日期时间类型
TLogicalTypePtr TzDate();
TLogicalTypePtr TzDatetime();
TLogicalTypePtr TzTimestamp();
TLogicalTypePtr TzDate32();
TLogicalTypePtr TzDatetime64();
TLogicalTypePtr TzTimestamp64();

// 特殊类型
TLogicalTypePtr Json();
TLogicalTypePtr Null();
TLogicalTypePtr Void();
TLogicalTypePtr Uuid();

// 复合类型
TLogicalTypePtr Yson();  // Any
TLogicalTypePtr Bool();

} // namespace NYT::NTableClient::NLogicalTypeShortcuts
```

### 复合类型构建器

```cpp
// 可选类型
TLogicalTypePtr Optional(const TLogicalTypePtr& element);

// 小数类型
TLogicalTypePtr Decimal(int precision, int scale);

// 列表类型
TLogicalTypePtr List(const TLogicalTypePtr& element);

// 元组类型
template <typename... T>
TLogicalTypePtr Tuple(const T&... args);

// 结构类型
template <typename... T>
TLogicalTypePtr Struct(const T&... args);

// 变体元组类型
template <typename... T>
TLogicalTypePtr VariantTuple(const T&... args);

// 变体结构类型
template <typename... T>
TLogicalTypePtr VariantStruct(const T&... args);

// 字典类型
TLogicalTypePtr Dict(const TLogicalTypePtr& key, const TLogicalTypePtr& value);

// 标签类型
TLogicalTypePtr Tagged(TString tag, const TLogicalTypePtr& element);
```

## 使用方法

### 基本类型使用示例

```cpp
#include <yt/yt/library/logical_type_shortcuts/logical_type_shortcuts.h>

using namespace NYT::NTableClient::NLogicalTypeShortcuts;

// 创建简单类型
auto intType = Int64();
auto stringType = String();
auto timestampType = Timestamp();
auto boolType = Bool();

// 创建可选类型
auto optionalInt = Optional(Int32());
auto optionalString = Optional(Utf8());

// 创建小数类型
auto decimalType = Decimal(18, 6);  // 精度18，小数位数6

// 创建列表类型
auto intList = List(Int32());
auto stringList = List(String());

// 创建字典类型
auto stringToIntMap = Dict(String(), Int64());
auto complexMap = Dict(String(), List(Struct("key", String(), "value", Double())));
```

### 复杂类型构建示例

```cpp
// 构建复杂的嵌套结构
auto userSchema = Struct(
    "id", Int64(),
    "name", String(),
    "email", Optional(String()),
    "age", Optional(Int32()),
    "tags", List(String()),
    "metadata", Dict(String(), String()),
    "created_at", Timestamp(),
    "is_active", Bool()
);

// 构建订单模式
auto orderSchema = Struct(
    "order_id", Int64(),
    "customer_id", Int64(),
    "items", List(Struct(
        "product_id", String(),
        "quantity", Int32(),
        "price", Decimal(10, 2),
        "discount", Optional(Decimal(5, 2))
    )),
    "total_amount", Decimal(12, 2),
    "status", String(),
    "order_date", Timestamp(),
    "shipping_address", Struct(
        "street", String(),
        "city", String(),
        "state", Optional(String()),
        "postal_code", String(),
        "country", String()
    )
);

// 构建变体类型
auto paymentMethod = VariantStruct(
    "credit_card", Struct(
        "card_number", String(),
        "expiry", String(),
        "cvv", String()
    ),
    "bank_transfer", Struct(
        "account_number", String(),
        "routing_number", String(),
        "bank_name", String()
    ),
    "digital_wallet", Struct(
        "provider", String(),
        "wallet_id", String()
    )
);
```

### 测试场景使用示例

```cpp
#include <gtest/gtest.h>

class LogicalTypeTest : public ::testing::Test {
protected:
    void SetUp() override {
        // 准备测试用的类型
        simpleType_ = Int32();
        optionalType_ = Optional(String());
        listType_ = List(Struct("x", Double(), "y", Double()));
        complexType_ = Struct(
            "id", Int64(),
            "data", List(Dict(String(), Json())),
            "timestamp", Timestamp(),
            "flags", VariantTuple(Bool(), Int32(), String())
        );
    }

    void TestTypeCompatibility() {
        // 测试类型兼容性
        EXPECT_TRUE(IsCompatible(simpleType_, Int32()));
        EXPECT_TRUE(IsCompatible(optionalType_, Optional(String())));

        // 测试类型转换
        auto convertedType = ConvertToV3Type(complexType_);
        EXPECT_NE(convertedType, nullptr);
    }

private:
    TLogicalTypePtr simpleType_;
    TLogicalTypePtr optionalType_;
    TLogicalTypePtr listType_;
    TLogicalTypePtr complexType_;
};
```

### 动态模式构建示例

```cpp
class DynamicSchemaBuilder {
public:
    DynamicSchemaBuilder() = default;

    // 添加字段
    void AddField(const TString& name, const TLogicalTypePtr& type, bool required = true) {
        if (required) {
            fields_.emplace_back(name, type);
        } else {
            fields_.emplace_back(name, Optional(type));
        }
    }

    // 构建最终模式
    TLogicalTypePtr BuildSchema() {
        return Struct(std::vector<TStructField>(fields_.begin(), fields_.end()));
    }

    // 构建分析表模式
    static TLogicalTypePtr BuildAnalyticsSchema() {
        return Struct(
            "event_time", Timestamp(),
            "user_id", Int64(),
            "session_id", String(),
            "event_type", String(),
            "properties", Json(),
            "device_info", Struct(
                "platform", String(),
                "os_version", String(),
                "app_version", String()
            ),
            "location", Optional(Struct(
                "country", String(),
                "city", String(),
                "coordinates", Optional(Struct(
                    "latitude", Double(),
                    "longitude", Double()
                ))
            )),
            "metrics", Dict(String(), Double())
        );
    }

    // 构建配置模式
    static TLogicalTypePtr BuildConfigSchema() {
        return Struct(
            "name", String(),
            "version", String(),
            "enabled", Bool(),
            "parameters", Dict(String(), VariantTuple(
                String(),
                Int64(),
                Double(),
                Bool(),
                List(String())
            )),
            "metadata", Optional(Struct(
                "author", String(),
                "created_at", Timestamp(),
                "description", Optional(String()),
                "tags", List(String())
            ))
        );
    }

private:
    std::vector<TStructField> fields_;
};
```

### 类型工厂模式示例

```cpp
class LogicalTypeFactory {
public:
    // 根据字符串创建类型
    static TLogicalTypePtr CreateFromString(const TString& typeStr) {
        if (typeStr == "int32") return Int32();
        if (typeStr == "int64") return Int64();
        if (typeStr == "string") return String();
        if (typeStr == "timestamp") return Timestamp();
        if (typeStr == "json") return Json();
        if (typeStr == "uuid") return Uuid();

        // 处理可选类型
        if (typeStr.StartsWith("optional[")) {
            auto innerTypeStr = typeStr.substr(9, typeStr.size() - 10);
            auto innerType = CreateFromString(innerTypeStr);
            return Optional(innerType);
        }

        // 处理列表类型
        if (typeStr.StartsWith("list[")) {
            auto elementTypeStr = typeStr.substr(5, typeStr.size() - 6);
            auto elementType = CreateFromString(elementTypeStr);
            return List(elementType);
        }

        throw std::invalid_argument("Unknown type string: " + typeStr);
    }

    // 创建数值类型
    static TLogicalTypePtr CreateNumericType(bool isSigned, int bits) {
        if (isSigned) {
            switch (bits) {
                case 8: return Int8();
                case 16: return Int16();
                case 32: return Int32();
                case 64: return Int64();
                default: throw std::invalid_argument("Unsupported signed integer bits: " + std::to_string(bits));
            }
        } else {
            switch (bits) {
                case 8: return Uint8();
                case 16: return Uint16();
                case 32: return Uint32();
                case 64: return Uint64();
                default: throw std::invalid_argument("Unsupported unsigned integer bits: " + std::to_string(bits));
            }
        }
    }

    // 创建精确时间类型
    static TLogicalTypePtr CreateTimestampType(bool withTimeZone = false, int precision = 6) {
        if (withTimeZone) {
            switch (precision) {
                case 0: return TzTimestamp();
                case 6: return TzTimestamp64();
                default: throw std::invalid_argument("Unsupported timezone timestamp precision: " + std::to_string(precision));
            }
        } else {
            switch (precision) {
                case 0: return Timestamp();
                case 6: return Timestamp64();
                default: throw std::invalid_argument("Unsupported timestamp precision: " + std::to_string(precision));
            }
        }
    }
};
```

## 性能考虑

### 类型缓存
- 类型对象可以被重用，避免重复创建
- 相同类型对象在内存中是共享的
- 合理使用类型缓存减少内存分配

### 编译时优化
- 模板函数在编译时展开，减少运行时开销
- 内联函数提供零成本抽象
- 类型检查主要在编译时完成

### 内存使用
- 复杂类型可能占用较多内存
- 避免创建过于深的嵌套结构
- 合理设计类型层次结构

## 最佳实践

### 1. 命名约定
```cpp
// 使用有意义的变量名
auto userIdType = Int64();
auto emailType = Optional(String());
var eventTimestampType = Timestamp();

// 对于复杂类型，使用描述性名称
var userProfileSchema = Struct(
    "basic_info", Struct(
        "user_id", Int64(),
        "username", String(),
        "email", Optional(String())
    ),
    "preferences", Dict(String(), String()),
    "activity_stats", Struct(
        "login_count", Int64(),
        "last_login", Timestamp()
    )
);
```

### 2. 类型组合
```cpp
// 创建可重用的类型组件
auto addressType = Struct(
    "street", String(),
    "city", String(),
    "state", String(),
    "postal_code", String(),
    "country", String()
);

auto contactInfoType = Struct(
    "email", String(),
    "phone", Optional(String()),
    "address", addressType
);

// 在多个模式中重用
auto customerSchema = Struct(
    "customer_id", Int64(),
    "name", String(),
    "contact", contactInfoType
);

auto vendorSchema = Struct(
    "vendor_id", String(),
    "company_name", String(),
    "contact", contactInfoType
);
```

### 3. 类型验证
```cpp
class TypeValidator {
public:
    static void ValidateStructType(const TLogicalTypePtr& type,
                                  const std::vector<TString>& requiredFields) {
        if (type->GetMetatype() != ELogicalMetatype::Struct) {
            throw std::invalid_argument("Expected struct type");
        }

        auto structType = type->AsStructType();
        auto fields = structType->GetFields();
        THashSet<TString> fieldNames;
        for (const auto& field : fields) {
            fieldNames.insert(field.Name);
        }

        for (const auto& requiredField : requiredFields) {
            if (fieldNames.find(requiredField) == fieldNames.end()) {
                throw std::invalid_argument("Missing required field: " + requiredField);
            }
        }
    }

    static void ValidateListElementType(const TLogicalTypePtr& listType,
                                       const TLogicalTypePtr& expectedElementType) {
        if (listType->GetMetatype() != ELogicalMetatype::List) {
            throw std::invalid_argument("Expected list type");
        }

        auto actualElementType = listType->AsListType()->GetElement();
        if (!actualElementType->Equals(expectedElementType)) {
            throw std::invalid_argument("List element type mismatch");
        }
    }
};
```

## 依赖项

- **YT Client Library**: 逻辑类型定义和实现
- **Standard Library**: STL 容器和字符串处理

## 注意事项

### 1. 类型一致性
- 确保在代码中使用的类型定义保持一致
- 避免在不同地方创建语义相同但结构不同的类型
- 使用共享的类型定义减少重复

### 2. 版本兼容性
- 逻辑类型定义可能随版本演进
- 注意类型系统的向后兼容性
- 测试代码应使用稳定的类型定义

### 3. 性能影响
- 复杂类型的创建和比较可能较慢
- 在性能关键路径上缓存类型对象
- 避免在热路径中频繁创建复杂类型

### 4. 内存管理
- 类型对象是引用计数的，正确管理生命周期
- 避免循环引用导致的内存泄漏
- 合理使用弱引用打破循环

### 5. 序列化兼容性
- 确保类型的序列化格式稳定
- 考虑类型演进对序列化的影响
- 测试类型序列化和反序列化的正确性