# YTsaurus Query Client 模块

## 概述

Query Client 模块是 YTsaurus 查询处理系统的客户端接口，提供了查询构建、执行和统计功能。该模块支持 YQL 查询语言，提供查询优化器、执行计划和性能统计等核心功能。

## 核心功能

### 1. 查询构建
- **YQL 支持**: 完整的 YQL 查询语言支持
- **查询构建器**: 程序化查询构建工具
- **类型安全**: 编译时类型检查的查询构建

### 2. 查询统计
- **性能统计**: 详细的查询执行统计
- **资源监控**: 查询资源使用情况
- **优化建议**: 查询性能优化建议

## 主要组件

### 1. 查询构建器 (query_builder.h/cpp)
```cpp
class TQueryBuilder {
public:
    TQueryBuilder& Select(const std::vector<TString>& columns);
    TQueryBuilder& From(const TString& table);
    TQueryBuilder& Where(const TString& condition);
    TString Build();
};
```

### 2. 查询统计 (query_statistics.h/cpp)
```cpp
struct TQueryStatistics {
    i64 RowsRead;
    i64 RowsWritten;
    TDuration ExecutionTime;
    i64 MemoryUsage;
    double CpuTime;
};
```

## 常量定义

```cpp
constexpr i64 DefaultRowsetProcessingBatchSize = 256;
constexpr i64 DefaultWriteRowsetSize = 256 * DefaultRowsetProcessingBatchSize;
constexpr i64 DefaultMaxJoinBatchSize = 512 * DefaultRowsetProcessingBatchSize;
```

## 使用方法

```cpp
#include <yt/yt/client/query_client/public.h>
#include <yt/yt/client/query_client/query_builder.h>

using namespace NYT::NQueryClient;

// 构建查询
auto query = TQueryBuilder()
    .Select({"user_id", "name", "email"})
    .From("users")
    .Where("registration_date >= '2023-01-01'")
    .Build();

// 执行查询
auto result = client->SelectRows(query);
```

## 统计聚合模式

```cpp
DEFINE_ENUM(EStatisticsAggregation,
    (None)            // 不聚合统计信息
    (Depth)           // 按深度聚合
    (DepthOmitNode)   // 按深度聚合但省略节点信息
);
```

## 依赖项

### 内部依赖
- `yt/yt/core/misc/public.h` - 核心公共定义

### 外部依赖
- 标准库 C++ 运行时

## 相关模块

- **Table Client**: 表数据操作
- **YQL Engine**: 查询执行引擎

## 贡献指南

在修改此模块时：
1. 确保查询语义的正确性
2. 优化查询性能
3. 添加充分的测试用例
4. 保持向后兼容性