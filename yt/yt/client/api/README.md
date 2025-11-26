# YTsaurus Client API

## 概述

`api` 目录是 YTsaurus 客户端的核心 API 模块，提供了与 YTsaurus 集群交互的完整客户端接口。该模块定义了统一的客户端 API，支持各种数据操作、事务管理、文件处理等功能。

## 核心功能

### 主要客户端接口
- **IClient**: 主要的客户端接口，提供完整的 YTsaurus 操作功能
- **IClientBase**: 基础客户端接口，包含可在独立模式和事务中共享的功能
- **ITransaction**: 事务接口，提供分布式事务管理功能
- **IConnection**: 连接管理接口，处理与集群的连接

### 专用客户端
- **IAdminClient**: 管理操作客户端，提供集群管理和维护功能
- **ICypressClient**: Cypress 元数据树操作客户端
- **ITableClient**: 表数据操作客户端，支持读写、查询等操作
- **IFileClient**: 文件操作客户端，处理分布式文件系统操作
- **IJournalClient**: 日志操作客户端，支持结构化日志写入和读取
- **IQueueClient**: 队列操作客户端，提供消息队列功能
- **ISecurityClient**: 安全相关操作客户端，处理用户和权限管理

### 分布式操作
- **IDistributedTableClient**: 分布式表操作
- **IDistributedFileClient**: 分布式文件操作
- **IOperationClient**: 操作管理客户端，处理 MapReduce、排序等分布式操作

### 特殊功能
- **IChaosClient**: 混沌测试客户端，支持故障注入和测试
- **IPrerequisiteClient**: 前置条件检查客户端
- **IQueryTrackerClient**: 查询跟踪客户端
- **IShuffleClient**: 数据混洗客户端

## 主要文件说明

### 核心头文件
- `client.h`: 主要客户端接口定义，包含 IClient 和 IClientBase
- `public.h`: 公共类型定义和枚举
- `config.h/.cpp`: 客户端配置管理
- `connection.h`: 连接接口定义

### 事务相关
- `transaction.h/.cpp`: 事务实现
- `delegating_transaction.h/.cpp`: 事务委托实现
- `sticky_transaction_pool.h/.cpp`: 粘性事务池

### 操作管理
- `operation_client.h/.cpp`: 分布式操作客户端，是最复杂的组件之一
- `persistent_queue.h/.cpp`: 持久化队列实现

### 数据处理
- `table_client.h/.cpp`: 表数据操作
- `file_client.h/.cpp`: 文件操作
- `journal_client.h/.cpp`: 日志操作

## 配置选项

### 连接配置
- `EConnectionType`: 连接类型枚举
- `EMasterChannelKind`: Master 通信通道类型
- `EUserWorkloadCategory`: 用户工作负载类别

### 超时和重试
- 支持各种操作的超时配置
- 自动重试机制
- 故障转移支持

## 使用示例

### 基本客户端使用
```cpp
#include <yt/yt/client/api/client.h>

// 创建客户端连接
auto connection = NYT::NApi::CreateConnection(config);
auto client = connection->CreateClient(NYT::NApi::TClientOptions());

// 基本操作
auto result = client->GetNode("/path/to/node");
```

### 事务使用
```cpp
// 开始事务
auto transaction = client->StartTransaction(NYT::NApi::TTransactionStartOptions());

// 在事务中执行操作
transaction->SetNode("/path", value);

// 提交事务
transaction->Commit();
```

## 架构设计

### 分层架构
1. **API 层**: 提供统一的客户端接口
2. **驱动层**: 处理网络通信和协议
3. **缓存层**: 客户端缓存优化
4. **重试层**: 自动故障处理和重试

### 异步支持
- 所有操作都支持异步模式
- 基于 Future/Promise 模式
- 支持操作取消

### 错误处理
- 统一的错误类型定义
- 详细的错误信息
- 自动重试策略

## 性能优化

### 缓存机制
- Master 信息缓存
- 连接池管理
- 结果缓存

### 批量操作
- 支持批量请求
- 请求合并优化
- 流式数据处理

### 负载均衡
- 多 Master 支持自动负载均衡
- 智能路由选择
- 故障自动转移

## 线程安全

- 所有客户端接口都是单线程亲和的
- 支持多客户端实例并行使用
- 提供线程安全的连接管理

## 依赖关系

### 核心依赖
- `yt/yt/client/` 下各个专用客户端模块
- `yt/yt/core/` 核心库
- `yt/yt/library/` 共享库

### 外部依赖
- Protocol Buffers (序列化)
- gRPC/RPC 框架
- Apache Arrow (列式存储)

## 注意事项

1. **资源管理**: 客户端和连接需要正确释放资源
2. **异常安全**: 所有操作都需要适当的异常处理
3. **性能考虑**: 避免频繁创建/销毁客户端连接
4. **配置管理**: 合理配置超时和重试参数
5. **版本兼容性**: 保持客户端与服务端版本兼容

## 扩展性

该模块设计支持：
- 新的客户端类型扩展
- 自定义负载均衡策略
- 插件化的错误处理机制
- 可配置的性能优化选项