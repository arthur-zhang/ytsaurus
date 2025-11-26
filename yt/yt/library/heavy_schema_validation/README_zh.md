# Heavy Schema Validation (重量级模式验证)

## 项目概述

Heavy Schema Validation 模块提供了 YTsaurus 表模式的深度验证功能。该模块负责验证表结构的正确性、一致性以及模式更新的合法性，确保数据模型的完整性和数据操作的安全性。

## 核心功能

### 模式验证
- **表模式验证**: 验证完整表结构的正确性和一致性
- **列模式验证**: 验证单个列的定义和约束
- **模式更新验证**: 验证模式变更的合法性和向后兼容性
- **计算列验证**: 专门处理计算列的复杂验证逻辑
- **动态表支持**: 针对动态表的特殊验证规则

### 高级验证功能
- **重量级验证**: 包含 QL 相关的复杂验证逻辑
- **聚合列验证**: 验证聚合列的定义和使用
- **计算列兼容性**: 验证计算列在不同模式间的兼容性
- **表达式验证**: 验证计算列中的表达式语法和语义

## 主要接口

### 核心验证函数

#### 1. 列模式验证

```cpp
// 验证列模式的更新
void ValidateColumnSchemaUpdate(
    const TColumnSchema& oldColumn,
    const TColumnSchema& newColumn);
```

#### 2. 表模式验证

```cpp
// 内部表模式验证（支持详细配置）
void ValidateTableSchemaUpdateInternal(
    const TTableSchema& oldSchema,
    const TTableSchema& newSchema,
    TSchemaUpdateEnabledFeatures enabledFeatures,
    bool isTableDynamic = false,
    bool isTableEmpty = false,
    bool allowAlterKeyColumnToAny = false,
    const TSchemaValidationOptions& options = {});

// 标准表模式验证
void ValidateTableSchemaUpdate(
    const TTableSchema& oldSchema,
    const TTableSchema& newSchema,
    bool isTableDynamic = false,
    bool isTableEmpty = false);

// 重量级表模式验证（包含 QL 相关验证）
void ValidateTableSchemaHeavy(
    const TTableSchema& schema,
    bool isTableDynamic,
    const TSchemaValidationOptions& options = {});
```

#### 3. 计算列验证

```cpp
// 验证计算列定义
void ValidateComputedColumns(
    const TTableSchema& schema,
    bool isTableDynamic);

// 验证计算列兼容性
TError ValidateComputedColumnsCompatibility(
    const TTableSchema& inputSchema,
    const TTableSchema& outputSchema);

// 验证计算列表达式
NQueryClient::TColumnSet ValidateComputedColumnExpression(
    const TColumnSchema& columnSchema,
    const TTableSchema& schema,
    bool isTableDynamic,
    bool allowDependenceOnNonKeyColumns);
```

### 配置结构

#### 1. 模式更新功能配置

```cpp
struct TSchemaUpdateEnabledFeatures
{
    bool EnableStaticTableDropColumn = false;    // 静态表删除列功能
    bool EnableDynamicTableDropColumn = false;    // 动态表删除列功能
};
```

## 使用方法

### 基本模式验证示例

```cpp
#include <yt/yt/library/heavy_schema_validation/schema_validation.h>

using namespace NYT::NTableClient;

// 创建旧模式
TTableSchema oldSchema;
oldSchema.AddColumn(TColumnSchema("id", ESimpleLogicalValueType::Int64));
oldSchema.AddColumn(TColumnSchema("name", ESimpleLogicalValueType::String));

// 创建新模式
TTableSchema newSchema;
newSchema.AddColumn(TColumnSchema("id", ESimpleLogicalValueType::Int64));
newSchema.AddColumn(TColumnSchema("name", ESimpleLogicalValueType::String));
newSchema.AddColumn(TColumnSchema("age", ESimpleLogicalValueType::Int64));

try {
    // 验证模式更新
    ValidateTableSchemaUpdate(oldSchema, newSchema, false, false);
    Cout << "Schema validation passed" << Endl;
} catch (const TErrorException& e) {
    Cerr << "Schema validation failed: " << e.Error().GetMessage() << Endl;
}
```

### 计算列验证示例

```cpp
// 创建包含计算列的模式
TTableSchema schemaWithComputed;
schemaWithComputed.AddColumn(TColumnSchema("id", ESimpleLogicalValueType::Int64));
schemaWithComputed.AddColumn(TColumnSchema("first_name", ESimpleLogicalValueType::String));
schemaWithComputed.AddColumn(TColumnSchema("last_name", ESimpleLogicalValueType::String));

// 添加计算列
auto computedColumn = TColumnSchema("full_name", ESimpleLogicalValueType::String);
computedColumn.SetExpression("first_name + ' ' + last_name");
schemaWithComputed.AddColumn(computedColumn);

try {
    // 验证计算列
    ValidateComputedColumns(schemaWithComputed, false);
    Cout << "Computed columns validation passed" << Endl;
} catch (const TErrorException& e) {
    Cerr << "Computed columns validation failed: " << e.Error().GetMessage() << Endl;
}
```

### 高级模式验证示例

```cpp
#include <yt/yt/library/query/base/public.h>

using namespace NYT;
using namespace NYT::NTableClient;

// 配置验证选项
TSchemaValidationOptions options;
options.AllowUnknownColumns = true;
options.RequireStrictTypeCompatibility = false;

// 配置启用功能
TSchemaUpdateEnabledFeatures features;
features.EnableStaticTableDropColumn = true;
features.EnableDynamicTableDropColumn = true;

try {
    // 使用高级配置验证模式更新
    ValidateTableSchemaUpdateInternal(
        oldSchema,
        newSchema,
        features,
        false,  // isTableDynamic
        false,  // isTableEmpty
        false,  // allowAlterKeyColumnToAny
        options);

    Cout << "Advanced schema validation passed" << Endl;
} catch (const TErrorException& e) {
    Cerr << "Advanced schema validation failed: " << e.Error().GetMessage() << Endl;
}
```

### 重量级验证示例

```cpp
try {
    // 执行重量级验证（包含 QL 相关检查）
    ValidateTableSchemaHeavy(
        schemaWithComputed,
        false,  // isTableDynamic
        options);

    Cout << "Heavy schema validation passed" << Endl;
} catch (const TErrorException& e) {
    Cerr << "Heavy schema validation failed: " << e.Error().GetMessage() << Endl;
}
```

## 配置说明

### 模式更新功能特性

| 功能 | 默认值 | 说明 |
|------|--------|------|
| EnableStaticTableDropColumn | false | 是否允许静态表删除列 |
| EnableDynamicTableDropColumn | false | 是否允许动态表删除列 |

### 验证选项参数

| 参数 | 类型 | 说明 |
|------|------|------|
| AllowUnknownColumns | bool | 是否允许未知列 |
| RequireStrictTypeCompatibility | bool | 是否要求严格的类型兼容性 |
| ValidateComputedColumns | bool | 是否验证计算列 |
| ValidateExpressionSyntax | bool | 是否验证表达式语法 |

### 验证规则

#### 1. 列类型兼容性
- 基本类型的扩展和转换规则
- 复杂类型的结构兼容性检查
- 可空性和默认值的一致性要求

#### 2. 键列约束
- 键列不能删除（特殊情况下除外）
- 键列类型变更的严格限制
- 排序顺序的一致性要求

#### 3. 计算列规则
- 表达式语法正确性
- 引用列的存在性和类型
- 循环依赖检测
- 动态表的特殊限制

## 性能考虑

### 验证复杂度
- **简单验证**: O(n) 时间复杂度，其中 n 为列数
- **重量级验证**: O(n²) 时间复杂度，包含表达式分析
- **计算列验证**: O(n * m)，其中 m 为表达式复杂度

### 优化建议
1. **缓存验证结果**: 对于重复验证的场景，考虑缓存验证结果
2. **增量验证**: 对于大型模式，使用增量验证策略
3. **并行验证**: 对于独立的列，可以并行验证
4. **延迟验证**: 非关键验证可以延迟执行

## 最佳实践

### 1. 验证策略选择
```cpp
// 根据场景选择合适的验证级别
void ValidateSchemaByScenario(const TTableSchema& oldSchema,
                              const TTableSchema& newSchema,
                              bool isProduction) {
    if (isProduction) {
        // 生产环境使用完整验证
        TSchemaValidationOptions strictOptions;
        strictOptions.RequireStrictTypeCompatibility = true;
        ValidateTableSchemaUpdate(oldSchema, newSchema, false, false);
        ValidateTableSchemaHeavy(newSchema, false, strictOptions);
    } else {
        // 开发环境使用基本验证
        ValidateTableSchemaUpdate(oldSchema, newSchema, false, false);
    }
}
```

### 2. 错误处理和报告
```cpp
class SchemaValidator {
public:
    TError ValidateAndReport(const TTableSchema& oldSchema,
                            const TTableSchema& newSchema) {
        try {
            ValidateTableSchemaUpdate(oldSchema, newSchema, false, false);
            return TError();
        } catch (const TErrorException& e) {
            // 记录详细错误信息
            auto error = e.Error();
            LogValidationError(error);
            return error;
        }
    }

private:
    void LogValidationError(const TError& error) {
        // 格式化错误信息用于日志记录
        auto formattedError = error.GetMessage();
        // 添加上下文信息
        formattedError += "\nSchema validation failed. Please check column definitions and constraints.";
        // 记录到监控系统
        Logger->LogEvent(TLogger::ELevel::Error, formattedError);
    }
};
```

### 3. 渐进式验证
```cpp
class ProgressiveSchemaValidator {
public:
    void ValidateProgressively(const TTableSchema& oldSchema,
                              const TTableSchema& newSchema) {
        // 第一阶段：基本结构验证
        ValidateBasicStructure(oldSchema, newSchema);

        // 第二阶段：类型兼容性验证
        ValidateTypeCompatibility(oldSchema, newSchema);

        // 第三阶段：计算列验证
        ValidateComputedColumns(newSchema, false);

        // 第四阶段：重量级验证
        ValidateTableSchemaHeavy(newSchema, false);
    }

private:
    void ValidateBasicStructure(const TTableSchema& oldSchema,
                               const TTableSchema& newSchema) {
        // 实现基本结构验证逻辑
    }

    void ValidateTypeCompatibility(const TTableSchema& oldSchema,
                                  const TTableSchema& newSchema) {
        // 实现类型兼容性验证逻辑
    }
};
```

## 依赖项

- **YT Client Library**: 表客户端和模式定义
- **YT Query Library**: 查询引擎支持和表达式验证
- **YT Core**: 基础数据结构和错误处理
- **Standard Library**: STL 容器和算法

## 注意事项

### 1. 验证范围
- 标准验证不包含 QL 相关的复杂检查
- 重量级验证需要查询引擎支持
- 计算列验证依赖于表达式解析器

### 2. 性能影响
- 重量级验证性能开销较大
- 复杂计算列可能显著增加验证时间
- 建议在非关键路径上使用重量级验证

### 3. 版本兼容性
- 不同版本间验证规则可能有差异
- 模式变更需要考虑向后兼容性
- 生产环境升级需要充分测试验证逻辑

### 4. 错误信息
- 验证失败时提供详细的错误信息
- 错误信息包含具体的失败原因和位置
- 建议实现用户友好的错误提示

### 5. 安全考虑
- 验证过程中的表达式执行需要沙箱环境
- 防止恶意表达式导致的资源耗尽
- 限制表达式的复杂度和执行时间