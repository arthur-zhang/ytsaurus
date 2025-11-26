# YTsaurus Table Client 模块

## 概述

Table Client 模块是 YTsaurus 表数据系统的核心客户端接口，提供了结构化数据的完整操作能力。该模块支持表的数据读写、模式管理、事务操作和性能优化等功能，是 YTsaurus 最重要和最常用的客户端模块。

## 核心功能

### 1. 表数据操作
- **读取操作**: SelectRows、LookupRows、Get 等读取功能
- **写入操作**: InsertRows、DeleteRows、UpdateRows 等写入功能
- **批量操作**: 高效的批量数据操作
- **流式处理**: 大数据量的流式读写

### 2. 模式管理
- **表模式**: 表结构定义和管理
- **动态模式**: 动态表模式支持
- **模式推断**: 自动模式推断
- **类型系统**: 丰富的数据类型支持

### 3. 事务支持
- **ACID 事务**: 完整的 ACID 事务支持
- **快照隔离**: 多版本并发控制
- **锁管理**: 精细的锁控制机制
- **嵌套事务**: 支持嵌套事务

### 4. 性能优化
- **列式存储**: 高效的列式存储格式
- **压缩**: 多种压缩算法支持
- **分区**: 表分区和分片
- **索引**: 多级索引支持

## 主要组件

### 1. 客户端接口
- **IClient**: 主要的表操作客户端接口
- **ITransaction**: 事务操作接口
- **ITableReader**: 表数据读取器
- **ITableWriter**: 表数据写入器

### 2. 数据类型
- **数据值**: TUnversionedValue、TVersionedValue
- **数据行**: TUnversionedRow、TVersionedRow
- **数据类型**: 丰富的数据类型系统
- **模式对象**: TTableSchema、TColumnSchema

### 3. 配置系统
- **读取器配置**: 表读取参数配置
- **写入器配置**: 表写入参数配置
- **客户端配置**: 客户端行为配置
- **性能配置**: 性能优化参数

## 使用方法

### 1. 基本表操作

```cpp
#include <yt/yt/client/table_client/public.h>

using namespace NYT::NTableClient;

// 创建表客户端
auto client = CreateClient(config);

// 创建表
auto schema = TTableSchema()
    .AddColumn(TColumnSchema("id", ESimpleLogicalValueType::Int64, "Row ID"))
    .AddColumn(TColumnSchema("name", ESimpleLogicalValueType::String, "Name"))
    .AddColumn(TColumnSchema("timestamp", ESimpleLogicalValueType::Timestamp, "Timestamp"));

client->CreateNode("/path/to/table", EObjectType::Table,
    NYTree::BuildYsonNodeFluently()
        .BeginMap()
            .Item("schema").Value(schema)
            .Item("dynamic").Value(false)
        .EndMap());

// 写入数据
auto writer = client->CreateTableWriter("/path/to/table");
writer->Write(BuildRow({{"id", 1}, {"name", "Alice"}, {"timestamp", 1234567890}}));
writer->Write(BuildRow({{"id", 2}, {"name", "Bob"}, {"timestamp", 1234567891}}));
writer->Close();

// 读取数据
auto reader = client->CreateTableReader("/path/to/table");
for (const auto& row : *reader) {
    std::cout << "ID: " << row["id"] << ", Name: " << row["name"] << std::endl;
}
```

### 2. 事务操作

```cpp
// 开始事务
auto transaction = client->StartTransaction(NTransactionClient::ETransactionType::Master);

// 在事务中执行操作
transaction->CreateNode("/path/to/table", EObjectType::Table, tableSchema);
auto writer = transaction->CreateTableWriter("/path/to/table");
writer->Write(rowData);
writer->Close();

// 提交事务
transaction->Commit();
```

### 3. 高级查询

```cpp
// 查询表数据
auto selectResult = client->SelectRows(
    "id, name FROM `/path/to/table` WHERE id > 100 ORDER BY name LIMIT 10");

// 查找特定行
TLookupRowsOptions lookupOptions;
lookupOptions.KeepMissingRows = true;
auto lookupResult = client->LookupRows(
    "/path/to/table",
    nameTable,
    keyColumns,
    lookupKeys,
    lookupOptions);
```

## 性能优化

### 1. 批量操作
- **批量写入**: 使用批量写入提高吞吐量
- **批量读取**: 一次读取多行数据
- **预取**: 智能数据预取策略

### 2. 内存优化
- **内存池**: 复用内存缓冲区
- **零拷贝**: 最小化内存拷贝操作
- **压缩**: 实时压缩减少内存使用

### 3. 并发优化
- **并行读取**: 并行读取多个数据块
- **连接池**: 复用网络连接
- **异步操作**: 异步 I/O 操作

## 依赖项

### 内部依赖
- `yt/yt/core/misc/public.h` - 核心公共定义
- `yt/yt/core/ytree/public.h` - YSON 处理

### 外部依赖
- 压缩库
- 网络通信库
- 线程库

## 相关模块

- **Formats Client**: 数据格式处理
- **Chunk Client**: 分片存储
- **Transaction Client**: 事务管理

## 参考文档

- [YTsaurus 表系统指南](../../../docs/table-system.md)
- [数据类型参考](../../../docs/data-types.md)
- [性能优化指南](../../../docs/performance-optimization.md)

## 贡献指南

在修改此模块时：
1. 确保数据一致性和事务正确性
2. 优化大规模数据处理性能
3. 保持 API 向后兼容性
4. 添加充分的测试覆盖
5. 考虑错误处理和恢复机制