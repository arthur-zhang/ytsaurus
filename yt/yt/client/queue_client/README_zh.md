# Queue Client - 队列客户端

本模块提供 YTsaurus 中队列系统的客户端功能，支持生产者-消费者模式的消息传递。队列系统基于表实现，提供高性能、可扩展、可靠的消息队列服务。

## 核心概念

### 1. 类型定义

```cpp
// 会话标识
using TQueueProducerSessionId = TString;
using TQueueProducerEpoch = i64;
using TQueueProducerSequenceNumber = i64;

// Rowset 接口
DECLARE_REFCOUNTED_STRUCT(IQueueRowset)
DECLARE_REFCOUNTED_STRUCT(IPersistentQueueRowset)

// 客户端接口
DECLARE_REFCOUNTED_STRUCT(IConsumerClient)
DECLARE_REFCOUNTED_STRUCT(ISubConsumerClient)
DECLARE_REFCOUNTED_STRUCT(IProducerClient)
DECLARE_REFCOUNTED_STRUCT(IProducerSession)
DECLARE_REFCOUNTED_STRUCT(IPartitionReader)
```

### 2. 错误类型

```cpp
DEFINE_ERROR_ENUM(
    (ConsumerOffsetConflict,            3100),  // 消费者偏移冲突
    (InvalidEpoch,                      3101),  // 无效的epoch
    (ZombieEpoch,                       3102),  // 僵尸epoch
    (InvalidRowSequenceNumbers,         3103),  // 无效的行序号
    (QueueAgentRetriableError,          3104),  // 队列代理可重试错误
    (QueueAgentObjectIsNotMapped,       3105),  // 队列代理对象未映射
);
```

## 核心组件

### 1. 生产者客户端 (IProducerClient)

生产者客户端用于向队列发送消息：

```cpp
struct IProducerClient : public virtual TRefCounted {
    // 创建生产者会话
    virtual TFuture<IProducerSessionPtr> CreateSession(
        const NYPath::TRichYPath& queuePath,        // 队列路径
        const NTableClient::TNameTablePtr& nameTable, // 名称表
        const NQueueClient::TQueueProducerSessionId& sessionId, // 会话ID
        const TProducerSessionOptions& options = {},    // 会话选项
        const IInvokerPtr& invoker = nullptr) = 0;      // 执行器
};
```

### 2. 生产者会话 (IProducerSession)

生产者会话管理消息的发送：

```cpp
struct IProducerSession : public NTableClient::IUnversionedRowsetWriter {
    // 获取最后发送的序列号
    virtual TQueueProducerSequenceNumber GetLastSequenceNumber() const = 0;

    // 获取用户元数据
    virtual const NYTree::INodePtr& GetUserMeta() const = 0;

    // 刷新所有写入的行
    virtual TFuture<void> Flush() = 0;

    // 取消未刷新的写入
    virtual void Cancel() = 0;
};
```

### 3. 生产者会话选项 (TProducerSessionOptions)

```cpp
struct TProducerSessionOptions {
    bool AutoSequenceNumber = false;  // 自动序列号
    TProducerSessionBatchOptions BatchOptions;  // 批处理选项
    std::optional<TDuration> BackgroundFlushPeriod;  // 后台刷新周期
    TBackoffStrategy BackoffStrategy;  // 退避策略
    TAckCallback AckCallback;  // 确认回调
    bool RequireSyncReplica = true;  // 需要同步副本
};

struct TProducerSessionBatchOptions {
    std::optional<i64> ByteSize;  // 字节大小阈值
    std::optional<i64> RowCount;  // 行数阈值
};
```

### 4. 消费者客户端 (IConsumerClient)

消费者客户端用于从队列接收消息：

```cpp
struct IConsumerClient : public TRefCounted {
    // 获取子消费者客户端
    virtual ISubConsumerClientPtr GetSubConsumerClient(
        const NApi::IClientPtr& queueClusterClient,
        const TCrossClusterReference& queueRef) const = 0;
};

struct ISubConsumerClient : public TRefCounted {
    // 推进分区偏移
    virtual void Advance(
        const NApi::ITransactionPtr& consumerTransaction,
        int partitionIndex,
        std::optional<i64> oldOffset,
        i64 newOffset) const = 0;

    // 收集分区信息
    virtual TFuture<std::vector<TPartitionInfo>> CollectPartitions(
        int expectedPartitionCount,
        bool withLastConsumeTime = false) const = 0;

    // 获取分区统计
    virtual TFuture<TPartitionStatistics> FetchPartitionStatistics(
        const NYPath::TYPath& queue,
        int partitionIndex) const = 0;
};
```

### 5. 分区信息 (TPartitionInfo)

```cpp
struct TPartitionInfo {
    i64 PartitionIndex = -1;           // 分区索引
    i64 NextRowIndex = -1;             // 下一行索引
    TInstant LastConsumeTime;          // 最后消费时间
    std::optional<TConsumerMeta> ConsumerMeta;  // 消费者元数据
};

struct TConsumerMeta : public NYTree::TYsonStructLite {
    std::optional<i64> CumulativeDataWeight;  // 累积数据权重
    std::optional<ui64> OffsetTimestamp;      // 偏移时间戳
};

struct TPartitionStatistics {
    i64 FlushedDataWeight = 0;  // 刷新的数据权重
    i64 FlushedRowCount = 0;    // 刷新的行数
};
```

## 使用示例

### 创建生产者并发送消息
```cpp
#include <yt/yt/client/queue_client/producer_client.h>
#include <yt/yt/client/api/client.h>

// 创建客户端
auto apiClient = connection->CreateClient(options);
auto producerClient = CreateProducerClient(apiClient, "//tmp/producer");

// 创建名称表
auto nameTable = NTableClient::TNameTable::FromKeyColumns(
    {"timestamp", "message", "user_id"}
);

// 创建会话选项
TProducerSessionOptions sessionOptions;
sessionOptions.AutoSequenceNumber = true;
sessionOptions.BatchOptions.RowCount = 100;
sessionOptions.BackgroundFlushPeriod = TDuration::Seconds(1);
sessionOptions.RequireSyncReplica = true;

// 创建会话
auto sessionId = TQueueProducerSessionId("my-session-1");
auto sessionFuture = producerClient->CreateSession(
    "//tmp/queue",
    nameTable,
    sessionId,
    sessionOptions
);

// 获取会话
auto session = sessionFuture.Get().ValueOrThrow();

// 写入消息
auto writer = session;
auto rowBuffer = New<NTableClient::TRowBuffer>();

// 写入第一行
auto row1 = NTableClient::TUnversionedRowBuilder()
    .AddValue(NTableClient::MakeUnversionedInt64Value(1234567890, 0))  // timestamp
    .AddValue(NTableClient::MakeUnversionedStringValue("Hello World", 1))  // message
    .AddValue(NTableClient::MakeUnversionedInt64Value(42, 2))  // user_id
    .Finish();
writer->WriteRow(row1);

// 写入更多行...
writer->WriteRow(row2);
writer->WriteRow(row3);

// 刷新确保消息发送
writer->Flush().Get().ThrowOnError();
```

### 创建消费者并接收消息
```cpp
#include <yt/yt/client/queue_client/consumer_client.h>

// 创建消费者客户端
auto consumerSchema = NTableClient::TTableSchema({
    NTableClient::TColumnSchema("partition_index", NTableClient::EValueType::Int64),
    NTableClient::TColumnSchema("offset", NTableClient::EValueType::Int64),
    NTableClient::TColumnSchema("last_consume_time", NTableClient::EValueType::Uint64)
});

auto consumerClient = CreateConsumerClient(
    apiClient,
    "//tmp/consumer",
    consumerSchema
);

// 获取子消费者客户端
TCrossClusterReference queueRef{
    .Cluster = "my-cluster",
    .Path = "//tmp/queue"
};
auto subConsumerClient = consumerClient->GetSubConsumerClient(
    apiClient,
    queueRef
);

// 收集分区信息
auto partitionsFuture = subConsumerClient->CollectPartitions(10, true);
auto partitions = partitionsFuture.Get().ValueOrThrow();

for (const auto& partition : partitions) {
    std::cout << "Partition " << partition.PartitionIndex
              << " next row: " << partition.NextRowIndex
              << " last consume: " << partition.LastConsumeTime << std::endl;
}

// 在事务中更新偏移
auto transaction = apiClient->StartTransaction(NApi::ETransactionType::Master);
subConsumerClient->Advance(
    transaction,
    0,  // partition index
    std::nullopt,  // 不检查旧偏移
    100  // 新偏移
);
transaction->Commit();
```

### 使用分区读取器
```cpp
#include <yt/yt/client/queue_client/partition_reader.h>

// 创建分区读取器配置
auto readerConfig = New<TPartitionReaderConfig>();
readerConfig->MaxRowsPerRead = 1000;
readerConfig->DataWeightPerRead = 16 * 1024 * 1024;  // 16MB

// 创建分区读取器
auto partitionReader = CreatePartitionReader(
    apiClient,
    queuePath,
    partitionIndex,
    lowerBound,  // 下界
    upperBound,  // 上界
    readerConfig
);

// 读取数据
while (true) {
    auto rowsetFuture = partitionReader->Read();
    auto rowset = rowsetFuture.Get().ValueOrThrow();

    if (rowset->GetRows().Empty()) {
        break;  // 没有更多数据
    }

    // 处理行
    for (auto row : rowset->GetRows()) {
        ProcessRow(row);
    }
}
```

## 设计原理

### 分区机制
1. **水平分区**：队列通过分区实现水平扩展
2. **有序保证**：每个分区内消息严格有序
3. **并行消费**：多个消费者可以并行消费不同分区

### 可靠性保证
1. **持久化存储**：消息持久化到表存储
2. **事务支持**：支持事务性读写
3. **副本机制**：支持多副本保证数据不丢失

### 性能优化
1. **批量处理**：支持批量读写减少RPC开销
2. **后台刷新**：可选的后台刷新机制
3. **预取**：支持数据预取提高读取性能

## 依赖项

- `yt/yt/client/api/public.h` - API客户端
- `yt/yt/client/table_client/public.h` - 表客户端
- `yt/yt/client/ypath/public.h` - YPath操作
- `yt/yt/core/actions/future.h` - 异步操作
- `yt/yt/core/misc/backoff_strategy.h` - 退避策略
- `yt/yt/core/ytree/yson_struct.h` - YSON结构

## 注意事项

1. **序列号管理**：使用自动序列号时不要手动设置
2. **事务边界**：确保在正确的事务边界内操作
3. **分区一致性**：同一分区内的消息顺序严格保证
4. **资源清理**：及时取消不需要的会话
5. **错误处理**：正确处理网络错误和重试
6. **批处理大小**：根据消息大小调整批处理参数

## 相关模块

- `yt/yt/server/lib/queues` - 队列服务端实现
- `yt/yt/client/table_client` - 表客户端（底层存储）
- `yt/yt/client/transaction_client` - 事务客户端
- `yt/yt/core/concurrency` - 并发控制