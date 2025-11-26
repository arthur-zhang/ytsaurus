# Query Client - 查询客户端

本模块提供 YTsaurus 的查询构建和统计功能，支持 SQL 风格的查询构建、执行统计收集和性能分析。

## 核心组件

### 1. 查询构建器 (TQueryBuilder)

`TQueryBuilder` 类提供了编程式构建查询的功能，支持常见的 SQL 操作：

```cpp
class TQueryBuilder {
public:
    // 设置数据源
    void SetSource(std::string source, int syntaxVersion = 1, bool subquerySource = false);
    void SetSource(std::string source, std::string alias, int syntaxVersion = 1, bool subquerySource = false);

    // SELECT 子句
    int AddSelectExpression(std::string expression);
    int AddSelectExpression(std::string expression, std::string alias);

    // WHERE 子句
    void AddWhereConjunct(std::string expression);

    // GROUP BY 子句
    void AddGroupByExpression(std::string expression);
    void AddGroupByExpression(std::string expression, std::string alias);

    // HAVING 子句
    void AddHavingConjunct(std::string expression);

    // ORDER BY 子句
    void AddOrderByExpression(std::string expression);
    void AddOrderByExpression(std::string expression, std::optional<EOrderByDirection> direction);
    void AddOrderByAscendingExpression(std::string expression);
    void AddOrderByDescendingExpression(std::string expression);

    // JOIN 操作
    void AddJoinExpression(std::string table, std::string alias, std::string onExpression, ETableJoinType type, std::string predicate = "");
    void AddArrayJoinExpression(const std::vector<std::string>& expressions, const std::vector<std::string>& aliases, ETableJoinType type, std::string predicate = "");

    // 分页
    void SetOffset(i64 offset);
    void SetLimit(i64 limit);

    // 构建最终查询字符串
    std::string Build();
};
```

#### 支持的枚举类型

**排序方向**：
```cpp
enum EOrderByDirection {
    Ascending,   // 升序
    Descending   // 降序
};
```

**表连接类型**：
```cpp
enum ETableJoinType {
    Inner,       // 内连接
    Left,        // 左连接
    ArrayInner,  // 数组内连接
    ArrayLeft    // 数组左连接
};
```

**总计模式**：
```cpp
enum EWithTotalsMode {
    None,         // 无总计
    BeforeHaving, // HAVING 之前计算总计
    AfterHaving   // HAVING 之后计算总计
};
```

### 2. 查询统计 (TQueryStatistics)

查询统计功能提供了详细的查询执行信息：

```cpp
struct TQueryStatistics {
    // 数据统计
    TAggregate<i64> RowsRead;          // 读取的行数
    TAggregate<i64> DataWeightRead;    // 读取的数据权重
    TAggregate<i64> RowsWritten;       // 写入的行数
    TAggregate<i64> MemoryUsage;       // 内存使用量
    TAggregate<i64> GroupedRowCount;   // 分组后的行数

    // 时间统计
    TAggregate<TDuration> SyncTime;              // 同步时间
    TAggregate<TDuration> AsyncTime;             // 异步时间
    TAggregate<TDuration> ExecuteTime;           // 执行时间
    TAggregate<TDuration> ReadTime;              // 读取时间
    TAggregate<TDuration> WriteTime;             // 写入时间
    TAggregate<TDuration> CodegenTime;           // 代码生成时间
    TAggregate<TDuration> WaitOnReadyEventTime; // 等待就绪事件时间

    // 执行状态
    bool IncompleteInput = false;  // 输入是否不完整
    bool IncompleteOutput = false; // 输出是否不完整
    i64 QueryCount = 1;            // 查询数量

    // 嵌套统计
    std::vector<TQueryStatistics> InnerStatistics;
};
```

### 3. 聚合统计 (TAggregate)

聚合统计类用于收集和合并统计数据：

```cpp
template <class T>
class TAggregate {
    DEFINE_BYVAL_RW_PROPERTY(T, Total);      // 总和
    DEFINE_BYVAL_RW_PROPERTY(T, Max);        // 最大值
    DEFINE_BYREF_RW_PROPERTY(std::string, ArgmaxNode); // 最大值对应的节点

    void Set(T value, EStatisticsAggregation statisticsAggregation);
    void Merge(const TAggregate<T>& other);
};
```

### 4. 执行统计 (TExecutionStatistics)

单次查询的执行统计信息：

```cpp
struct TExecutionStatistics {
    i64 RowsRead = {};
    i64 DataWeightRead = {};
    i64 RowsWritten = {};
    i64 GroupedRowCount = {};

    TDuration SyncTime;
    TDuration AsyncTime;
    TDuration ExecuteTime;
    TDuration ReadTime;
    TDuration WriteTime;
    TDuration CodegenTime;
    TDuration WaitOnReadyEventTime;

    bool IncompleteInput = false;
    bool IncompleteOutput = false;
};
```

## 使用示例

### 使用查询构建器
```cpp
#include <yt/yt/client/query_client/query_builder.h>

// 创建查询构建器
TQueryBuilder builder;

// 设置数据源
builder.SetSource("//my_table", "t");

// 添加 SELECT 字段
builder.AddSelectExpression("user_id", "uid");
builder.AddSelectExpression("COUNT(*)", "cnt");
builder.AddSelectExpression("SUM(amount)", "total");

// 添加 WHERE 条件
builder.AddWhereConjunct("timestamp >= 2024-01-01");
builder.AddWhereConjunct("status = 'active'");

// 添加 GROUP BY
builder.AddGroupByExpression("user_id");

// 添加 ORDER BY
builder.AddOrderByDescendingExpression("cnt");

// 添加 LIMIT
builder.SetLimit(100);

// 构建查询
std::string query = builder.Build();
// 结果：SELECT user_id AS uid, COUNT(*) AS cnt, SUM(amount) AS total
//        FROM //my_table AS t
//        WHERE timestamp >= 2024-01-01 AND status = 'active'
//        GROUP BY user_id
//        ORDER BY cnt DESC
//        LIMIT 100
```

### 使用 JOIN
```cpp
TQueryBuilder builder;

// 主表
builder.SetSource("//orders", "o");

// 添加 JOIN
builder.AddJoinExpression(
    "//users",                    // 表名
    "u",                          // 别名
    "o.user_id = u.id",           // ON 条件
    ETableJoinType::Left          // 连接类型
);

// 选择字段
builder.AddSelectExpression("o.id", "order_id");
builder.AddSelectExpression("u.name", "user_name");
builder.AddSelectExpression("o.amount");

// 条件
builder.AddWhereConjunct("u.status = 'premium'");

std::string query = builder.Build();
// 结果：SELECT o.id AS order_id, u.name AS user_name, o.amount
//        FROM //orders AS o
//        LEFT JOIN //users AS u ON o.user_id = u.id
//        WHERE u.status = 'premium'
```

### 使用统计信息
```cpp
#include <yt/yt/client/query_client/query_statistics.h>

// 创建查询统计
TQueryStatistics statistics;

// 设置统计值
statistics.RowsRead.Set(1000, EStatisticsAggregation::None);
statistics.ExecuteTime.Set(TDuration::Seconds(5), EStatisticsAggregation::None);

// 合并其他统计
TQueryStatistics otherStats;
statistics.Merge(otherStats);

// 添加嵌套统计
statistics.AddInnerStatistics(innerStats);

// 序列化
NYson::TYsonString yson = ConvertToYsonString(statistics);
```

## 默认配置

```cpp
constexpr i64 DefaultRowsetProcessingBatchSize = 256;      // 行集处理批次大小
constexpr i64 DefaultWriteRowsetSize = 256 * DefaultRowsetProcessingBatchSize;  // 写入行集大小
constexpr i64 DefaultMaxJoinBatchSize = 512 * DefaultRowsetProcessingBatchSize; // 最大连接批次大小
```

## 统计聚合模式

```cpp
enum EStatisticsAggregation {
    None,           // 不聚合
    Depth,          // 按深度聚合
    DepthOmitNode   // 按深度聚合但省略节点
};
```

## 设计原理

### 查询构建器设计
1. **渐进式构建**：逐步添加查询组件
2. **类型安全**：编译时检查查询语法
3. **别名支持**：自动处理表和字段别名
4. **嵌套查询**：支持子查询作为数据源

### 统计系统设计
1. **多层次统计**：支持单个查询和聚合统计
2. **时间分解**：详细记录各个阶段的时间消耗
3. **聚合支持**：支持多种聚合策略
4. **嵌套查询**：跟踪嵌套查询的统计信息

## 依赖项

- `yt/yt/core/yson/public.h` - YSON 序列化
- `yt/yt/core/ytree/fluent.h` - YTree 流式接口
- 标准 C++ 库
- Yandex Util 库

## 注意事项

1. **查询构建**：查询字符串通过 `Build()` 方法生成，在此之前查询不完整
2. **别名管理**：重复的别名会导致构建失败
3. **统计聚合**：不同聚合模式会产生不同的统计结果
4. **性能影响**：统计收集会对查询性能产生轻微影响
5. **内存使用**：大量统计数据可能占用较多内存

## 相关模块

- `yt/yt/server/query_agent` - 查询代理服务端
- `yt/yt/core/concurrency` - 并发控制（查询执行的底层支持）
- `yt/yt/tablet_client` - Tablet 客户端（查询的主要数据源）