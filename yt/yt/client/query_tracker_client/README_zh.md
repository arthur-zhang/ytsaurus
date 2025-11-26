# Query Tracker Client - 查询跟踪客户端

本模块提供查询跟踪系统的客户端接口，用于管理、监控和跟踪 YTsaurus 中执行的各类查询。支持多种查询引擎，包括 YQL、CHYT、SPYT 等。

## 核心概念

### 1. 查询标识符 (TQueryId)

每个查询都有唯一的 128 位标识符：

```cpp
using TQueryId = TGuid;  // 全局唯一查询ID
```

### 2. 查询引擎 (EQueryEngine)

支持多种查询引擎：

```cpp
enum EQueryEngine {
    Ql,           // YTsaurus Query Language (原生查询语言)
    Yql,          // YQL (Yandex Query Language)
    Chyt,         // ClickHouse on YT (ClickHouse集成)
    Mock,         // 模拟引擎（用于测试）
    Spyt,         // Spark on YT (Spark集成)
    SpytConnect   // Spark Connect (Spark连接器)
};
```

### 3. 查询状态 (EQueryState)

查询的生命周期状态：

```cpp
enum EQueryState {
    Draft,      // 草稿 - 查询已创建但未提交
    Pending,    // 等待中 - 查询已提交，等待执行
    Running,    // 运行中 - 查询正在执行
    Aborting,   // 中止中 - 正在中止查询
    Aborted,    // 已中止 - 查询被中止
    Completing, // 完成中 - 查询即将完成
    Completed,  // 已完成 - 查询成功完成
    Failing,    // 失败中 - 查询即将失败
    Failed,     // 已失败 - 查询执行失败
};
```

## 查询生命周期

```
[Draft] -> [Pending] -> [Running] -> [Completing] -> [Completed]
                     |            |
                     v            v
                  [Aborting] -> [Aborted]
                     |
                     v
                  [Failing] -> [Failed]
```

## 错误处理

```cpp
DEFINE_ERROR_ENUM(
    (IncarnationMismatch, 3900),  // 实例不匹配 - 查询跟踪器实例已改变
    (QueryNotFound,       3901),  // 查询未找到 - 指定的查询ID不存在
    (QueryResultNotFound, 3902),  // 查询结果未找到 - 查询完成但结果不可用
    (TooManyAcos,         3903),  // ACOS过多 - 访问控制对象过多
    (StateMismatch,       3904),  // 状态不匹配 - 操作与当前查询状态冲突
);
```

## 常量定义

```cpp
inline const std::string ProductionStage = "production";  // 生产阶段标识
```

## 使用示例

### 创建和跟踪查询
```cpp
#include <yt/yt/client/query_tracker_client/public.h>

// 查询ID会在提交查询时由系统生成
TQueryId queryId;  // 将从查询响应中获取

// 可以通过查询ID跟踪查询状态
// 伪代码示例：
// auto response = SubmitQuery(yqlQuery, EQueryEngine::Yql);
// queryId = response.QueryId;
//
// while (true) {
//     auto status = GetQueryStatus(queryId);
//     switch (status.State) {
//         case EQueryState::Running:
//             std::cout << "Query is running..." << std::endl;
//             break;
//         case EQueryState::Completed:
//             std::cout << "Query completed!" << std::endl;
//             auto result = GetQueryResult(queryId);
//             ProcessResult(result);
//             break;
//         case EQueryState::Failed:
//             std::cout << "Query failed: " << status.Error << std::endl;
//             break;
//     }
// }
```

### 错误处理
```cpp
try {
    auto result = GetQueryResult(queryId);
    // 处理结果
} catch (const NYT::NQueryTrackerClient::TErrorException& e) {
    if (e.GetErrorCode() == NYT::NQueryTrackerClient::EErrorCode::QueryNotFound) {
        std::cerr << "Query not found: " << queryId << std::endl;
    } else if (e.GetErrorCode() == NYT::NQueryTrackerClient::EErrorCode::StateMismatch) {
        std::cerr << "Invalid operation for current query state" << std::endl;
    }
}
```

## 设计原理

### 多引擎支持
1. **统一接口**：为不同查询引擎提供统一的客户端接口
2. **引擎特定优化**：每种引擎可以利用其特定的功能
3. **透明切换**：用户可以在不同引擎间切换而无需改变客户端代码

### 状态管理
1. **严格状态转换**：查询状态只能按照预定义的路径转换
2. **状态持久化**：查询状态持久化存储，支持故障恢复
3. **并发安全**：状态转换是原子的，避免竞态条件

### 生命周期管理
1. **自动清理**：完成的查询会在一定时间后自动清理
2. **资源限制**：限制同时运行的查询数量
3. **优先级调度**：支持查询优先级和资源分配

## 集成说明

### 与 YQL 集成
- 支持完整的 YQL 语法
- 自动处理 UDF 和外部数据源
- 支持查询优化和执行计划

### 与 ClickHouse 集成 (CHYT)
- 利用 ClickHouse 的高性能分析能力
- 支持ClickHouse扩展函数
- 无缝访问 YTsaurus 中的数据

### 与 Spark 集成 (SPYT)
- 支持 Spark 作业提交
- 利用 Spark 生态系统
- 支持流处理和批处理

## 性能考虑

1. **查询跟踪开销**：跟踪系统对查询性能影响最小
2. **状态更新频率**：状态更新采用批处理以减少开销
3. **结果缓存**：支持查询结果缓存
4. **资源监控**：实时监控查询资源使用

## 依赖项

- `yt/yt/core/misc/guid.h` - GUID 生成和操作
- `library/cpp/yt/misc/enum.h` - 枚举支持

## 注意事项

1. **查询ID管理**：保存查询ID以便后续跟踪
2. **状态检查**：在执行操作前检查查询状态
3. **错误处理**：妥善处理各种错误情况
4. **资源清理**：及时取消不需要的查询以释放资源
5. **超时设置**：为长时间运行的查询设置合理的超时

## 相关模块

- `yt/yt/server/query_tracker` - 查询跟踪服务端实现
- `yt/yt/client/query_client` - 查询客户端
- `yt/yt/client/table_client` - 表客户端（查询数据源）
- `yt/yt/core/rpc` - RPC 通信层

## 最佳实践

1. **查询组织**：为查询设置有意义的描述和标签
2. **资源估算**：提交查询时估算所需资源
3. **超时管理**：根据查询复杂度设置合理超时
4. **结果处理**：及时获取并处理查询结果
5. **错误重试**：实现适当的重试机制处理临时故障