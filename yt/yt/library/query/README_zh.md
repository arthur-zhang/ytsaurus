# Query (查询引擎)

Query 是 YTsaurus 中实现的查询引擎，提供了类似 SQL 的查询语言支持，包括解析、优化和执行查询的完整功能。

## 概述

Query 库提供以下核心功能：
- 查询语言解析（类 SQL 语法）
- 查询表达式构建和评估
- 分布式查询执行
- 类型推断和验证
- 查询优化

## 目录结构

```
query/
├── base/                    # 查询基础组件
│   ├── ast.h              # 抽象语法树定义
│   ├── query.h            # 查询对象定义
│   ├── expr_builder*.cpp  # 表达式构建器
│   ├── functions.*        # 内置函数
│   └── parser.ypp         # 语法解析器
├── engine/                  # 查询执行引擎
├── engine_api/              # 执行引擎API
├── distributed/             # 分布式查询
├── row_comparer/            # 行比较器
├── row_comparer_api/        # 行比较器API
├── secondary_index/         # 二级索引
├── proto/                   # Protobuf定义
└── unittests/              # 单元测试
```

## 核心组件

### 1. AST (抽象语法树)
查询的抽象语法树表示：

```cpp
namespace NAst {

// 表达式类型
XX(TExpression)              // 基础表达式
XX(TLiteralExpression)        // 字面量表达式
XX(TReferenceExpression)      // 引用表达式
XX(TFunctionExpression)       // 函数表达式
XX(TBinaryOpExpression)       // 二元操作表达式
XX(TUnaryOpExpression)        // 一元操作表达式
XX(TInExpression)             // IN表达式
XX(TBetweenExpression)        // BETWEEN表达式
XX(TCaseExpression)           // CASE表达式
XX(TLikeExpression)           // LIKE表达式

// 查询表达式
struct TQueryExpression {
    std::vector<std::string> SelectExpressions;  // SELECT子句
    std::optional<std::string> FromTable;         // FROM子句
    std::optional<std::string> WherePredicate;    // WHERE子句
    std::optional<std::string> GroupByExpression;  // GROUP BY子句
    std::optional<std::string> HavingPredicate;   // HAVING子句
    std::vector<TOrderExpression> OrderExpressions; // ORDER BY子句
    std::optional<i64> Limit;                       // LIMIT子句
    std::optional<i64> Offset;                      // OFFSET子句
};

} // namespace NAst
```

### 2. 表达式系统
查询表达式的类型化表示：

```cpp
// 表达式基类
struct TExpression : public TRefCounted {
    TLogicalTypePtr LogicalType;          // 逻辑类型
    TLogicalTypePtr OriginalLogicalType;  // 原始类型

    // 获取传输类型
    EValueType GetWireType() const;

    // 类型转换
    template <class TDerived>
    const TDerived* As() const;
};

// 字面量表达式
struct TLiteralExpression : public TExpression {
    TOwningValue Value;  // 字面量值
};

// 引用表达式
struct TReferenceExpression : public TExpression {
    std::string ColumnName;  // 列名
};

// 函数表达式
struct TFunctionExpression : public TExpression {
    std::string FunctionName;                    // 函数名
    std::vector<TConstExpressionPtr> Arguments;  // 参数列表
};
```

### 3. 查询对象
查询的结构化表示：

```cpp
// 基础查询
struct TBaseQuery : public TRefCounted {
    std::optional<TString> SourcePath;    // 数据源路径
    std::optional<TString> TablePath;      // 表路径
    TTableSchemaPtr TableSchema;          // 表结构
    TJoinClausePtr JoinClause;            // JOIN子句
    TWhereClausePtr WhereClause;          // WHERE子句
    TGroupClausePtr GroupClause;          // GROUP BY子句
    THavingClausePtr HavingClause;        // HAVING子句
    TOrderClausePtr OrderClause;          // ORDER BY子句
    TProjectClausePtr ProjectClause;      // PROJECT子句
    i64 Limit = -1;                       // LIMIT
    i64 Offset = 0;                      // OFFSET
};

// 查询
struct TQuery : public TBaseQuery {
    std::vector<TConstExpressionPtr> SelectExpressions;  // SELECT表达式
    bool IsSimple = false;                                     // 是否简单查询
    bool IsFlagSet = false;                                     // 是否设置标志
};
```

## 主要功能

### 1. 查询解析
```cpp
#include <yt/yt/library/query/base/public.h>

using namespace NYT::NQueryClient;

// 解析查询字符串
TQueryPtr ParseQuery(const TString& query) {
    // 使用解析器将字符串转换为AST
    auto astHead = ParseAst(query);

    // 将AST转换为查询对象
    return PrepareQuery(astHead);
}

// 示例
auto query = ParseQuery(R"(
    SELECT user_id, COUNT(*) AS cnt
    FROM `//tmp/table`
    WHERE timestamp > 1000000
    GROUP BY user_id
    HAVING cnt > 10
    ORDER BY cnt DESC
    LIMIT 100
)");
```

### 2. 表达式构建
```cpp
// 构建引用表达式
auto refExpr = New<TReferenceExpression>(
    MakeLogicalType(EValueType::Int64),
    "user_id");

// 构建字面量表达式
auto literalExpr = New<TLiteralExpression>(
    EValueType::Int64,
    MakeUnversionedInt64Value(42));

// 构建函数表达式
auto funcExpr = New<TFunctionExpression>(
    MakeLogicalType(EValueType::Int64),
    "hash",
    std::vector<TConstExpressionPtr>{refExpr, literalExpr});
```

### 3. 查询执行
```cpp
// 创建执行器
auto executor = CreateExecutor(executorConfig);

// 准备查询
auto preparedQuery = PrepareQuery(query);

// 执行查询
auto reader = executor->Execute(
    preparedQuery,
    dataSplits,
    queryOptions,
    executionContext);

// 读取结果
TRow row;
while (reader->Read(&row)) {
    ProcessRow(row);
}
```

### 4. 分布式查询
```cpp
// 创建分布式执行器
auto distributedExecutor = CreateDistributedExecutor(
    executorConfig,
    channelFactory);

// 分割查询
auto fragments = SplitQuery(query, dataSplits);

// 执行片段
std::vector<ISchemafulUnversionedReaderPtr> readers;
for (const auto& fragment : fragments) {
    auto reader = distributedExecutor->ExecuteFragment(fragment);
    readers.push_back(reader);
}

// 合并结果
auto mergedReader = CreateMergeReader(readers);
```

## 内置函数

### 1. 聚合函数
```cpp
// COUNT
COUNT(*)            // 计数
COUNT(column)       // 非空值计数

// SUM, AVG, MIN, MAX
SUM(column)         // 求和
AVG(column)         // 平均值
MIN(column)         // 最小值
MAX(column)         // 最大值

// 其他
SUM_IF(column, condition)     // 条件求和
AVG_IF(column, condition)      // 条件平均值
```

### 2. 字符串函数
```cpp
// 字符串操作
LOWER(str)           // 转小写
UPPER(str)           // 转大写
SUBSTR(str, start, len)  // 子串
LENGTH(str)          // 长度
CONCAT(str1, str2)   // 连接

// 模式匹配
LIKE(str, pattern)   // 模式匹配
REGEXP_MATCH(str, regex)  // 正则匹配
```

### 3. 数学函数
```cpp
// 基础数学
ABS(x)               // 绝对值
ROUND(x)             // 四舍五入
CEIL(x)              // 向上取整
FLOOR(x)             // 向下取整

// 高级数学
SQRT(x)              // 平方根
POW(x, y)            // 幂运算
LOG(x)               // 自然对数
EXP(x)               // 指数
```

### 4. 时间函数
```cpp
// 时间操作
NOW()                // 当前时间
DATE(timestamp)      // 日期部分
HOUR(timestamp)      // 小时部分
MINUTE(timestamp)    // 分钟部分
SECOND(timestamp)    // 秒部分

// 时间计算
DATE_ADD(timestamp, interval)  // 时间加法
DATE_DIFF(start, end)           // 时间差
```

## 查询示例

### 1. 基础查询
```sql
-- 选择列
SELECT column1, column2 FROM table;

-- 带过滤
SELECT * FROM table WHERE condition;

-- 排序
SELECT * FROM table ORDER BY column DESC;
```

### 2. 聚合查询
```sql
-- 分组聚合
SELECT column, COUNT(*), AVG(value)
FROM table
WHERE timestamp > 1000000
GROUP BY column
HAVING COUNT(*) > 10;

-- 时间窗口聚合
SELECT
    DATE(timestamp) AS date,
    COUNT(*) AS cnt,
    AVG(value) AS avg_val
FROM table
GROUP BY DATE(timestamp)
ORDER BY date;
```

### 3. JOIN查询
```sql
-- 内连接
SELECT a.*, b.value
FROM table1 AS a
JOIN table2 AS b
ON a.key = b.key;

-- 左连接
SELECT a.*, b.value
FROM table1 AS a
LEFT JOIN table2 AS b
ON a.key = b.key;
```

### 4. 子查询
```sql
-- 标量子查询
SELECT column
FROM table
WHERE value > (SELECT AVG(value) FROM table2);

-- IN子查询
SELECT column
FROM table
WHERE key IN (SELECT key FROM table2 WHERE condition);
```

## 性能优化

### 1. 查询优化
- **谓词下推**: 将过滤条件尽可能下推到数据源
- **投影下推**: 只读取需要的列
- **常量折叠**: 编译时计算常量表达式
- **索引使用**: 利用索引加速查询

### 2. 内存优化
```cpp
// 使用行缓冲区
auto rowBuffer = New<TRowBuffer>();

// 批量处理
constexpr int BatchSize = 1000;
std::vector<TRow> batch;
batch.reserve(BatchSize);

while (reader->Read(&row)) {
    batch.push_back(row);
    if (batch.size() >= BatchSize) {
        ProcessBatch(batch);
        batch.clear();
    }
}
```

### 3. 并行执行
```cpp
// 并行执行片段
std::vector<TFuture<void>> futures;
for (const auto& fragment : fragments) {
    auto future = AsyncExecuteFragment(fragment);
    futures.push_back(future);
}

// 等待所有完成
WaitFor(AllSucceeded(futures));
```

## 最佳实践

### 1. 查询设计
```sql
-- 避免SELECT *
SELECT column1, column2  -- 明确列出需要的列

-- 使用索引友好的过滤
WHERE indexed_column = value  -- 利用索引

-- 限制结果集
LIMIT 1000  -- 避免返回过多数据
```

### 2. 类型使用
```cpp
// 使用强类型
auto intType = MakeLogicalType(EValueType::Int64);
auto stringType = MakeLogicalType(EValueType::String);
auto optionalType = MakeOptionalLogicalType(intType);

// 类型转换
auto castExpr = New<TFunctionExpression>(
    targetType,
    "cast",
    std::vector<TConstExpressionPtr>{sourceExpr});
```

### 3. 错误处理
```cpp
try {
    auto query = ParseQuery(sql);
    auto result = ExecuteQuery(query);
    ProcessResult(result);
} catch (const TQueryException& e) {
    YT_LOG_ERROR(e, "Query execution failed");
    HandleQueryError(e);
}
```

## 扩展机制

### 1. 自定义函数
```cpp
// 注册自定义函数
class MyFunctionRegistry : public IFunctionRegistry {
public:
    TFunctionDescriptorPtr FindFunction(const TString& name) override {
        if (name == "my_custom_func") {
            return CreateMyCustomFunctionDescriptor();
        }
        return nullptr;
    }
};

// 使用自定义函数注册表
auto customRegistry = New<MyFunctionRegistry>();
auto executor = CreateExecutor(executorConfig, customRegistry);
```

### 2. 自定义聚合函数
```cpp
// 实现聚合函数
struct MyAggregateFunction : public IAggregateFunction {
    // 状态初始化
    void Initialize(TMutableState& state) override;

    // 更新状态
    void Update(TMutableState& state, TUnversionedValue value) override;

    // 合并状态
    void Merge(TMutableState& state, const TState& other) override;

    // 生成结果
    TUnversionedValue Finalize(const TState& state) override;
};
```

## 依赖项

- YTsaurus 核心库 (`yt/yt/core/`)
- 表客户端库 (`yt/yt/client/table_client/`)
- 事务客户端库 (`yt/yt/client/transaction_client/`)
- YTree 库 (`yt/yt/core/ytree/`)
- Protocol Buffers

## 注意事项

1. **查询性能**: 复杂查询可能影响性能，合理使用索引
2. **内存使用**: 大结果集可能消耗大量内存
3. **类型安全**: 注意类型转换和隐式类型提升
4. **分布式特性**: 分布式查询需要考虑网络开销
5. **事务一致性**: 查询在事务上下文中的一致性保证
6. **并发控制**: 查询执行过程中的并发控制