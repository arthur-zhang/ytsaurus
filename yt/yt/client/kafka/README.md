# YTsaurus Kafka Client 模块

## 概述

Kafka Client 模块提供了 YTsaurus 与 Apache Kafka 消息队列系统的集成接口。该模块实现了 Kafka 协议的客户端功能，支持消息生产、消费和集群管理，为 YTsaurus 与外部系统的数据交换提供桥梁。

## 核心功能

### 1. Kafka 协议实现
- **完整的 Kafka 协议支持**: 实现 Kafka 0.8+ 版本的协议
- **消息序列化**: 支持 JSON、Avro、Protobuf 等格式
- **压缩处理**: 支持 Gzip、Snappy、LZ4 等压缩算法
- **分区管理**: 自动分区选择和负载均衡

### 2. 生产者功能
- **异步发送**: 高性能异步消息发送
- **批量发送**: 批量消息聚合提高吞吐量
- **重试机制**: 自动重试失败的消息
- **事务支持**: 原子性消息发送

### 3. 消费者功能
- **拉取模式**: 高效的消息拉取机制
- **偏移量管理**: 自动或手动偏移量管理
- **消费组**: 支持消费组协调和负载均衡
- **重平衡处理**: 智能的消费组重平衡

## 主要组件

### 1. 协议层 (protocol.h/cpp)
实现 Kafka 二进制协议的编解码：
- **请求/响应**: Kafka 协议的请求响应结构
- **序列化**: 高效的二进制序列化
- **错误处理**: Kafka 错误码映射
- **版本协商**: 协议版本协商机制

### 2. 数据包层 (packet.h/cpp)
网络数据包处理：
- **数据包封装**: Kafka 消息的数据包格式
- **校验和**: 数据完整性校验
- **分片处理**: 大消息的分片和重组
- **压缩处理**: 数据包的压缩和解压缩

### 3. 请求层 (requests.h/cpp)
各种 Kafka 操作的请求实现：
- **元数据请求**: 获取集群元数据信息
- **生产请求**: 消息发送请求
- **消费请求**: 消息拉取请求
- **偏移量请求**: 偏移量管理请求

### 4. 错误处理 (error.h)
Kafka 错误处理：
```cpp
enum class EKafkaErrorCode {
    None = 0,
    Unknown = -1,
    OffsetOutOfRange = 1,
    CorruptMessage = 2,
    UnknownTopicOrPartition = 3,
    InvalidMessageSize = 4,
    // ... 更多错误码
};
```

## 使用方法

### 1. 基本生产者使用

```cpp
#include <yt/yt/client/kafka/public.h>
#include <yt/yt/client/kafka/protocol.h>
#include <yt/yt/client/kafka/requests.h>

using namespace NYT::NKafkaClient;

// 创建 Kafka 生产者
auto producer = CreateKafkaProducer({
    .Brokers = {"kafka1:9092", "kafka2:9092"},
    .Topic = "yt-events",
    .Compression = EKafkaCompression::Lz4,
    .BatchSize = 1000,
    .Timeout = TDuration::Seconds(30)
});

// 发送消息
auto message = CreateKafkaMessage()
    .SetKey("user-123")
    .SetValue(R"({"action": "login", "timestamp": 1234567890})")
    .SetHeaders({{"source", "yt-system"}});

producer->SendAsync(message)
    .Subscribe([] (const TError& error) {
        if (error.IsOK()) {
            YT_LOG_INFO("Message sent successfully");
        } else {
            YT_LOG_ERROR("Failed to send message: %v", error);
        }
    });
```

### 2. 消费者使用

```cpp
// 创建 Kafka 消费者
auto consumer = CreateKafkaConsumer({
    .Brokers = {"kafka1:9092", "kafka2:9092"},
    .Topic = "yt-events",
    .GroupId = "yt-consumer-group",
    .OffsetCommitPolicy = EOffsetCommitPolicy::Auto,
    .MaxPollRecords = 1000
});

// 消费消息
while (true) {
    auto messages = consumer->Poll(TDuration::MilliSeconds(100));

    for (const auto& message : messages) {
        ProcessMessage(message);
    }

    consumer->CommitOffsets();
}
```

### 3. 事务处理

```cpp
// 事务性消息发送
auto producer = CreateTransactionalKafkaProducer(config);

producer->BeginTransaction()
    .Then([producer] {
        return producer->SendAsync(message1);
    })
    .Then([producer] {
        return producer->SendAsync(message2);
    })
    .Then([producer] {
        return producer->CommitTransaction();
    })
    .Subscribe([] (const TError& error) {
        if (!error.IsOK()) {
            YT_LOG_ERROR("Transaction failed: %v", error);
        }
    });
```

## 性能优化

### 1. 批量发送优化
- **消息聚合**: 自动聚合小消息
- **延迟优化**: 平衡延迟和吞吐量
- **压缩优化**: 批量压缩提高效率

### 2. 连接池管理
- **连接复用**: 复用 TCP 连接
- **负载均衡**: 智能的分区选择
- **故障转移**: 自动连接切换

### 3. 内存优化
- **零拷贝**: 减少内存拷贝开销
- **内存池**: 复用内存缓冲区
- **压缩缓存**: 缓存压缩结果

## 监控和诊断

### 1. 关键指标
- **消息吞吐量**: 每秒处理的消息数
- **延迟统计**: 消息发送和接收延迟
- **错误率**: 各种错误的发生频率
- **资源使用**: 内存、网络、CPU 使用情况

### 2. 健康检查
- **连接状态**: 与 Kafka 集群的连接状态
- **分区状态**: 各分区的健康状况
- **消费者滞后**: 消费者偏移量滞后情况

## 依赖项

### 内部依赖
- `yt/yt/core/misc/public.h` - 核心公共定义
- `yt/yt/core/rpc/public.h` - RPC 通信框架

### 外部依赖
- 网络通信库
- 压缩库
- JSON/YAML 解析库
- 线程和同步库

## 版本兼容性

- **Kafka 协议**: 支持 Kafka 0.8+ 版本
- **API 兼容性**: 保持向后兼容的接口
- **格式兼容性**: 支持多种序列化格式

## 相关模块

- **Table Client**: 表数据操作
- **RPC Client**: 网络通信层
- **Formats Client**: 数据格式处理

## 参考文档

- [Kafka 协议规范](https://kafka.apache.org/protocol.html)
- [YTsaurus 外部系统集成](../../../docs/external-integration.md)
- [消息队列最佳实践](../../../docs/messaging-best-practices.md)

## 贡献指南

在修改此模块时：
1. 确保协议实现的正确性
2. 充分测试各种故障场景
3. 保持与官方 Kafka 协议的兼容性
4. 优化性能和内存使用
5. 添加详细的错误处理